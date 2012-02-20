import doctest
import unittest

import zope.component
from Products.CMFTestCase import CMFTestCase
from Products.CMFTestCase.layer import CMFSite
from Products.GenericSetup import EXTENSION, profile_registry
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

from Products.CMFQuickInstallerTool.QuickInstallerTool import QuickInstallerTool
from Products.CMFQuickInstallerTool.events import handleBeforeProfileImportEvent
from Products.CMFQuickInstallerTool.events import handleProfileImportedEvent

CMFTestCase.installProduct('CMFQuickInstallerTool')
CMFTestCase.installProduct('CMFCalendar')

CMFTestCase.setupCMFSite()

OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


class QILayer(CMFSite):

    @classmethod
    def setUp(cls):
        sm = zope.component.getSiteManager()
        sm.registerHandler(handleBeforeProfileImportEvent)
        sm.registerHandler(handleProfileImportedEvent)

        profile_registry.registerProfile('test',
                   'CMFQI test profile',
                   'Test profile for CMFQuickInstallerTool',
                   'profiles/test',
                   'Products.CMFQuickInstallerTool',
                   EXTENSION,
                   for_=None)
        
        # install a test-only patch to make sure the CMFCalendar profile is installable
        cls.orig_isProductInstallable = QuickInstallerTool.isProductInstallable
        def patched_isProductInstallable(self, productname):
            if 'CMFCalendar' in productname or 'CMFQuickInstallerTool' in productname:
                return True
            return cls.orig_isProductInstallable(self, productname)
        QuickInstallerTool.isProductInstallable = patched_isProductInstallable
    
    @classmethod
    def tearDown(cls):
        QuickInstallerTool.isProductInstallable = cls.orig_isProductInstallable

        profile_registry.unregisterProfile('test', 'Products.CMFQuickInstallerTool')

        sm = zope.component.getSiteManager()
        sm.unregisterHandler(handleBeforeProfileImportEvent)
        sm.unregisterHandler(handleProfileImportedEvent)


class QITestCase(CMFTestCase.FunctionalTestCase):
    layer = QILayer


def test_suite():
    return unittest.TestSuite((
        Suite('actions.txt',
              optionflags=OPTIONFLAGS,
              package='Products.CMFQuickInstallerTool.tests',
              test_class=QITestCase),
        Suite('profiles.txt',
              optionflags=OPTIONFLAGS,
              package='Products.CMFQuickInstallerTool.tests',
              test_class=QITestCase),
        Suite('install.txt',
              optionflags=OPTIONFLAGS,
              package='Products.CMFQuickInstallerTool.tests',
              test_class=QITestCase),
        ))
