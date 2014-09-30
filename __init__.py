
''' Flipper is a program for computing the action of mapping classes on
laminations on punctured surfaces using ideal triangulation coordinates.

It can decide the Nielsen--Thurston type of a given mapping class and,
for pseudo-Anosov mapping classes, construct a layered, veering
triangulation of their mapping torus, as described by Agol.

Get started by creating an AbstractTriangulation using the helper function:
	flipper.abstract_triangulation(...)
or by loading one of the provided EquippedTriangulations using:
	flipper.load.equipped_triangulation(...) '''

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

if __name__ == '__main__':
	print('Hello')

