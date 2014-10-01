
# This directory provides several test cases. Eventually there should be one
# for each module in the kernel. Each one provides a function main(verbose=False)
# which returns True if and only if the test succeeds. Running:
#    >>> python setup.py test
# automatically runs all tests listed here.

from . import abstracttriangulation
from . import algebraicapproximation
from . import algebraicnumber
from . import encoding
from . import interval
from . import lamination
from . import layeredtriangulation
from . import matrix
from . import numberfield
from . import permutation
from . import polynomial

