
''' A module for representing a splitting sequence of a lamination.

Provides one class: SplittingSequence. '''

import flipper

class SplittingSequence(object):
	''' This represents a sequence of flips of an Triangulation. '''
	def __init__(self, encoding, index, dilatation, lamination):
		assert(isinstance(encoding, flipper.kernel.Encoding))
		assert(isinstance(index, flipper.IntegerType))
		# assert(isinstance(dilatation, flipper.kernel.NumberFieldElement))
		assert(isinstance(lamination, flipper.kernel.Lamination))
		
		# We wont bother to save encoding as it can always be reconstructed by:
		#  self.mapping_class.inverse() * self.preperiodic
		
		self.index = index
		self.dilatation = dilatation
		self.lamination = lamination
		
		self.triangulation = self.lamination.triangulation
		
		# This is the same as: flipper.kernel.product(encodings[:self.index])
		self.preperiodic = encoding[-self.index:]
		
		# We will reverse the direction of self.mapping_class so that self.lamination
		# is the stable lamination.
		# This is the same as: flipper.kernel.product(encodings[self.index:]).inverse()
		self.mapping_class = encoding[:-self.index].inverse()
		# Write some things into the cache.
		self.mapping_class._cache['invariant_lamination'] = (self.dilatation, self.lamination)

