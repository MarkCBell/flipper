
from itertools import combinations

import flipper

class Isometry(object):
	''' This represents an isometry from one AbstractTriangulation to another. '''
	def __init__(self, source_triangulation, target_triangulation, triangle_map):
		''' This represents an isometry from source_triangulation to target_triangulation. It is given
		by a map taking each triangle to a triangle and a permutation (on 3 elements). '''
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.zeta = self.source_triangulation.zeta
		self.triangle_map = triangle_map
		edge_map = [(triangle[i], self.triangle_map[triangle][0][self.triangle_map[triangle][1][i]]) for triangle in self.source_triangulation for i in range(3)]
		if any((a == b) != (x == y) for (a, x), (b, y) in combinations(edge_map, 2)):
			raise flipper.AssumptionError('Map does not induce a well defined map on edges.')
		
		self.edge_map = dict(edge_map)
		# Check that the thing that we've built is actually well defined.
	def __repr__(self):
		return str(self.triangle_map)
	def __getitem__(self, index):
		return self.triangle_map[index]
	def __eq__(self, other):
		return self.triangle_map == other.triangle_map
	def __iter__(self):
		return iter(self.source_triangulation)
	def __mul__(self, other):
		if isinstance(other, Isometry):
			assert(other.target_triangulation == self.source_triangulation)
			new_triangle_map = dict((triangle, self.apply(*other[triangle])) for triangle in other.source_triangulation)
			return Isometry(other.source_triangulation, self.target_triangulation, new_triangle_map)
		elif isinstance(other, flipper.kernel.Lamination) and self.source_triangulation == other.abstract_triangulation:
			return self.target_triangulation.lamination([other[j] for i in range(self.zeta) for j in range(self.zeta) if i == self.edge_map[j]])
		else:
			return NotImplemented
	# !?! Add in __pow__.
	def apply(self, triangle, permutation):
		new_triangle, perm = self[triangle]
		return (new_triangle, perm * permutation)
	def inverse(self):
		Id_Perm = flipper.kernel.Permutation([0, 1, 2])
		possible_inverses = self.target_triangulation.all_isometries(self.source_triangulation)
		return [isom for isom in possible_inverses if all((isom * self)[triangle] == (triangle, Id_Perm) for triangle in self.source_triangulation)][0]
	def adapt_isometry(self, new_source_triangulation, new_target_triangulation):
		# Assumes some stuff.
		return isometry_from_edge_map(new_source_triangulation, new_target_triangulation, self.edge_map)
	def permutation(self):
		return flipper.kernel.Permutation([self.edge_map[i] for i in range(self.zeta)])
	def encode(self):
		f = [flipper.kernel.PartialFunction(self.source_triangulation, self.target_triangulation, self.permutation().matrix())]
		b = [flipper.kernel.PartialFunction(self.target_triangulation, self.source_triangulation, self.permutation().inverse().matrix())]
		
		return flipper.kernel.Encoding([flipper.kernel.PLFunction(f, b)])

#### Some special Isometries we know how to build.

def isometry_from_edge_map(source_triangulation, target_triangulation, edge_map):
	# There is more than one solution iff S = S_1_1.
	return [isom for isom in source_triangulation.all_isometries(target_triangulation) if isom.edge_map == edge_map][0]

