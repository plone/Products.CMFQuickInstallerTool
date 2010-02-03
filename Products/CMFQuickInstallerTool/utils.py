import logging
import os
import os.path

from Acquisition import aq_base
from OFS.Application import get_products
from zExceptions import BadRequest

logger = logging.getLogger('CMFQuickInstallerTool')

IGNORED = frozenset([
    'BTreeFolder2', 'ExternalEditor', 'ExternalMethod', 'Five', 'MIMETools',
    'MailHost', 'OFSP', 'PageTemplates', 'PlacelessTranslationService',
    'PluginIndexes', 'PythonScripts', 'Sessions', 'SiteAccess', 'SiteErrorLog',
    'StandardCacheManagers', 'TemporaryFolder', 'Transience', 'ZCTextIndex',
    'ZCatalog', 'ZODBMountPoint', 'ZReST', 'ZSQLMethods',
])


def updatelist(a, b, c=None):
    for l in b:
        if not l in a:
            if c is None:
                a.append(l)
            else:
                if not l in c:
                    a.append(l)


def delObjects(cont, ids):
    """ abbreviation to delete objects """
    delids=[id for id in ids if hasattr(aq_base(cont),id)]
    for delid in delids:
        try:
            cont.manage_delObjects(delid)
        except (AttributeError, KeyError, BadRequest):
            logger.warning("Failed to delete '%s' in '%s'" % (delid, cont.id))


def get_packages():
    """Returns a dict of package name to package path."""
    result = {}

    import Products
    packages = getattr(Products, '_registered_packages', ())
    for package in packages:
        name = package.__name__
        path = package.__path__[0]
        result[name] = path

    for product in get_products():
        name = product[1]
        if name in IGNORED:
            continue
        basepath = product[3]
        fullname = 'Products.' + name
        # Avoid getting products registered as packages twice
        if result.get(fullname):
            continue
        result[fullname] = os.path.join(basepath, name)

    return result
