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

from parser import ActionParser,PropertyParser,ActionIconParser
from Products.CMFCore.utils import getToolByName
from string import join

class Installer:

    def get_tool(self,pobj,tname):
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
        print actions
        if actions:
            for action in actions:
                action_data=[]
                tname=action.get('tool',None)
                del action['tool']
                tool=self.get_tool(pobj,tname)
                if tool:
                    existing_actions=[a.id for a in tool._cloneActions()]
                    for key in action.keys():
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
                    res += tname+' does not longer exist removing of '+action['name']+' is not possible\n'                    
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
            res += 'There are no actions to create\n'

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
