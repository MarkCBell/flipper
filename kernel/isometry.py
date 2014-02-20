
from itertools import combinations

import Flipper

class Isometry:
	def __init__(self, source_triangulation, target_triangulation, triangle_map):
		# source_triangulation and target_triangulation are two AbstractTriangulations
		# triangle_map is a dictionary sending each AbstractTriangle of source_triangulation to a pair
		# (AbstractTriangle, Permutation).
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.triangle_map = triangle_map
		self.edge_map = dict((triangle[i], self.triangle_map[triangle][0][self.triangle_map[triangle][1][i]]) for triangle in self.source_triangulation for i in range(3))
		# Check that the thing that we've built is actually well defined.
		if any(self.edge_map[i] == self.edge_map[j] for i, j in combinations(range(self.source_triangulation.zeta), 2)):
			raise Flipper.AssumptionError('Map does not induce a well defined map on edges.')
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
		else:
			return NotImplemented
	def apply(self, triangle, permutation):
		new_triangle, perm = self[triangle]
		return (new_triangle, perm * permutation)
	def inverse(self):
		Id_Perm = Flipper.kernel.permutation.Permutation([0,1,2])
		possible_inverses = self.target_triangulation.all_isometries(self.source_triangulation)
		return [isom for isom in possible_inverses if all((isom*self)[triangle] == (triangle, Id_Perm) for triangle in self.source_triangulation)][0]
	def adapt_isometry(self, new_source_triangulation, new_target_triangulation):
		# Assumes some stuff.
		return isometry_from_edge_map(new_source_triangulation, new_target_triangulation, self.edge_map)
	def encode_isometry(self):
		return Flipper.kernel.encoding.Encoding([Flipper.kernel.matrix.Permutation_Matrix(self.edge_map)], [Flipper.kernel.matrix.Empty_Matrix(self.source_triangulation.zeta)], self.source_triangulation, self.target_triangulation)


#### Some special Isometries we know how to build.

def isometry_from_edge_map(source_triangulation, target_triangulation, edge_map):
	# There is more than one solution iff S = S_1_1.
	return [isom for isom in source_triangulation.all_isometries(target_triangulation) if isom.edge_map == edge_map][0]
