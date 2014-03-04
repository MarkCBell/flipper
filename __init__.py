
import Flipper.kernel
import Flipper.examples
import Flipper.tests
import Flipper.application

# Load shorter names for commonly used classes and functions.
Lamination =  Flipper.kernel.lamination.Lamination
AbstractTriangulation = Flipper.kernel.abstracttriangulation.AbstractTriangulation
Isometry = Flipper.kernel.isometry.Isometry
LayeredTriangulation = Flipper.kernel.layeredtriangulation.LayeredTriangulation
Matrix = Flipper.kernel.matrix.Matrix
Polynomial = Flipper.kernel.polynomial.Polynomial

isometry_from_edge_map = Flipper.kernel.isometry.isometry_from_edge_map

AbortError = Flipper.kernel.error.AbortError
ApproximationError = Flipper.kernel.error.ApproximationError
AssumptionError = Flipper.kernel.error.AssumptionError
ComputationError = Flipper.kernel.error.ComputationError

Integer_Type = Flipper.kernel.types.Integer_Type
