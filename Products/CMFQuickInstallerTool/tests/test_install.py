import doctest
import unittest

from Products.CMFTestCase import CMFTestCase
from Products.GenericSetup import EXTENSION, profile_registry
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

CMFTestCase.installProduct('CMFQuickInstallerTool')
CMFTestCase.installProduct('CMFCalendar')

CMFTestCase.setupCMFSite()

OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def registerTestProfile(test):
    profile_registry.registerProfile('test',
               'CMFQI test profile',
               'Test profile for CMFQuickInstallerTool',
               'profiles/test',
               'Products.CMFQuickInstallerTool',
               EXTENSION,
               for_=None)


def test_suite():
    return unittest.TestSuite((
        Suite('actions.txt',
              optionflags=OPTIONFLAGS,
              package='Products.CMFQuickInstallerTool.tests',
              setUp=registerTestProfile,
              test_class=CMFTestCase.FunctionalTestCase),
        Suite('profiles.txt',
              optionflags=OPTIONFLAGS,
              package='Products.CMFQuickInstallerTool.tests',
              test_class=CMFTestCase.FunctionalTestCase),
        Suite('install.txt',
              optionflags=OPTIONFLAGS,
              package='Products.CMFQuickInstallerTool.tests',
              test_class=CMFTestCase.FunctionalTestCase),
        ))
