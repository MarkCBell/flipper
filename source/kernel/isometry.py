
''' A module for representing isometries between Triangulations.

Provides one class: Isometry. '''

import flipper

class Isometry(object):
	''' This represents an isometry from one Triangulation to another. '''
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
		return str(self.edge_map)
	def __eq__(self, other):
		return self.source_triangulation == other.source_triangulation and \
			self.target_triangulation == other.target_triangulation and \
			self.label_map == other.label_map
	def __ne__(self, other):
		return not (self == other)
	def __call__(self, other):
		if isinstance(other, flipper.kernel.Vertex):
			if other not in self.source_triangulation:
				raise ValueError('Vertex no in source triangulation.')
			return self.vertex_map[other]
		elif isinstance(other, flipper.kernel.Edge):
			if other not in self.source_triangulation:
				raise ValueError('Edge no in source triangulation.')
			return self.edge_map[other]
		elif isinstance(other, flipper.kernel.Triangle):
			if other not in self.source_triangulation:
				raise ValueError('Triangle no in source triangulation.')
			return self.triangle_map[other]
		elif isinstance(other, flipper.kernel.Corner):
			if other not in self.source_triangulation:
				raise ValueError('Corner no in source triangulation.')
			return self.corner_map[other]
		elif isinstance(other, flipper.IntegerType):  # Integers are assumed to be labels.
			return self.label_map[other]
		else:
			return NotImplemented
	def __mul__(self, other):
		if isinstance(other, Isometry):
			if other.target_triangulation != self.source_triangulation:
				raise ValueError('Cannot compose isometries between different triangulations.')
			
			composed_edge_map = dict((corner, self(other(corner))) for corner in other.corner_map)
			return Isometry(other.source_triangulation, self.target_triangulation, composed_edge_map)
		else:
			return NotImplemented
	def adapt(self, new_source_triangulation, new_target_triangulation):
		''' Return this isometry but mapping from  new_source_triangulation to new_target_triangulation. '''
		
		assert(isinstance(new_source_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(new_target_triangulation, flipper.kernel.Triangulation))
		
		return new_source_triangulation.find_isometry(new_target_triangulation, 0, self.label_map[0])
	def inverse(self):
		''' Return the inverse of this isometry. '''
		
		inverse_corner_map = dict((self(corner), corner) for corner in self.corner_map)
		return Isometry(self.target_triangulation, self.source_triangulation, inverse_corner_map)
	def permutation_matrix(self):
		''' Return the permutation on edges induced by this isometry. '''
		
		return flipper.kernel.Permutation([self.index_map[i] for i in range(self.zeta)]).matrix()
	def signed_permutation_matrix(self):
		''' Return the permutation on oriented edges induced by this isometry. '''
		
		return flipper.kernel.Matrix([[0 if i != self.index_map[j] else +1 if i == self.label_map[j] else -1 for j in range(self.zeta)] for i in range(self.zeta)])
	
	def encode(self):
		''' Return the Encoding induced by this isometry. '''
		
		inv = self.inverse()
		
		f = [flipper.kernel.PartialFunction(self.permutation_matrix())]
		b = [flipper.kernel.PartialFunction(inv.permutation_matrix())]
		
		return flipper.kernel.Encoding(self.source_triangulation, self.target_triangulation,
			flipper.kernel.PLFunction([flipper.kernel.BasicPLFunction(f, b)]),
			flipper.kernel.LFunction(self.signed_permutation_matrix(), inv.signed_permutation_matrix()))

