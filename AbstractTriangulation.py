from itertools import product, combinations
from Matrix import Matrix, Id_Matrix, Empty_Matrix, nonnegative, nontrivial, nonnegative_image
from Encoding import Encoding, Encoding_Sequence, Id_Encoding_Sequence
from Symbolic_Computation import simplify, compute_powers
from time import time
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
	
	def find_isometries(self, other):
		# Returns a list of permutations of [0,...,self.zeta], each of which maps the edges of self 
		# to the edges of other isometrically.
		if self.zeta != other.zeta: return []
		# return [list(range(self.zeta))]
		
		def safe_assign(perm, i, j):
			if perm[i] != -1 and perm[i] != j: return False
			perm[i] = j
			return True
		
		def extend_map(other, t, k):
			permutation = [-1] * self.zeta
			base_triangle = self.triangles[0]
			if not safe_assign(permutation, base_triangle[0], t[k]): return None
			if not safe_assign(permutation, base_triangle[1], t[k+1]): return None
			if not safe_assign(permutation, base_triangle[2], t[k+2]): return None
			
			seen_triangles = set([base_triangle])
			triangles_to_process = Queue()
			triangles_to_process.put((base_triangle, t, k))
			
			while not triangles_to_process.empty():
				from_triangle, to_triangle, cycle = triangles_to_process.get()
				# print(from_triangle.index, to_triangle.index)
				for side in range(3):
					from_triangle_neighbour, from_neighbour_side = self.find_neighbour(from_triangle, side)
					to_triangle_neighbour, to_neighbour_side = other.find_neighbour(to_triangle, (side+cycle) % 3)
					for i in range(3):
						if not safe_assign(permutation, from_triangle_neighbour[from_neighbour_side+i], to_triangle_neighbour[to_neighbour_side+i]): return None
					if from_triangle_neighbour not in seen_triangles:
						triangles_to_process.put((from_triangle_neighbour, to_triangle_neighbour, (to_neighbour_side-from_neighbour_side) % 3))
						seen_triangles.add(from_triangle_neighbour)
				
			return permutation
		
		return list(filter(lambda x: x is not None, [extend_map(other, triangle, i) for triangle in other for i in range(3)]))
	
	def puncture_trigons(self, vector):
		new_triangulation = [list(triangle.edge_indices) for triangle in self.triangles]
		new_vector = list(vector)
		zeta = self.zeta
		for triangle in self.triangles:
			a, b, c = triangle.edge_indices
			if new_vector[a] + new_vector[b] > new_vector[c] and new_vector[b] + new_vector[c] > new_vector[a] and new_vector[c] + new_vector[a] > new_vector[b]:
				x, y, z = zeta, zeta+1, zeta+2
				new_triangulation.extend([[a,z,y], [b,x,z], [c,y,x]])
				new_triangulation.remove([a,b,c])
				new_vector.extend([(new_vector[b] + new_vector[c] - new_vector[a]) / 2, (new_vector[c] + new_vector[a] - new_vector[b]) / 2, (new_vector[a] + new_vector[b] - new_vector[c]) / 2])
				zeta = zeta + 3
		return Abstract_Triangulation(new_triangulation), new_vector
	
	def collapse_trivial_weights(self, vector):
		# TO DO !?!
		def replace(x, y, L):
			return [y if l == y else l for l in L]
		
		
		working_copy, vector_copy = self.copy(), list(vector)
		new_labels = [list(triangle.edge_vectors) for triangle in working_copy]
		while any(v == 0 for v in vector_copy):
			i = vector_copy.index(0)
			a, b, c, d = working_copy.find_indicies_of_square_about_edge(i)  # Get the square about it.
			if b < a: a, b = b, a
			if d < c: c, d = d, c
			
			
			
			# new_labels = [replace(d, c, replace(b, a, label) for label in new_labels]
			
			# vector_copy[i] = -1
			
	
	def splitting_sequence(self, vector):
		# We assume that vector is a list of algebraic numbers. 
		# We continually use Symbolic_Computation.simplify() just to be safe.
		# This assumes that the edges are labelled 0, ..., self.zeta-1, this is a very sane labelling system.
		
		# !?! TO DO compress virtual edges of weight 0.
		working_copy, vector_copy = self.puncture_trigons(vector)
		
		def projectivise_vector(vector):
			return [simplify(v / vector[0]) for v in vector]
			s = simplify(sum(vector))
			return [simplify(v / s) for v in vector]
		
		flipped = []
		seen_vectors = [(0, list(vector_copy), projectivise_vector(vector_copy), working_copy)]
		while True:
			i = max(range(self.zeta), key=lambda i: vector_copy[i])  # Find the index of the largest entry
			a, b, c, d = working_copy.find_indicies_of_square_about_edge(i)  # Get the square about it.
			working_copy = working_copy.flip_edge(i)  # Flip the square.
			vector_copy[i] = simplify(max(vector_copy[a] + vector_copy[c], vector_copy[b] + vector_copy[d]) - vector_copy[i])  # Update the weights.
			flipped.append(i)
			# print(i, ', '.join('%0.4f' % v for v in vector_copy))
			for index, old_vector, old_projective_vector, old_triangulation in seen_vectors:
				for isometry in working_copy.find_isometries(old_triangulation):
					permuted_old_projective_vector = [old_projective_vector[isometry[i]] for i in range(working_copy.zeta)]
					projective_vector = projectivise_vector(vector_copy)
					if projective_vector == permuted_old_projective_vector:
						return flipped[:index], flipped[index:], simplify(old_vector[isometry[0]] / vector_copy[0])
			else:
				seen_vectors.append((len(seen_vectors), list(vector_copy), projectivise_vector(vector_copy), working_copy))

if __name__ == '__main__':
	T = Abstract_Triangulation([[2, 1, 3], [2, 0, 4], [1, 5, 0], [4, 3, 5]])
	a = T.encode_twist([0,0,1,1,1,0])
	b = T.encode_twist([0,1,0,1,0,1])
	c = T.encode_twist([1,0,0,0,1,1])
	A = T.encode_twist([0,0,1,1,1,0], k=-1)
	B = T.encode_twist([0,1,0,1,0,1], k=-1)
	C = T.encode_twist([1,0,0,0,1,1], k=-1)
	
	def random_mapping_class(n):
		h = Id_Encoding_Sequence(T)
		for i in range(n):
			h = choice([a,b,c,A,B,C]) * h
		return h
	
	print('Start')
	for k in range(3, 50):
		# h = (a*b*C*b)**k * (a*b*C) * (B*c*B*A)**k
		h = random_mapping_class(25)
		start_time = time()
		V, dilatation = h.stable_lamination(exact=True)
		t1 = time() - start_time
		start_time = time()
		x, y, z = T.splitting_sequence(V)
		t2 = time() - start_time
		print(k, len(x), len(y), t1, t2)
