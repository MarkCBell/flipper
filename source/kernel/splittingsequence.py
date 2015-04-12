
''' A module for representing a splitting sequence of a lamination.

Provides one class: SplittingSequence. '''

import flipper

class SplittingSequence(object):
	''' This represents a sequence of flips of an Triangulation. '''
	def __init__(self, encodings, index, dilatation, lamination):
		assert(isinstance(encodings, (list, tuple)))
		assert(all(isinstance(encoding, flipper.kernel.Encoding) for encoding in encodings))
		assert(isinstance(index, flipper.IntegerType))
		# assert(isinstance(dilatation, flipper.kernel.NumberFieldElement))
		assert(isinstance(lamination, flipper.kernel.Lamination))
		
		self.encodings = encodings
		self.index = index
		self.dilatation = dilatation
		self.lamination = lamination
		
		self.triangulation = self.lamination.triangulation
		
		self.preperiodic = flipper.kernel.product(self.encodings[:self.index])
		# We will reverse the direction of self.mapping_class so that self.lamination
		# is the stable lamination.
		self.mapping_class = flipper.kernel.product(self.encodings[self.index:]).inverse()  #pylint: disable=maybe-no-member
		# Write some things into the cache.
		self.mapping_class._cache['invariant_lamination'] = (self.dilatation, self.lamination)

