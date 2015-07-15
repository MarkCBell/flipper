
''' A module for representing isometries between Triangulations.

Provides one class: Isometry. '''

import flipper

class Isometry(object):
	''' This represents an isometry from one Triangulation to another.
	
	Triangulations can create the isometries between themselves and this
	is the standard way users are expected to create these. '''
	def __init__(self, source_triangulation, target_triangulation, corner_map):
		''' This represents an isometry from source_triangulation to target_triangulation.
		
		It is given by a map taking each corner of source_triangulation to a corner of target_triangulation. '''
		
		assert(isinstance(source_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(target_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(corner_map, dict))
		
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.zeta = self.source_triangulation.zeta
		self.corner_map = corner_map
		# We should check that the each of these maps are actually well defined.
		self.edge_map = dict((corner.edge, self.corner_map[corner].edge) for corner in self.corner_map)
		self.vertex_map = dict((corner.vertex, self.corner_map[corner].vertex) for corner in self.corner_map)
		self.triangle_map = dict((corner.triangle, self.corner_map[corner].triangle) for corner in self.corner_map)
		self.index_map = dict((corner.index, self.corner_map[corner].index) for corner in self.corner_map)
		self.label_map = dict((corner.label, self.corner_map[corner].label) for corner in self.corner_map)
		
	def __repr__(self):
		return str(self)
	def __str__(self):
		return 'Isometry ' + str([self.edge_map[edge] for edge in sorted(self.source_triangulation.oriented_edges, key=lambda e: e.index)])
	def __reduce__(self):
		return (self.__class__, (self.source_triangulation, self.target_triangulation, self.corner_map))
	def __call__(self, other):
		if isinstance(other, flipper.kernel.Lamination):
			if other.triangulation != self.source_triangulation:
				raise TypeError('Cannot apply Isometry to a lamination not on the source triangulation.')
			
			geometric = [None] * self.zeta
			algebraic = [None] * self.zeta
			for i in range(self.zeta):
				geometric[self.index_map[i]] = other(i)
				algebraic[self.index_map[i]] = (+1 if self.index_map[i] == self.label_map[i] else -1) * other[i]
			
			return flipper.kernel.Lamination(self.target_triangulation, geometric, algebraic)
		if isinstance(other, flipper.kernel.Vertex):
			if other not in self.source_triangulation:
				raise ValueError('Vertex not in source triangulation.')
			return self.vertex_map[other]
		elif isinstance(other, flipper.kernel.Edge):
			if other not in self.source_triangulation:
				raise ValueError('Edge not in source triangulation.')
			return self.edge_map[other]
		elif isinstance(other, flipper.kernel.Triangle):
			if other not in self.source_triangulation:
				raise ValueError('Triangle not in source triangulation.')
			return self.triangle_map[other]
		elif isinstance(other, flipper.kernel.Corner):
			if other not in self.source_triangulation:
				raise ValueError('Corner not in source triangulation.')
			return self.corner_map[other]
		elif isinstance(other, flipper.IntegerType):  # Integers are assumed to be labels.
			return self.label_map[other]
		else:
			return NotImplemented
	def inverse(self):
		''' Return the inverse of this isometry. '''
		
		inverse_corner_map = dict((self(corner), corner) for corner in self.corner_map)
		return Isometry(self.target_triangulation, self.source_triangulation, inverse_corner_map)
	
	def applied_geometric(self, lamination):
		''' Return the action and condition matrices describing the isometry
		applied to the geometric coordinates of the given lamination. '''
		
		return flipper.kernel.Permutation([self.index_map[i] for i in range(self.zeta)]).matrix(), flipper.kernel.zero_matrix(0)
	
	def encode(self):
		''' Return the Encoding induced by this isometry. '''
		
		return flipper.kernel.Encoding([self])
	
	def flip_length(self):
		''' Return the number of flips needed to realise this move. '''
		
		return 0

