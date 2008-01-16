from Products.CMFCore.utils import ToolInit
from Products.CMFQuickInstallerTool.QuickInstallerTool import AlreadyInstalled
from zope.i18nmessageid import MessageFactory
MessageFactory = MessageFactory("plone")

def initialize( context ):
    import Products.CMFQuickInstallerTool.QuickInstallerTool
    ToolInit( 'CMF QuickInstaller Tool',
                    tools = (QuickInstallerTool.QuickInstallerTool, ),
                    icon='tool.gif'
                    ).initialize( context )

    context.registerClass(
        QuickInstallerTool.QuickInstallerTool,
        meta_type="CMFQuickInstallerTool",
        constructors=(QuickInstallerTool.addQuickInstallerTool,),
        icon = 'tool.gif')
