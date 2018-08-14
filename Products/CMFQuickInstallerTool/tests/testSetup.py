# -*- coding: utf-8 -*-
#
# Setup tests
#
from Products.CMFQuickInstallerTool.testing import CQI_INTEGRATION_TESTING

import unittest


class TestQuickInstaller(unittest.TestCase):

    layer = CQI_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = getattr(self.portal, 'portal_quickinstaller', None)

    def testTool(self):
        self.assertTrue('portal_quickinstaller' in self.portal.objectIds())

    def testIsNotInstalled(self):
        self.assertFalse(self.qi.isProductInstalled('CMFQuickInstallerTool'))
        self.assertFalse(self.qi.isProductInstalled(
            'Products.CMFQuickInstallerTool'))

    def testIsNotListedAsInstallable(self):
        prods = self.qi.listInstallableProducts()
        prods = [x['id'] for x in prods]
        self.assertFalse('CMFQuickInstallerTool' in prods)
        self.assertFalse('Products.CMFQuickInstallerTool' in prods)

    def testIsNotListedAsInstalled(self):
        prods = self.qi.listInstalledProducts()
        prods = [x['id'] for x in prods]
        self.assertFalse('CMFQuickInstallerTool' in prods)
        self.assertFalse('Products.CMFQuickInstallerTool' in prods)

    def test_getToolByName(self):
        from Products.CMFCore.utils import getToolByName
        self.assertIsNotNone(
            getToolByName(self.portal, 'portal_quickinstaller', None))

    def test_uninstall_self_via_portal_setup(self):
        self.assertTrue('portal_quickinstaller' in self.portal.objectIds())
        setup_tool = self.portal.portal_setup
        name = 'Products.CMFQuickInstallerTool:uninstall'
        if name not in [i['id'] for i in setup_tool.listProfileInfo()]:
            from Products.GenericSetup import profile_registry
            from Products.GenericSetup import EXTENSION
            profile_registry.registerProfile(
                'uninstall',
                'CMFQI uninstall profile',
                'Uninstall profile for CMFQuickInstallerTool',
                'profiles/uninstall',
                'Products.CMFQuickInstallerTool',
                EXTENSION,
                for_=None)

        setup_tool.runAllImportStepsFromProfile(
            'Products.CMFQuickInstallerTool:uninstall')
        self.assertFalse('portal_quickinstaller' in self.portal.objectIds())


class TestInstalledProduct(unittest.TestCase):

    layer = CQI_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = getattr(self.portal, 'portal_quickinstaller', None)

    def testSlotsMigration(self):
        from Products.CMFQuickInstallerTool.InstalledProduct import \
            InstalledProduct
        # leftslots and rightslots have been class variables ones. Make sure
        # using old instances without these properties doesn't break.

        # New instances should have the properties
        new = InstalledProduct('new')
        self.assertTrue(hasattr(new, 'leftslots'))
        self.assertTrue(hasattr(new, 'rightslots'))

        # Now emulate an old instance
        old = InstalledProduct('old')
        del(old.leftslots)
        del(old.rightslots)

        # Make sure calling the API will give you no error but silently
        # add the property
        left = old.getLeftSlots()
        self.assertTrue(left == [])
        self.assertTrue(old.leftslots == [])

        right = old.getRightSlots()
        self.assertTrue(right == [])
        self.assertTrue(old.rightslots == [])

        slots = old.getSlots()
        self.assertTrue(slots == [])
