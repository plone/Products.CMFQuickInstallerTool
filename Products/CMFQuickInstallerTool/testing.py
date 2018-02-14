# -*- coding: utf-8 -*-
from plone.app import testing
from Products.CMFQuickInstallerTool.events import handleBeforeProfileImportEvent  # noqa
from Products.CMFQuickInstallerTool.events import handleProfileImportedEvent
from Products.CMFQuickInstallerTool.QuickInstallerTool import QuickInstallerTool  # noqa
from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry

import pkg_resources
import zope.component


try:
    pkg_resources.get_distribution('plone.app.contenttypes')
except pkg_resources.DistributionNotFound:
    # assume we have an other content framework (Archetypes) here
    TESTING_FIXTURE = testing.PLONE_FIXTURE
else:
    from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
    TESTING_FIXTURE = PLONE_APP_CONTENTTYPES_FIXTURE


# We patch a method and store the original here so we can restore it later:
TEST_PATCHES = {}


class QuickInstallerInstalledFixture(testing.PloneSandboxLayer):

    defaultBases = (TESTING_FIXTURE, )
    installed_self = False

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
        qi = getattr(portal, 'portal_quickinstaller', None)
        if qi is None:
            setup_tool = portal.portal_setup
            setup_tool.runAllImportStepsFromProfile(
                'Products.CMFQuickInstallerTool:CMFQuickInstallerTool')
            self.installed_self = True

    def tearDownPloneSite(self, portal):
        if self.installed_self:
            setup_tool = portal.portal_setup
            setup_tool.runAllImportStepsFromProfile(
                'Products.CMFQuickInstallerTool:uninstall')

    def tearDownZope(self, app):
        profile_registry.unregisterProfile(
            'test',
            'Products.CMFQuickInstallerTool'
        )
        sm = zope.component.getSiteManager()
        sm.unregisterHandler(handleBeforeProfileImportEvent)
        sm.unregisterHandler(handleProfileImportedEvent)

BASE_CQI_FIXTURE = QuickInstallerInstalledFixture()
CQI_INTEGRATION_TESTING = testing.IntegrationTesting(
    bases=(BASE_CQI_FIXTURE, ), name='CMFQuickInstallerToolTest:Integration')


class QuickInstallerCaseFixture(testing.PloneSandboxLayer):

    defaultBases = (BASE_CQI_FIXTURE,)

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

    def tearDownZope(self, app):
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
