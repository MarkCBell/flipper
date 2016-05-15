
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

import flipper.kernel.interface
from . import algebraicapproximation
from . import bundle
from . import encoding
from . import error
from . import equippedtriangulation
from . import flatstructure
from . import interval
from . import lamination
from . import matrix
from . import moves
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
Encoding = encoding.Encoding
AbortError = error.AbortError
ApproximationError = error.ApproximationError
AssumptionError = error.AssumptionError
ComputationError = error.ComputationError
FatalError = error.FatalError
EquippedTriangulation = equippedtriangulation.EquippedTriangulation
Vector2 = flatstructure.Vector2
FlatStructure = flatstructure.FlatStructure
Interval = interval.Interval
Lamination = lamination.Lamination
Matrix = matrix.Matrix
Move = moves.Move
Isometry = moves.Isometry
EdgeFlip = moves.EdgeFlip
Spiral = moves.Spiral
LinearTransformation = moves.LinearTransformation
NumberField = numberfield.NumberField
NumberFieldElement = numberfield.NumberFieldElement
PolynomialRoot = polynomial.PolynomialRoot
Permutation = permutation.Permutation
Polynomial = polynomial.Polynomial
SplittingSequence = splittingsequence.SplittingSequence
SplittingSequences = splittingsequence.SplittingSequences
Tetrahedron = triangulation3.Tetrahedron
Triangulation3 = triangulation3.Triangulation3

id_matrix = matrix.id_matrix
zero_matrix = matrix.zero_matrix
dot = matrix.dot
height_int = numberfield.height_int
norm = triangulation.norm
StringType = types.StringType
IntegerType = types.IntegerType
FileType = types.FileType

# Functions that help with construction.
create_triangulation = Triangulation.from_tuple
triangulation_from_iso_sig = Triangulation.from_string
create_equipped_triangulation = EquippedTriangulation.from_tuple

product = utilities.product
gcd = utilities.gcd

