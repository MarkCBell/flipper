
''' A module for representing a splitting sequence of a lamination.

Provides one class: SplittingSequence. '''

import flipper

class SplittingSequence(object):
	''' This represents a sequence of flips of an Triangulation. '''
	def __init__(self, preperiodic, mapping_class, dilatation, lamination):
		assert(isinstance(preperiodic, flipper.kernel.Encoding))
		assert(isinstance(mapping_class, flipper.kernel.Encoding))
		# assert(isinstance(dilatation, flipper.kernel.NumberFieldElement))
		assert(isinstance(lamination, flipper.kernel.Lamination))
		
		# We wont bother to save encoding as it can always be reconstructed by:
		#  self.mapping_class.inverse() * self.preperiodic
		
		self.preperiodic = preperiodic
		self.mapping_class = mapping_class
		self.dilatation = dilatation
		self.lamination = lamination
		
		self.triangulation = self.lamination.triangulation
		
		# Write some things into the cache.
		# Hmmm, this assumes we're not taking roots.
		self.mapping_class._cache['invariant_lamination'] = (self.dilatation, self.lamination)

class SplittingSequences(object):
	''' This represents a sequence of flips of an Triangulation. '''
	def __init__(self, encoding, isometries, index, dilatation, lamination):
		assert(isinstance(encoding, flipper.kernel.Encoding))
		
		assert(isinstance(index, flipper.IntegerType))
		# assert(isinstance(dilatation, flipper.kernel.NumberFieldElement))
		assert(isinstance(lamination, flipper.kernel.Lamination))
		
		# We wont bother to save encoding as it can always be reconstructed by:
		#  self.mapping_class.inverse() * self.preperiodic
		
		self.encoding = encoding
		self.isometries = isometries
		self.index = index
		self.dilatation = dilatation
		self.lamination = lamination
		
		self.preperiodic = self.encoding[-self.index:]
		self.open_periodic = self.encoding[:-self.index]
	
	def __iter__(self):
		for isometry in self.isometries:
			# We will reverse the direction of self.mapping_class so that self.lamination is the stable lamination.
			yield SplittingSequence(self.preperiodic, (isometry.encode() * self.open_periodic).inverse(), self.dilatation, self.lamination)
		
		return


