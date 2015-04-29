# Introduction #

Wing just updated the Customer, Vehicle, Workorder wrapper classes in the code repository so that the initializer for the objects sets the internal data fields to None instead of empty strings.  This introduces a conflict between the requirements for the Model implementation and for the View.  We need to resolve this issue soon.


# Details #

The conflict here occurs for the following reason:

  * On the database side, we want to store empty fields with the None value rather than with empty strings.
  * On the UI level, html doesn't understand None, so will need empty strings.

Because of this conflict, we need to agree on a design for the internal representation of empty fields in the wrapper objects and on a technique for providing the correct representation for each side.

I temporarily hacked the wrapper classes so that the getter methods invoke a nz() function call on the internal value before returning it to the caller.

_def nz(val): return "" if val is None else val_

As long as the clients outside the Model use the getters for accessing the data members of these classes, there should be no problems.  The main question is whether the UI layer would be cleaner by accessing the data more directly through the data members or can work effectively with getter methods.

One possibility, of course, would be for the View to wrap all of the data member accesses with nz().