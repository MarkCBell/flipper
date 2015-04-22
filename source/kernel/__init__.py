
''' The flipper kernel.

Some of the functions and methods have assumptions on them. We denote
in a functions docstring:
	Assumes that ...
		If the assumptions are met then this function is guaranteed to terminate correctly.
		If not then this function will either:
			terminate correctly, OR
			a flipper.AssumptionError will be raised.
	
	Assumes (and checks) that ...
		If the assumptions are met then this function is guaranteed to terminate correctly.
		If not then this a flipper.AssumptionError will be raised. '''

from . import algebraicapproximation
from . import bundle
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
from . import triangulation
from . import triangulation3
from . import types
from . import utilities

# Set up shorter names for all of the different classes.
Vertex = triangulation.Vertex
Edge = triangulation.Edge
Triangle = triangulation.Triangle
Triangulation = triangulation.Triangulation
Corner = triangulation.Corner
AlgebraicApproximation = algebraicapproximation.AlgebraicApproximation
Bundle = bundle.Bundle
EdgeFlip = encoding.EdgeFlip
LinearTransformation = encoding.LinearTransformation
Encoding = encoding.Encoding
AbortError = error.AbortError
ApproximationError = error.ApproximationError
AssumptionError = error.AssumptionError
ComputationError = error.ComputationError
FatalError = error.FatalError
EquippedTriangulation = equippedtriangulation.EquippedTriangulation
Interval = interval.Interval
Isometry = isometry.Isometry
Lamination = lamination.Lamination
Matrix = matrix.Matrix
NumberField = numberfield.NumberField
NumberFieldElement = numberfield.NumberFieldElement
PolynomialRoot = polynomial.PolynomialRoot
Permutation = permutation.Permutation
Polynomial = polynomial.Polynomial
SplittingSequence = splittingsequence.SplittingSequence
Tetrahedron = triangulation3.Tetrahedron
Triangulation3 = triangulation3.Triangulation3

id_matrix = matrix.id_matrix
zero_matrix = matrix.zero_matrix
dot = matrix.dot
height_int = numberfield.height_int
norm = triangulation.norm
StringType = types.StringType
IntegerType = types.IntegerType
NumberType = types.NumberType

# Functions that help with construction.
create_triangulation = triangulation.create_triangulation
create_equipped_triangulation = equippedtriangulation.create_equipped_triangulation
triangulation_from_iso_sig = triangulation.triangulation_from_iso_sig
create_algebraic_approximation = algebraicapproximation.create_algebraic_approximation
create_polynomial_root = polynomial.create_polynomial_root
create_interval = interval.create_interval
create_number_field = numberfield.create_number_field

package = utilities.package
product = utilities.product
gcd = utilities.gcd

