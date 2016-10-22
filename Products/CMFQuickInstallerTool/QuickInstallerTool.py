# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from AccessControl.requestmethod import postonly
from Acquisition import aq_base
from Acquisition import aq_get
from Acquisition import aq_inner
from Acquisition import aq_parent
from App.class_init import InitializeClass
from App.config import getConfiguration
from OFS.ObjectManager import ObjectManager
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject
from Products.CMFQuickInstallerTool.InstalledProduct import InstalledProduct
from Products.CMFQuickInstallerTool.interfaces import INonInstallable
from Products.CMFQuickInstallerTool.interfaces import IQuickInstallerTool
from Products.CMFQuickInstallerTool.utils import get_install_method
from Products.CMFQuickInstallerTool.utils import get_packages
from Products.GenericSetup import EXTENSION
from Products.GenericSetup.utils import _getDottedName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.annotation.interfaces import IAnnotatable
from zope.component import getAllUtilitiesRegisteredFor
from zope.component import getSiteManager
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer
import logging
import os
import pkg_resources
import warnings

try:
    pkg_resources.get_distribution('Products.CMFPlone')
except pkg_resources.DistributionNotFound:
    from Products.CMFCore.interfaces import ISiteRoot
else:
    from Products.CMFPlone.interfaces import IPloneSiteRoot as ISiteRoot

_ = MessageFactory("plone")

logger = logging.getLogger('CMFQuickInstallerTool')

# By convention the uninstall-profile is called 'uninstall'
UNINSTALL_ID = 'uninstall'

INSTALLED_PRODUCTS_HEADER = """
    Installed Products
    ====================
    """


class AlreadyInstalled(Exception):
    """ Would be nice to say what Product was trying to be installed """
    pass


def addQuickInstallerTool(self, REQUEST=None):
    """ """
    qt = QuickInstallerTool()
    self._setObject('portal_quickinstaller', qt, set_owner=False)
    if REQUEST:
        return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])


@implementer(INonInstallable)
class HiddenProducts(object):

    def getNonInstallableProducts(self):
        return ['CMFQuickInstallerTool', 'Products.CMFQuickInstallerTool']


@implementer(IQuickInstallerTool)
class QuickInstallerTool(UniqueObject, ObjectManager, SimpleItem):
    """
      Let's make sure that this implementation actually fulfills the
      'IQuickInstallerTool' API.

      >>> from zope.interface.verify import verifyClass
      >>> verifyClass(IQuickInstallerTool, QuickInstallerTool)
      True
    """

    meta_type = 'CMF QuickInstaller Tool'
    id = 'portal_quickinstaller'

    security = ClassSecurityInfo()

    manage_options = (
        {
            'label': 'Install',
            'action': 'manage_installProductsForm'},
        ) + ObjectManager.manage_options

    security.declareProtected(ManagePortal, 'manage_installProductsForm')
    manage_installProductsForm = PageTemplateFile(
        'forms/install_products_form', globals(),
        __name__='manage_installProductsForm')

    def __init__(self):
        self.id = 'portal_quickinstaller'

    @property
    def errors(self):
        return getattr(self, '_v_errors', {})

    def _init_errors(self, reset=False):
        """init or reset the list of broken products
        """
        if not self.errors or reset:
            self._v_errors = {}

    def _install_profile_info(self, productname):
        """list extension profile infos of a given name
        """
        portal_setup = getToolByName(self, 'portal_setup')
        profiles = portal_setup.listProfileInfo()

        # We are only interested in extension profiles for the product
        # TODO Remove the manual Products.* check here. It is still needed.
        profiles = [
            prof for prof in profiles
            if prof['type'] == EXTENSION
            and (
                prof['product'] == productname
                or prof['product'] == 'Products.%s' % productname
            )
        ]
        return profiles

    @security.protected(ManagePortal)
    def getInstallProfiles(self, productname):
        """ list all installer profile ids of the given name
        """
        return [prof['id'] for prof in self._install_profile_info(productname)]

    @security.protected(ManagePortal)
    def getInstallProfile(self, productname):
        """ Return the installer profile
        """
        profiles = self._install_profile_info(productname)

        # XXX Currently QI always uses the first profile
        if profiles:
            return profiles[0]
        return None

    @security.protected(ManagePortal)
    def getUninstallProfile(self, productname):
        """ Return the uninstaller profile id
        """
        profiles = self._install_profile_info(productname)

        if profiles:
            for profile in profiles:
                if profile['id'].split(':')[-1] == UNINSTALL_ID:
                    return profile
        return None

    @security.protected(ManagePortal)
    def getInstallMethod(self, productname):
        """ Return the installer method
        """
        res = get_install_method(productname)
        if res is None:
            raise AttributeError('No Install method found for '
                                 'product %s' % productname)
        return res

    @security.protected(ManagePortal)
    def getBrokenInstalls(self):
        """ Return all the broken installs """
        errs = getattr(self, "_v_errors", {})
        return errs.values()

    @security.protected(ManagePortal)
    def isProductInstallable(self, productname):
        """Asks wether a product is installable by trying to get its install
           method or an installation profile.
        """
        not_installable = []
        utils = getAllUtilitiesRegisteredFor(INonInstallable)
        for util in utils:
            not_installable.extend(util.getNonInstallableProducts())
        if productname in not_installable:
            return False
        try:
            self.getInstallMethod(productname)
            return True
        except AttributeError:
            # this means it has no install method, go on from here
            pass

        profiles = self.getInstallProfiles(productname)
        if not profiles:
            return False

        setup_tool = getToolByName(self, 'portal_setup')
        try:
            # XXX Currently QI always uses the first profile
            setup_tool.getProfileDependencyChain(profiles[0])
        except KeyError, e:
            self._init_errors()
            # Don't show twice the same error: old install and profile
            # oldinstall is test in first in other methods we may have an
            # extra 'Products.' in the namespace
            checkname = productname
            if checkname.startswith('Products.'):
                checkname = checkname[9:]
            else:
                checkname = 'Products.' + checkname
            if checkname in self.errors:
                if self.errors[checkname]['value'] == e.args[0]:
                    return False
                # A new error is found, register it
                self.errors[productname] = dict(
                    type=_(
                        u"dependency_missing",
                        default=u"Missing dependency"
                    ),
                    value=e.args[0],
                    productname=productname
                )
            else:
                self.errors[productname] = dict(
                    type=_(
                        u"dependency_missing",
                        default=u"Missing dependency"
                    ),
                    value=e.args[0],
                    productname=productname
                )
            return False
        return True

    @security.protected(ManagePortal)
    def isProductAvailable(self, productname):
        warnings.warn(
            'use instead: isProductInstallable',
            DeprecationWarning
        )
        return self.isProductInstallable(productname)

    @security.protected(ManagePortal)
    def listInstallableProfiles(self):
        """List candidate products which have a GS profiles.
        """
        portal_setup = getToolByName(self, 'portal_setup')
        profiles = portal_setup.listProfileInfo(ISiteRoot)

        # We are only interested in extension profiles
        profiles = [
            prof['product'] for prof in profiles
            if prof['type'] == EXTENSION
        ]
        return set(profiles)

    @security.protected(ManagePortal)
    def listInstallableProducts(self, skipInstalled=True):
        """List candidate CMF products for installation -> list of dicts
           with keys:(id,title,hasError,status)
        """
        self._init_errors(reset=True)

        # Returns full names with Products. prefix for all packages / products
        packages = get_packages()

        pids = []
        for pkg in packages:
            if not self.isProductInstallable(pkg):
                continue
            if pkg.startswith('Products.'):
                pkg = pkg[9:]
            pids.append(pkg)

        # Get product list from the extension profiles
        profile_pids = self.listInstallableProfiles()

        for pp in profile_pids:
            if pp in pids or pp in packages:
                continue
            if not self.isProductInstallable(pp):
                continue
            pids.append(pp)

        if skipInstalled:
            installed = [
                p['id'] for p in self.listInstalledProducts(showHidden=True)
            ]
            pids = [r for r in pids if r not in installed]

        res = []
        for pid in pids:
            installed_product = self._getOb(pid, None)
            name = pid
            profile = self.getInstallProfile(pid)
            if profile:
                name = profile['title']
            record = {'id': pid, 'title': name}
            if installed_product:
                record['status'] = installed_product.getStatus()
                record['hasError'] = installed_product.hasError()
            else:
                record['status'] = 'new'
                record['hasError'] = False
            res.append(record)
        res.sort(
            lambda x, y: cmp(
                x.get('title', x.get('id', None)),
                y.get('title', y.get('id', None))
            )
        )
        return res

    @security.protected(ManagePortal)
    def listInstalledProducts(self, showHidden=False):
        """Returns a list of products that are installed -> list of
        dicts with keys:(id, title, hasError, status, isLocked, isHidden,
        installedVersion)
        """
        pids = [o.id for o in self.objectValues()
                if o.isInstalled() and (o.isVisible() or showHidden)]
        pids = [pid for pid in pids if self.isProductInstallable(pid)]

        res = []
        for pid in pids:
            installed_product = self._getOb(pid, None)
            name = pid
            profile = self.getInstallProfile(pid)
            if profile:
                name = profile['title']

            res.append({
                'id': pid,
                'title': name,
                'status': installed_product.getStatus(),
                'hasError': installed_product.hasError(),
                'isLocked': installed_product.isLocked(),
                'isHidden': installed_product.isHidden(),
                'installedVersion': installed_product.getInstalledVersion()
            })
        res.sort(
            lambda x, y: cmp(
                x.get('title', x.get('id', None)),
                y.get('title', y.get('id', None))
            )
        )
        return res

    @security.protected(ManagePortal)
    def getProductFile(self, product_name, fname='readme.txt'):
        """Return the content of a file of the product
        case-insensitive, if it does not exist -> None
        """
        packages = get_packages()
        prodpath = packages.get(product_name)
        if prodpath is None:
            prodpath = packages.get('Products.' + product_name)

        if prodpath is None:
            return None

        # now list the directory to get the readme.txt case-insensitive
        try:
            files = os.listdir(prodpath)
        except OSError:
            return None

        for fil in files:
            if fil.lower() != fname:
                continue
            text = open(os.path.join(prodpath, fil)).read()
            try:
                return unicode(text)
            except UnicodeDecodeError:
                try:
                    return unicode(text, 'utf-8')
                except UnicodeDecodeError:
                    return unicode(text, 'utf-8', 'replace')
        return None

    @security.protected(ManagePortal)
    def getProductReadme(self, product_name, fname='readme.txt'):
        warnings.warn(
            'use instead: getProductFile',
            DeprecationWarning
        )
        return self.getProductFile(product_name, fname=fname)

    @security.protected(ManagePortal)
    def getProductDescription(self, p):
        """Returns the profile description for a given product.
        """
        profile = self.getInstallProfile(p)
        if profile is None:
            return None
        return profile.get('description', None)

    @security.protected(ManagePortal)
    def getProductVersion(self, p):
        """Return the version string stored in version.txt.
        """
        try:
            dist = pkg_resources.get_distribution(p)
            return dist.version
        except pkg_resources.DistributionNotFound:
            pass

        if "." not in p:
            try:
                dist = pkg_resources.get_distribution("Products." + p)
                return dist.version
            except pkg_resources.DistributionNotFound:
                pass

        res = self.getProductFile(p, 'version.txt')
        if res is not None:
            res = res.strip()
        return res

    @security.protected(ManagePortal)
    def snapshotPortal(self, portal):
        portal_types = getToolByName(portal, 'portal_types')
        portal_skins = getToolByName(portal, 'portal_skins')
        portal_actions = getToolByName(portal, 'portal_actions')
        portal_workflow = getToolByName(portal, 'portal_workflow')
        type_registry = getToolByName(portal, 'content_type_registry')

        state = {}
        state['leftslots'] = getattr(portal, 'left_slots', [])
        if callable(state['leftslots']):
            state['leftslots'] = state['leftslots']()
        state['rightslots'] = getattr(portal, 'right_slots', [])
        if callable(state['rightslots']):
            state['rightslots'] = state['rightslots']()
        state['registrypredicates'] = [
            pred[0] for pred in type_registry.listPredicates()
        ]

        state['types'] = portal_types.objectIds()
        state['skins'] = portal_skins.objectIds()
        actions = set()
        for category in portal_actions.objectIds():
            for action in portal_actions[category].objectIds():
                actions.add((category, action))
        state['actions'] = actions
        state['workflows'] = portal_workflow.objectIds()
        state['portalobjects'] = portal.objectIds()
        state['adapters'] = tuple(getSiteManager().registeredAdapters())
        state['utilities'] = tuple(getSiteManager().registeredUtilities())

        jstool = getToolByName(portal, 'portal_javascripts', None)
        state['resources_js'] = jstool and jstool.getResourceIds() or []
        csstool = getToolByName(portal, 'portal_css', None)
        state['resources_css'] = csstool and csstool.getResourceIds() or []
        return state

    @security.protected(ManagePortal)
    def deriveSettingsFromSnapshots(self, before, after):
        actions = [a for a in (after['actions'] - before['actions'])]

        adapters = []
        if len(after['adapters']) > len(before['adapters']):
            registrations = [reg for reg in after['adapters']
                             if reg not in before['adapters']]
            # TODO: expand this to actually cover adapter registrations

        utilities = []
        if len(after['utilities']) > len(before['utilities']):
            registrations = [reg for reg in after['utilities']
                             if reg not in before['utilities']]

            for registration in registrations:
                utilities.append(
                    (_getDottedName(registration.provided), registration.name)
                )

        settings = dict(
            types=[t for t in after['types'] if t not in before['types']],
            skins=[s for s in after['skins'] if s not in before['skins']],
            actions=actions,
            workflows=[
                w for w in after['workflows']
                if w not in before['workflows']
            ],
            portalobjects=[
                a for a in after['portalobjects']
                if a not in before['portalobjects']
            ],
            leftslots=[
                s for s in after['leftslots']
                if s not in before['leftslots']
            ],
            rightslots=[
                s for s in after['rightslots']
                if s not in before['rightslots']
            ],
            adapters=adapters,
            utilities=utilities,
            registrypredicates=[
                s for s in after['registrypredicates']
                if s not in before['registrypredicates']
            ],
        )

        jstool = getToolByName(self, 'portal_javascripts', None)
        if jstool is not None:
            settings['resources_js'] = [
                r for r in after['resources_js']
                if r not in before['resources_js']
            ]
            settings['resources_css'] = [
                r for r in after['resources_css']
                if r not in before['resources_css']
            ]
        return settings

    @security.protected(ManagePortal)
    def installProduct(
        self,
        product_name,
        locked=False,
        hidden=False,
        swallowExceptions=None,
        reinstall=False,
        forceProfile=False,
        omitSnapshots=True,
        profile=None,
        blacklistedSteps=None
    ):
        """Install a product by name
        """
        __traceback_info__ = (product_name, )

        if profile is not None:
            forceProfile = True

        if self.isProductInstalled(product_name):
            prod = self._getOb(product_name)
            msg = ('This product is already installed, '
                   'please uninstall before reinstalling it.')
            prod.log(msg)
            return msg

        portal = aq_parent(aq_inner(self))

        before = self.snapshotPortal(portal)

        if hasattr(self, "REQUEST"):
            reqstorage = IAnnotatable(self.REQUEST, None)
            if reqstorage is not None:
                installing = reqstorage.get(
                    "Products.CMFQUickInstaller.Installing",
                    set()
                )
                installing.add(product_name)
        else:
            reqstorage = None

        # XXX We can not use getToolByName since that returns a utility
        # without a RequestContainer. This breaks import steps that need
        # to run tools which request self.REQUEST.
        portal_setup = aq_get(portal, 'portal_setup', None, 1)
        status = None
        res = ''

        # Create a snapshot before installation
        before_id = portal_setup._mangleTimestampName(
            'qi-before-%s' % product_name
        )
        if not omitSnapshots:
            portal_setup.createSnapshot(before_id)

        install = False
        if not forceProfile:
            try:
                # Install via external method
                install = self.getInstallMethod(product_name).__of__(portal)
            except AttributeError:
                # No classic install method found
                pass

        if install and not forceProfile:
            try:
                res = install(portal, reinstall=reinstall)
            except TypeError:
                res = install(portal)
            status = 'installed'
        else:
            profiles = self.getInstallProfiles(product_name)
            if profiles:
                if profile is None:
                    profile = profiles[0]
                    if len(profiles) > 1:
                        logger.info(
                            'Multiple extension profiles found for product '
                            '%s. Used profile: %s' % (product_name, profile)
                        )

                portal_setup.runAllImportStepsFromProfile(
                    'profile-%s' % profile,
                    blacklisted_steps=blacklistedSteps,
                )
                status = 'installed'
            else:
                # No install method and no profile, log / abort?
                pass

        if reqstorage is not None:
            installing.remove(product_name)

        # Create a snapshot after installation
        after_id = portal_setup._mangleTimestampName(
            'qi-after-%s' % product_name
        )
        if not omitSnapshots:
            portal_setup.createSnapshot(after_id)

        if profile:
            # If installation was done via a profile, the settings were already
            # snapshotted in the IProfileImportedEvent handler, and we should
            # use those because the ones derived here include settings from
            # dependency profiles.
            settings = {}
        else:
            after = self.snapshotPortal(portal)
            settings = self.deriveSettingsFromSnapshots(before, after)

        rr_css = getToolByName(self, 'portal_css', None)
        if rr_css is not None:
            if (
                'resources_css' in settings
                and len(settings['resources_css']) > 0
            ):
                rr_css.cookResources()

        msg = str(res)
        version = self.getProductVersion(product_name)

        # add the product
        self.notifyInstalled(
            product_name,
            settings=settings,
            installedversion=version,
            logmsg=res,
            status=status,
            error=False,
            locked=locked,
            hidden=hidden,
            afterid=after_id,
            beforeid=before_id
        )

        prod = getattr(self, product_name)
        afterInstall = prod.getAfterInstallMethod()
        if afterInstall is not None:
            afterInstall = afterInstall.__of__(portal)
            afterRes = afterInstall(portal, reinstall=reinstall, product=prod)
            if afterRes:
                res = res + '\n' + str(afterRes)
        return res

    @postonly
    @security.protected(ManagePortal)
    def installProducts(
        self,
        products=None,
        stoponerror=True,
        reinstall=False,
        REQUEST=None,
        forceProfile=False,
        omitSnapshots=True
    ):
        """ """
        if products is None:
            products = []
        res = INSTALLED_PRODUCTS_HEADER
        # return products
        for product in products:
            res += product + ':'
            step_result = self.installProduct(
                product,
                swallowExceptions=not stoponerror,
                reinstall=reinstall,
                forceProfile=forceProfile,
                omitSnapshots=omitSnapshots
            )
            res += 'ok:\n'
            if step_result:
                res += str(step_result) + '\n'
        if REQUEST:
            url = REQUEST['HTTP_REFERER']
            if url:
                # The url should be in the portal, otherwise this could be a
                # hacking attempt.
                urltool = getToolByName(self, 'portal_url')
                # In tests, the referer can be 'localhost', which would be
                # treated as a relative url to the not existing
                # http://nohost/plone/portal_quickinstaller/localhost
                if url == 'localhost' or not urltool.isURLInPortal(url):
                    url = self.absolute_url()
            REQUEST.RESPONSE.redirect(url)
        return res

    @security.protected(ManagePortal)
    def isProductInstalled(self, productname):
        """Check wether a product is installed (by name)
        """
        ob = self._getOb(productname, None)
        return ob is not None and ob.isInstalled()

    @security.protected(ManagePortal)
    def notifyInstalled(
        self,
        product_name,
        locked=True,
        hidden=False,
        settings={},
        **kw
    ):
        """Marks a product that has been installed
        without QuickInstaller as installed
        """
        if product_name not in self.objectIds():
            ip = InstalledProduct(product_name)
            self._setObject(product_name, ip)

        installed_product = getattr(self, product_name)
        installed_product.update(
            settings,
            locked=locked,
            hidden=hidden,
            **kw
        )

    @postonly
    @security.protected(ManagePortal)
    def uninstallProducts(
        self,
        products=None,
        cascade=InstalledProduct.default_cascade,
        reinstall=False,
        REQUEST=None
    ):
        """Removes a list of products
        """
        if products is None:
            products = []
        portal_setup = getToolByName(self, 'portal_setup')
        for pid in products:
            prod = getattr(self, pid)
            prod.uninstall(cascade=cascade, reinstall=reinstall)
            if not reinstall:
                self.manage_delObjects(pid)
                profile = self.getInstallProfile(pid)
                if profile is not None:
                    # Mark profile as uninstalled/unknown.
                    profile_id = profile['id']
                    portal_setup.unsetLastVersionForProfile(profile_id)

        if REQUEST:
            return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    @postonly
    @security.protected(ManagePortal)
    def reinstallProducts(self, products, REQUEST=None, omitSnapshots=True):
        """Reinstalls a list of products, the main difference to
        uninstall/install is that it does not remove portal objects
        created during install (e.g. tools, etc.)
        """
        if isinstance(products, basestring):
            products = [products]

        # only delete everything EXCEPT portalobjects (tools etc) for reinstall
        cascade = [
            c for c in InstalledProduct.default_cascade
            if c != 'portalobjects'
        ]
        self.uninstallProducts(products, cascade, reinstall=True)
        self.installProducts(
            products,
            stoponerror=True,
            reinstall=True,
            omitSnapshots=omitSnapshots
        )

        if REQUEST:
            return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    def getQIElements(self):
        res = [
            'types', 'skins', 'actions', 'portalobjects', 'workflows',
            'leftslots', 'rightslots', 'registrypredicates',
            'resources_js', 'resources_css'
        ]
        return res

    def getAlreadyRegistered(self):
        """Get a list of already registered elements
        """
        result = {}
        products = [p for p in self.objectValues() if p.isInstalled()]
        for element in self.getQIElements():
            v = result.setdefault(element, [])
            for product in products:
                pv = getattr(aq_base(product), element, None)
                if pv:
                    v.extend(list(pv))
        return result

    @security.protected(ManagePortal)
    def isDevelopmentMode(self):
        """Is the Zope server in debug mode?
        """
        return bool(getConfiguration().debug_mode)

    @security.protected(ManagePortal)
    def getInstanceHome(self):
        """Return location of $INSTANCE_HOME
        """
        return os.environ.get('INSTANCE_HOME')

InitializeClass(QuickInstallerTool)
