from Products.CMFCore.utils import ToolInit
from Products.GenericSetup import EXTENSION, profile_registry

import QuickInstallerTool
from QuickInstallerTool import AlreadyInstalled

tools = ( QuickInstallerTool.QuickInstallerTool,
          )

quickinstaller_globals = globals()

def initialize( context ):
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
