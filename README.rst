Products.CMFQuickInstallerTool
==============================

Features
--------

CMFQuickInstallerTool is a facility for comfortable activation/deactivation of CMF compliant products inside a Zope/CMF site.

Therefore it has to be installed as a tool inside a CMF portal,
where it stores the information about the installed products.

The requirements for a product to be installable with QuickInstallerTool are quite simple
(almost all existing CMF products fulfill them):

- the product has to implement an external method ``install`` in a python module ``Install.py`` in its ``Extensions`` directory (old style).

OR

- The addon/product ships with a GenericSetup extension profile (but has no install method as above).
  If there are multiple profiles the alphabetically first wins.

Products can be uninstalled and QuickInstallerTool removes the following items a product creates during install:

- portal actions,
- portal skins,
- portal types,
- portal objects (objects created in the root of the portal),
- workflows,
- left and right slots (also checks them only for the portal),
- resource registry entries

.. note::
   QuickInstallerTool just tracks which objects are **added**, but not what is changed or deleted.

Usage
-----

In the ZMI click on portal_quickinstaller.
The management screen allows you to select products for installation and uninstallation.
You can browse into the installed products and see what was created and the logs of the install process.

Customized uninstall
--------------------

In order to use a customize uninstall, the following requirements must be met:

- the product has to implement an external method ``uninstall`` in a python module ``Install.py`` in its ``Extensions`` directory.
  Please note that the customized uninstall method is invoked before (and in addition to) the standard removal of objects.

OR

- the addon/product has to ship with a GenericSetup extension profile postfixed with ``uninstall``.
  That will be run on uninstall only if there is no external method ``uninstall``.


Install:
--------

  `install(portal) or install(portal, reinstall)`

Uninstall:
----------

  `uninstall(portal) or uninstall(portal, reinstall)`

Reinstall
---------

Reinstalling a product invokes uninstall() and install().
If you have special code which should work differently on reinstall than uninstall/install you can add a second argument to the install or uninstall method named 'reinstall' which is true only for a reinstallation.
In most cases you shouldn't react differently when reinstalling!
