
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
from . import matrix
from . import numberfield
from . import permutation
from . import polynomial
from . import splittingsequence
from . import symboliccomputation
from . import types
from . import triangulation3
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
Matrix = matrix.Matrix
NumberField = numberfield.NumberField
PolynomialRoot = polynomial.PolynomialRoot
AlgebraicMonomial = algebraicnumber.AlgebraicMonomial
AlgebraicNumber = algebraicnumber.AlgebraicNumber
Permutation = permutation.Permutation
Polynomial = polynomial.Polynomial
SplittingSequence = splittingsequence.SplittingSequence
Triangulation3 = triangulation3.Triangulation3

empty_matrix = matrix.empty_matrix
id_matrix = matrix.id_matrix
zero_matrix = matrix.zero_matrix
height_int = algebraicnumber.height_int
norm = abstracttriangulation.norm
IntegerType = types.IntegerType
StringType = types.StringType
NumberType = types.NumberType

# Functions that help with construction.
create_abstract_triangulation = abstracttriangulation.create_abstract_triangulation
create_algebraic_approximation = algebraicapproximation.create_algebraic_approximation
create_polynomial_root = polynomial.create_polynomial_root
create_algebraic_number = algebraicnumber.create_algebraic_number
create_interval = interval.create_interval
create_number_field = numberfield.create_number_field

package = utilities.package
product = utilities.product

