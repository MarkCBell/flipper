
''' A module for representing a splitting sequence of a triangulation.

Provides one class: SplittingSequence. '''

import flipper

class SplittingSequence(object):
	''' This represents a sequence of flips of an Triangulation. '''
	def __init__(self, laminations, encodings, isometry, index):
		assert(isinstance(laminations, (list, tuple)))
		assert(all(isinstance(lamination, flipper.kernel.Lamination) for lamination in laminations))
		assert(isinstance(encodings, (list, tuple)))
		assert(all(isinstance(encoding, flipper.kernel.Encoding) for encoding in encodings))
		assert(isinstance(isometry, flipper.kernel.Isometry))
		assert(isinstance(index, flipper.IntegerType))
		
		self.laminations = laminations
		self.encodings = encodings
		self.isometry = isometry
		
		self.index = index
		self.lamination = self.laminations[index]
		self.triangulation = self.lamination.triangulation
		
		self.preperiodic = flipper.kernel.product(self.encodings[:self.index])
		self.periodic = flipper.kernel.product(self.encodings[self.index:])
		self.mapping_class = self.isometry.encode() * self.periodic
	
	def dilatation(self):
		''' Return the dilatation of the corresponding mapping class (as a float). '''
		
		return float(self.periodic(self.lamination).weight()) / float(self.lamination.weight())

