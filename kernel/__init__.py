
from . import abstracttriangulation
from . import algebraicapproximation
from . import encoding
from . import error
from . import interval
from . import isometry
from . import lamination
from . import layeredtriangulation
from . import matrix
from . import numberfield
from . import permutation
from . import polynomial
from . import splittingsequence
from . import symboliccomputation
from . import types

# Set up shorter names for all of the different classes and some common constructors.
AbstractTriangle = abstracttriangulation.AbstractTriangle
AbstractTriangulation = abstracttriangulation.AbstractTriangulation
AlgebraicApproximation = algebraicapproximation.AlgebraicApproximation
PartialFunction = encoding.PartialFunction
Encoding = encoding.Encoding
EncodingSequence = encoding.EncodingSequence
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
Permutation = permutation.Permutation
Polynomial = polynomial.Polynomial
SplittingSequence = splittingsequence.SplittingSequence

Empty_Matrix = matrix.Empty_Matrix
Id_Matrix = matrix.Id_Matrix
Zero_Matrix = matrix.Zero_Matrix
Integer_Type = types.Integer_Type
log_height_int = algebraicapproximation.log_height_int
