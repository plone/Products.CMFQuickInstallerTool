from zope.interface import Interface

class INonInstallable(Interface):

    def getNonInstallableProducts():
        """Returns a list of products that should not be available for
           installation.
        """

class IInstallable(Interface):
    """Used by QuickInstallerTool to only list extension profiles registered for IInstallable
       interface or not specified ('for' attribute not specified in the registerProfile zcml directive).
       This fixes extension profiles used with an upgradeStep showing up in the list returned by listProfileInfo.
    """
