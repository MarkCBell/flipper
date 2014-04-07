
# import Flipper.application  # Don't do this import so people without tkinter can still use the kernel.
import Flipper.kernel
import Flipper.examples
import Flipper.tests
import Flipper.version

# Set up really short names for the most commonly used classes and functions by users.
Flipper.AbstractTriangulation = Flipper.kernel.AbstractTriangulation

Flipper.isometry_from_edge_map = Flipper.kernel.isometry.isometry_from_edge_map
Flipper.Integer_Type = Flipper.kernel.Integer_Type

Flipper.AbortError = Flipper.kernel.AbortError
Flipper.ApproximationError = Flipper.kernel.ApproximationError
Flipper.AssumptionError = Flipper.kernel.AssumptionError
Flipper.ComputationError = Flipper.kernel.ComputationError

Flipper.package = Flipper.kernel.package
Flipper.depackage = Flipper.kernel.depackage

