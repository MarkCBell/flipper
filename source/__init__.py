
''' Flipper is a program for computing the action of mapping classes on
laminations on punctured surfaces using ideal triangulation coordinates.

It can decide the Nielsen--Thurston type of a given mapping class and,
for pseudo-Anosov mapping classes, construct a layered, veering
triangulation of their mapping torus, as described by Agol.

Get started by starting the GUI:
	> import flipper.app
	> flipper.app.start()
or by creating a Triangulation using the helper function:
	> flipper.create_triangulation(...)
or from an isomorphism signature:
	> flipper.create_triangulation_from_iso_sig(...)
or by loading one of the provided EquippedTriangulations using:
	> flipper.load.equipped_triangulation(...) '''

from flipper.version import __version__

# We'll only import the bare minimum. This way people missing packages
# can still use the flipper kernel at least.
# import flipper.app  # Uses tkinter.
import flipper.kernel
# import flipper.example  # Uses snappy.
import flipper.load
import flipper.doc
# import flipper.test  # Uses snappy.
import flipper.profile

# Set up really short names for the most commonly used classes and functions by users.
flipper.create_triangulation = flipper.kernel.create_triangulation
flipper.triangulation_from_iso_sig = flipper.kernel.triangulation_from_iso_sig

flipper.StringType = flipper.kernel.StringType
flipper.IntegerType = flipper.kernel.IntegerType
flipper.NumberType = flipper.kernel.NumberType

flipper.AbortError = flipper.kernel.AbortError
flipper.ApproximationError = flipper.kernel.ApproximationError
flipper.AssumptionError = flipper.kernel.AssumptionError
flipper.ComputationError = flipper.kernel.ComputationError
flipper.FatalError = flipper.kernel.FatalError

flipper.package = flipper.kernel.package

