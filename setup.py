from setuptools import setup, find_packages
import sys, os

version = '2.1.8'

setup(name='Products.CMFQuickInstallerTool',
      version=version,
      description="CMFQuickInstallerTool is a facility for comfortable "
                  "activation/deactivation of CMF compliant products.",
      long_description=open("README.txt").read() + "\n" + \
                       open(os.path.join("Products", "CMFQuickInstallerTool", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
      ],
      keywords='Zope CMF Plone quickinstall install activation',
      author='Philipp Auersperg',
      author_email='plone-developers@lists.sourceforge.net',
      maintainer='Hanno Schlichting',
      maintainer_email='plone@hannosch.info',
      url='http://pypi.python.org/pypi/Products.CMFQuickInstallerTool',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
)
