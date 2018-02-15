# -*- coding: utf-8 -*-
from plone.testing import layered
from Products.CMFQuickInstallerTool.testing import CQI_FUNCTIONAL_TESTING
from Products.CMFQuickInstallerTool.testing import CQI_INTEGRATION_TESTING

import doctest
import unittest


OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def test_suite():
    suite = unittest.TestSuite()
    for testfile in ['actions.txt', 'profiles.txt']:
        suite.addTest(layered(
            doctest.DocFileSuite(
                testfile,
                package='Products.CMFQuickInstallerTool.tests',
                optionflags=OPTIONFLAGS),
            layer=CQI_INTEGRATION_TESTING))
    for testfile in ['install.txt']:
        suite.addTest(layered(
            doctest.DocFileSuite(
                testfile,
                package='Products.CMFQuickInstallerTool.tests',
                optionflags=OPTIONFLAGS),
            layer=CQI_FUNCTIONAL_TESTING))
    return suite
