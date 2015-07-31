
''' A module for the standard types.

Provides a standard reference for the type of integers, strings, etc. as these depend on the
version of Python being used. This is similar to the six module. '''

import sys

if sys.version_info >= (3, 0):
	StringType = str
	IntegerType = (int,)
else:
	# In Python 2.x an integer can be an int or long (Python automatically switches to longs when required).
	StringType = str
	IntegerType = (int, long)

