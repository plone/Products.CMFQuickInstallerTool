# -*- coding: utf-8 -*-
from Products.CMFQuickInstallerTool.tests.test_install import CQI_FUNCTIONAL_TESTING  # noqa
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.protect import createToken
from plone.testing import z2
from zExceptions import Forbidden

import unittest


class QIBrowserTest(unittest.TestCase):
    layer = CQI_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        import transaction; transaction.commit()
        self.browser = z2.Browser(app)
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,))
        self.browser.handleErrors = False

    def _get_product_for_install(self, qi):
        installable_ids = [
            product['id'] for product in qi.listInstallableProducts()
            if product['status'] == 'new' and product['hasError'] is False]
        if not installable_ids:
            raise ValueError('Cannot find any product to install.')
        # Take a known one that should be available in all Plone versions.
        # Some give problems in some version, because they may need to be made
        # available to Zope first, or their zcml loaded, or they are not
        # installable in some versions, or an Install.py works in one version
        # and is gone in another, or whatever..
        known_ids = ('Marshall', 'plone.session', 'plone.app.iterate')
        for known in known_ids:
            if known in installable_ids:
                return known
        # Fall back to the first one.
        return installable_ids[0]

    def test_installProducts_call(self):
        # It should work fine without a REQUEST argument.
        qi = self.portal.portal_quickinstaller
        product = self._get_product_for_install(qi)
        qi.installProducts(products=[product])
        # The product must have successfully been installed.
        self.assertTrue(qi.isProductInstalled(product))

    def test_installProducts_good_referrer(self):
        qi = self.portal.portal_quickinstaller
        self.request.environ['HTTP_REFERER'] = self.portal.absolute_url()
        self.request.method = 'POST'
        product = self._get_product_for_install(qi)
        qi.installProducts(products=[product], REQUEST=self.request)
        # The product must have successfully been installed.
        self.assertTrue(qi.isProductInstalled(product))
        # We should have been redirected to the good referrer.
        self.assertEqual(self.request.response.headers.get('location'),
                         self.portal.absolute_url())

    def test_installProducts_attacker(self):
        qi = self.portal.portal_quickinstaller
        self.request.environ['HTTP_REFERER'] = 'http://www.attacker.com'
        self.request.method = 'POST'
        product = self._get_product_for_install(qi)
        qi.installProducts(products=[product], REQUEST=self.request)
        # The product must have successfully been installed.
        self.assertTrue(qi.isProductInstalled(product))
        # We should NOT have been redirected to the attacker.
        self.assertEqual(self.request.response.headers.get('location'),
                         qi.absolute_url())

    def test_installProducts_post(self):
        # Access with a browser should remain working.  In manual testing I got
        # a 404 (missing docstring) and somehow the selected product for
        # install was not passed along, so nothing happened.  In this test we
        # are not checking for any attacker as referer, which is tricky to do
        # here.  We just check that the normal stuff works.
        qi = self.portal.portal_quickinstaller
        product = self._get_product_for_install(qi)
        url = '%s/installProducts' % qi.absolute_url()
        csrf_token = createToken()
        # First we need to get a url so we have a referer to get back to.
        # Otherwise we get a redirect to '', which means to 'installProducts',
        # which will fail because it is a GET request.
        self.browser.open(qi.absolute_url())
        # Now the POST.
        self.browser.post(url, 'products:list=%s&_authenticator=%s' % (
            product, csrf_token))
        # The product must have successfully been installed.
        self.assertTrue(qi.isProductInstalled(product),
                        'Failed to install %s' % product)
        self.assertEqual(
            self.browser.url,
            'http://nohost/plone/portal_quickinstaller')

    def test_installProducts_get(self):
        # Now with a GET request.
        qi = self.portal.portal_quickinstaller
        product = self._get_product_for_install(qi)
        url = '%s/installProducts' % qi.absolute_url()
        csrf_token = createToken()
        # Note: if we use 'browser.open' and pass the same url and data as in
        # 'test_installProducts_post', automatically a POST request is used.
        # We want to test a GET request here, so we need to include the data in
        # the url.
        url += '?products:list=%s&_authenticator=%s' % (
            product, csrf_token)
        self.assertRaises(Forbidden, self.browser.open, url)
        # The product must NOT have successfully been installed.
        self.failIf(
            qi.isProductInstalled(product),
            'Should not have installed %s using GET request.' % product)
