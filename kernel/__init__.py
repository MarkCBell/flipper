
''' The flipper kernel. '''

from . import abstracttriangulation
from . import algebraicapproximation
from . import algebraicnumber
from . import encoding
from . import error
from . import equippedtriangulation
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
from . import utilities

# Set up shorter names for all of the different classes.
AbstractVertex = abstracttriangulation.AbstractVertex
AbstractEdge = abstracttriangulation.AbstractEdge
AbstractTriangle = abstracttriangulation.AbstractTriangle
AbstractTriangulation = abstracttriangulation.AbstractTriangulation
AbstractCorner = abstracttriangulation.AbstractCorner
AlgebraicApproximation = algebraicapproximation.AlgebraicApproximation
PartialFunction = encoding.PartialFunction
PLFunction = encoding.PLFunction
Encoding = encoding.Encoding
AbortError = error.AbortError
ApproximationError = error.ApproximationError
AssumptionError = error.AssumptionError
ComputationError = error.ComputationError
EquippedTriangulation = equippedtriangulation.EquippedTriangulation
Interval = interval.Interval
Isometry = isometry.Isometry
Lamination = lamination.Lamination
Triangulation3 = layeredtriangulation.Triangulation3
Matrix = matrix.Matrix
NumberField = numberfield.NumberField
PolynomialRoot = polynomial.PolynomialRoot
AlgebraicMonomial = algebraicnumber.AlgebraicMonomial
AlgebraicNumber = algebraicnumber.AlgebraicNumber
Permutation = permutation.Permutation
Polynomial = polynomial.Polynomial
SplittingSequence = splittingsequence.SplittingSequence

empty_matrix = matrix.empty_matrix
id_matrix = matrix.id_matrix
zero_matrix = matrix.zero_matrix
height_int = algebraicnumber.height_int
norm = abstracttriangulation.norm
IntegerType = types.IntegerType
StringType = types.StringType
NumberType = types.NumberType

# Functions that help with construction.
abstract_triangulation = abstracttriangulation.abstract_triangulation
algebraic_approximation = algebraicapproximation.algebraic_approximation
polynomial_root = polynomial.polynomial_root
algebraic_number = algebraicnumber.algebraic_number
interval_from_string = interval.interval_from_string  # Careful - don't overwrite kernel.interval.
number_field = numberfield.number_field

package = utilities.package
depackage = utilities.depackage
product = utilities.product

