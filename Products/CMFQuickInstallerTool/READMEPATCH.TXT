1.5.1

	Oooouuuhhhh so many changes.
	ok lets begin. 

	-The parser es completly new. The *.conf files
	are now completely parsed from ZConfig. 
	For ZConfig parsing i added a schemas Folder were the xml schemas for
	every type are in.

	-A result of using ZConfig is that we now have a better xml or should
	 i better say zope xml configuration file syntax.
	
	-Configuration files are now not longer without format.
	 for example: formerly:actions , just actions.conf
	 
	-I added a support for adding action icons from xml
	
	-Change the documentation for creating *.conf files
	
	-Changed Installer. Put every installer and uninstaller method
	 pair in a own class, put get_tool in a ouwn class.
	 Changed installer and uninstaller methods to only install and uninstall

1.5.0

How To Use:

Create two files in the Extension Directory of your Product.
One called actions and the other properties.

The first,actions, fill in this way:

<portal_actions>
  name=Testaction
  id=testaction
  action=string:test_form
  condition=member
  permission=View
  category=folder
  visible=1
</portal_daytatool>

<portal_undo> 
  name=Testaction2
  id=testaction2
  action=string:test_form2
  condition=
  permission=ModifyPortalContent
  category=user
  visible=0
</portal_undo>

These two actions are examples. The xml tag provides the name where you
want to install your action. 
The rest are the id value pair you normaly fill in in zmi or you give
to the addAction method from the tool you want to install your action.
Don't change the varnames bevor the '=' these are the parameter names
you give to addAction. The Rest edit in the same way as if you put a new
action to a action provider from zmi.

The second,properties,fill in this way.

<tool_name>
  propertyname=propertyvalue=type
  propertyname=propertyvalue1,propertyvalue2,propertyvalue3=list
  propertyname=1=boolean
</tool_name>

<tool_name>
  propertyname=1=boolean
  propertyname=propertyvalue=type
  propertyname=propertyvalue1,propertyvalue2,propertyvalue3=list
  propertyname=1=boolean
  propertyname=propertyvalue1,propertyvalue2,propertyvalue3=list
</tool_name>
 
 Its the same as making actions over xml the diffrent is that you 
 have to think about is what doc you need for properties.
 You need an property id, a property value, and you have to define the type
 and seperate these three parts with a = like above. Don't care about using = in
 the value part i thought on that. The type name has be the same as the tipe name in zmi
 if you add there a property.