
from . import abstracttriangulation
#from . import algebraicapproximation
from . import algebraicnumber
from . import encoding
from . import error
from . import interval
from . import io
from . import isometry
from . import lamination
from . import layeredtriangulation
from . import matrix
from . import numberfield
from . import numberring
from . import permutation
from . import polynomial
from . import splittingsequence
from . import symboliccomputation
from . import types
from . import utilities

# Set up shorter names for all of the different classes and some common constructors.
AbstractTriangle = abstracttriangulation.AbstractTriangle
AbstractTriangulation = abstracttriangulation.AbstractTriangulation
AlgebraicNumber = algebraicnumber.AlgebraicNumber
AlgebraicApproximation = algebraicnumber.AlgebraicApproximation
PartialFunction = encoding.PartialFunction
PLFunction = encoding.PLFunction
Encoding = encoding.Encoding
AbortError = error.AbortError
ApproximationError = error.ApproximationError
AssumptionError = error.AssumptionError
ComputationError = error.ComputationError
Interval = interval.Interval
Isometry = isometry.Isometry
Lamination = lamination.Lamination
LayeredTriangulation = layeredtriangulation.LayeredTriangulation
Matrix = matrix.Matrix
NumberField = numberfield.NumberField
NumberRing = numberring.NumberRing
Permutation = permutation.Permutation
Polynomial = polynomial.Polynomial
SplittingSequence = splittingsequence.SplittingSequence

Empty_Matrix = matrix.Empty_Matrix
Id_Matrix = matrix.Id_Matrix
Zero_Matrix = matrix.Zero_Matrix
Integer_Type = types.Integer_Type
String_Type = types.String_Type
height_int = algebraicnumber.height_int

product = utilities.product

package = io.package
depackage = io.depackage

