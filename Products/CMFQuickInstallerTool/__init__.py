# -*- coding: utf-8 -*-
from Products.CMFCore.utils import ToolInit
from Products.CMFQuickInstallerTool.QuickInstallerTool import AlreadyInstalled

# this is probably a shortcut. don't let pyflakes complain
AlreadyInstalled


def initialize(context):
    from Products.CMFQuickInstallerTool.QuickInstallerTool import QuickInstallerTool  # noqa
    from Products.CMFQuickInstallerTool.QuickInstallerTool import addQuickInstallerTool  # noqa
    ToolInit(
        'CMF QuickInstaller Tool',
        tools=(QuickInstallerTool, ),
        icon='tool.gif'
    ).initialize(context)

    context.registerClass(
        QuickInstallerTool,
        meta_type="CMFQuickInstallerTool",
        constructors=(addQuickInstallerTool, ),
        icon='tool.gif'
    )
