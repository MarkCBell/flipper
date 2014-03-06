
import Flipper.kernel
import Flipper.examples
import Flipper.tests
import Flipper.application

# Load shorter names for commonly used classes and functions.
Flipper.Lamination = Flipper.kernel.lamination.Lamination
Flipper.AbstractTriangulation = Flipper.kernel.abstracttriangulation.AbstractTriangulation
Flipper.Isometry = Flipper.kernel.isometry.Isometry
Flipper.LayeredTriangulation = Flipper.kernel.layeredtriangulation.LayeredTriangulation
Flipper.Matrix = Flipper.kernel.matrix.Matrix
Flipper.Polynomial = Flipper.kernel.polynomial.Polynomial

Flipper.isometry_from_edge_map = Flipper.kernel.isometry.isometry_from_edge_map

Flipper.AbortError = Flipper.kernel.error.AbortError
Flipper.ApproximationError = Flipper.kernel.error.ApproximationError
Flipper.AssumptionError = Flipper.kernel.error.AssumptionError
Flipper.ComputationError = Flipper.kernel.error.ComputationError

Flipper.Integer_Type = Flipper.kernel.types.Integer_Type
