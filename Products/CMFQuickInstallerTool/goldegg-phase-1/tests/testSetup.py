#
# Setup tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFTestCase import CMFTestCase

CMFTestCase.installProduct('CMFQuickInstallerTool')
CMFTestCase.setupCMFSite()


class TestQuickInstaller(CMFTestCase.CMFTestCase):

    def afterSetUp(self):
        self.addProduct('CMFQuickInstallerTool')
        self.qi = getattr(self.portal, 'portal_quickinstaller', None)

    def testTool(self):
        self.failUnless('portal_quickinstaller' in self.portal.objectIds())

    def testIsInstalled(self):
        self.failUnless(self.qi.isProductInstalled('CMFQuickInstallerTool'))

    def testIsLockedAndHidden(self):
        for p in self.qi.listInstalledProducts(showHidden=1):
            if p['id'] == 'CMFQuickInstallerTool':
                self.failUnless(p['isLocked'])
                self.failUnless(p['isHidden'])
                break
        else:
            self.fail('CMFQuickInstallerTool is not installed')

    def testIsNotListedAsInstallable(self):
        prods = self.qi.listInstallableProducts()
        prods = [x['id'] for x in prods]
        self.failIf('CMFQuickInstallerTool' in prods)

    def testIsNotListedAsInstalled(self):
        prods = self.qi.listInstalledProducts()
        prods = [x['id'] for x in prods]
        self.failIf('CMFQuickInstallerTool' in prods)

    def testUpgradeQuickInstaller(self):
        # "Uninstall"
        self.qi._delObject('CMFQuickInstallerTool')
        # Should be marked as installed
        self.qi.installProduct('CMFQuickInstallerTool')
        self.failUnless(self.qi.isProductInstalled('CMFQuickInstallerTool'))
        # But neither locked nor hidden
        for p in self.qi.listInstalledProducts(showHidden=1):
            if p['id'] == 'CMFQuickInstallerTool':
                self.failIf(p['isLocked'])
                self.failIf(p['isHidden'])
                break
        else:
            self.fail('CMFQuickInstallerTool is not installed')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestQuickInstaller))
    return suite

if __name__ == '__main__':
    framework()

