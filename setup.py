from setuptools import setup, find_packages
import sys, os

version = '2.1.3'

setup(name='Products.CMFQuickInstallerTool',
      version=version,
      description="CMFQuickInstallerTool is a facility for comfortable "
                  "activation/deactivation of CMF compliant products.",
      long_description="""\
      """,
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
      ],
      keywords='Zope CMF Plone quickinstall install activation',
      author='Philipp Auersperg',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/collective/CMFQuickInstallerTool/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      download_url='http://plone.org/products/cmfquickinstallertool/releases',
      install_requires=[
        'setuptools',
      ],
)
