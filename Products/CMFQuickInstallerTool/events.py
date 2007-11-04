from zope.component import adapter
from zope.annotation.interfaces import IAnnotatable
from Products.GenericSetup.interfaces import IBeforeProfileImportEvent
from Products.GenericSetup.interfaces import IProfileImportedEvent
from Products.CMFCore.utils import getToolByName


def findProductForProfile(context, profile_id):
    qi=getToolByName(context, "portal_quickinstaller", None)
    if qi is None:
        return None

    if profile_id.startswith("profile-"):
        profile_id=profile_id[8:]

    for product in qi.listInstallableProducts(skipInstalled=False):
        profiles=qi.getInstallProfiles(product["id"])
        if profile_id in profiles:
            return product["id"]

    return None


@adapter(IBeforeProfileImportEvent)
def handleBeforeProfileImportEvent(event):
    if event.profile_id is None:
        return

    context=event.tool

    # We need a request to scribble some data in
    request=getattr(context, "REQUEST", None)
    if request is None:
        return

    product=findProductForProfile(context, event.profile_id)
    if product is None:
        return

    storage=IAnnotatable(request)
    storage["Products.CMFQuickInstallerTool.GenericSetupEvents"]=dict(product=product)



@adapter(IProfileImportedEvent)
def handleProfileImportedEvent(event):
    if event.profile_id is None:
        return

    context=event.tool

    # We need a request to scribble some data in
    if not hasattr(context, "REQUEST"):
        return

