"""
    QuickInstaller tests.
"""

from Products.CMFTestCase import CMFTestCase
CMFTestCase.installProduct('CMFQuickInstallerTool')
CMFTestCase.installProduct('CMFCalendar')

CMFTestCase.setupCMFSite()

import unittest
from zope.testing import doctest
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def test_suite():
    return unittest.TestSuite((
        Suite('install.txt',
              optionflags=OPTIONFLAGS,
              package='Products.CMFQuickInstallerTool.tests',
              test_class=CMFTestCase.FunctionalTestCase),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
