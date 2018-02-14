# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFQuickInstallerTool import tests
from Products.CMFQuickInstallerTool.testing import CQI_INTEGRATION_TESTING
from zope.configuration import xmlconfig

import unittest


class TestQuickInstallerTool(unittest.TestCase):

    layer = CQI_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal.portal_quickinstaller

    def _installed(self):
        return [p['id'] for p in self.qi.listInstalledProducts()]

    def _available(self):
        return [p['id'] for p in self.qi.listInstallableProducts()]

    def testInstallUninstallProduct(self):
        import pkg_resources
        try:
            pkg_resources.get_distribution('Products.CMFPlacefulWorkflow')
        except pkg_resources.DistributionNotFound:
            return
        # CMFPlacefulWorkflow should be uninstalled, we install it and
        # it should not show up as installable
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.qi.installProducts(['CMFPlacefulWorkflow', ])
        self.assertTrue('CMFPlacefulWorkflow' in self._installed())
        self.assertFalse('CMFPlacefulWorkflow' in self._available())
        self.qi.uninstallProducts(['CMFPlacefulWorkflow', ])
        self.assertTrue('CMFPlacefulWorkflow' in self._available())
        self.assertFalse('CMFPlacefulWorkflow' in self._installed())

    def testLatestUpgradeProfiles(self):
        xmlconfig.file(
            'test_upgrades1.zcml',
            package=tests,
            context=self.layer['configurationContext']
        )
        latest = self.qi.getLatestUpgradeStep(
            'Products.CMFQuickInstallerTool.tests:default')
        self.assertEqual(latest, '3')

    def testLatestUpgradeProfiles2(self):
        # make sure strings don't break things
        # note that pkg_resources interprets 1 as
        # ''00000001', which is > 'banana'
        xmlconfig.file(
            'test_upgrades2.zcml',
            package=tests,
            context=self.layer['configurationContext']
        )
        latest = self.qi.getLatestUpgradeStep(
            'Products.CMFQuickInstallerTool.tests:default')
        self.assertEqual(latest, '3')


def dummy_handler():
    pass
