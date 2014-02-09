
# We can also produce Isometries using:
#	1) isometry_from_edge_map(source_triangulation, target_triangulation, edge_map),
#	2) extend_isometry(source_triangulation, target_triangulation, source_triangle, target_triangle, cycle),
#	3) all_isometries(source_triangulation, target_triangulation)

from itertools import combinations
try:
	from Queue import Queue
except ImportError: # Python 3
	from queue import Queue

import Flipper

class Isometry:
	def __init__(self, source_triangulation, target_triangulation, triangle_map):
		# source_triangulation and target_triangulation are two Abstract_Triangulations
		# triangle_map is a dictionary sending each Abstract_Triangle of source_triangulation to a pair
		# (Abstract_Triangle, Permutation).
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.triangle_map = triangle_map
		self.edge_map = dict((triangle[i], self.triangle_map[triangle][0][self.triangle_map[triangle][1][i]]) for triangle in self.source_triangulation for i in range(3))
		# Check that the thing that we've built is actually well defined.
		if any(self.edge_map[i] == self.edge_map[j] for i, j in combinations(range(self.source_triangulation.zeta), 2)):
			raise Flipper.Kernel.Error.AssumptionError('Map does not induce a well defined map on edges.')
	def __repr__(self):
		return str(self.triangle_map)
	def __getitem__(self, index):
		return self.triangle_map[index]
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
		target_triangle = self.source_triangulation[0]
		source_triangle, cycle = self[target_triangle]
		return extend_isometry(self.target_triangulation, self.source_triangulation, source_triangle, target_triangle, cycle.inverse()[0])
	def adapt_isometry(self, new_source_triangulation, new_target_triangulation):
		# Assumes some stuff.
		return isometry_from_edge_map(new_source_triangulation, new_target_triangulation, self.edge_map)

#### Some special Isometries we know how to build.

def isometry_from_edge_map(source_triangulation, target_triangulation, edge_map):
	source_triangle = source_triangulation.triangles[0]
	target_triangle = target_triangulation.find_triangle([edge_map[x] for x in source_triangle])  # There is more than one solution iff S = S_1_1.
	cycle = min(i for i in range(3) if all(edge_map[source_triangle[j]] == target_triangle[j + i] for j in range(3))) 
	return extend_isometry(source_triangulation, target_triangulation, source_triangle, target_triangle, cycle)

# @profile
def extend_isometry(source_triangulation, target_triangulation, source_triangle, target_triangle, cycle):
	triangle_map = {}
	triangles_to_process = Queue()
	# We start by assuming that the source_triangle gets mapped to target_triangle via the permutation (cycle,cycle+1,cycle+2).
	triangles_to_process.put((source_triangle, target_triangle, cycle))
	seen_triangles = set([source_triangle])
	triangle_map[source_triangle] = (target_triangle, cycle)
	while not triangles_to_process.empty():
		from_triangle, to_triangle, cycle = triangles_to_process.get()
		triangle_map[from_triangle] = (to_triangle, Flipper.Kernel.Permutation.cyclic_permutation(cycle, 3))
		for side in range(3):
			from_triangle_neighbour, from_neighbour_side = source_triangulation.find_neighbour(from_triangle, side)
			to_triangle_neighbour, to_neighbour_side = target_triangulation.find_neighbour(to_triangle, (side+cycle)%3)
			if from_triangle_neighbour not in seen_triangles:
				triangles_to_process.put((from_triangle_neighbour, to_triangle_neighbour, (to_neighbour_side-from_neighbour_side) % 3))
				seen_triangles.add(from_triangle_neighbour)
	
	return Isometry(source_triangulation, target_triangulation, triangle_map)

def all_isometries(source_triangulation, target_triangulation):
	# Returns a list of all orientation preserving isometries from source_triangulation to target_triangulation.
	if source_triangulation.zeta != target_triangulation.zeta: return []
	
	isometries = []
	for triangle in target_triangulation:
		for i in range(3):
			try:
				isometry = extend_isometry(source_triangulation, target_triangulation, source_triangulation.triangles[0], triangle, i)
			except Flipper.Kernel.Error.AssumptionError:
				pass
			else:
				isometries.append(isometry)
	
	return isometries

def is_isometric_to(source_triangulation, target_triangulation):
	return len(all_isometries(source_triangulation, target_triangulation)) > 0
