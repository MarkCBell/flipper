
import sys

# The point of this is to make sure that we check integers agains the correct types regardless of which version
# of Python is being run. In Python 2.x an integer can be an int or long (Python automatically switches to longs
# when required). In Python 3.x these were unified under one type named int. Hence why we need this.

if sys.version_info >= (3, 0):
	Integer_Type = (int,)
else:
	Integer_Type = (int, long)