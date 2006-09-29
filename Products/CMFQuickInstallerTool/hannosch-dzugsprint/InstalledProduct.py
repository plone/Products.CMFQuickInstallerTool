import logging
from zope.interface import implements

from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ManagePortal
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFQuickInstallerTool.interfaces.portal_quickinstaller \
    import IInstalledProduct
from Products.CMFQuickInstallerTool.utils import updatelist, delObjects

logger = logging.getLogger('CMFQuickInstallerTool')

class InstalledProduct(SimpleItem):
    """Class storing information about an installed product

      Let's make sure that this implementation actually fulfills the
      'IInstalledProduct' API.

      >>> from zope.interface.verify import verifyClass
      >>> verifyClass(IInstalledProduct, InstalledProduct)
      True
    """
    implements(IInstalledProduct)

    meta_type = "Installed Product"

    manage_options=(
        {'label':'View','action':'manage_installationInfo'},
        ) + SimpleItem.manage_options

    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, 'manage_installationInfo')
    manage_installationInfo = PageTemplateFile(
        'forms/installed_product_overview', globals(),
        __name__='manage_installationInfo')

    leftslots=[]
    rightslots=[]
    transcript=[]
    error=False #error flag
    default_cascade=['types', 'skins', 'actions', 'portalobjects',
                     'workflows', 'slots', 'registrypredicates']

    def __init__(self, id):
        self.id=id
        self.transcript=[]
        self.locked=None
        self.hidden=None
        self.installedversion=None
        self.status='new'
        self.error=None

    security.declareProtected(ManagePortal, 'update')
    def update(self, settings, installedversion='',
               logmsg='', status='installed', error=False,
               locked=False, hidden=False):

        #check for the availability of attributes before assiging
        for att in settings.keys():
            if not hasattr(self.aq_base, att):
                setattr(self, att, [])
                
        qi = getToolByName(self, 'portal_quickinstaller')
        reg = qi.getAlreadyRegistered()

        for k in settings.keys():
            updatelist(getattr(self,k), settings[k], reg[k])

        self.transcript.insert(0, {'timestamp':DateTime(), 'msg':logmsg})
        self.locked=locked
        self.hidden=hidden
        self.installedversion=installedversion

        if status:
            self.status=status

        self.error=error

    security.declareProtected(ManagePortal, 'log')
    def log(self, logmsg):
        """Adds a log to the transcript
        """
        self.transcript.insert(0, {'timestamp':DateTime(), 'msg':logmsg})

    security.declareProtected(ManagePortal, 'hasError')
    def hasError(self):
        """Returns if the prod is in error state
        """
        return getattr(self, 'error', False)

    security.declareProtected(ManagePortal, 'isLocked')
    def isLocked(self):
        """Is the product locked for uninstall
        """
        return getattr(self, 'locked', False)

    security.declareProtected(ManagePortal, 'isHidden')
    def isHidden(self):
        """Is the product hidden
        """
        return getattr(self, 'hidden', False)

    security.declareProtected(ManagePortal, 'isVisible')
    def isVisible(self):
        return not self.isHidden()

    security.declareProtected(ManagePortal, 'isInstalled')
    def isInstalled(self):
        return self.status=='installed'

    security.declareProtected(ManagePortal, 'getStatus')
    def getStatus(self):
        return self.status

    security.declareProtected(ManagePortal, 'getTypes')
    def getTypes(self):
        return self.types

    security.declareProtected(ManagePortal, 'getSkins')
    def getSkins(self):
        return self.skins

    security.declareProtected(ManagePortal, 'getActions')
    def getActions(self):
        return self.actions

    security.declareProtected(ManagePortal, 'getPortalObjects')
    def getPortalObjects(self):
        return self.portalobjects

    security.declareProtected(ManagePortal, 'getWorkflows')
    def getWorkflows(self):
        return self.workflows

    security.declareProtected(ManagePortal, 'getLeftSlots')
    def getLeftSlots(self):
        return self.leftslots

    security.declareProtected(ManagePortal, 'getRightSlots')
    def getRightSlots(self):
        return self.rightslots

    security.declareProtected(ManagePortal, 'getSlots')
    def getSlots(self):
        return self.leftslots+self.rightslots

    security.declareProtected(ManagePortal, 'getValue')
    def getValue(self,name):
        return getattr(self,name,[])
    
    security.declareProtected(ManagePortal, 'getRegistryPredicates')
    def getRegistryPredicates(self):
        """Return the custom entries in the content_type_registry
        """
        return getattr(self, 'registrypredicates', [])

    security.declareProtected(ManagePortal, 'getTranscriptAsText')
    def getTranscriptAsText(self):
        if getattr(self,'transcript',None):
            msgs = [t['timestamp'].ISO()+'\n'+str(t['msg'])
                    for t in self.transcript]
            return '\n=============\n'.join(msgs)
        else:
            return 'no messages'

    def _getMethod(self, modfunc):
        """Returns a method
        """
        try:
            productInCP = self.Control_Panel.Products[self.id]
        except KeyError:
            return None

        for mod, func in modfunc:
            if mod in productInCP.objectIds():
                modFolder = productInCP[mod]
                if func in modFolder.objectIds():
                    return modFolder[func]

            try:
                return ExternalMethod('temp','temp',self.id+'.'+mod, func)
            except:
                pass

        return None

    security.declareProtected(ManagePortal, 'getInstallMethod')
    def getInstallMethod(self):
        """ returns the installer method """
        res = self._getMethod((('Install','install'),
                                ('Install','Install'),
                                ('install','install'),
                                ('install','Install'),
                               ))
        if res is None:
            raise AttributeError, ('No Install method found for '
                                   'product %s' % self.id)
        else:
            return res

    security.declareProtected(ManagePortal, 'getUninstallMethod')
    def getUninstallMethod(self):
        """ returns the uninstaller method """
        return self._getMethod((('Install','uninstall'),
                                ('Install','Uninstall'),
                                ('install','uninstall'),
                                ('install','Uninstall'),
                               ))

    security.declareProtected(ManagePortal, 'getAfterInstallMethod')
    def getAfterInstallMethod(self):
        """ returns the after installer method """
        return self._getMethod((('Install','afterInstall'),
                                ('install','afterInstall'),
                               ))

    security.declareProtected(ManagePortal, 'getBeforeUninstallMethod')
    def getBeforeUninstallMethod(self):
        """ returns the before uninstaller method """
        return self._getMethod((('Install','beforeUninstall'),
                                ('install','beforeUninstall'),
                               ))

    security.declareProtected(ManagePortal, 'uninstall')
    def uninstall(self, cascade=default_cascade, reinstall=False, REQUEST=None):
        """Uninstalls the product and removes its dependencies
        """

        portal=getToolByName(self,'portal_url').getPortalObject()

        # XXX eventually we will land Event system and could remove
        # this 'removal_inprogress' hack
        if self.isLocked() and getattr(portal, 'removal_inprogress', False):
            raise ValueError, 'The product is locked and cannot be uninstalled!'

        res=''
        afterRes=''

        uninstaller = self.getUninstallMethod()
        beforeUninstall = self.getBeforeUninstallMethod()

        if uninstaller:
            uninstaller = uninstaller.__of__(portal)
            try:
                res=uninstaller(portal, reinstall=reinstall)
                # XXX log it
            except TypeError:
                res=uninstaller(portal)

        if beforeUninstall:
            beforeUninstall = beforeUninstall.__of__(portal)
            beforeRes, cascade = beforeUninstall(portal, reinstall=reinstall,
                                                product=self, cascade=cascade)
        
        self._cascadeRemove(cascade)

        self.status='uninstalled'
        self.log('uninstalled\n'+str(res)+str(afterRes))

        if REQUEST and REQUEST.get('nextUrl',None):
            return REQUEST.RESPONSE.redirect(REQUEST['nextUrl'])

    def _cascadeRemove(self, cascade):
        """Cascaded removal of objects
        """
        portal=getToolByName(self,'portal_url').getPortalObject()
        
        if 'types' in cascade:
            portal_types=getToolByName(self,'portal_types')
            delObjects(portal_types, self.types)

        if 'skins' in cascade:
            portal_skins=getToolByName(self,'portal_skins')
            delObjects(portal_skins, self.skins)

        if 'actions' in cascade:
            # XXX ugly ugly :(
            portal_actions=getToolByName(self,'portal_actions')
            actids= [o.id.lower() for o in portal_actions._actions]
            delactions=[actids.index(id) for id in self.actions if id in actids]
            if delactions:
                portal_actions.deleteActions(delactions)

        if 'portalobjects' in cascade:
            delObjects(portal, self.portalobjects)

        if 'workflows' in cascade:
            portal_workflow=getToolByName(self, 'portal_workflow')
            delObjects(portal_workflow, self.workflows)

        if 'slots' in cascade:
            if self.leftslots:
                portal.left_slots=[s for s in portal.left_slots
                                   if s not in self.leftslots]
            if self.rightslots:
                portal.right_slots=[s for s in portal.right_slots
                                    if s not in self.rightslots]

        if 'registrypredicates' in cascade:
            ctr = getToolByName(self,'content_type_registry')
            ids = [id for id, predicate in ctr.listPredicates()]
            predicates=getattr(self,'registrypredicates',[])
            for p in predicates:
                if p in ids:
                    ctr.removePredicate(p)
                else:
                    logger.log("Failed to delete '%s' from content type " \
                               "registry" % p, severity=logging.WARNING)

        if self.getId() != 'ResourceRegistries' and \
           getToolByName(self,'portal_quickinstaller').isProductInstalled('ResourceRegistries'):
            rr_js=getToolByName(self,'portal_javascripts')
            for js in getattr(self,'resources_js',[]):
                rr_js.unregisterResource(js)
                
            rr_css=getToolByName(self,'portal_css')
            for css in getattr(self,'resources_css',[]):
                rr_css.unregisterResource(css)

    security.declareProtected(ManagePortal, 'getInstalledVersion')
    def getInstalledVersion(self):
        """Return the version of the product in the moment of installation
        """
        return getattr(self, 'installedversion', None)

InitializeClass(InstalledProduct)
