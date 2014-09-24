
# import flipper.application  # Don't do this import so people without tkinter can still use the kernel.
import flipper.kernel
import flipper.examples
import flipper.load
import flipper.tests
import flipper.profiles
import flipper.versions

# Set up really short names for the most commonly used classes and functions by users.
flipper.abstract_triangulation = flipper.kernel.abstract_triangulation

flipper.IntegerType = flipper.kernel.IntegerType
flipper.StringType = flipper.kernel.StringType
flipper.NumberType = flipper.kernel.NumberType

flipper.AbortError = flipper.kernel.AbortError
flipper.ApproximationError = flipper.kernel.ApproximationError
flipper.AssumptionError = flipper.kernel.AssumptionError
flipper.ComputationError = flipper.kernel.ComputationError

flipper.package = flipper.kernel.package
flipper.depackage = flipper.kernel.depackage

flipper.version = flipper.versions.version

