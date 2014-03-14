
import Flipper.kernel
import Flipper.examples
import Flipper.tests
import Flipper.version


# Set up shorter names for all of the different classes and common constructors.
Flipper.kernel.AbstractTriangle = Flipper.kernel.abstracttriangulation.AbstractTriangle
Flipper.kernel.AbstractTriangulation = Flipper.kernel.abstracttriangulation.AbstractTriangulation
Flipper.kernel.AlgebraicApproximation = Flipper.kernel.algebraicapproximation.AlgebraicApproximation
Flipper.kernel.PartialFunction = Flipper.kernel.encoding.PartialFunction
Flipper.kernel.Encoding = Flipper.kernel.encoding.Encoding
Flipper.kernel.EncodingSequence = Flipper.kernel.encoding.EncodingSequence
Flipper.kernel.AbortError = Flipper.kernel.error.AbortError
Flipper.kernel.ApproximationError = Flipper.kernel.error.ApproximationError
Flipper.kernel.AssumptionError = Flipper.kernel.error.AssumptionError
Flipper.kernel.ComputationError = Flipper.kernel.error.ComputationError
Flipper.kernel.Interval = Flipper.kernel.interval.Interval
Flipper.kernel.Isometry = Flipper.kernel.isometry.Isometry
Flipper.kernel.Lamination = Flipper.kernel.lamination.Lamination
Flipper.kernel.LayeredTriangulation = Flipper.kernel.layeredtriangulation.LayeredTriangulation
Flipper.kernel.Matrix = Flipper.kernel.matrix.Matrix
Flipper.kernel.NumberField = Flipper.kernel.numberfield.NumberField
Flipper.kernel.Permutation = Flipper.kernel.permutation.Permutation
Flipper.kernel.Polynomial = Flipper.kernel.polynomial.Polynomial
Flipper.kernel.SplittingSequence = Flipper.kernel.splittingsequence.SplittingSequence

Flipper.kernel.Empty_Matrix = Flipper.kernel.matrix.Empty_Matrix
Flipper.kernel.Id_Matrix = Flipper.kernel.matrix.Id_Matrix
Flipper.kernel.Zero_Matrix = Flipper.kernel.matrix.Zero_Matrix
Flipper.kernel.Integer_Type = Flipper.kernel.types.Integer_Type


# And really short names for the most commonly used classes and functions by users.
Flipper.AbortError = Flipper.kernel.AbortError
Flipper.ApproximationError = Flipper.kernel.ApproximationError
Flipper.AssumptionError = Flipper.kernel.AssumptionError
Flipper.ComputationError = Flipper.kernel.ComputationError
Flipper.AbstractTriangulation = Flipper.kernel.AbstractTriangulation
Flipper.Lamination = Flipper.kernel.Lamination

Flipper.isometry_from_edge_map = Flipper.kernel.isometry.isometry_from_edge_map
Flipper.Integer_Type = Flipper.kernel.Integer_Type