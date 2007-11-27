import logging
import os
import sys
import traceback
import transaction

from zope.component import getSiteManager
from zope.component import getAllUtilitiesRegisteredFor
from zope.interface import implements
from zope.annotation.interfaces import IAnnotatable

from AccessControl import ClassSecurityInfo
from AccessControl.requestmethod import postonly
from Acquisition import aq_base, aq_parent, aq_get

from Globals import DevelopmentMode
from Globals import InitializeClass
from Globals import INSTANCE_HOME
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import ObjectManager
from StringIO import StringIO
from ZODB.POSException import ConflictError
from ZODB.POSException import InvalidObjectReference
from zExceptions import NotFound

from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.GenericSetup import EXTENSION
from Products.GenericSetup.utils import _getDottedName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFQuickInstallerTool.interfaces import INonInstallable
from Products.CMFQuickInstallerTool.interfaces import IQuickInstallerTool
from Products.CMFQuickInstallerTool.InstalledProduct import InstalledProduct


logger = logging.getLogger('CMFQuickInstallerTool')


class AlreadyInstalled(Exception):
    """ Would be nice to say what Product was trying to be installed """
    pass

def addQuickInstallerTool(self, REQUEST=None):
    """ """
    qt = QuickInstallerTool()
    self._setObject('portal_quickinstaller', qt, set_owner=False)
    if REQUEST:
        return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])


class HiddenProducts(object):
    implements(INonInstallable)

    def getNonInstallableProducts(self):
        return ['CMFQuickInstallerTool', 'Products.CMFQuickInstallerTool']


class QuickInstallerTool(UniqueObject, ObjectManager, SimpleItem):
    """
      Let's make sure that this implementation actually fulfills the
      'IQuickInstallerTool' API.

      >>> from zope.interface.verify import verifyClass
      >>> verifyClass(IQuickInstallerTool, QuickInstallerTool)
      True
    """
    implements(IQuickInstallerTool)

    meta_type = 'CMF QuickInstaller Tool'
    id = 'portal_quickinstaller'

    security = ClassSecurityInfo()

    manage_options=(
        {'label':'Install', 'action':'manage_installProductsForm'},
        ) + ObjectManager.manage_options

    security.declareProtected(ManagePortal, 'manage_installProductsForm')
    manage_installProductsForm = PageTemplateFile(
        'forms/install_products_form', globals(),
        __name__='manage_installProductsForm')

    security = ClassSecurityInfo()

    def __init__(self):
        self.id = 'portal_quickinstaller'

    security.declareProtected(ManagePortal, 'getInstallProfiles')
    def getInstallProfiles(self, productname):
        """ Return the installer profile id
        """
        portal_setup = getToolByName(self, 'portal_setup')
        profiles = portal_setup.listProfileInfo()

        # We are only interested in extension profiles for the product
        # BBB CMF 1.6: The manual check for Products.* profiles can go away once
        # we do not support CMF 1.6 anymore.
        profiles = [prof['id'] for prof in profiles if
            prof['type'] == EXTENSION and
            (prof['product'] == productname or
             prof['product'] == 'Products.%s' % productname)]
        return profiles

    security.declareProtected(ManagePortal, 'getInstallProfile')
    def getInstallProfile(self, productname):
        """ Return the installer profile
        """
        portal_setup = getToolByName(self, 'portal_setup')
        profiles = portal_setup.listProfileInfo()

        profiles = [prof for prof in profiles if
            prof['type'] == EXTENSION and
            prof['product'] == productname]
        if profiles:
            return profiles[0]
        return None

    security.declareProtected(ManagePortal, 'getInstallMethod')
    def getInstallMethod(self, productname):
        """ Return the installer method
        """
        for mod, func in (('Install','install'),
                          ('Install','Install'),
                          ('install','install'),
                          ('install','Install')):
            if productname in self.Control_Panel.Products.objectIds():
                productInCP = self.Control_Panel.Products[productname]

                if mod in productInCP.objectIds():
                    modFolder = productInCP[mod]
                    if func in modFolder.objectIds():
                        return modFolder[func]

            try:
                return ExternalMethod('temp', 'temp', productname+'.'+mod, func)
            except RuntimeError, msg:
                # external method can throw a bunch of these
                msg = "%s, RuntimeError: %s" % (productname, msg)
                logger.log(logging.ERROR, msg)
            except (ConflictError, KeyboardInterrupt):
                pass
            except:
                # catch a string exception
                t, v, tb = sys.exc_info()

                if not getattr(self, "errors", {}):
                    self.errors = {}
                    
                if t not in ("Module Error", NotFound):
                    msg = "%s, %s: %s" % (productname, t, v)
                    logger.log(logging.ERROR, msg)
                    
                    # write into errors so user can see
                    strtb = StringIO()
                    traceback.print_tb(tb, limit=50, file=strtb)
    
                    e = {}
                    e["type"] = str(t)
                    e["value"] = str(v)
                    e["traceback"] = strtb.getvalue()
                    e["productname"] = productname
            
                    self.errors[productname] = e

        raise AttributeError, ('No Install method found for '
                               'product %s' % productname)

    security.declareProtected(ManagePortal, 'getBrokenInstalls')
    def getBrokenInstalls(self):
        """ Return all the broken installs """
        errs = getattr(self, "errors", {})
        return errs.values()
    
    security.declareProtected(ManagePortal, 'isProductInstallable')
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
            meth=self.getInstallMethod(productname)
            return True
        except (ConflictError, KeyboardInterrupt):
            raise
        except:
            if self.getInstallProfiles(productname):
                return True
            return False

    security.declareProtected(ManagePortal, 'isProductAvailable')
    isProductAvailable = isProductInstallable

    security.declareProtected(ManagePortal, 'listInstallableProducts')
    def listInstallableProducts(self, skipInstalled=True):
        """List candidate CMF products for installation -> list of dicts
           with keys:(id,title,hasError,status)
        """
        # reset the list of broken products
        self.errors = {}
        pids = self.Control_Panel.Products.objectIds()
        pids = [pid for pid in pids if self.isProductInstallable(pid)]

        if skipInstalled:
            installed=[p['id'] for p in self.listInstalledProducts(showHidden=True)]
            pids=[r for r in pids if r not in installed]

        res=[]
        for r in pids:
            p=self._getOb(r,None)
            name = r
            profile = self.getInstallProfile(r)
            if profile:
                name = profile['title']
            if p:
                res.append({'id':r, 'title':name, 'status':p.getStatus(),
                            'hasError':p.hasError()})
            else:
                res.append({'id':r, 'title':name,'status':'new', 'hasError':False})
        res.sort(lambda x,y: cmp(x.get('id',None),y.get('id',None)))
        return res

    security.declareProtected(ManagePortal, 'listInstalledProducts')
    def listInstalledProducts(self, showHidden=False):
        """Returns a list of products that are installed -> list of
        dicts with keys:(id, title, hasError, status, isLocked, isHidden,
        installedVersion)
        """
        pids = [o.id for o in self.objectValues()
                if o.isInstalled() and (o.isVisible() or showHidden)]
        pids = [pid for pid in pids if self.isProductInstallable(pid)]

        res=[]

        for r in pids:
            p = self._getOb(r,None)
            name = r
            profile = self.getInstallProfile(r)
            if profile:
                name = profile['title']
            
            res.append({'id':r,
                        'title':name,
                        'status':p.getStatus(),
                        'hasError':p.hasError(),
                        'isLocked':p.isLocked(),
                        'isHidden':p.isHidden(),
                        'installedVersion':p.getInstalledVersion()})
        res.sort(lambda x,y: cmp(x.get('id',None),y.get('id',None)))
        return res

    security.declareProtected(ManagePortal, 'getProductFile')
    def getProductFile(self,p,fname='readme.txt'):
        """Return the content of a file of the product
        case-insensitive, if it does not exist -> None
        """
        try:
            prodpath=self.Control_Panel.Products._getOb(p).home
        except AttributeError:
            return None

        #now list the directory to get the readme.txt case-insensitive
        try:
            files=os.listdir(prodpath)
        except OSError:
            return None

        for f in files:
            if f.lower()==fname:
                return open(os.path.join(prodpath,f)).read()

        return None

    security.declareProtected(ManagePortal, 'getProductReadme')
    getProductReadme=getProductFile

    security.declareProtected(ManagePortal, 'getProductVersion')
    def getProductVersion(self,p):
        """Return the version string stored in version.txt
        """
        res = self.getProductFile(p, 'version.txt')
        if res is not None:
            res = res.strip()
        return res


    security.declareProtected(ManagePortal, 'snapshotPortal')
    def snapshotPortal(self, portal):
        portal_types=getToolByName(portal,'portal_types')
        portal_skins=getToolByName(portal,'portal_skins')
        portal_actions=getToolByName(portal,'portal_actions')
        portal_workflow=getToolByName(portal,'portal_workflow')
        type_registry=getToolByName(portal,'content_type_registry')

        state={}
        state['leftslots']=getattr(portal,'left_slots',[])
        if callable(state['leftslots']):
            state['leftslots']=state['leftslots']()
        state['rightslots']=getattr(portal,'right_slots',[])
        if callable(state['rightslots']):
            state['rightslots']=state['rightslots']()
        state['registrypredicates']=[pred[0] for pred in type_registry.listPredicates()]

        state['types']=portal_types.objectIds()
        state['skins']=portal_skins.objectIds()
        actions= set()
        for category in portal_actions.objectIds():
            for action in portal_actions[category].objectIds():
                actions.add((category, action))
        state['actions']=actions
        state['workflows']=portal_workflow.objectIds()
        state['portalobjects']=portal.objectIds()
        state['adapters']= tuple(getSiteManager().registeredAdapters())
        state['utilities']= tuple(getSiteManager().registeredUtilities())

        jstool = getToolByName(portal,'portal_javascripts', None)
        if jstool is not None:
            state['resources_js']= jstool.getResourceIds()
        else:
            state['resources_js']= []
        csstool = getToolByName(portal,'portal_css', None)
        if jstool is not None:
            state['resources_css']= csstool.getResourceIds()
        else:
            state['resources_css']= []

        return state


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
                reg = (_getDottedName(registration.provided), registration.name)
                utilities.append(reg)

        settings=dict(
            types=[t for t in after['types'] if t not in before['types']],
            skins=[s for s in after['skins'] if s not in before['skins']],
            actions=actions,
            workflows=[w for w in after['workflows'] if w not in before['workflows']],
            portalobjects=[a for a in after['portalobjects']
                           if a not in before['portalobjects']],
            leftslots=[s for s in after['leftslots'] if s not in before['leftslots']],
            rightslots=[s for s in after['rightslots'] if s not in before['rightslots']],
            adapters=adapters,
            utilities=utilities,
            registrypredicates=[s for s in after['registrypredicates']
                                if s not in before['registrypredicates']],
            )

        jstool = getToolByName(self,'portal_javascripts', None)
        if jstool is not None:
            settings['resources_js']=[r for r in after['resources_js'] if r not in before['resources_js']]
            settings['resources_css']=[r for r in after['resources_css'] if r not in before['resources_css']]

        return settings


    security.declareProtected(ManagePortal, '')

    security.declareProtected(ManagePortal, 'installProduct')
    def installProduct(self, p, locked=False, hidden=False,
                       swallowExceptions=False, reinstall=False,
                       forceProfile=False, omitSnapshots=True,
                       profile=None):
        """Install a product by name
        """
        __traceback_info__ = (p,)

        if profile is not None:
            forceProfile = True

        if self.isProductInstalled(p):
            prod = self._getOb(p)
            msg = ('This product is already installed, '
                   'please uninstall before reinstalling it.')
            prod.log(msg)
            return msg

        portal=aq_parent(self)

        before=self.snapshotPortal(portal)

        if hasattr(self, "REQUEST"):
            reqstorage=IAnnotatable(self.REQUEST, None)
            if reqstorage is not None:
                key="Products.CMFQUickInstaller.Installing"
                if reqstorage.has_key(key):
                    installing=reqstorage[key]
                else:
                    installing=reqstorage[key]=set()
                installing.add(p)
        else:
            reqstorage=None

        # XXX We can not use getToolByName since that returns a utility
        # without a RequestContainer. This breaks import steps that need
        # to run tools which request self.REQUEST.
        portal_setup =  aq_get(portal, 'portal_setup', None, 1)
        status=None
        error=True
        res=''

        # Create a snapshot before installation
        before_id = portal_setup._mangleTimestampName('qi-before-%s' % p)
        if not omitSnapshots:
            portal_setup.createSnapshot(before_id)

        install = False
        if not forceProfile:
            try:
                # Install via external method
                install = self.getInstallMethod(p).__of__(portal)
            except AttributeError:
                # No classic install method found
                pass

        if install and not forceProfile:
            # Some heursitics to figure out if its already been installed
            if swallowExceptions:
                transaction.savepoint(optimistic=True)
            try:
                try:
                   res=install(portal, reinstall=reinstall)
                   # XXX log it
                except TypeError:
                    res=install(portal)
                status='installed'
                error = False
                if swallowExceptions:
                    transaction.savepoint(optimistic=True)
            except InvalidObjectReference, e:
                raise
            except:
                tb=sys.exc_info()
                if str(tb[1]).endswith('already in use.') and not reinstall:
                    self.error_log.raising(tb)
                    res='This product has already been installed without Quickinstaller!'
                    if not swallowExceptions:
                        raise AlreadyInstalled, p

                res+='failed:'+'\n'+'\n'.join(traceback.format_exception(*tb))
                try:
                    self.error_log.raising(tb)
                except AttributeError:
                    raise

                # Try to avoid reference
                del tb

                if swallowExceptions:
                    transaction.abort(sub=True)
                else:
                    raise
        else:
            profiles = self.getInstallProfiles(p)
            if profiles:
                if profile is None:
                    profile = profiles[0]
                    if len(profiles) > 1:
                        logger.log(logging.INFO,
                                   'Multiple extension profiles found for product '
                                   '%s. Used profile: %s' % (p, profile))

                portal_setup.runAllImportStepsFromProfile('profile-%s' % profile)

                status='installed'
                error = False
            else:
                # No install method and no profile, log / abort?
                pass

        if reqstorage is not None:
            installing.remove(p)

        # Create a snapshot after installation
        after_id = portal_setup._mangleTimestampName('qi-after-%s' % p)
        if not omitSnapshots:
            portal_setup.createSnapshot(after_id)

        after=self.snapshotPortal(portal)

        settings=self.deriveSettingsFromSnapshots(before, after)

        jstool = getToolByName(self,'portal_javascripts', None)
        if jstool is not None:
            if len(settings['types']) > 0:
                rr_css=getToolByName(portal,'portal_css')
                rr_css.cookResources()

        msg=str(res)
        version=self.getProductVersion(p)

        # add the product
        try:
            self.notifyInstalled(p,
                          settings=settings,
                          installedversion=version,
                          logmsg=res,
                          status=status,
                          error=error,
                          locked=locked,
                          hidden=hidden,
                          afterid=after_id,
                          beforeid=before_id)
        except InvalidObjectReference,e:
            raise
        except:
            tb=sys.exc_info()
            res+='failed:'+'\n'+'\n'.join(traceback.format_exception(*tb))
            self.error_log.raising(tb)

            # Try to avoid reference
            del tb

            if swallowExceptions:
                transaction.abort(sub=True)
            else:
                raise
        
        prod = getattr(self, p)
        afterInstall = prod.getAfterInstallMethod()
        if afterInstall is not None:
            afterInstall = afterInstall.__of__(portal)
            afterRes=afterInstall(portal, reinstall=reinstall, product=prod)
            if afterRes:
                res = res + '\n' + str(afterRes)
        
        return res

    security.declareProtected(ManagePortal, 'installProducts')
    def installProducts(self, products=[], stoponerror=False, reinstall=False,
                        REQUEST=None, forceProfile=False, omitSnapshots=True):
        """ """
        res = """
    Installed Products
    ====================
    """
        ok = True
        # return products
        for p in products:
            res += p +':'
            try:
                r=self.installProduct(p, swallowExceptions=not stoponerror,
                                      reinstall=reinstall,
                                      forceProfile=forceProfile,
                                      omitSnapshots=omitSnapshots)
                res +='ok:\n'
                if r:
                    r += str(r)+'\n'
            except InvalidObjectReference, e:
                raise
            except Exception, e:
                ok = False
                if stoponerror:
                    raise
                res += 'failed:'+str(e)+'\n'
            except:
                ok = False
                if stoponerror:
                    raise
                res += 'failed\n'

        if REQUEST :
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

        return res

    def isProductInstalled(self, productname):
        """Check wether a product is installed (by name)
        """
        o = self._getOb(productname, None)
        return o is not None and o.isInstalled()

    security.declareProtected(ManagePortal, 'notifyInstalled')
    def notifyInstalled(self,p,locked=True,hidden=False,settings={},**kw):
        """Marks a product that has been installed
        without QuickInstaller as installed
        """

        if not p in self.objectIds():
            ip = InstalledProduct(p)
            self._setObject(p,ip)
            
        p = getattr(self, p)
        p.update(settings,locked=locked, hidden=hidden, **kw)

    security.declareProtected(ManagePortal, 'uninstallProducts')
    def uninstallProducts(self, products=[],
                          cascade=InstalledProduct.default_cascade,
                          reinstall=False,
                          REQUEST=None):
        """Removes a list of products
        """
        for pid in products:
            prod=getattr(self,pid)
            prod.uninstall(cascade=cascade, reinstall=reinstall)

        if REQUEST:
            return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])
    uninstallProducts = postonly(uninstallProducts)

    security.declareProtected(ManagePortal, 'reinstallProducts')
    def reinstallProducts(self, products, REQUEST=None, omitSnapshots=True):
        """Reinstalls a list of products, the main difference to
        uninstall/install is that it does not remove portal objects
        created during install (e.g. tools, etc.)
        """
        if isinstance(products, basestring):
            products=[products]

        # only delete everything EXCEPT portalobjects (tools etc) for reinstall
        cascade=[c for c in InstalledProduct.default_cascade
                 if c != 'portalobjects']
        self.uninstallProducts(products, cascade, reinstall=True)
        self.installProducts(products,
                             stoponerror=True,
                             reinstall=True,
                             omitSnapshots=omitSnapshots)

        if REQUEST:
            return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])
    # XXX: Should be enabled once the Plone control panel supports this.
    # reinstallProducts = postonly(reinstallProducts)

    def getQIElements(self):
        res = ['types', 'skins', 'actions', 'portalobjects', 'workflows', 
                  'leftslots', 'rightslots', 'registrypredicates',
                  'resources_js', 'resources_css']
        return res

    def getAlreadyRegistered(self):
        """Get a list of already registered elements
        """
        result = {}
        products = [p for p in self.objectValues() if p.isInstalled() ]
        for element in self.getQIElements():
            v = result.setdefault(element, [])
            for product in products:
                pv = getattr(aq_base(product), element, None)
                if pv:
                    v.extend(list(pv))
        return result

    security.declareProtected(ManagePortal, 'isDevelopmentMode')
    def isDevelopmentMode(self):
        """Is the Zope server in debug mode?
        """
        return not not DevelopmentMode

    security.declareProtected(ManagePortal, 'getInstanceHome')
    def getInstanceHome(self):
        """Return location of $INSTANCE_HOME
        """
        return INSTANCE_HOME

InitializeClass(QuickInstallerTool)
