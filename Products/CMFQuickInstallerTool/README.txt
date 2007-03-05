CMFQuickInstallerTool
==================

Features
----------

CMFQuickInstallerTool is a facility for comfortable activation/deactivation of
CMF compliant products inside a CMF 1.6+ site.

Therefore it has to be installed as a tool inside a CMF portal, where it stores
the information about the installed products.

The requirements for a product to be installable with QuickInstallerTool are
quite simple (almost all existing CMF  products fulfill them):

  External Product:  The product has to implement an external 
                     method 'install' in a python module 'Install.py' 
                     in its Extensions directory.
                     
                     OR
                     
                     The product ships with a GenericSetup extension profile
                     and has no install method. It can still use an uninstall
                     method for custom uninstallation tasks though.

Products can be uninstalled and QuickInstellerTool removes the following items
a product creates during install:

portal actions,
portal skins,
portal types,
portalobjects (objects created in the root of the portal),
workflows,
left and right slots (also checks them only for the portal),
resource registry entries

Attention:
QuickInstallerTool just tracks which objects are ADDED, but notwhat is changed
or deleted.

Second Attention:
QuickInstallerTool can only uninstall products that are installed via
QuickInstallerTool.

Installation
------------

- Drop the CMFQuickInstallerTool into the Products directory.

- inside the portal instanciate a CMF QuickInstaller Tool

Usage
-----

In the ZMI click on portal_quickinstaller. The management screen allows you to
select products for installation and uninstallation. You can browse into the
installed products and see what was created and the logs of the install process.

API
---

QuickInstaller is also intended to be called from other modules
in order to automate installing of application.
For API reference see interfaces/portal_quickinstaller.py

Customized uninstall
--------------------

In order to use a customize uninstall, the following
requirements must be met:

  External Product:  The product has to implement an external 
                     method 'uninstall in a python module 'Install.py' 
                     in its Extensions directory.

Please note that the customized uninstall method is invoked before (and in
addition to) the standard removal of objects.

Reinstall
---------

Reinstalling a product invokes uninstall() and install(). If you have special
code which should work differently on reinstall than uninstall/install you can
add a second argument to the install or uninstall method named 'reinstall' which
is true only for a reinstallation. In most cases you shouldn't react differently
when reinstalling!

Install:
--------

  install(portal) or install(portal, reinstall)

Uninstall:
----------

  uninstall(portal) or uninstall(portal, reinstall)

Reinstall
---------

Reinstalling a product invokes uninstall() and install(). If you have special
code which should work differently on reinstall than uninstall/install you can
add a second argument to the install or uninstall method named 'reinstall' which
is true only for a reinstallation. In most cases you shouldn't react differently
when reinstalling!
