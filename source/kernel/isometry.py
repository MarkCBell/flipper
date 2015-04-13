
''' A module for representing isometries between Triangulations.

Provides one class: Isometry. '''

import flipper

class Isometry(object):
	''' This represents an isometry from one Triangulation to another.
	
	Triangulations can create the isometries between themselves and this
	is the standard way users are expected to create these.
	
	>>> import flipper
	>>> T = flipper.load.equipped_triangulation('S_1_1').triangulation
	>>> i = T.find_isometry(T, 0, 0)
	>>> i
	Isometry [0, 1, 2]
	>>> f = T.find_isometry(T, 0, ~0)
	>>> f
	Isometry [~0, ~1, ~2]
	'''
	
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
	def __eq__(self, other):
		return self.source_triangulation == other.source_triangulation and \
			self.target_triangulation == other.target_triangulation and \
			self.label_map == other.label_map
	def __ne__(self, other):
		return not (self == other)
	def __call__(self, other):
		if isinstance(other, flipper.kernel.Lamination):
			if other.triangulation != self.source_triangulation:
				raise TypeError('Cannot apply Isometry to a lamination not on the source triangulation.')
			
			geometric = [None] * self.zeta
			algebraic = [None] * self.zeta
			for i in range(self.zeta):
				geometric[self.index_map[i]] = other.geometric[i]
				algebraic[self.index_map[i]] = (+1 if self.index_map[i] == self.label_map[i] else -1) * other.algebraic[i]
			
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
	def triangle_permutation(self, triangle):
		''' Return the permutation induced by this isometry on this triangle. '''
		
		# We could use any of the three corners of this triangle.
		return flipper.kernel.permutation.cyclic_permutation(self(triangle.corners[0]).side - 0, 3)  #pylint: disable=maybe-no-member
	def __mul__(self, other):
		if isinstance(other, Isometry):
			if other.target_triangulation != self.source_triangulation:
				raise ValueError('Cannot compose isometries between different triangulations.')
			
			composed_edge_map = dict((corner, self(other(corner))) for corner in other.corner_map)
			return Isometry(other.source_triangulation, self.target_triangulation, composed_edge_map)
		else:
			return NotImplemented
	def inverse(self):
		''' Return the inverse of this isometry.
		
		>>> i.inverse()
		Isometry [0, 1, 2]
		>>> f.inverse()
		Isometry [~0, ~1, ~2]
		'''
		
		inverse_corner_map = dict((self(corner), corner) for corner in self.corner_map)
		return Isometry(self.target_triangulation, self.source_triangulation, inverse_corner_map)
	
	def encode(self):
		''' Return the Encoding induced by this isometry.
		
		>>> i.encode()
		[Isometry [0, 1, 2]]
		'''
		
		return flipper.kernel.Encoding([self])
	
	def applied_geometric(self, lamination):
		''' Return the action and condition matrices describing the isometry
		applied to the geometric coordinates of the given lamination. '''
		
		return flipper.kernel.Permutation([self.index_map[i] for i in range(self.zeta)]).matrix(), flipper.kernel.zero_matrix(0)

def doctest_globs():
	''' Return the globals needed to run doctest on this module. '''
	
	
	T = flipper.load.equipped_triangulation('S_1_1').triangulation
	i = T.find_isometry(T, 0, 0)
	f = T.find_isometry(T, 0, ~0)
	
	return {'f': f, 'i': i}

