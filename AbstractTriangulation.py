from __future__ import print_function
from itertools import product, combinations
from Matrix import Matrix, Id_Matrix, Empty_Matrix, nonnegative, nontrivial, nonnegative_image
from Encoding import Encoding, Encoding_Sequence, Id_Encoding_Sequence, Permutation_Encoding
from Symbolic_Computation import simplify, compute_powers
from Error import AbortError
from time import time
from random import choice
try:
	from Queue import Queue
except ImportError: # Python 3
	from queue import Queue

weight = sum

def cycle_x_to_front(L, x):
	assert(x in L)
	i = L.index(x)
	return L[i:] + L[:i]

def tweak_vector(v, add, subtract):
	for i in add: v[i] += 1
	for i in subtract: v[i] -= 1
	return v

class Abstract_Triangle:
	def __init__(self, index=None):
		# Edges are ordered anti-clockwise.
		self.index = index
		self.edge_indices = [-1, -1, -1]
	
	def __repr__(self):
		return '%s: %s' % (self.index, self.edge_indices)
	
	def __getitem__(self, index):
		return self.edge_indices[index % 3]

class Abstract_Triangulation:
	def __init__(self, all_edge_indices):
		# Convention (although this is not enforced (yet)): flattening all_edge_indices must give the list
		# 0,...,self.zeta-1 with each number appearing twice.
		self.triangles = [Abstract_Triangle(i) for i in range(len(all_edge_indices))]
		self.num_triangles = len(self.triangles)
		self.zeta = self.num_triangles * 3 // 2
		
		# We should assert a load of stuff here first. !?!
		for triangle, edge_indices in zip(self.triangles, all_edge_indices):
			triangle.edge_indices = list(edge_indices)
		
		# Now build all the equivalence classes of corners.
		corners = set(product(self.triangles, range(3)))
		self.corner_classes = []
		while len(corners) > 0:
			new_corner_class = [corners.pop()]
			while True:
				current_corner = new_corner_class[-1]
				adjacent_corner = (current_corner[0], (current_corner[1]+1)%3)
				containing = self.find_edge(adjacent_corner[0][adjacent_corner[1]])
				opposite_corner = containing[0] if containing[0] != adjacent_corner else containing[1]
				next_corner = (opposite_corner[0], (opposite_corner[1]+1)%3)
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
		return Abstract_Triangulation([list(triangle.edge_indices) for triangle in self.triangles])
	
	def __repr__(self):
		return '\n'.join(str(triangle) for triangle in self.triangles)
	
	def __iter__(self):
		return iter(self.triangles)
	
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
		return nonnegative_image(self.face_matrix(), vector) and any(nonnegative_image(M, vector) for M in self.marking_matrices())
	
	def find_edge(self, edge_index):
		return [(triangle, side) for triangle in self.triangles for side in range(3) if triangle[side] == edge_index]
	
	def find_neighbour(self, triangle, side):
		containing = self.find_edge(triangle[side])
		return containing[0] if containing[0] != (triangle, side) else containing[1]
	
	def edge_is_flippable(self, edge_index):
		# An edge is flippable iff it lies in two distinct triangles.
		containing_triangles = self.find_edge(edge_index)
		return containing_triangles[0][0] != containing_triangles[1][0]
	
	def find_indicies_of_square_about_edge(self, edge_index):
		assert(self.edge_is_flippable(edge_index))
		
		containing_triangles = self.find_edge(edge_index)
		actual_containing_triangles = [containing_triangles[0][0], containing_triangles[1][0]]
		
		A_edge_indices = cycle_x_to_front(actual_containing_triangles[0].edge_indices, edge_index)
		B_edge_indices = cycle_x_to_front(actual_containing_triangles[1].edge_indices, edge_index)
		return A_edge_indices[1:] + B_edge_indices[1:]
	
	def flip_edge(self, edge_index):
		# Returns a new triangulation obtained by flipping the edge of index edge_index.
		assert(self.edge_is_flippable(edge_index))
		
		a, b, c, d = self.find_indicies_of_square_about_edge(edge_index)
		new_edge_indices = [list(triangle.edge_indices) for triangle in self.triangles if edge_index not in triangle.edge_indices] + [[edge_index, d, a], [edge_index, b, c]]
		return Abstract_Triangulation(new_edge_indices)
	
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
		''' Returns an Encoding of a left Dehn twist about v raised to the power k.
		If k is zero this will return the identity Encoding. If k is negative this 
		will return an Encoding of a right Dehn twist about v raised to the power -k.
		This assumes v represents a curve and not a multicurve, god only knows what will
		happen in that case. '''
		# assert self.is_multicurve(vector)  # and self.is_curve(vector)  # Don't know how to do this.
		# More asserts here !?!
		
		if k == 0: return Id_Encoding_Sequence(self)
		
		vector = list(vector)
		
		# We'll keep track of what we have conjugated by as well as it's inverse
		# we could compute this at the end by doing:
		#   conjugation_inverse = conjugation.inverse()
		# but this is much faster as we don't need to invert a load of matrices.
		conjugation = Id_Encoding_Sequence(self)
		conjugation_inverse = Id_Encoding_Sequence(self)
		
		while weight(vector) > 2:
			# Find an edge which decreases our weight, if it exists.
			working_copy = conjugation.target_triangulation
			for edge_index in range(working_copy.zeta):
				if working_copy.edge_is_flippable(edge_index):
					if working_copy.flipping_edge_improves(edge_index, vector):
						vector = working_copy.flip_effect(edge_index, vector)
						forward, backwards = conjugation.target_triangulation.encode_flip(edge_index)
						conjugation = forward * conjugation
						conjugation_inverse = conjugation_inverse * backwards
						break
			else:  # If none exist then it doesn't matter which edge we flip, so long as it meets the curve.
				for edge_index in range(working_copy.zeta):
					if working_copy.edge_is_flippable(edge_index):
						if vector[edge_index] > 0:
							vector = working_copy.flip_effect(edge_index, vector)
							forward, backwards = conjugation.target_triangulation.encode_flip(edge_index)
							conjugation = forward * conjugation
							conjugation_inverse = conjugation_inverse * backwards
							break
		
		assert(weight(vector) == 2)
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
	
	def find_isometries(self, other, as_Encodings=False):
		# Returns a list of permutations of [0,...,self.zeta], each of which maps the edges of self 
		# to the edges of other isometrically.
		if self.zeta != other.zeta: return []
		
		def safe_assign(perm, i, j):
			if perm[i] != -1 and perm[i] != j: return False
			perm[i] = j
			return True
		
		def extend_map(other, t, k):
			permutation = [-1] * self.zeta
			base_triangle = self.triangles[0]
			
			triangles_to_process = Queue()
			triangles_to_process.put((base_triangle, t, k))  # We start by assuming that the base_triangle gets mapped to t via the permutation (k,k+1,k+2).
			seen_triangles = set([base_triangle])
			while not triangles_to_process.empty():
				from_triangle, to_triangle, cycle = triangles_to_process.get()
				for side in range(3):
					if not safe_assign(permutation, from_triangle[side], to_triangle[side+cycle]): return None
					from_triangle_neighbour, from_neighbour_side = self.find_neighbour(from_triangle, side)
					to_triangle_neighbour, to_neighbour_side = other.find_neighbour(to_triangle, (side+cycle)%3)
					if from_triangle_neighbour not in seen_triangles:
						triangles_to_process.put((from_triangle_neighbour, to_triangle_neighbour, (to_neighbour_side-from_neighbour_side) % 3))
						seen_triangles.add(from_triangle_neighbour)
			
			return permutation
		
		if as_Encodings:
			return [Permutation_Encoding(p, self) for p in [extend_map(other, triangle, i) for triangle in other for i in range(3)] if p is not None]
		else:
			return [p for p in [extend_map(other, triangle, i) for triangle in other for i in range(3)] if p is not None]
	
	def puncture_trigons(self, vector):
		new_labels = [list(triangle.edge_indices) for triangle in self.triangles]
		new_vector = list(vector)
		zeta = self.zeta
		for triangle in self.triangles:
			a, b, c = triangle.edge_indices
			if new_vector[a] + new_vector[b] > new_vector[c] and new_vector[b] + new_vector[c] > new_vector[a] and new_vector[c] + new_vector[a] > new_vector[b]:
				x, y, z = zeta, zeta+1, zeta+2
				new_labels.extend([[a,z,y], [b,x,z], [c,y,x]])
				new_labels.remove([a,b,c])
				new_vector.extend([(new_vector[b] + new_vector[c] - new_vector[a]) / 2, (new_vector[c] + new_vector[a] - new_vector[b]) / 2, (new_vector[a] + new_vector[b] - new_vector[c]) / 2])
				zeta = zeta + 3
		return Abstract_Triangulation(new_labels), new_vector
	
	def collapse_trivial_weight(self, vector, edge_index):
		a, b, c, d = self.find_indicies_of_square_about_edge(edge_index)  # Get the square about it.
		# WLOG: a < b and c < d.
		if b < a: a, b = b, a
		if d < c: c, d = d, c
		
		replacement = dict(zip([i for i in range(self.zeta) if i not in [edge_index, b, d]], range(self.zeta)))
		replacement[b] = replacement[a]
		replacement[d] = replacement[c]
		
		new_labels = [[replacement[i] for i in triangle.edge_indices] for triangle in self if edge_index not in triangle.edge_indices]
		new_vector = [[vector[j] for j in range(self.zeta) if j != edge_index and replacement[j] == i][0] for i in range(self.zeta - 3)]
		return Abstract_Triangulation(new_labels), new_vector
	
	def splitting_sequence(self, vector):
		# We assume that vector is a list of algebraic numbers. 
		# We continually use Symbolic_Computation.simplify() just to be safe.
		# This assumes that the edges are labelled 0, ..., self.zeta-1, this is a very sane labelling system.
		# In fact this algorithm currently assumes that vector is the stable lamination.
		
		# At the end len(working_copy.corner_classes) - len(self.corner_classes) will be the number of singularities of vector.
		
		def projectivise_vector(vector):
			s = simplify(sum(vector))
			return tuple([simplify(v / s) for v in vector])
		
		# Check if vector is obviously reducible.
		if any(v == 0 for v in vector):
			return [], [], 1
		
		working_copy, vector_copy = self.puncture_trigons(vector)
		flipped = []
		seen_vectors = [(0, list(vector_copy), projectivise_vector(vector_copy), working_copy)]
		while True:
			i = max(range(working_copy.zeta), key=lambda i: vector_copy[i])  # Find the index of the largest entry
			a, b, c, d = working_copy.find_indicies_of_square_about_edge(i)  # Get the square about it.
			working_copy = working_copy.flip_edge(i)  # Flip the square.
			vector_copy[i] = simplify(max(vector_copy[a] + vector_copy[c], vector_copy[b] + vector_copy[d]) - vector_copy[i])  # Update the weights.
			if vector_copy[i] == 0:  
				# Assumes pA.
				working_copy, vector_copy = working_copy.collapse_trivial_weight(vector_copy, i)
				# If (some property of the graph is not met): raise AbortError.
				# This is one such property but there should be more subtle ones.
				if working_copy.zeta < self.zeta:
					return [], [], 1
			flipped.append(i)
			projective_vector = projectivise_vector(vector_copy)
			print(i, '| ' + ', '.join('%0.4f' % v for v in projective_vector))
			for index, old_vector, old_projective_vector, old_triangulation in seen_vectors:
				for isometry in working_copy.find_isometries(old_triangulation):
					permuted_old_projective_vector = tuple([old_projective_vector[isometry[i]] for i in range(working_copy.zeta)])
					if projective_vector == permuted_old_projective_vector:
						return flipped[:index], flipped[index:], simplify(old_vector[isometry[0]] / vector_copy[0])
			else:
				seen_vectors.append((len(seen_vectors), list(vector_copy), projectivise_vector(vector_copy), working_copy))

if __name__ == '__main__':
	import sys
	
	# This a 12--gon with one vertex at the centre and opposite sides identified.
	T = Abstract_Triangulation([[6, 7, 0], [8, 1, 7], [8, 9, 2], [9, 10, 3], [11, 4, 10], [12, 5, 11], 
	[12, 13, 0], [14, 1, 13], [14, 15, 2], [15, 16, 3], [16, 17, 4], [6, 5, 17]])
	a = T.encode_twist([1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0])
	A = T.encode_twist([1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], k=-1)
	b = T.encode_twist([1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0])
	B = T.encode_twist([1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0], k = -1)
	
	p = T.find_isometries(T, as_Encodings=True)[1]  # I've checked, this is a 1/12 click of a 12--gon.
	
	h = (b*A*A*b*p)**6
	V, dilatation = h.stable_lamination(exact=True)
	x, y, z = T.splitting_sequence(V)
	print(len(x), len(y), compute_powers(dilatation, z))
	# exit(1)
	
	# Another n--gon. (n==24)
	T = Abstract_Triangulation([[12, 13, 0], [14, 1, 13], [15, 2, 14], [15, 16, 3], [17, 4, 16], [17, 18, 5], 
		[18, 19, 6], [20, 7, 19], [21, 8, 20], [21, 22, 9], [22, 23, 10], [24, 11, 23], [25, 0, 24], [25, 26, 1], 
		[26, 27, 2], [28, 3, 27], [29, 4, 28], [29, 30, 5], [30, 31, 6], [32, 7, 31], [33, 8, 32], [33, 34, 9], 
		[34, 35, 10], [12, 11, 35]])
	
	a = T.encode_twist([0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
	A = T.encode_twist([0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], k=-1)
	b = T.encode_twist([0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0])
	B = T.encode_twist([0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], k=-1)
	
	p = T.find_isometries(T, as_Encodings=True)[1]  # This is a click of some sort.
	h = (a*B*B*a*p)**12
	V, dilatation = h.stable_lamination(exact=True)
	x, y, z = T.splitting_sequence(V)
	print(k, len(x), len(y), compute_powers(dilatation, z))
	
	
	
	# S_1_2: We'll do some random twists.
	T = Abstract_Triangulation([[2, 1, 3], [2, 0, 4], [1, 5, 0], [4, 3, 5]])
	a = T.encode_twist([0,0,1,1,1,0])
	b = T.encode_twist([0,1,0,1,0,1])
	c = T.encode_twist([1,0,0,0,1,1])
	A = T.encode_twist([0,0,1,1,1,0], k=-1)
	B = T.encode_twist([0,1,0,1,0,1], k=-1)
	C = T.encode_twist([1,0,0,0,1,1], k=-1)
	
	def expand_class(string):
		print(string)
		h = Id_Encoding_Sequence(T)
		for letter in string:
			h = {'a':a, 'b':b, 'c':c, 'A':A, 'B':B, 'C':C}[letter] * h
		return h
	
	
	def random_mapping_class(n):
		return ''.join(choice('abcABC') for i in range(n))
	
	print('Start')
	for k in range(3, 50):
		# h = (a*b*C*b)**k * (a*b*C) * (B*c*B*A)**k
		# h = expand_class(random_mapping_class(10))
		# h = expand_class('aBc')
		h = expand_class(sys.argv[1] if len(sys.argv) > 1 else random_mapping_class(10))
		
		start_time = time()
		try:
			V, dilatation = h.stable_lamination(exact=True)
		except AbortError:
			pass
		else:
			t1 = time() - start_time
			start_time = time()
			x, y, z = T.splitting_sequence(V)
			t2 = time() - start_time
			if z > 1:
				print('Times:', t1, t2)
				print(k, len(x), len(y), compute_powers(dilatation, z))
				print(float(dilatation), float(z))
			else:
				print('Probably reducible')
		exit(0)
