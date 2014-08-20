
from . import abstracttriangulation
from . import algebraicapproximation
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
from . import permutation
from . import polynomial
from . import splittingsequence
from . import symboliccomputation
from . import types
from . import utilities

# Set up shorter names for all of the different classes and some common constructors.
AbstractVertex = abstracttriangulation.AbstractVertex
AbstractEdge = abstracttriangulation.AbstractEdge
AbstractTriangle = abstracttriangulation.AbstractTriangle
AbstractTriangulation = abstracttriangulation.AbstractTriangulation
AlgebraicApproximation = algebraicapproximation.AlgebraicApproximation
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
PolynomialRoot = polynomial.PolynomialRoot
AlgebraicMonomial = algebraicnumber.AlgebraicMonomial
AlgebraicNumber = algebraicnumber.AlgebraicNumber
Permutation = permutation.Permutation
Polynomial = polynomial.Polynomial
SplittingSequence = splittingsequence.SplittingSequence

Empty_Matrix = matrix.Empty_Matrix
Id_Matrix = matrix.Id_Matrix
Zero_Matrix = matrix.Zero_Matrix
Integer_Type = types.Integer_Type
String_Type = types.String_Type
Number_Type = types.Number_Type
height_int = algebraicnumber.height_int
norm = abstracttriangulation.norm

# Functions that help with construction.
abstract_triangulation_helper = abstracttriangulation.abstract_triangulation_helper
algebraic_approximation_helper = algebraicapproximation.algebraic_approximation_helper
polynomial_root_helper = polynomial.polynomial_root_helper
algebraic_number_helper = algebraicnumber.algebraic_number_helper
interval_helper = interval.interval_helper
number_field_helper = numberfield.number_field_helper

product = utilities.product

package = io.package
depackage = io.depackage

