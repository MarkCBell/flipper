
''' A module for representing a splitting sequence of a triangulation.

Provides one class: SplittingSequence. '''

import flipper


class SplittingSequence(object):
	''' This represents a sequence of flips of an Triangulation. '''
	def __init__(self, laminations, encodings, isometry, index):
		assert(isinstance(laminations, (list, tuple)))
		assert(all(isinstance(lamination, flipper.kernel.Lamination) for lamination in laminations))
		assert(isinstance(encodings, (list, tuple)))
		assert(all(edge_index is None or isinstance(edge_index, flipper.IntegerType) for edge_index, _ in encodings))
		assert(all(isinstance(encoding, flipper.kernel.Encoding) for _, encoding in encodings))
		assert(isinstance(isometry, flipper.kernel.Isometry))
		assert(isinstance(index, flipper.IntegerType))
		
		self.laminations = laminations
		self.edge_flips = [edge_index for edge_index, _ in encodings]
		self.encodings = [encoding for _, encoding in encodings]
		self.isometry = isometry
		
		self.index = index
		self.lamination = self.laminations[index]
		self.triangulation = self.lamination.triangulation
		self.periodic_flips = self.edge_flips[self.index:]
		
		self.preperiodic = flipper.kernel.product(self.encodings[:self.index])
		self.periodic = flipper.kernel.product(self.encodings[self.index:])
		self.mapping_class = self.isometry.encode() * self.periodic
		
		self.preperiodic_length = sum(1 for edge in self.edge_flips[:self.index] if edge is not None)
		self.periodic_length = len(self.edge_flips) - self.index  # == sum(1 for edge in self.edge_flips[self.index:] if edge is not None)
	
	def dilatation(self):
		''' Return the dilatation of the corresponding mapping class (as a float). '''
		
		return float(self.periodic(self.lamination).weight()) / float(self.lamination.weight())
	
	def bundle(self):
		''' Return the corresponding veering layered triangulation of the corresponding mapping torus. '''
		
		return self.triangulation.bundle(self.periodic_flips, self.isometry)

