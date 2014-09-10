
''' A module for the standard types.

Provides a standard reference for the type of integers, strings, etc. as these depend on the
version of Python being used. This is similar to the six module. '''

import sys

if sys.version_info >= (3, 0):
	Integer_Type = (int,)
	String_Type = str
	Number_Type = (int, float)
else:
	# In Python 2.x an integer can be an int or long (Python automatically switches to longs when required).
	Integer_Type = (int, long)
	String_Type = str
	Number_Type = (int, long, float)

