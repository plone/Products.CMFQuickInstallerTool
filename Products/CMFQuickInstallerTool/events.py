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

    qi=getToolByName(context, "portal_quickinstaller", None)
    snapshot=qi.snapshotPortal(context.aq_parent)

    storage=IAnnotatable(request, None)
    if storage is None:
        return

    
    installing=storage.get("Products.CMFQuickInstaller.Installing", [])
    if product in installing:
        return

    if storage.has_key("Products.CMFQuickInstallerTool.Events"):
        data=storage["Products.CMFQuickInstallerTool.Events"]
    else:
        data=storage["Products.CMFQuickInstallerTool.Events"]={}
    data[event.profile_id]=dict(product=product, snapshot=snapshot)


@adapter(IProfileImportedEvent)
def handleProfileImportedEvent(event):
    if event.profile_id is None:
        return

    context=event.tool

    # We need a request to scribble some data in
    request=getattr(context, "REQUEST", None)
    if request is None:
        return

    storage=IAnnotatable(request, None)
    if storage is None:
        return

    data=storage.get("Products.CMFQuickInstallerTool.Events", [])
    if event.profile_id not in data:
        return
    info=data[event.profile_id]

    qi=getToolByName(context, "portal_quickinstaller", None)
    after=qi.snapshotPortal(context.aq_parent)


    settings=qi.deriveSettingsFromSnapshots(info["snapshot"], after)
    version=qi.getProductVersion(info["product"])
    qi.notifyInstalled(
            info["product"],
            logmsg="Installed via setup tool",
            settings=settings,
            installedversion=version,
            status='installed',
            error=False)



