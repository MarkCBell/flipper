
# TO DO: We need an is_curve() function to make sure we never try to Dehn twist about a multicurve, for example.

from __future__ import print_function
from itertools import product, combinations
from Matrix import Matrix, Id_Matrix, Empty_Matrix, nonnegative, nontrivial, nonnegative_image
from Encoding import Encoding, Encoding_Sequence, Id_Encoding_Sequence, Permutation_Encoding
from Error import AbortError, ComputationError, AssumptionError
try:
	from Queue import Queue
except ImportError: # Python 3
	from queue import Queue

weight = sum

def tweak_vector(v, add, subtract):
	for i in add: v[i] += 1
	for i in subtract: v[i] -= 1
	return v

class Isometry:
	def __init__(self, source_triangulation, target_triangulation, triangle_map):
		# source_triangulation and target_triangulation are two Abstract_Triangulations
		# triangle_map is a dictionary sending each Abstract_Triangle of source_triangulation to a pair
		# (Abstract_Triangle, cycle).
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.triangle_map = triangle_map
		self.edge_map = dict([(triangle[i], self.triangle_map[triangle][0][i+self.triangle_map[triangle][1]]) for triangle in self.source_triangulation for i in range(3)])
		# Check that the thing that we've built is actually a permutation.
		if any(self.edge_map[i] == self.edge_map[j] for i, j in combinations(range(self.source_triangulation.zeta), 2)): self = None
	def __repr__(self):
		return str(self.triangle_map)
	def __getitem__(self, index):
		return self.triangle_map[index]
	def encoding(self):
		return Permutation_Encoding(self.edge_map, self.source_triangulation)

class Abstract_Triangle:
	__slots__ = ['index', 'edge_indices', 'corner_labels']  # !?! Force minimal RAM usage?
	
	def __init__(self, index=None, edge_indices=None, corner_labels=None):
		# Edges are ordered anti-clockwise.
		self.index = index
		self.edge_indices = list(edge_indices) if edge_indices is not None else [-1, -1, -1]
		self.corner_labels = list(corner_labels) if corner_labels is not None else [None, None, None]
	
	def __iter__(self):
		return iter(self.edge_indices)
	
	def __repr__(self):
		return '(%s, %s, %s)' % (self.index, self.edge_indices, self.corner_labels)
	
	def __getitem__(self, index):
		return self.edge_indices[index % 3]

class Abstract_Triangulation:
	def __init__(self, all_edge_indices, all_corner_labels=None):
		self.num_triangles = len(all_edge_indices)
		self.zeta = self.num_triangles * 3 // 2
		
		# We should assert a load of stuff here first. !?!
		# Convention: Flattening all_edge_indices must give the list 0,...,self.zeta-1 with each number appearing exactly twice.
		assert(sorted([x for edge_indices in all_edge_indices for x in edge_indices]) == sorted(list(range(self.zeta)) + list(range(self.zeta))))
		
		if all_corner_labels is None: all_corner_labels = [None] * self.num_triangles
		self.triangles = [Abstract_Triangle(i, edge_indices, corner_labels) for i, edge_indices, corner_labels in zip(range(self.num_triangles), all_edge_indices, all_corner_labels)]
		
		# Now build all the equivalence classes of corners.
		corners = set(product(self.triangles, range(3)))
		self.corner_classes = []
		while len(corners) > 0:
			new_corner_class = [corners.pop()]
			while True:
				next_corner = self.find_adjacent(*new_corner_class[-1])
				if next_corner in corners: 
					new_corner_class.append(next_corner)
					corners.remove(next_corner)
				else:
					break
			
			self.corner_classes.append(new_corner_class)
		
		self.Euler_characteristic = 0 - self.zeta + self.num_triangles  # 0 - E + F as we have no vertices.
		self.max_order = 6 - self.Euler_characteristic  # The maximum order of a periodic mapping class.
		self._face_matrix = None
		self._marking_matrices = None
		
		for edge_index in range(self.zeta):
			assert(len(self.find_edge(edge_index)) == 2)
	
	def copy(self):
		return Abstract_Triangulation([list(triangle.edge_indices) for triangle in self.triangles], [list(triangle.corner_labels) for triangle in self.triangles])
	
	def __repr__(self):
		return '\n'.join(str(triangle) for triangle in self.triangles)
	
	def __iter__(self):
		return iter(self.triangles)
	
	def find_corner_class(self, triangle, side):
		for corner_class in self.corner_classes:
			if (triangle, side) in corner_class:
				return corner_class
	
	def face_matrix(self):
		if self._face_matrix is None:
			self._face_matrix = Matrix([tweak_vector([0] * self.zeta, [triangle[i], triangle[i+1]], [triangle[i+2]]) for triangle in self.triangles for i in range(3)], self.zeta)
		return self._face_matrix
	
	def marking_matrices(self):
		if self._marking_matrices is None:
			corner_choices = [P for P in product(*self.corner_classes) if all(t1 != t2 for ((t1, s1), (t2, s2)) in combinations(P, r=2))]
			self._marking_matrices = [Matrix([tweak_vector([0] * self.zeta, [triangle[side]], [triangle[side+1], triangle[side+2]]) for (triangle, side) in P], self.zeta) for P in corner_choices]
		return self._marking_matrices
	
	def is_multicurve(self, vector):
		if vector == [0] * self.zeta: return False
		
		if not nonnegative_image(self.face_matrix(), vector): return False
		
		for vertex in self.corner_classes:
			for triangle, side in vertex:
				weights = [vector[index] for index in triangle]
				dual_weights_doubled = [weights[1] + weights[2] - weights[0], weights[2] + weights[0] - weights[1], weights[0] + weights[1] - weights[2]]
				for i in range(3):
					if dual_weights_doubled[i] % 2 != 0:  # Is odd.
						return False
				if dual_weights_doubled[side] == 0:
					break
			else:
				return False
		
		return True
		
		return nonnegative_image(self.face_matrix(), vector) and any(nonnegative_image(M, vector) for M in self.marking_matrices())
	
	def geometric_to_algebraic(self, vector):
		# Converts a vector of geometric intersection numbers to a vector of algebraic intersection numbers.
		# !?! TO DO.
		return vector
	
	def find_edge(self, edge_index):
		return [(triangle, side) for triangle in self.triangles for side in range(3) if triangle[side] == edge_index]
	
	def find_neighbour(self, triangle, side):
		# Returns the (triangle, side) opposite to this one.
		containing = self.find_edge(triangle[side])
		return containing[0] if containing[0] != (triangle, side) else containing[1]
	
	def find_adjacent(self, triangle, side):
		# Returns the (triangle, side) one click anti-clockwise around this vertex from this one.
		opposite_corner = self.find_neighbour(triangle,(side+1)%3)
		return (opposite_corner[0], (opposite_corner[1]+1)%3)
	
	def edge_is_flippable(self, edge_index):
		# An edge is flippable iff it lies in two distinct triangles.
		containing_triangles = self.find_edge(edge_index)
		return containing_triangles[0][0] != containing_triangles[1][0]
	
	def find_triangle(self, edge_indices):
		return [triangle for triangle in self.triangles if set(triangle.edge_indices) == set(edge_indices)][0]
	
	def find_indicies_of_square_about_edge(self, edge_index):
		assert(self.edge_is_flippable(edge_index))
		
		containing_triangles = self.find_edge(edge_index)
		return [containing_triangles[i][0][containing_triangles[i][1] + j] for i in (0,1) for j in (1,2)]
	
	def find_corner_labels_of_square_about_edge(self, edge_index):
		assert(self.edge_is_flippable(edge_index))
		
		containing_triangles = self.find_edge(edge_index)
		return [containing_triangles[i][0].corner_labels[(containing_triangles[i][1] + j) % 3] for i in (0,1) for j in (-1,0,1)]
	
	def flip_edge(self, edge_index):
		# Returns a new triangulation obtained by flipping the edge of index edge_index.
		assert(self.edge_is_flippable(edge_index))
		
		a, b, c, d = self.find_indicies_of_square_about_edge(edge_index)
		r, s, t, u, v, w = self.find_corner_labels_of_square_about_edge(edge_index)
		
		new_edge_indices = [list(triangle.edge_indices) for triangle in self.triangles if edge_index not in triangle] + [[edge_index, d, a], [edge_index, b, c]]
		new_corner_labels = [list(triangle.corner_labels) for triangle in self.triangles if edge_index not in triangle] + [[r,s,v], [u,v,s]]
		return Abstract_Triangulation(new_edge_indices, new_corner_labels)
	
	def flip_effect(self, edge_index, vector):
		# Computes the effect of an edge flip on a vector.
		assert(self.edge_is_flippable(edge_index))
		
		a, b, c, d = self.find_indicies_of_square_about_edge(edge_index)
		new_vector = list(vector)
		new_vector[edge_index] = max(vector[a] + vector[c], vector[b] + vector[d]) - vector[edge_index]
		return new_vector
	
	def flipping_edge_improves(self, edge_index, vector):
		assert(self.edge_is_flippable(edge_index))
		
		return weight(self.flip_effect(edge_index, vector)) < weight(vector)
	
	def encode_swap(self, i, j, target_triangulation):
		# Should use an Isometry.
		A = Id_Matrix(self.zeta)
		A[i][i] = 0
		A[j][j] = 0
		A[i][j] = 1
		A[j][i] = 1
		return Encoding([A], [Empty_Matrix(self.zeta)], self, target_triangulation)
	
	def encode_flip(self, edge_index):
		# Returns a pair of Encodings, one from this triangulation to the flipped version and
		# the second its inverse.
		assert(self.edge_is_flippable(edge_index))
		
		a, b, c, d = self.find_indicies_of_square_about_edge(edge_index)
		A1 = Id_Matrix(self.zeta)
		tweak_vector(A1[edge_index], [a, c], [edge_index, edge_index])  # The double -f here forces A1[f][f] = -1.
		C1 = Matrix(tweak_vector([0] * self.zeta, [a, c], [b, d]), self.zeta)
		A2 = Id_Matrix(self.zeta)
		tweak_vector(A2[edge_index], [b, d], [edge_index, edge_index])  # The double -f here forces A2[f][f] = -1.
		C2 = Matrix(tweak_vector([0] * self.zeta, [b, d], [a, c]), self.zeta)
		new_triangulation = self.flip_edge(edge_index)
		return Encoding([A1, A2], [C1, C2], self, new_triangulation), Encoding([A1, A2], [C1, C2], new_triangulation, self)
	
	def encode_twist(self, vector, k=1):
		''' Returns an Encoding of a left Dehn twist about vector raised to the power k.
		If k is zero this will return the identity Encoding. If k is negative this 
		will return an Encoding of a right Dehn twist about vector raised to the power -k.
		Assumes that vector represents a curve and not a multicurve, if given a multicurve an
		AssumptionError is thrown. '''
		if not self.is_multicurve(vector):
			raise AssumptionError('Not a multicurve.')
		
		if k == 0: return Id_Encoding_Sequence(self)
		
		vector = list(vector)
		
		# We'll keep track of what we have conjugated by as well as it's inverse
		# we could compute this at the end by doing:
		#   conjugation_inverse = conjugation.inverse()
		# but this is much faster as we don't need to invert a load of matrices.
		conjugation = Id_Encoding_Sequence(self)
		conjugation_inverse = Id_Encoding_Sequence(self)
		
		time_since_last_weight_loss = 0
		old_weight = weight(vector)
		while weight(vector) > 2:
			# Find the edge which decreases our weight the most.
			# If none exist then it doesn't matter which edge we flip, so long as it meets the curve.
			# By Lee Mosher's work there is a complexity that we will reduce to by doing this and eventually we will reach weight 2.
			# We should spot when we are looping and throw a AssumptionError.
			working_copy = conjugation.target_triangulation
			edge_index = min([i for i in range(working_copy.zeta) if vector[i] > 0], key=lambda i: weight(working_copy.flip_effect(i, vector)))
			
			vector = working_copy.flip_effect(edge_index, vector)
			forward, backwards = conjugation.target_triangulation.encode_flip(edge_index)
			conjugation = forward * conjugation
			conjugation_inverse = conjugation_inverse * backwards
			
			if weight(vector) < old_weight:
				time_since_last_weight_loss = 0
				old_weight = weight(vector)
			else:
				time_since_last_weight_loss += 1
			
			# If we ever fail to make progress more than once it is because our curve was really a multicurve.
			if time_since_last_weight_loss > 2:
				raise AssumptionError('Not a curve.')
		
		working_copy = conjugation.target_triangulation
		# Grab the indices of the two edges we meet.
		e1, e2 = [edge_index for edge_index in range(self.zeta) if vector[edge_index] > 0]
		# We might need to swap these edge indices so we have a good frame of reference.
		containing_triangles = working_copy.find_edge(e1)
		if containing_triangles[0][0][containing_triangles[0][1] + 2] != e2: e1, e2 = e2, e1
		# But to do a right twist we'll need to switch framing again.
		if k < 0: e1, e2 = e2, e1
		# Finally we can encode the twist.
		forwards, backwards = conjugation.target_triangulation.encode_flip(e1)
		swap = forwards.target_triangulation.encode_swap(e1, e2, working_copy)
		T = Encoding_Sequence([swap, forwards], working_copy, working_copy)
		
		return conjugation_inverse * T**abs(k) * conjugation
	
	def regular_neighbourhood(self, edge_index):
		vector = [0] * self.zeta
		(t1, s1), (t2, s2) = self.find_edge(edge_index)
		corner_classes = [corner_class for corner_class in self.corner_classes if (t1, (s1+1) % 3) in corner_class or (t2, (s2+1) % 3) in corner_class]
		for corner_class in corner_classes:
			for triangle, side in corner_class:
				if triangle[side+2] != edge_index:
					vector[triangle[side+2]] += 1
		return vector
	
	def key_curves(self):
		return [self.regular_neighbourhood(edge_index) for edge_index in range(self.zeta)]
	
	def extend_isometry(self, other, source_triangle, target_triangle, cycle, as_Encoding=False):
		if self.zeta != other.zeta: return None
		permutation = {}
		
		triangles_to_process = Queue()
		# We start by assuming that the source_triangle gets mapped to target_triangle via the permutation (cycle,cycle+1,cycle+2).
		triangles_to_process.put((source_triangle, target_triangle, cycle))
		seen_triangles = set([source_triangle])
		permutation[source_triangle] = (target_triangle, cycle)
		while not triangles_to_process.empty():
			from_triangle, to_triangle, cycle = triangles_to_process.get()
			for side in range(3):
				permutation[from_triangle] = (to_triangle, cycle)
				from_triangle_neighbour, from_neighbour_side = self.find_neighbour(from_triangle, side)
				to_triangle_neighbour, to_neighbour_side = other.find_neighbour(to_triangle, (side+cycle)%3)
				if from_triangle_neighbour not in seen_triangles:
					triangles_to_process.put((from_triangle_neighbour, to_triangle_neighbour, (to_neighbour_side-from_neighbour_side) % 3))
					seen_triangles.add(from_triangle_neighbour)
		
		d = dict([(triangle[i], permutation[triangle][0][i+permutation[triangle][1]]) for triangle in self for i in range(3)])
		# Check that the thing that we've built is actually a permutation.
		if any(d[i] == d[j] for i, j in combinations(range(self.zeta), 2)): return None
		
		if as_Encoding:
			return Isometry(self, other, permutation).encoding()
		else:
			return Isometry(self, other, permutation)
	
	def all_isometries(self, other, as_Encodings=False):
		# Returns a list of permutations of [0,...,self.zeta], each of which maps the edges of self 
		# to the edges of other by an orientation preserving isometry.
		if self.zeta != other.zeta: return []
		
		isometries = []
		for triangle in other:
			for i in range(3):
				isometry = self.extend_isometry(other, self.triangles[0], triangle, i, as_Encodings)
				if isometry is not None:
						isometries.append(isometry)
		
		return isometries
