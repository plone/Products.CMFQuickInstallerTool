from setuptools import setup, find_packages

version = '3.0.6'

setup(name='Products.CMFQuickInstallerTool',
      version=version,
      description="CMFQuickInstallerTool is a facility for comfortable "
                  "activation/deactivation of CMF compliant products.",
      long_description=open("README.txt").read() + "\n" + \
                       open("CHANGES.txt").read(),
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
      maintainer_email='hannosch@plone.org',
      url='http://pypi.python.org/pypi/Products.CMFQuickInstallerTool',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
        test=[
            'zope.testing',
            'Products.CMFCalendar',
            'Products.CMFTestCase',
        ]
      ),
      install_requires=[
        'setuptools',
        'zope.annotation',
        'zope.component',
        'zope.i18nmessageid',
        'zope.interface',
        'Products.CMFCore',
        'Products.GenericSetup',
        'Acquisition',
        'DateTime',
        'Zope2',
      ],
)
