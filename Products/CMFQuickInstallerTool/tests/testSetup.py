#
# Setup tests
#

import unittest

from Testing import ZopeTestCase
from Products.CMFTestCase import CMFTestCase

CMFTestCase.installProduct('CMFQuickInstallerTool')
CMFTestCase.setupCMFSite()

class TestQuickInstaller(CMFTestCase.CMFTestCase):

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.addProduct('CMFQuickInstallerTool')
        self.qi = getattr(self.portal, 'portal_quickinstaller', None)

    def testTool(self):
        self.failUnless('portal_quickinstaller' in self.portal.objectIds())

    def testIsNotInstalled(self):
        self.failIf(self.qi.isProductInstalled('CMFQuickInstallerTool'))

    def testIsNotListedAsInstallable(self):
        prods = self.qi.listInstallableProducts()
        prods = [x['id'] for x in prods]
        self.failIf('CMFQuickInstallerTool' in prods)

    def testIsNotListedAsInstalled(self):
        prods = self.qi.listInstalledProducts()
        prods = [x['id'] for x in prods]
        self.failIf('CMFQuickInstallerTool' in prods)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestQuickInstaller))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
