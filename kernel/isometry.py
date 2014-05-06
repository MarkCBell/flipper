
from itertools import combinations

import flipper

def norm(x):
	return max(x, ~x)

class Isometry(object):
	''' This represents an isometry from one AbstractTriangulation to another. '''
	def __init__(self, source_triangulation, target_triangulation, oriented_edge_map):
		''' This represents an isometry from source_triangulation to target_triangulation. It is given
		by a map taking each triangle to a triangle and a permutation (on 3 elements). '''
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.zeta = self.source_triangulation.zeta
		self.oriented_edge_map = dict(oriented_edge_map)
		self.edge_map = dict((norm(edge), norm(self.oriented_edge_map[edge])) for edge in self.oriented_edge_map)
		# Should check that the thing that we've built is actually well defined.
	def __repr__(self):
		return str(self.edge_map)
	def __getitem__(self, index):
		return self.oriented_edge_map[index]
	#def __eq__(self, other):
	#	return self.triangle_map == other.triangle_map
	def __iter__(self):
		return iter(self.oriented_edge_map)  # Iteration is over ORIENTED EDGES!
	def __call__(self, other):
		if isinstance(other, flipper.kernel.Lamination):
			if self.source_triangulation != other.triangulation:
				raise ValueError('Cannot apply isometry to Lamination on a different triangulation.')
			return self.encode()(other)
		else:
			return NotImplemented
	def __mul__(self, other):
		if isinstance(other, Isometry):
			if other.target_triangulation != self.source_triangulation:
				raise ValueError('Cannot compose isometries between different triangulations.')
			return Isometry(other.source_triangulation, self.target_triangulation, dict((edge, self[other[edge]]) for edge in other))
		else:
			return NotImplemented
	def triangle_image(self, triangle):
		corner = self.target_triangulation.find_edge(self[triangle.labels[0]])
		return (corner.triangle, flipper.kernel.permutation.cyclic_permutation(corner.side-0, 3))
	def inverse(self):
		return Isometry(self.target_triangulation, self.source_triangulation, dict((self[edge], edge) for edge in self))
	def permutation(self):
		return flipper.kernel.Permutation([self.edge_map[i] for i in range(self.zeta)])
	def encode(self):
		f = [flipper.kernel.PartialFunction(self.permutation().matrix())]
		b = [flipper.kernel.PartialFunction(self.inverse().permutation().matrix())]
		
		return flipper.kernel.Encoding(self.source_triangulation, self.target_triangulation, [flipper.kernel.PLFunction(f, b)])

