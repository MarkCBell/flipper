
from itertools import product, combinations
try:
	from Queue import Queue
except ImportError: # Python 3
	from queue import Queue

import flipper

def norm(value):
	return max(value, ~value)

class AbstractTriangle(object):
	''' This represents a triangle in a trianglulation of a punctured surface. '''
	def __init__(self, labels, corner_labels=None):
		''' A Triangle is specified by giving the labels on its edges, ordered anticlockwise. '''
		# Edges are ordered anti-clockwise.
		self.labels = list(labels)
		self.indices = [norm(x) for x in self.labels]
		self.corner_labels = list(corner_labels) if corner_labels is not None else [None, None, None]
	
	def __repr__(self):
		return str((self.labels, self.corner_labels))
	
	# Note that this is NOT the same convention as used in pieces.
	# There iterating and index accesses return vertices.
	def __iter__(self):
		return iter(self.indices)
	
	def __getitem__(self, index):
		return self.indices[index % 3]

class Corner(object):
	def __init__(self, triangulation, triangle, side):
		self.triangulation = triangulation
		self.triangle = triangle
		self.side = side
		self.label = self.triangle.labels[self.side]
		self.index = self.triangle[self.side]  # Shorthand for triangle.indices[side].
		self.corner_label = self.triangle.corner_labels[self.side]
	def rotate(self, turn):
		return [corner for corner in self.triangulation.corners if corner.triangle == self.triangle and corner.side == (self.side + turn) % 3][0]
	def opposite(self):
		return [corner for corner in self.triangulation.corners if corner.label == ~self.label][0]
	def adjacent(self):
		# Returns the corner 1 click anti-clockwise around this vertex.
		return self.rotate(1).opposite().rotate(-1)

# Remark: In other places in the code you will often see L(abstract_triangulation). This is the space
# of laminations on abstract_triangulation with the coordinate system induced by the triangulation.

class AbstractTriangulation(object):
	''' This represents a triangulation of a puctured surface, it is a collection of AbstractTriangles whose
	edge labels satisfy certain criteria. '''
	def __init__(self, all_labels, all_corner_labels=None):
		''' An abstract triangulation is a collection of abstract triangles and is given by a list of triples 
		each of which specifies a triangle. '''
		# We label one side of an edge with x and its other side with ~x := -x-1.
		
		self.num_triangles = len(all_labels)
		self.zeta = self.num_triangles * 3 // 2
		
		# We should assert a load of stuff here first. !?!
		assert(all(len(labels) == 3 for labels in all_labels))
		assert(len(all_labels) % 2 == 0)  # There must be an even number of triangles.
		flat = [x for labels in all_labels for x in labels]
		assert(all(x in flat and ~x in flat for x in range(self.zeta)))  # Every number and its ~ must appear.
		
		if all_corner_labels is None: all_corner_labels = [None] * self.num_triangles
		self.triangles = [AbstractTriangle(labels, corner_labels) for labels, corner_labels in zip(all_labels, all_corner_labels)]
		self.corners = [Corner(self, triangle, side) for triangle in self for side in range(3)]
		self.edge_contained_in = dict((corner.label, corner) for corner in self.corners)
		
		# Now build all the equivalence classes of corners. These are each guaranteed to be ordered anti-clockwise about the vertex.
		used = dict(zip(self.corners, [False] * len(self.corners)))
		self.vertices = []
		while not all(used.values()):
			new_vertex = []
			unused_corners = [corner for corner in self.corners if not used[corner]]
			next_corner = unused_corners[0]
			while not used[next_corner]:
				new_vertex.append(next_corner)
				used[next_corner] = True
				next_corner = next_corner.adjacent()
			
			self.vertices.append(tuple(new_vertex))
		
		self.num_vertices = len(self.vertices)
		self.Euler_characteristic = 0 - self.zeta + self.num_triangles  # 0 - E + F as we have no vertices.
		self.max_order = 6 - 4 * self.Euler_characteristic  # The maximum order of a periodic mapping class.
		self._face_matrix = None
		self._marking_matrices = None
	
	def copy(self):
		return AbstractTriangulation([list(triangle.indices) for triangle in self], [list(triangle.corner_labels) for triangle in self])
	
	def __repr__(self):
		return '\n'.join(str(triangle) for triangle in self)
	
	def __iter__(self):
		return iter(self.triangles)
	
	def __getitem__(self, index):
		return self.triangles[index]
	
	def face_matrix(self):
		if self._face_matrix is None:
			X = [[(3*i + j, self.triangles[i][j+k]) for i in range(self.num_triangles) for j in range(3)] for k in range(3)]
			self._face_matrix = flipper.kernel.Zero_Matrix(self.zeta, 3*self.num_triangles).tweak(X[0] + X[1], X[2])
		return self._face_matrix
	
	def marking_matrices(self):
		if self._marking_matrices is None:
			corner_choices = [P for P in product(*self.vertices) if all(t1 != t2 for ((t1, s1), (t2, s2)) in combinations(P, r=2))]
			X = dict((P, [[(i, triangle[side+j]) for i, (triangle, side) in enumerate(P)] for j in range(3)]) for P in corner_choices)
			self._marking_matrices = [flipper.kernel.Zero_Matrix(self.zeta, len(P)).tweak(X[P][0], X[P][1]+X[P][2]) for P in corner_choices]
		return self._marking_matrices
	
	def vertex_orders(self):
		return [len(vertex) for vertex in self.vertices]
	
	def find_vertex(self, corner):
		for vertex in self.vertices:
			if corner in vertex:
				return vertex
		print(corner.label)
		assert(False)
	
	def find_edge_vertices(self, edge_index):
		# Returns the two corner classes contain the ends of the specified edge.
		corner = self.find_edge(edge_index)
		return [self.find_vertex(corner.rotate(1)), self.find_vertex(corner.rotate(-1))]
	
	def find_edge(self, edge_index):
		# Return the corner with this edge_index.
		return self.edge_contained_in[edge_index]
	
	def is_flippable(self, edge_index):
		# An edge is flippable iff it lies in two distinct triangles.
		return self.find_edge(edge_index).triangle != self.find_edge(~edge_index).triangle
	
	def flip_edge(self, edge_index):
		# Returns a new triangulation obtained by flipping the edge of index edge_index.
		assert(self.is_flippable(edge_index))
		
		e = edge_index
		a, b, c, d = self.find_indicies_of_square_about_edge(e)
		r, s, t, u, v, w = self.find_corner_labels_of_square_about_edge(e)
		
		dont_copy = [self.find_edge(e).triangle, self.find_edge(~e).triangle]
		labels = [list(triangle.labels) for triangle in self if triangle not in dont_copy] + [[e, d, a], [~e, b, c]]
		corner_labels = [list(triangle.corner_labels) for triangle in self if edge_index not in triangle] + [[r, s, v], [t, v, s]]
		
		return AbstractTriangulation(labels, corner_labels)
	
	def find_indicies_of_square_about_edge(self, edge_index):
		# Returns the indices of the 4 edges surrounding this edge (ordered anti-clockwise).
		#       a
		# #-----------#
		# |          /|
		# |         / |
		# |        /  |
		# |       /   |
		#b|     E/    |d
		# |     /     |
		# |    /      |
		# |   /       |
		# |  /        |
		# | /         |
		# |/          |
		# #-----------#
		#       c
		assert(self.is_flippable(edge_index))
		
		A, B = self.find_edge(edge_index), self.find_edge(~edge_index)
		return [A.rotate(1).label, A.rotate(2).label, B.rotate(1).label, B.rotate(2).label]
	
	def find_corner_labels_of_square_about_edge(self, edge_index):
		# Returns the 6 corner labels surrounding this edge (ordered anti-clockwise).
		# #-----------#
		# |s        r/|
		# |         /w|
		# |        /  |
		# |       /   |
		# |     E/    |
		# |     /     |
		# |    /      |
		# |   /       |
		# |  /        |
		# |t/         |
		# |/u        v|
		# #-----------#
		assert(self.is_flippable(edge_index))
		
		A, B = self.find_edge(edge_index), self.find_edge(~edge_index)
		return [A.rotate(-1).corner_label, A.rotate(0).corner_label, A.rotate(1).corner_label,
			B.rotate(-1).corner_label, B.rotate(0).corner_label, B.rotate(1).corner_label]
	
	def homology_basis(self):
		# Returns a basis for H_1 of the underlying punctured surface. Each element is given as a path
		# in the dual 1--skeleton. Each pair of paths is guaranteed to meet at most once. 
		
		# Construct a maximal spanning tree in the 1--skeleton of the triangulation.
		tree = [False] * self.zeta
		vertices_used = dict((vertex, False) for vertex in self.vertices)
		vertices_used[self.vertices[0]] = True
		while True:
			for edge_index in range(self.zeta):
				a, b = self.find_edge_vertices(edge_index)
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
	
	def extend_isometry(self, other_triangulation, source_edge, target_edge):
		''' Returns the isometry from this triangulation to other which sends
		source_edge to target_edge or None if no such edge exists. '''
		edge_map = {}
		to_process = Queue()
		to_process.put((source_edge, target_edge))
		while not to_process.empty():
			from_edge, to_edge = to_process.get()
			consequences = []
			consequences.append((from_edge, to_edge))
			consequences.append((~from_edge, ~to_edge))
			from_corner = self.find_edge(from_edge)
			to_corner = other_triangulation.find_edge(to_edge)
			
			consequences.append((from_corner.rotate(1).label, to_corner.rotate(1).label))
			consequences.append((from_corner.rotate(2).label, to_corner.rotate(2).label))
			
			for from_edge, to_edge in consequences:
				if from_edge in edge_map:
					if to_edge != edge_map[from_edge]:
						return None  # Map doesn't specify an isometry.
				else:
					edge_map[from_edge] = to_edge
					to_process.put((~from_edge, ~to_edge))
		
		return flipper.kernel.Isometry(self, other_triangulation, edge_map)
	
	def all_isometries(self, other_triangulation):
		# Returns a list of all orientation preserving isometries from self to other_triangle.
		if self.zeta != other_triangulation.zeta: return []
		
		source_vertex = min(self.vertices, key=len)
		min_degree = len(source_vertex)
		possible_targets = [corner.label for vertex in other_triangulation.vertices for corner in vertex if len(vertex) == min_degree]
		
		source_edge = source_vertex[0].label
		isometries = [self.extend_isometry(other_triangulation, source_edge, target_edge) for target_edge in possible_targets]
		isometries = [isom for isom in isometries if isom is not None]  # Discard any bad ones that we tried to create.
		
		return isometries
	
	def is_isometric_to(self, other):
		return isinstance(other, AbstractTriangulation) and len(self.all_isometries(other)) > 0
	
	# Laminations we can build on the triangulation.
	def lamination(self, vector, remove_peripheral=False):
		return flipper.kernel.Lamination(self, vector, remove_peripheral)
	
	def empty_lamination(self):
		return self.lamination([0] * self.zeta)
	
	def regular_neighbourhood(self, edge_index):
		vector = [0] * self.zeta
		vertices = set(self.find_edge_vertices(edge_index))
		for vertex in vertices:
			for corner in vertex:
				if corner.rotate(2).label not in [edge_index, ~edge_index]:
					vector[corner.rotate(2).edge] += 1
		return self.lamination(vector)
	
	def key_curves(self):
		# These curves fill so if they are all fixed by a mapping class then it is the identity
		# (or possibly the hyperelliptic if we are on S_{0, 4} or S_{1, 1}).
		return [self.regular_neighbourhood(edge_index) for edge_index in range(self.zeta)]
	
	def Id_Encoding(self):
		f = b = [flipper.kernel.PartialFunction(self, self, flipper.kernel.Id_Matrix(self.zeta))]
		return flipper.kernel.Encoding([flipper.kernel.PLFunction(f, b)])
	
	def encode_flip(self, edge_index):
		assert(self.is_flippable(edge_index))
		
		new_triangulation = self.flip_edge(edge_index)
		
		a, b, c, d = [norm(x) for x in self.find_indicies_of_square_about_edge(edge_index)]
		e = norm(edge_index)  # Give it a shorter name.
		A1 = flipper.kernel.Id_Matrix(self.zeta).tweak([(e, a), (e, c)], [(e, e), (e, e)])
		C1 = flipper.kernel.Zero_Matrix(self.zeta, 1).tweak([(0, a), (0, c)], [(0, b), (0, d)])
		
		A2 = flipper.kernel.Id_Matrix(self.zeta).tweak([(e, b), (e, d)], [(e, e), (e, e)])
		C2 = flipper.kernel.Zero_Matrix(self.zeta, 1).tweak([(0, b), (0, d)], [(0, a), (0, c)])
		
		f = flipper.kernel.PartialFunction(self, new_triangulation, A1, C1)
		g = flipper.kernel.PartialFunction(self, new_triangulation, A2, C2)
		
		f_inv = flipper.kernel.PartialFunction(new_triangulation, self, A1, C1)
		g_inv = flipper.kernel.PartialFunction(new_triangulation, self, A2, C2)
		
		return flipper.kernel.Encoding([flipper.kernel.PLFunction([f, g], [f_inv, g_inv])])
	
	def encode_puncture_triangles(self, to_puncture):
		''' Returns an encoding from this triangulation to one in which each triangle
		on the list to_puncture has been punctured, that is the triangulation obtained
		by applying 1-->3 Pachner moves to the given triangles. '''
		# We label real punctures with a 0 and number fake one by intergers > 0.
		
		old_zeta = self.zeta
		M = flipper.kernel.Id_Matrix(old_zeta) * 2
		
		new_labels = []
		new_corner_labels = []
		zeta = self.zeta
		num_fake = 0
		for triangle in self:
			a, b, c = triangle.labels
			A, B, C = triangle.indices
			if triangle in to_puncture:
				num_fake += 1
				x, y, z = zeta, zeta+1, zeta+2
				new_labels.append([a, z, ~y])
				new_labels.append([b, x, ~z])
				new_labels.append([c, y, ~x])
				new_corner_labels.append([num_fake, 0, 0])
				new_corner_labels.append([num_fake, 0, 0])
				new_corner_labels.append([num_fake, 0, 0])
				
				X = flipper.kernel.Zero_Matrix(old_zeta, 3).tweak([(0, B), (0, C), (1, A), (1, C), (2, A), (2, B)], [(0, A), (1, B), (2, C)])
				M = M.join(X)
				
				zeta = zeta + 3
			else:
				new_labels.append([a, b, c])
				new_corner_labels.append([0, 0, 0])
		
		T = flipper.AbstractTriangulation(new_labels, new_corner_labels)
		return flipper.kernel.PLFunction([flipper.kernel.PartialFunction(self, T, M)])

