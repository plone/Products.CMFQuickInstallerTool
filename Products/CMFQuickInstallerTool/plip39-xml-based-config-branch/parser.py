#-----------------------------------------------------------------------------
# Name:        parser.py
# Purpose:
#
# Author:      Kai Hoppert
# Firm:        tomcom GmbH
# Created:     2004/06/29
# Copyright:   (c) 2004 tomcom GmbH
# Licence:     GPL
#-----------------------------------------------------------------------------

import os
from string import strip,split
import ZConfig

def _split(s):
    return s, None, None, None

#We don't nee substitution in value because value can be a python
#or string expression
ZConfig.substitution._split=_split

class Parser:

    configName=''
    schemaName=''

    def __init__(self):
        self.data=[]

    def get_config(self,productName):
        try:
            schema = ZConfig.loadSchema(os.path.join(INSTANCE_HOME,'Products','CMFQuickInstallerTool','schemas',self.schemaName))
            config, handler = ZConfig.loadConfig(schema, os.path.join(INSTANCE_HOME,'Products',productName,'Extensions',self.configName))
        except:
            return None
        return config

    def get_data(self):
        return self.data


class ActionParser(Parser):
    """With this class you can parse action informations from xml files
    The structure for actions has be the follwing:

        filename:actions.conf
        put the file in your Extension Directory from your Product

        the tool name has be the name of the installed tool not the name from the module
        eg. portal_actions not ActionTool

        <action>
          tool toolidfromzmi
          name My Action
          id myaction
          action string:my_from
          condition member
          permission View
          category folder
          visible true
        </action>

    Key and value is every time seperated by space. The key name is everytime the same.        

    Installing actions over xml is the same as installing over python.
    The only diffrent is that you only have to write where and what do
    you want to install.
    """

    configName='actions.conf'
    schemaName='actions.xml'

    def parse(self,productName):
        config = self.get_config(productName)
        if not config:
            return 'There is no actions.conf file'

        for action in config.action:
            self.data.append({'tool':action.tool,
                              'name':action.name,
    	                      'id':action.id,
    	                      'action':action.action,
    	                      'condition':action.condition,
    	                      'permission':action.permission,
    	                      'category':action.category,
    	                      'visible':action.visible})


class ActionIconParser(Parser):
    """With this class you can parse ActionIcon informations from xml files
    The structure for actions has be the follwing:

        filename:actionicons.conf
        put the file in your Extension Directory from your Product

        the name has be the name of the installed tool not the name from the module
        eg. portal_actions not ActionTool

        <action>
          tool toolidfromzmi
          name Testaction
          id testaction
          action string:test_form
          condition member
          permission View
          category folder
          visible true
         </action>

    Key and value is every time seperated by space. The key name is everytime the same.

    Installing actions icons  over xml is the same as installing over python.
    The only diffrent is that you only have to write where and what do
    you want to install.
    """

    configName='actionicons.conf'
    schemaName='actionicons.xml'

    def parse(self,productName):
        config = self.get_config(productName)

        if not config:
            return 'There is no actionicons.conf file'

        for actionIcon in config.actionicon:
            self.data.append({'tool':actionIcon.tool,
                              'category':actionIcon.category,
                              'action_id':actionIcon.action_id,
                              'icon_expr':actionIcon.icon_expr,
                              'title':actionIcon.title,
                              'priority':actionIcon.priority})

class PropertyParser(Parser):
    """With this object you can parse property informations from xml files
    The structure for properties has be the follwing:

        filename:actions
        put the file in your Extension Directory from your Product

        the name has be the name of the installed tool not the name from the module
        eg. portal_actions not ActionTool

        <property>
          tool toolidfromzmi
          id mypropertyid
          value true
          type boolean
        </property>

    Key and value is every time seperated by space. The key name is everytime the same.

    If you choose a boolean value only true or false is allowed not 1 or 0.
    
    Installing Properties over xml is the same as Creating them over
    ZMI choose a id choose a value and choose a type.
    """

    configName='properties.conf'
    schemaName='properties.xml'

    def parse(self,productName):
        config = self.get_config(productName)

        if not config:
            return 'There is no properties.conf file'

        for property in config.property:
            if property.type=='lines':
                property.value=split(property.value,';')
            self.data.append({'tool':property.tool,
                              'id':property.id,
                              'value':property.value,
                              'type':property.type})

class DependencyParser(Parser):
    """With this class you can parse dependency informations from xml files
    The structure for dependency has be the follwing:

        filename:dependencies.conf
        put the file in your Extension Directory from your Product

        the product Name has be the same as the root directory name from the product.
        How it is displayed in Quickinstaller.
        <dependency>
          product ProductName
        </dependency>

    Key and value is every time seperated by space. The key name is everytime the same.        

    """

    configName='dependencies.conf'
    schemaName='dependencies.xml'

    def parse(self,productName):
        config = self.get_config(productName)
        if not config:
            return 'There is no dependencies.conf file'

        for dependency in config.dependency:
            self.data.append({'product':dependency.product})
            