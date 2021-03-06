# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

version = '4.0.4.dev0'
long_description = open("README.rst").read()
long_description += '\n'
long_description += open("CHANGES.rst").read()

setup(
    name='Products.CMFQuickInstallerTool',
    version=version,
    description="A facility for comfortable activation/deactivation of CMF "
                "compliant add ons for Zope.",
    long_description=long_description,
    classifiers=[
        "Development Status :: 6 - Mature",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Framework :: Zope2",
        "Framework :: Zope :: 4",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords='Zope CMF Plone quickinstall install activation',
    author='Philipp Auersperg',
    author_email='plone-developers@lists.sourceforge.net',
    maintainer='Hanno Schlichting',
    maintainer_email='hannosch@plone.org',
    url='https://pypi.org/project/Products.CMFQuickInstallerTool',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    extras_require=dict(
      test=[
          'zope.testing',
          'plone.app.testing',
          'plone.protect>=2.0.2',
      ]
    ),
    install_requires=[
      'setuptools',
      'six',
      'zope.annotation',
      'zope.component',
      'zope.i18nmessageid',
      'zope.interface',
      'Products.CMFCore',
      'Products.ExternalMethod',
      'Products.GenericSetup>=1.8.1',
      'Acquisition',
      'DateTime',
      'Zope2',
    ],
)
