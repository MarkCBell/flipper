
# import flipper.application  # Don't do this import so people without tkinter can still use the kernel.
import flipper.kernel
import flipper.examples
import flipper.tests
import flipper.profiles
import flipper.version

# Set up really short names for the most commonly used classes and functions by users.
flipper.AbstractTriangulation = flipper.kernel.AbstractTriangulation

flipper.Integer_Type = flipper.kernel.Integer_Type
flipper.String_Type = flipper.kernel.String_Type

flipper.AbortError = flipper.kernel.AbortError
flipper.ApproximationError = flipper.kernel.ApproximationError
flipper.AssumptionError = flipper.kernel.AssumptionError
flipper.ComputationError = flipper.kernel.ComputationError

flipper.package = flipper.kernel.package
flipper.depackage = flipper.kernel.depackage

