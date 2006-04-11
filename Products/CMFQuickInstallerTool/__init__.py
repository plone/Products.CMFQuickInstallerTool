#-----------------------------------------------------------------------------
# Name:        __init__.py
# Purpose:
#
# Author:      Philipp Auersperg
#
# Created:     2003/10/01
# RCS-ID:      $Id$
# Copyright:   (c) 2003 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------
# CMF based tool for installing/uninstalling CMF products


from Products.CMFCore.utils import initializeBasesPhase1,  \
    initializeBasesPhase2, ToolInit
    
import QuickInstallerTool
from QuickInstallerTool import AlreadyInstalled

import sys
this_module = sys.modules[ __name__ ]

tools = ( QuickInstallerTool.QuickInstallerTool,
          )

z_tool_bases = initializeBasesPhase1( tools, this_module )
quickinstaller_globals = globals()


def initialize( context ):
    initializeBasesPhase2( z_tool_bases, context )
    ToolInit( 'CMF QuickInstaller Tool',
                    tools = tools,
                    icon='tool.gif'
                    ).initialize( context )

    context.registerClass(
        QuickInstallerTool.QuickInstallerTool,
        meta_type="CMFQuickInstallerTool",
        constructors=(QuickInstallerTool.addQuickInstallerTool,),
        icon = 'tool.gif')         #Visibility was added recently, so may be a problem
