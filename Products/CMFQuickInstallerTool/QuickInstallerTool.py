#-----------------------------------------------------------------------------
# Name:        QuickInstallerTool.py
# Purpose:     
#
# Author:      Philipp Auersperg
#
# Created:     2003/10/01
# RCS-ID:      $Id: QuickInstallerTool.py,v 1.5 2003/06/09 19:08:28 zworkb Exp $
# Copyright:   (c) 2003 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

import sys
import traceback
import os

import Globals
from Globals import HTMLFile, InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import ObjectManager

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_inner, aq_parent
from App.Common import package_home

from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CMFCorePermissions import ManagePortal

from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate


from InstalledProduct import InstalledProduct

def addQuickInstallerTool(self,REQUEST=None):
    ''' '''
    qt=QuickInstallerTool()
    self._setObject('portal_quickinstaller',qt,set_owner=0)
    if REQUEST:
        return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])
    

    
class QuickInstallerTool( UniqueObject,  ObjectManager, SimpleItem  ):

    meta_type = 'CMF QuickInstaller Tool'
    id='portal_quickinstaller'
    
    security = ClassSecurityInfo()
    
    manage_options=(
        {'label':'install','action':'installForm'},
        ) +ObjectManager.manage_options
    
    installForm=ZopePageTemplate('installForm',open(os.path.join(package_home(globals()),'forms','install_products_form.pt')).read())
    security = ClassSecurityInfo()
    
    def __init__(self):
        self.id = 'portal_quickinstaller'
    
    def getInstallMethod(self,productname):
        ''' returns the installer method '''

        productInCP = self.Control_Panel.Products[productname]
        
        for mod,func in (('Install','install'),('Install','Install'),('install','install'),('install','Install')):

            if mod in productInCP.objectIds():
                modFolder = productInCP[mod]
                if func in modFolder.objectIds():
                    return modFolder[func]

            try:
                return ExternalMethod('temp','temp',productname+'.'+mod, func)
            except:
                pass
            
        return None
    
    isProductInstallable=getInstallMethod
    
    def listInstallableProducts(self,skipInstalled=1):
        ''' list candidate CMF products for installation '''
        pids=self.Control_Panel.Products.objectIds()
        
        import sys
        sys.stdout.flush()

        pids = [pid for pid in pids if self.isProductInstallable(pid)]
        sys.stdout.flush()
        
        if skipInstalled:
            installed=[p['id'] for p in self.listInstalledProducts()]
            pids=[r for r in pids if r not in installed]
            
        res=[]
        
        for r in pids:
            p=self._getOb(r,None)
            if p:
                res.append({'id':r,'status':p.getStatus(),'hasError':p.hasError()})
            else:
                res.append({'id':r,'status':'new','hasError':0})
                
        return res
    

    
    def listInstalledProducts(self):
        ''' returns a list of products that are installed -> list of strings'''
        pids = [o.id for o in self.objectValues() if o.isInstalled()]

        res=[]
        
        for r in pids:
            p=self._getOb(r,None)
            res.append({'id':r,'status':p.getStatus(),'hasError':p.hasError()})
 
        return res
        
    security.declareProtected(ManagePortal, 'installProducts')
    def installProducts(self,products=[],stoponerror=0,REQUEST=None):
        ''' '''
        res='''
    Installed Products
    ====================
    '''
        ok=1
        #return products
        for p in products:
            res += p +':'
            try:
                r=self.installProduct(p)
                res +='ok:\n'
                if r:
                    r += str(r)+'\n'
            except Exception,e:
                ok=0
                if stoponerror:
                    raise
                res += 'failed:'+str(e)+'\n'
            except :
                ok=0
                if stoponerror:
                    raise
                res += 'failed\n'
            
        if REQUEST :
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])
                    
        return res
    
    def isProductInstalled(self,productname):
        ''' checks wether a product is installed (by name) '''
        o=self._getOb(productname,None)
        return o and o.isInstalled()
        
    security.declareProtected(ManagePortal, 'installProduct')
    def installProduct(self,p):
        ''' installs a product by name '''
        
        if self.isProductInstalled(p):
            prod=self._getOb(p)
            msg='this product is already installed, please uninstall before reinstalling it'
            prod.log(msg)
            return msg
            
        portal_types=getToolByName(self,'portal_types')
        portal_skins=getToolByName(self,'portal_skins')
        portal_actions=getToolByName(self,'portal_actions')
        portal_workflow=getToolByName(self,'portal_workflow')
        portal=getToolByName(self,'portal_url').getPortalObject()
        leftslotsbefore=getattr(portal,'left_slots',[])
        rightslotsbefore=getattr(portal,'right_slots',[])
        

        emid='install'+p
        typesbefore=portal_types.objectIds()
        skinsbefore=portal_skins.objectIds()
        actionsbefore=[a.id for a in portal_actions._actions]
        workflowsbefore=portal_workflow.objectIds()
        portalobjectsbefore=portal.objectIds()
        error=0
        
        install = self.getInstallMethod(p).__of__(portal)

        try:
            tran=get_transaction()
            res=install()
            tran.commit()
            status='installed'
        except:
            tran.abort()
            tb=sys.exc_info()
            res='failed:'+'\n'+'\n'.join(traceback.format_exception(tb[0],tb[1],tb[2]))
            
            status=None
            error=1
        
        
        typesafter=portal_types.objectIds()
        skinsafter=portal_skins.objectIds()
        actionsafter=portal_actions.objectIds()
        workflowsafter=portal_workflow.objectIds()
        portalobjectsafter=portal.objectIds()
        leftslotsafter=getattr(portal,'left_slots',[])
        rightslotsafter=getattr(portal,'right_slots',[])
        
        types=[t for t in typesafter if t not in typesbefore]
        skins=[s for s in skinsafter if s not in skinsbefore]
        actions=[a.id for a in portal_actions._actions if a.id not in actionsbefore]
        workflows=[w for w in workflowsafter if w not in workflowsbefore]
        portalobjects=[a for a in portalobjectsafter if a not in portalobjectsbefore]
        leftslots=[s for s in leftslotsafter if s not in leftslotsbefore]
        rightslots=[s for s in rightslotsafter if s not in rightslotsbefore]
        
        msg=str(res)
        
        #add the product
        if p in self.objectIds():
            p=getattr(self,p)
            p.update(types,skins,actions,portalobjects,workflows,leftslots,rightslots,res,status,error)
        else:
            ip=InstalledProduct(p,types,skins,actions,portalobjects,workflows,leftslots,rightslots,res,status,error)
            self._setObject(p,ip)
            
        return res

    security.declareProtected(ManagePortal, 'uninstallProducts')
    def uninstallProducts(self, products, REQUEST=None):
        ''' removes a list of products '''
        
        for pid in products:
            prod=getattr(self,pid)
            prod.uninstall()
            
        if REQUEST:
            return REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])
    

InitializeClass( QuickInstallerTool )
