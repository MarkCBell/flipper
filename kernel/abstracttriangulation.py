
from itertools import product, combinations
try:
	from Queue import Queue
except ImportError: # Python 3
	from queue import Queue

import Flipper

class AbstractTriangle(object):
	# __slots__ = ['index', 'edge_indices', 'corner_labels']  # Force minimal RAM usage.
	
	def __init__(self, index=None, edge_indices=None, corner_labels=None):
		# Edges are ordered anti-clockwise.
		self.index = index
		self.edge_indices = list(edge_indices) if edge_indices is not None else [-1, -1, -1]
		self.corner_labels = list(corner_labels) if corner_labels is not None else [None, None, None]
	
	def __repr__(self):
		return '(%s, %s, %s)' % (self.index, self.edge_indices, self.corner_labels)
		# return '(%s, %s)' % (self.index, self.edge_indices)
	
	# Note that this is NOT the same convention as used in pieces.
	# There iterating and index accesses return edges.
	def __iter__(self):
		return iter(self.edge_indices)
	
	def __getitem__(self, index):
		return self.edge_indices[index % 3]

class AbstractTriangulation(object):
	def __init__(self, all_edge_indices, all_corner_labels=None):
		self.num_triangles = len(all_edge_indices)
		self.zeta = self.num_triangles * 3 // 2
		
		# We should assert a load of stuff here first. !?!
		# Convention: Flattening all_edge_indices must give the list 0,...,self.zeta-1 with each number appearing exactly twice.
		assert(sorted([x for edge_indices in all_edge_indices for x in edge_indices]) == sorted(list(range(self.zeta)) + list(range(self.zeta))))
		
		if all_corner_labels is None: all_corner_labels = [None] * self.num_triangles
		self.triangles = [AbstractTriangle(i, edge_indices, corner_labels) for i, edge_indices, corner_labels in zip(range(self.num_triangles), all_edge_indices, all_corner_labels)]
		self.edge_contained_in = dict((edge_index, [(triangle, side) for triangle in self.triangles for side in range(3) if triangle[side] == edge_index]) for edge_index in range(self.zeta))
		
		# Now build all the equivalence classes of corners. These are each guaranteed to be ordered anti-clockwise about the vertex.
		corners = list(product(self.triangles, range(3)))
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
			
			self.corner_classes.append(tuple(new_corner_class))
		
		self.num_vertices = len(self.corner_classes)
		self.Euler_characteristic = 0 - self.zeta + self.num_triangles  # 0 - E + F as we have no vertices.
		self.max_order = 6 - 6 * self.Euler_characteristic  # The maximum order of a periodic mapping class. # !?! CHECK THIS IN THE PRIMER.
		self._face_matrix = None
		self._marking_matrices = None
		
		for edge_index in range(self.zeta):
			assert(len(self.find_edge(edge_index)) == 2)
	
	def copy(self):
		return AbstractTriangulation([list(triangle.edge_indices) for triangle in self.triangles], [list(triangle.corner_labels) for triangle in self.triangles])
	
	def __repr__(self):
		return '\n'.join(str(triangle) for triangle in self.triangles)
	
	def __iter__(self):
		return iter(self.triangles)
	
	def __getitem__(self, index):
		return self.triangles[index]
	
	def find_corner_class(self, triangle, side):
		side = side % 3
		for corner_class in self.corner_classes:
			if (triangle, side) in corner_class:
				return corner_class
	
	def find_edge_corner_classes(self, edge_index):
		# Returns the two corner classes contain the ends of the specified edge.
		containing_triangles = self.find_edge(edge_index)
		triangle, side = containing_triangles[0]
		return [self.find_corner_class(triangle, side + 1), self.find_corner_class(triangle, side + 2)]
	
	def face_matrix(self):
		if self._face_matrix is None:
			self._face_matrix = Flipper.kernel.Matrix([Flipper.kernel.matrix.tweak_vector([0] * self.zeta, [triangle[i], triangle[i+1]], [triangle[i+2]]) for triangle in self.triangles for i in range(3)], self.zeta)
		return self._face_matrix
	
	def marking_matrices(self):
		if self._marking_matrices is None:
			corner_choices = [P for P in product(*self.corner_classes) if all(t1 != t2 for ((t1, s1), (t2, s2)) in combinations(P, r=2))]
			self._marking_matrices = [Flipper.kernel.Matrix([Flipper.kernel.matrix.tweak_vector([0] * self.zeta, [triangle[side]], [triangle[side+1], triangle[side+2]]) for (triangle, side) in P], self.zeta) for P in corner_choices]
		return self._marking_matrices
	
	def find_edge(self, edge_index):
		# Return the list of (triangle, side) which have label edge_index.
		return self.edge_contained_in[edge_index]
	
	def find_neighbour(self, triangle, side):
		# Returns the (triangle, side) opposite to this one.
		containing = self.find_edge(triangle[side])
		return containing[0] if containing[0] != (triangle, side) else containing[1]
	
	def find_adjacent(self, triangle, side):
		# Returns the (triangle, side) one click anti-clockwise around this vertex from this one.
		opposite_corner = self.find_neighbour(triangle, (side+1)%3)
		return (opposite_corner[0], (opposite_corner[1]+1)%3)
	
	def edge_is_flippable(self, edge_index):
		# An edge is flippable iff it lies in two distinct triangles.
		containing_triangles = self.find_edge(edge_index)
		return containing_triangles[0][0] != containing_triangles[1][0]
	
	def flip_edge(self, edge_index):
		# Returns a new triangulation obtained by flipping the edge of index edge_index.
		assert(self.edge_is_flippable(edge_index))
		
		a, b, c, d = self.find_indicies_of_square_about_edge(edge_index)
		r, s, t, u, v, w = self.find_corner_labels_of_square_about_edge(edge_index)
		
		new_edge_indices = [list(triangle.edge_indices) for triangle in self if edge_index not in triangle] + [[edge_index, d, a], [edge_index, b, c]]
		new_corner_labels = [list(triangle.corner_labels) for triangle in self if edge_index not in triangle] + [[r, s, v], [u, v, s]]
		
		return AbstractTriangulation(new_edge_indices, new_corner_labels)
	
	def find_triangle(self, edge_indices):
		# There can be more than one match in the case of S_1_1.
		matches = [triangle for triangle in self if any(all(triangle[i+j] == edge_indices[j] for j in range(3)) for i in range(3))]
		if matches != []:
			return matches[0]
		else:
			return None
	
	def find_indicies_of_square_about_edge(self, edge_index):
		assert(self.edge_is_flippable(edge_index))
		
		containing_triangles = self.find_edge(edge_index)
		return [containing_triangles[i][0][containing_triangles[i][1] + j] for i in (0, 1) for j in (1, 2)]
	
	def find_corner_labels_of_square_about_edge(self, edge_index):
		assert(self.edge_is_flippable(edge_index))
		
		containing_triangles = self.find_edge(edge_index)
		return [containing_triangles[i][0].corner_labels[(containing_triangles[i][1] + j) % 3] for i in (0, 1) for j in (-1, 0, 1)]
	
	def homology_basis(self):
		# Returns a basis for H_1 of the underlying punctured surface. Each element is given as a path
		# in the dual 1--skeleton. Each pair of paths is guaranteed to meet at most once. 
		
		# Construct a maximal spanning tree in the 1--skeleton of the triangulation.
		tree = [False] * self.zeta
		vertices_used = dict((vertex, False) for vertex in self.corner_classes)
		vertices_used[self.corner_classes[0]] = True
		while True:
			for edge_index in range(self.zeta):
				a, b = self.find_edge_corner_classes(edge_index)
				if not tree[edge_index] and (vertices_used[a] != vertices_used[b]):
					tree[edge_index] = True
					vertices_used[a] = True
					vertices_used[b] = True
					break
			else:
				break  # If there are no more to add then our tree is maximal
		
		# Now construct a maximal spanning tree in the complement of the tree in the 1--skeleton of the dual triangulation.
		dual_tree = [False] * self.zeta
		faces_used = dict((triangle, False) for triangle in self.triangles)
		faces_used[self.triangles[0]] = True
		while True:
			for edge_index in range(self.zeta):
				(a, side_a), (b, side_b) = self.find_edge(edge_index)
				if not tree[edge_index] and not dual_tree[edge_index] and (faces_used[a] != faces_used[b]):
					dual_tree[edge_index] = True
					faces_used[a] = True
					faces_used[b] = True
					break
			else:
				break  # If there are no more to add then our tree is maximal
		
		# Generators are given by edges not in the tree or the dual tree (along with some segment 
		# in the dual tree to make it into a loop).
		dual_tree_indices = [edge_index for edge_index in range(self.zeta) if dual_tree[edge_index]]
		homology_generators = []
		for edge_index in range(self.zeta):
			if not tree[edge_index] and not dual_tree[edge_index]:
				generator = [edge_index]
				(source, side_source), (target, side_target) = self.find_edge(edge_index)
				
				# Find a path in dual_tree from source to target. This is a really
				# inefficient way to do this. We initially define the distance to
				# each point to be self.num_triangles+1 which we know is larger than any possible
				# distance.
				distance = dict((triangle, self.num_triangles+1) for triangle in self.triangles)
				distance[source] = 0
				while distance[target] == self.num_triangles+1:
					for edge in dual_tree_indices:  # Only allowed to move in the tree.
						(a, side_a), (b, side_b) = self.find_edge(edge)
						distance[a] = min(distance[b]+1, distance[a])
						distance[b] = min(distance[a]+1, distance[b])
				
				# Now find a way from the target back to the source by following the distance
				current = target
				while current != source:
					for edge in dual_tree_indices:
						(a, side_a), (b, side_b) = self.find_edge(edge)
						if b == current: a, b = b, a
						
						if a == current and distance[b] == distance[a]-1:
							generator.append(edge)
							current = b
							break
				
				# We've now made a generating loop.
				homology_generators.append(generator)
		
		return homology_generators
	
	def all_isometries(self, other_triangulation):
		# Returns a list of all orientation preserving isometries from self to other_triangle.
		if self.zeta != other_triangulation.zeta: return []
		
		def extend_isometry(source_triangulation, target_triangulation, source_triangle, target_triangle, cycle):
			triangle_map = {}
			triangles_to_process = Queue()
			# We start by assuming that the source_triangle gets mapped to target_triangle via the permutation (cycle,cycle+1,cycle+2).
			triangles_to_process.put((source_triangle, target_triangle, cycle))
			seen_triangles = set([source_triangle])
			while not triangles_to_process.empty():
				from_triangle, to_triangle, cycle = triangles_to_process.get()
				triangle_map[from_triangle] = (to_triangle, cycle)
				for side in range(3):
					from_triangle_neighbour, from_neighbour_side = source_triangulation.find_neighbour(from_triangle, side)
					to_triangle_neighbour, to_neighbour_side = target_triangulation.find_neighbour(to_triangle, cycle[side])
					if from_triangle_neighbour not in seen_triangles:
						triangles_to_process.put((from_triangle_neighbour, to_triangle_neighbour, Flipper.kernel.permutation.cyclic_permutation((to_neighbour_side-from_neighbour_side) % 3, 3)))
						seen_triangles.add(from_triangle_neighbour)
			
			return Flipper.kernel.Isometry(source_triangulation, target_triangulation, triangle_map)
		
		isometries = []
		for other_triangle in other_triangulation:
			for i in range(3):
				try:
					isometry = extend_isometry(self, other_triangulation, self.triangles[0], other_triangle, Flipper.kernel.permutation.cyclic_permutation(i, 3))
				except Flipper.AssumptionError:
					pass
				else:
					for triangle in self:
						target, perm = isometry[triangle]
						if any(target.corner_labels[perm[side]] != triangle.corner_labels[side] for side in range(3)):
							break
					else:
						isometries.append(isometry)
		
		return isometries

	def is_isometric_to(self, other_triangulation):
		return len(self.all_isometries(other_triangulation)) > 0
	
	# Laminations we can build on the triangulation.
	def lamination(self, vector):
		return Flipper.kernel.Lamination(self, vector)
	
	def empty_lamination(self):
		return self.lamination([0] * self.zeta)
	
	def regular_neighbourhood(self, edge_index):
		vector = [0] * self.zeta
		(t1, s1), (t2, s2) = self.find_edge(edge_index)
		corner_classes = [corner_class for corner_class in self.corner_classes if (t1, (s1+1) % 3) in corner_class or (t2, (s2+1) % 3) in corner_class]
		for corner_class in corner_classes:
			for triangle, side in corner_class:
				if triangle[side+2] != edge_index:
					vector[triangle[side+2]] += 1
		return self.lamination(vector)
	
	def key_curves(self):
		# These curves fill so if they are all fixed by a mapping class then it is the identity
		# (or possibly the hyperelliptic if we are on S_{0, 4} or S_{1, 1}).
		return [self.regular_neighbourhood(edge_index) for edge_index in range(self.zeta)]
	
	def Id_Encoding(self):
		f = b = [Flipper.kernel.PartialFunction(self, self, Flipper.kernel.Id_Matrix(self.zeta))]
		return Flipper.kernel.Encoding(f, b)
	
	def Id_EncodingSequence(self):
		return Flipper.kernel.EncodingSequence([self.Id_Encoding()])
	
	def encode_flip(self, edge_index):
		# Returns a forwards and backwards maps to a new triangulation obtained by flipping the edge of index edge_index.
		assert(self.edge_is_flippable(edge_index))
		
		new_triangulation = self.flip_edge(edge_index)
		
		a, b, c, d = self.find_indicies_of_square_about_edge(edge_index)
		A1 = Flipper.kernel.Id_Matrix(self.zeta)
		Flipper.kernel.matrix.tweak_vector(A1[edge_index], [a, c], [edge_index, edge_index])  # The double -f here forces A1[f][f] = -1.
		C1 = Flipper.kernel.Matrix(Flipper.kernel.matrix.tweak_vector([0] * self.zeta, [a, c], [b, d]), self.zeta)
		
		A2 = Flipper.kernel.Id_Matrix(self.zeta)
		Flipper.kernel.matrix.tweak_vector(A2[edge_index], [b, d], [edge_index, edge_index])  # The double -f here forces A2[f][f] = -1.
		C2 = Flipper.kernel.Matrix(Flipper.kernel.matrix.tweak_vector([0] * self.zeta, [b, d], [a, c]), self.zeta)
		
		f = Flipper.kernel.PartialFunction(self, new_triangulation, A1, C1)
		g = Flipper.kernel.PartialFunction(self, new_triangulation, A2, C2)
		
		f_inv = Flipper.kernel.PartialFunction(new_triangulation, self, A1, C1)
		g_inv = Flipper.kernel.PartialFunction(new_triangulation, self, A2, C2)
		
		return Flipper.kernel.Encoding([f, g], [f_inv, g_inv])
