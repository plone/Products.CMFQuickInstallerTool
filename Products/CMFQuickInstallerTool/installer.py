#-----------------------------------------------------------------------------
# Name:        installer.py
# Purpose:
#
# Author:      Kai Hoppert
# Firm:        tomcom GmbH
# Created:     2004/06/29
# Copyright:   (c) 2004 tomcom GmbH
# Licence:     GPL
#-----------------------------------------------------------------------------

from parser import ActionParser,PropertyParser,ActionIconParser,DependencyParser
from Products.CMFCore.utils import getToolByName
from string import join,split

class Installer:

    def get_tool(self,pobj,tname):
        if not len(split(tname,'.'))==1:
            return pobj.restrictedTraverse(split(tname,'.'))
        if tname=='portal_url':
            return getToolByName(pobj,tname).getPortalObject()
        else:
            try:
                return getToolByName(pobj,tname)
            except:
                return None


class ActionInstaller(Installer):

    def install(self,product_name,pobj):
        """Install actions to the specified tool"""
        res=''
        aparser=ActionParser()
        aparser.parse(product_name)
        actions=aparser.get_data()
        if actions:
            for action in actions:
                action_data=[]
                tname=action.get('tool',None)
                del action['tool']
                tool=self.get_tool(pobj,tname)
                if tool:
                    existing_actions=[a.id for a in tool._cloneActions()]
                    for key in action.keys():
                        if key=='visible':
                            action_data.append("%s=%s" %(key,action[key]))
                        else:
                            action_data.append("%s='%s'" %(key,action[key]))
                    if action['id'] not in existing_actions:
                        eval("tool.addAction(%s)" %join(action_data,','))
                        res += action['name']+'was successfully created\n'
                    else:
                        res += action['name']+'already exists\n'
                else:
                    res += 'tool: '+ tname + ' does not exist\n'
        else:
            res += 'There are no actions to create\n'

        return res

    def uninstall(self,product_name,pobj):
        """Install actions to the specified tool"""
        res=''
        aparser=ActionParser()
        aparser.parse(product_name)
        actions=aparser.get_data()
        if actions:
            for action in actions:
                action_data=[]
                tname=action.get('tool',None)
                tool=self.get_tool(pobj,tname)
                if tool:
                    existing_actions=[a.id for a in tool._cloneActions()]
                    if action['id'] in existing_actions:
                        tool.deleteActions([existing_actions.index(action['id'])])
                        res += action['name']+'was successfully removed\n'
                    else:
                        res += action['name']+' does not exists\n'
                else:
                    res += tname+' does not longer exist removing of '+action['name']+' is not possible\n'
        else:
            res += 'There are no actions to remove\n'

        return res

class PropertyInstaller(Installer):

    def install(self,product_name,pobj):
        """Install properties to the specified tool"""
        res=''
        pparser=PropertyParser()
        pparser.parse(product_name)
        properties=pparser.get_data()
        if properties:
            for property in properties:
                tname=property.get('tool',None)
                del property['tool']
                tool=self.get_tool(pobj,tname)
                if tool:
                    if not tool.hasProperty(property['id']):
                        tool.manage_addProperty(property['id'],property['value'],property['type'])
                        res += property['id']+'was successfully created\n'
                    else:
                        res += property['id']+'already exists\n'
                else:
                    res += 'tool: '+ tname +' does not exist\n'
        else:
            res += 'There are no properties to create\n'
            
        return res

    def uninstall(self,product_name,pobj):
        """Install properties to the specified tool"""
        res=''
        pparser=PropertyParser()
        pparser.parse(product_name)
        properties=pparser.get_data()
        if properties:
            for property in properties:
                tname=property.get('tool',None)
                tool=self.get_tool(pobj,tname)
                if tool:
                    if tool.hasProperty(property['id']):
                        tool.manage_delProperties([property['id']])
                        res += property['id']+'was successfully removed\n'
                    else:
                        res += property['id']+'does not exist \n'
                else:
                    res += tname+' does not longer exist removing of '+property['id']+' is not possible\n'                    
        else:
            res += 'There are no properties to remove\n'
            
        return res

class ActionIconInstaller(Installer):

    def install(self,product_name,pobj):
        res=''
        aiparser=ActionIconParser()
        aiparser.parse(product_name)
        action_icons=aiparser.get_data()
        if action_icons:
            for action in action_icons:
                action_data=[]
                tname=action.get('tool',None)
                del action['tool']
                tool=self.get_tool(pobj,tname)
                if tool:
                    for key in action.keys():
                        action_data.append("%s='%s'" %(key,action[key]))
                    if not tool.queryActionIcon(action['category'],action['action_id']):
                        eval("tool.addActionIcon(%s)" %join(action_data,','))
                        res += action['action_id']+'was successfully created\n'
                    else:
                        res += action['action_id']+'already exists\n'
                else:
                    res += 'tool: '+ tname + ' does not exist\n'
        else:
            res += 'There are no action icons to create\n'

        return res

    def uninstall(self,product_name,pobj):
        res=''
        aiparser=ActionIconParser()
        aiparser.parse(product_name)
        action_icons=aiparser.get_data()
        if action_icons:
            for action in action_icons:
                tname=action.get('tool',None)
                tool=self.get_tool(pobj,tname)
                if tool:
                    if tool.queryActionIcon(action['category'],action['action_id']):
                        tool.removeActionIcon(action['category'],action['action_id'])
                        res += action['action_id']+'was successfully removed\n'
                    else:
                        res += action['action_id']+'already exists\n'
                else:
                    res += tname+' does not longer exist removing of '+action['action_id']+' is not possible\n'                    
        else:
            res += 'There are no action icons to remove\n'

        return res

class DependencyInstaller:    
    
    def install(self,product_name,pobj):
        """Install Dependency Tools"""
        res=''
        dparser=DependencyParser()
        dparser.parse(product_name)
        dependencies=dparser.get_data()
        iproducts=self.get_installed_products(pobj)
        iaproducts=self.get_installable_products(pobj)
        qtool=pobj.portal_quickinstaller
        if dependencies:
            for dependency in dependencies:
                if dependency['product'] in iaproducts:
                    res += 'Try to install dependency Product: %s\n' %dependency['product']
                    qtool.installProducts(products=[dependency['product']])
                elif dependency['product'] in iproducts:
                    res += 'Dependency Product: %s is already installed\n' %dependency['product']
                else:
                    errormsg = 'failed:\n%s is not avaliable\n' %dependency['product']
                    res += errormsg
                    qtool.error_log.raising(errormsg)
        return res
    
    def uninstall(self,product_name,pobj):
        """UnInstall Dependency Tools"""
        res=''
        dparser=DependencyParser()
        dparser.parse(product_name)
        dependencies=dparser.get_data()
        iproducts=self.get_installed_products(pobj)
        iproducts.remove(product_name)
        dep_dict=self.get_other_product_dependencies(iproducts,pobj)
        qtool=pobj.portal_quickinstaller
        if dependencies:
            for dependency in dependencies:
                if dependency['product'] in dep_dict.keys():
                    res += "Can't uninstall Product Dependency: %s\n" %dependency['product']
                    res += 'This tool is already needed from : ' +','.join(dep_dict[dependency['product']])
                elif dependency['product'] not in iproducts:
                    errormsg='failed:\n check your dependency to Product %s. It is NOT INSTALLED or DOES NOt EXISTS\n' %dependency['product']
                    res += errormsg
                    qtool.error_log.raising(errormsg)
                else:
                    res += 'Try to uninstall: %s\n' %dependency['product']
                    qtool.uninstallProducts(products=[dependency['product']])
                    qtool.error_log.raising('failed:\n%s is not avaliable\n' %dependency['product'])
        return res

    def get_other_product_dependencies(self,iproducts,pobj):
        dep_dict = {}
        for iproduct in iproducts:
            dparser=DependencyParser()
            dparser.parse(iproduct)
            dependencies=dparser.get_data()
            if dependencies:
                for dependency in dependencies:
                    if dependency['product'] not in dep_dict.keys():
                        dep_dict[dependency['product']]=[iproduct]
                    elif dependency['product'] in dep_dict.keys():
                        dep_dict[dependency['product']].append(iproduct)
        return dep_dict
                        
    def get_installed_products(self,pobj):
        qtool=pobj.portal_quickinstaller
        products=qtool.listInstalledProducts()
        return [x['id'] for x in products]

    def get_installable_products(self,pobj):
        qtool=pobj.portal_quickinstaller
        products=qtool.listInstallableProducts()
        return [x['id'] for x in products]

def install_from_xml(self,productName):
    """It would be nice if in future only this method is called from quickinstaller
       and all configuration script will be done in xml and the Quickinstaller install
       the tools"""
    res=''

    Action=ActionInstaller()
    Property=PropertyInstaller()
    ActionIcon=ActionIconInstaller()

    res +=Action.install(productName,self)
    res +=Property.install(productName,self)
    res +=ActionIcon.install(productName,self)

    return res

def uninstall_from_xml(self,productName):
    res=''

    Action=ActionInstaller()
    Property=PropertyInstaller()
    ActionIcon=ActionIconInstaller()

    res +=Action.uninstall(productName,self)
    res +=Property.uninstall(productName,self)
    res +=ActionIcon.uninstall(productName,self)

    return res

def install_before(self,productName):
    #hhmm a dependency Product should be installed before
    #the product and all other is installed the same for uninstall 
    res=''
    Dependency=DependencyInstaller()

    res +=Dependency.install(productName,self)

    return res

def uninstall_before(self,productName):
    res=''
    Dependency=DependencyInstaller()

    res +=Dependency.uninstall(productName,self)

    return res
