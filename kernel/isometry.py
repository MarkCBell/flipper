
''' A module for representing isometries between AbstractTriangulations.

Provides one class: Isometry. '''

import flipper

class Isometry(object):
	''' This represents an isometry from one AbstractTriangulation to another. '''
	def __init__(self, source_triangulation, target_triangulation, corner_map):
		''' This represents an isometry from source_triangulation to target_triangulation.
		
		It is given by a map taking each corner of source_triangulation to a corner of target_triangulation. '''
		
		assert(isinstance(source_triangulation, flipper.kernel.AbstractTriangulation))
		assert(isinstance(target_triangulation, flipper.kernel.AbstractTriangulation))
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
		return str(self.edge_map)
	def __eq__(self, other):
		return self.source_triangulation == other.source_triangulation and \
			self.target_triangulation == other.target_triangulation and \
			self.label_map == other.label_map
	def __ne__(self, other):
		return not (self == other)
	def __iter__(self):
		return iter(self.label_map)  # Iteration is over ORIENTED EDGES!
	def __call__(self, other):
		if isinstance(other, flipper.kernel.AbstractVertex):
			if other not in self.source_triangulation:
				raise ValueError('Vertex no in source triangulation.')
			return self.vertex_map[other]
		elif isinstance(other, flipper.kernel.AbstractEdge):
			if other not in self.source_triangulation:
				raise ValueError('Edge no in source triangulation.')
			return self.edge_map[other]
		elif isinstance(other, flipper.kernel.AbstractTriangle):
			if other not in self.source_triangulation:
				raise ValueError('Triangle no in source triangulation.')
			return self.triangle_map[other]
		elif isinstance(other, flipper.kernel.AbstractCorner):
			if other not in self.source_triangulation:
				raise ValueError('Corner no in source triangulation.')
			return self.corner_map[other]
		else:
			return NotImplemented
	def __mul__(self, other):
		if isinstance(other, Isometry):
			if other.target_triangulation != self.source_triangulation:
				raise ValueError('Cannot compose isometries between different triangulations.')
			return Isometry(other.source_triangulation, self.target_triangulation, dict((edge, self[other[edge]]) for edge in other))
		else:
			return NotImplemented
	def adapt(self, new_source_triangulation, new_target_triangulation):
		''' Return this isometry but mapping from  new_source_triangulation to new_target_triangulation. '''
		
		assert(isinstance(new_source_triangulation, flipper.kernel.AbstractTriangulation))
		assert(isinstance(new_target_triangulation, flipper.kernel.AbstractTriangulation))
		
		return new_source_triangulation.find_isometry(new_target_triangulation, 0, self.label_map[0])
	def triangle_image(self, triangle):
		''' Return the image of the give triangle along with a cyclic permutation. '''
		
		corner = self(triangle.corners[0])
		return (corner.triangle, flipper.kernel.permutation.cyclic_permutation(corner.side-0, 3))
	def inverse(self):
		''' Return the inverse of this isometry. '''
		
		return Isometry(self.target_triangulation, self.source_triangulation, dict((self.corner_map[corner], corner) for corner in self.corner_map))
	def permutation(self):
		''' Return the permutation on edges induced by this isometry. '''
		
		return flipper.kernel.Permutation([self.index_map[i] for i in range(self.zeta)])
	def encode(self):
		''' Return the Encoding induced by this isometry. '''
		
		f = [flipper.kernel.PartialFunction(self.permutation().matrix())]
		b = [flipper.kernel.PartialFunction(self.inverse().permutation().matrix())]
		
		return flipper.kernel.Encoding(self.source_triangulation, self.target_triangulation, [flipper.kernel.PLFunction(f, b)])
