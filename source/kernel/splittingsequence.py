
''' A module for representing a splitting sequence of a triangulation.

Provides one class: SplittingSequence. '''

import flipper

class SplittingSequence(object):
	''' This represents a sequence of flips of an Triangulation. '''
	def __init__(self, laminations, encodings, isometry, index, dilatation):
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
		self.dilatation = dilatation
		
		self.preperiodic = flipper.kernel.product(self.encodings[:self.index])
		self.periodic = flipper.kernel.product(self.encodings[self.index:])
		# We will reverse the direction of self.mapping_class so that self.lamination
		# is the stable lamination.
		self.mapping_class = (self.isometry.encode() * self.periodic).inverse()
		# Write some things into the cache.
		self.mapping_class._cache['invariant_lamination'] = (self.dilatation, self.lamination)

