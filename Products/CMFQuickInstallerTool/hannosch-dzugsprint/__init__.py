from Products.CMFCore.utils import initializeBasesPhase1,  \
    initializeBasesPhase2, ToolInit
from Products.GenericSetup import EXTENSION, profile_registry

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
        icon = 'tool.gif')

    profile_registry.registerProfile('CMFQuickInstallerTool',
            'CMFQuickInstallerTool',
            'Extension profile for CMFQuickInstallerTool',
            'profiles/default',
            'CMFQuickInstallerTool',
            EXTENSION,
            for_=None)
