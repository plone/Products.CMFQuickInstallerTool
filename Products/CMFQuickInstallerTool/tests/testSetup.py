# -*- coding: utf-8 -*-
#
# Setup tests
#
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from Products.CMFQuickInstallerTool.InstalledProduct import InstalledProduct
import unittest


class TestQuickInstaller(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = getattr(self.portal, 'portal_quickinstaller', None)

    def testTool(self):
        self.assertTrue('portal_quickinstaller' in self.portal.objectIds())

    def testIsNotInstalled(self):
        self.assertFalse(self.qi.isProductInstalled('CMFQuickInstallerTool'))

    def testIsNotListedAsInstallable(self):
        prods = self.qi.listInstallableProducts()
        prods = [x['id'] for x in prods]
        self.assertFalse('CMFQuickInstallerTool' in prods)

    def testIsNotListedAsInstalled(self):
        prods = self.qi.listInstalledProducts()
        prods = [x['id'] for x in prods]
        self.assertFalse('CMFQuickInstallerTool' in prods)


class TestInstalledProduct(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = getattr(self.portal, 'portal_quickinstaller', None)

    def testSlotsMigration(self):
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
