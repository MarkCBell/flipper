
''' A module for representing a splitting sequence of abstract triangulations.

Provides one class: SplittingSequence. '''

import flipper

class SplittingSequence(object):
	''' This represents a sequence of flips of an AbstractTriangulation. '''
	def __init__(self, initial_lamination, preperiodic, periodic, isometry, periodic_flips):
		assert(isinstance(initial_lamination, flipper.kernel.Lamination))
		assert(preperiodic is None or isinstance(preperiodic, flipper.kernel.Encoding))
		assert(isinstance(periodic, flipper.kernel.Encoding))
		assert(isinstance(isometry, flipper.kernel.Isometry))
		assert(all(isinstance(flip, flipper.IntegerType) for flip in periodic_flips))
		
		self.initial_lamination = initial_lamination
		self.preperiodic = preperiodic  # Unused.
		self.periodic = periodic  # Unused.
		self.isometry = isometry
		self.periodic_flips = periodic_flips
	
	def dilatation(self):
		''' Return the dilatation of the corresponding mapping class (as a float). '''
		
		return float(self.periodic(self.initial_lamination).weight()) / float(self.initial_lamination.weight())
	
	def bundle(self):
		''' Return the corresponding veering layered triangulation of the corresponding mapping torus. '''
		
		return flipper.kernel.LayeredTriangulation(self.initial_lamination.triangulation, self.periodic_flips, self.isometry).closed_triangulation

