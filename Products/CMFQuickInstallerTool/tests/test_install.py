# -*- coding: utf-8 -*-
from plone.app import testing
from plone.testing import layered
from Products.CMFQuickInstallerTool.events import handleBeforeProfileImportEvent  # noqa
from Products.CMFQuickInstallerTool.events import handleProfileImportedEvent
from Products.CMFQuickInstallerTool.QuickInstallerTool import QuickInstallerTool  # noqa
from Products.GenericSetup import EXTENSION, profile_registry
import doctest
import unittest
import zope.component

import pkg_resources
try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    # assume we have an other content framework (Archetypes) here
    TESTING_FIXTURE = testing.PLONE_FIXTURE
else:
    from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
    TESTING_FIXTURE = PLONE_APP_CONTENTTYPES_FIXTURE


OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

TEST_PATCHES = {}


class QuickInstallerCaseFixture(testing.PloneSandboxLayer):

    defaultBases = (TESTING_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        sm = zope.component.getSiteManager()
        sm.registerHandler(handleBeforeProfileImportEvent)
        sm.registerHandler(handleProfileImportedEvent)

        profile_registry.registerProfile(
            'test',
            'CMFQI test profile',
            'Test profile for CMFQuickInstallerTool',
            'profiles/test',
            'Products.CMFQuickInstallerTool',
            EXTENSION,
            for_=None)

    def setUpPloneSite(self, portal):
        TEST_PATCHES['orig_isProductInstallable'] = QuickInstallerTool.isProductInstallable  # noqa

        def patched_isProductInstallable(self, productname):
            if (
                'QITest' in productname
                or 'CMFQuickInstallerTool' in productname
            ):
                return True
            return TEST_PATCHES['orig_isProductInstallable'](self, productname)
        QuickInstallerTool.isProductInstallable = patched_isProductInstallable

    def tearDownPloneSite(self, portal):
        QuickInstallerTool.isProductInstallable = TEST_PATCHES['orig_isProductInstallable']  # noqa
        profile_registry.unregisterProfile(
            'test',
            'Products.CMFQuickInstallerTool'
        )
        sm = zope.component.getSiteManager()
        sm.unregisterHandler(handleBeforeProfileImportEvent)
        sm.unregisterHandler(handleProfileImportedEvent)

CQI_FIXTURE = QuickInstallerCaseFixture()
CQI_FUNCTIONAL_TESTING = testing.FunctionalTesting(
    bases=(CQI_FIXTURE, ), name='CMFQuickInstallerToolTest:Functional')


def test_suite():
    suite = unittest.TestSuite()
    for testfile in ['actions.txt', 'profiles.txt', 'install.txt']:
        suite.addTest(layered(
            doctest.DocFileSuite(
                testfile,
                package='Products.CMFQuickInstallerTool.tests',
                optionflags=OPTIONFLAGS),
            layer=CQI_FUNCTIONAL_TESTING))
    return suite
