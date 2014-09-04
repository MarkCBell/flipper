
from itertools import product, combinations
try:
	from Queue import Queue
except ImportError: # Python 3
	from queue import Queue

import flipper

def norm(value):
	return max(value, ~value)

class AbstractVertex(object):
	def __init__(self, label):
		assert(isinstance(label, flipper.Integer_Type))
		self.label = label
	
	def __repr__(self):
		return str(self.label)

class AbstractEdge(object):
	''' Represents an oriented edge. '''
	def __init__(self, source_vertex, target_vertex, label, reversed_edge=None):
		assert(isinstance(source_vertex, AbstractVertex))
		assert(isinstance(target_vertex, AbstractVertex))
		assert(isinstance(label, flipper.Integer_Type))
		assert(reversed_edge is None or isinstance(reversed_edge, AbstractEdge))
		
		self.source_vertex = source_vertex
		self.target_vertex = target_vertex
		self.label = label
		self.index = norm(self.label)
		if reversed_edge is None: reversed_edge = AbstractEdge(self.target_vertex, self.source_vertex, ~self.label, self)
		self.reversed_edge = reversed_edge
	
	def __repr__(self):
		return ('' if self.is_positive() else '~') + str(self.index)
	
	def __invert__(self):
		return self.reverse()
	
	def is_positive(self):
		return self.label == self.index
	
	def reverse(self):
		return self.reversed_edge

class AbstractTriangle(object):
	''' This represents a triangle in a trianglulation of a punctured surface. '''
	def __init__(self, edges):
		''' A Triangle is specified by giving the labels on its edges, ordered anticlockwise. '''
		assert(isinstance(edges, (list, tuple)))
		assert(all(isinstance(edge, AbstractEdge) for edge in edges))
		assert(len(edges) == 3)
		
		# Edges are ordered anti-clockwise.
		self.edges = edges
		self.labels = [edge.label for edge in self]
		self.indices = [edge.index for edge in self]
		self.vertices = [self.edges[1].target_vertex, self.edges[2].target_vertex, self.edges[0].target_vertex]
	
	def __repr__(self):
		return str(tuple(self.edges))  # + '--' + str(list(self.vertices))
	
	# Note that this is NOT the same convention as used in pieces.
	# There iterating and index accesses return vertices.
	def __iter__(self):
		return iter(self.edges)
	
	def __getitem__(self, index):
		return self.edges[index]
	
	def __contains__(self, item):
		if isinstance(item, AbstractEdge):
			return item in self.edges
		elif isinstance(item, AbstractVertex):
			return item in self.vertices
		else:
			return NotImplemented

class AbstractCorner(object):
	''' A corner of a triangulation is a triangle along with a side number (the side opposite this corner). '''
	def __init__(self, triangle, side):
		assert(isinstance(triangle, AbstractTriangle))
		assert(isinstance(side, flipper.Integer_Type))
		
		self.triangle = triangle
		self.side = side
		
		self.edges = self.triangle.edges[self.side:] + self.triangle.edges[:self.side]
		self.labels = self.triangle.labels[self.side:] + self.triangle.labels[:self.side]
		self.indices = self.triangle.indices[self.side:] + self.triangle.indices[:self.side]
		self.vertices = self.triangle.vertices[self.side:] + self.triangle.vertices[:self.side]
		
		self.label = self.labels[0]
		self.index = self.indices[0]
		self.vertex = self.triangle.vertices[self.side]
		self.edge = self.edges[0]
	
	def __repr__(self):
		return str((self.triangle, self.side))


# Remark: In other places in the code you will often see L(abstract_triangulation). This is the space
# of laminations on abstract_triangulation with the coordinate system induced by the triangulation.

class AbstractTriangulation(object):
	''' This represents a triangulation of a puctured surface, it is a collection of AbstractTriangles whose
	edge labels satisfy certain criteria. '''
	def __init__(self, triangles):
		''' An abstract triangulation is a collection of abstract triangles and is given by a list of triples
		each of which specifies a triangle.
		We label one side of an edge with x and its other side with ~x := -x-1.
		!?! OUT OF DATE. '''
		assert(isinstance(triangles, (list, tuple)))
		assert(all(isinstance(triangle, AbstractTriangle) for triangle in triangles))
		
		self.triangles = triangles
		
		self.edges = [edge for triangle in self for edge in triangle.edges]
		self.oriented_edges = [edge for edge in self.edges if edge.is_positive()]
		self.vertices = list(set(vertex for triangle in self for vertex in triangle.vertices))
		self.corners = [AbstractCorner(triangle, index) for triangle in self for index in range(3)]
		
		self.num_triangles = len(self.triangles)
		self.zeta = len(self.oriented_edges)
		assert(self.zeta == self.num_triangles * 3 // 2)
		self.num_vertices = len(self.vertices)
		assert(all(any(edge.label == i for edge in self.edges) for i in range(self.zeta)))
		assert(all(any(edge.label == ~i for edge in self.edges) for i in range(self.zeta)))
		
		self.triangle_lookup = dict((edge.label, triangle) for triangle in self for edge in triangle.edges)
		self.edge_lookup = dict((edge.label, edge) for edge in self.edges)
		self.corner_lookup = dict((corner.label, corner) for corner in self.corners)
		self.vertex_lookup = dict((corner.label, corner.vertex) for corner in self.corners)
		assert(all(i in self.edge_lookup and ~i in self.edge_lookup for i in range(self.zeta)))
		
		# Ensure that each corner class is ordered ANTI-CLOCKWISE about the vertex.
		# This orders the corner class anti-clockwise about the vertex.
		def order_corner_class(corner_class):
			corner_class = list(corner_class)
			ordered_class = [corner_class.pop()]
			while corner_class:
				for corner in corner_class:
					if corner.edges[2] == ~ordered_class[-1].edges[1]:
						ordered_class.append(corner)
						corner_class.remove(corner)
						break
				else:
					raise ValueError('Corners do not close up about vertex.')
			
			if ordered_class[0].edges[2] != ~ordered_class[-1].edges[1]:
				raise ValueError('Corners do not close up about vertex.')
			
			return ordered_class
		self.corner_classes = [order_corner_class([corner for corner in self.corners if corner.vertex == vertex]) for vertex in self.vertices]
		
		self.Euler_characteristic = 0 - self.zeta + self.num_triangles  # 0 - E + F as we have no vertices.
		self.max_order = 6 - 4 * self.Euler_characteristic  # The maximum order of a periodic mapping class.
		self._face_matrix = None
		self._marking_matrices = None
	
	def __repr__(self):
		return str(list(self))
	def __iter__(self):
		return iter(self.triangles)
	def __getitem__(self, index):
		return self.triangles[index]
	def __contains__(self, item):
		if isinstance(item, AbstractVertex):
			return item in self.vertices
		elif isinstance(item, AbstractEdge):
			return item in self.edges
		elif isinstance(item, AbstractTriangle):
			return item in self.triangles
		elif isinstance(item, AbstractCorner):
			return item in self.corners
		else:
			return NotImplemented
	def copy(self):
		nv = dict((vertex, AbstractVertex(vertex.label)) for vertex in self.vertices)
		ne = dict((edge, AbstractEdge(nv[edge.source_vertex], nv[edge.target_vertex], edge.label)) for edge in self.oriented_edges)
		for edge in self.oriented_edges:
			ne[~edge] = ~ne[edge]
		new_triangles = [AbstractTriangle([ne[edge] for edge in triangle]) for triangle in self]
		return AbstractTriangulation(new_triangles)
	
	def face_matrix(self):
		assert(False)
		if self._face_matrix is None:
			X = [[(3*i + j, self.triangles[i][j+k]) for i in range(self.num_triangles) for j in range(3)] for k in range(3)]
			self._face_matrix = flipper.kernel.Zero_Matrix(self.zeta, 3*self.num_triangles).tweak(X[0] + X[1], X[2])
		return self._face_matrix
	
	def marking_matrices(self):
		assert(False)
		if self._marking_matrices is None:
			corner_choices = [P for P in product(*self.vertices) if all(t1 != t2 for ((t1, s1), (t2, s2)) in combinations(P, r=2))]
			X = dict((P, [[(i, triangle[side+j]) for i, (triangle, side) in enumerate(P)] for j in range(3)]) for P in corner_choices)
			self._marking_matrices = [flipper.kernel.Zero_Matrix(self.zeta, len(P)).tweak(X[P][0], X[P][1]+X[P][2]) for P in corner_choices]
		return self._marking_matrices
	
	def vertices_of_edge(self, edge_index):
		# Returns the two vertices at the ends of this edge.
		# Refactor out?
		return [self.edge_lookup[edge_index].source_vertex, self.edge_lookup[~edge_index].source_vertex]
	
	def triangles_of_edge(self, edge_index):
		# Returns the two triangles containing this edge.
		# Refactor out?
		return [self.triangle_lookup[edge_index], self.triangle_lookup[~edge_index]]
	
	def corner_of_edge(self, edge_index):
		# Return the corner opposite this edge.
		# Refactor out?
		return self.corner_lookup[edge_index]
	
	def corner_class_of_vertex(self, vertex):
		# Returns the corner class containing this vertex.
		# Refactor out?
		for cc in self.corner_classes:
			if cc[0].vertex == vertex:
				return cc
		raise ValueError('Given vertex does not correspond to a corner class.')
	
	def opposite_corner(self, corner):
		# Returns the corner opposite this one.
		return self.corner_of_edge(~(corner.label))
	
	def rotate_corner(self, corner):
		# Returns the corner obtained by rotating this one one click anti-clockwise.
		return self.corner_of_edge(corner.labels[1])
	
	def is_flippable(self, edge_index):
		# An edge is flippable iff it lies in two distinct triangles.
		return self.triangle_lookup[edge_index] != self.triangle_lookup[~edge_index]
	
	def flip_edge(self, edge_index):
		# Returns a new triangulation obtained by flipping the edge of index edge.
		assert(self.is_flippable(edge_index))
		
		# #-----------#     #-----------#
		# |     a    /|     |\          |
		# |         / |     | \         |
		# |  A     /  |     |  \   A2   |
		# |       /   |     |   \       |
		# |b    e/   d| --> |    \e'    |
		# |     /     |     |     \     |
		# |    /      |     |      \    |
		# |   /       |     |       \   |
		# |  /     B  |     |  B2    \  |
		# | /         |     |         \ |
		# |/    c     |     |          \|
		# #-----------#     #-----------#
		
		A, B = self.corner_lookup[edge_index], self.corner_lookup[~edge_index]
		new_edge = AbstractEdge(A.vertex, B.vertex, edge_index)
		
		a, b, c, d = self.find_edges_of_square_about_edge(edge_index)
		A2 = AbstractTriangle([new_edge, d, a])
		B2 = AbstractTriangle([~new_edge, b, c])
		
		unchanged_triangles = [triangle for triangle in self if triangle != A.triangle and triangle != B.triangle]
		return AbstractTriangulation(unchanged_triangles + [A2, B2])
	
	def find_edges_of_square_about_edge(self, edge_index):
		assert(self.is_flippable(edge_index))
		
		# #-----------#
		# |     a    /|
		# |         / |
		# |  A     /  |
		# |       /   |
		# |b    e/    |
		# |     /     |
		# |    /      |
		# |   /       |
		# |  /     B  |
		# | /         |
		# |/    c     |
		# #-----------#
		
		A, B = self.corner_lookup[edge_index], self.corner_lookup[~edge_index]
		return [A.edges[1], A.edges[2], B.edges[1], B.edges[2]]
	
	def find_labels_of_square_about_edge(self, edge_index):
		# Returns the inside labels of the 4 edges surrounding this edge (ordered anti-clockwise).
		assert(self.is_flippable(edge_index))
		
		return [edge.label for edge in self.find_edges_of_square_about_edge(edge_index)]
	
	def find_indicies_of_square_about_edge(self, edge_index):
		return [norm(x) for x in self.find_labels_of_square_about_edge(edge_index)]
	
	def homology_basis(self):
		''' Returns a basis for H_1 of the underlying punctured surface. Each element is given as a path
		in the dual 1--skeleton. Each pair of paths is guaranteed to meet at most once. '''
		
		# Construct a maximal spanning tree in the 1--skeleton of the triangulation.
		tree = [False] * self.zeta
		vertices_used = dict((vertex, False) for vertex in self.vertices)
		vertices_used[self.vertices[0]] = True
		while True:
			for edge_index in range(self.zeta):
				if not tree[edge_index]:
					a, b = self.vertices_of_edge(edge_index)
					if vertices_used[a] != vertices_used[b]:
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
				if not tree[edge_index] and not dual_tree[edge_index]:
					a, b = self.triangles_of_edge(edge_index)
					if faces_used[a] != faces_used[b]:
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
				generator = [~edge_index]
				source, target = self.triangles_of_edge(edge_index)
				
				# Find a path in dual_tree from source to target. This is a really
				# inefficient way to do this. We initially define the distance to
				# each point to be self.num_triangles+1 which we know is larger than any possible
				# distance.
				distance = dict((triangle, self.num_triangles+1) for triangle in self.triangles)
				distance[source] = 0
				while distance[target] == self.num_triangles+1:
					for edge in dual_tree_indices:  # Only allowed to move in the tree.
						a, b = self.triangles_of_edge(edge)
						distance[a] = min(distance[b]+1, distance[a])
						distance[b] = min(distance[a]+1, distance[b])
				
				# Now find a way from the target back to the source by following the distance
				current = target
				while current != source:
					for edge in dual_tree_indices:
						a, b = self.triangles_of_edge(edge)
						if b == current and distance[a] == distance[b]-1:
							generator.append(edge)
							current = a
							break
						elif a == current and distance[b] == distance[a]-1:
							generator.append(~edge)
							current = b
							break
				
				# We've now made a generating loop.
				homology_generators.append(generator)
		
		return homology_generators
	
	def all_isometries(self, other, respect_vertex_labels=True):
		''' Returns a list of all orientation preserving isometries from self to other_triangulation. '''
		assert(isinstance(other, AbstractTriangulation))
		
		source_cc = min(self.corner_classes, key=len)
		target_corners = [corner for target_cc in other.corner_classes for corner in target_cc if len(target_cc) == len(source_cc)]
		
		source_corner = source_cc[0]
		isometries = []
		for target_corner in target_corners:
			corner_map = {}
			to_process = Queue()
			to_process.put((source_corner, target_corner))
			while not to_process.empty():
				from_corner, to_corner = to_process.get()
				new_from_corner, new_to_corner = self.opposite_corner(from_corner), other.opposite_corner(to_corner)
				if new_from_corner in corner_map:
					if new_to_corner != corner_map[new_from_corner]:
						break
				else:
					corner_map[new_from_corner] = new_to_corner
					to_process.put((new_from_corner, new_to_corner))
				
				new_from_corner, new_to_corner = self.rotate_corner(from_corner), other.rotate_corner(to_corner)
				if new_from_corner in corner_map:
					if new_to_corner != corner_map[new_from_corner]:
						break
				else:
					corner_map[new_from_corner] = new_to_corner
					to_process.put((new_from_corner, new_to_corner))
			else:
				isometries.append(flipper.kernel.Isometry(self, other, corner_map))
		
		if respect_vertex_labels: isometries = [isom for isom in isometries if all((vertex.label >= 0) == (isom.vertex_map[vertex].label >= 0) for vertex in self.vertices)]
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
		for vertex in set(self.vertices_of_edge(edge_index)):
			for corner in self.corner_class_of_vertex(vertex):
				vector[corner.indices[2]] += 1
		vector[norm(edge_index)] = 0
		return self.lamination(vector)
	
	def key_curves(self):
		# These curves fill so if they are all fixed by a mapping class then it is the identity
		# (or possibly the hyperelliptic if we are on S_{0, 4} or S_{1, 1}).
		return [self.regular_neighbourhood(edge_index) for edge_index in range(self.zeta)]
	
	def id_encoding(self):
		f = b = [flipper.kernel.PartialFunction(flipper.kernel.Id_Matrix(self.zeta))]
		return flipper.kernel.Encoding(self, self, [flipper.kernel.PLFunction(f, b)])
	
	def encode_flip(self, edge_index):
		assert(self.is_flippable(edge_index))
		
		new_triangulation = self.flip_edge(edge_index)
		
		a, b, c, d = self.find_indicies_of_square_about_edge(edge_index)
		e = norm(edge_index)  # Give it a shorter name.
		A1 = flipper.kernel.Id_Matrix(self.zeta).tweak([(e, a), (e, c)], [(e, e), (e, e)])
		C1 = flipper.kernel.Zero_Matrix(self.zeta, 1).tweak([(0, a), (0, c)], [(0, b), (0, d)])
		
		A2 = flipper.kernel.Id_Matrix(self.zeta).tweak([(e, b), (e, d)], [(e, e), (e, e)])
		C2 = flipper.kernel.Zero_Matrix(self.zeta, 1).tweak([(0, b), (0, d)], [(0, a), (0, c)])
		
		f = flipper.kernel.PartialFunction(A1, C1)
		g = flipper.kernel.PartialFunction(A2, C2)
		
		f_inv = flipper.kernel.PartialFunction(A1, C1)
		g_inv = flipper.kernel.PartialFunction(A2, C2)
		
		return flipper.kernel.Encoding(self, new_triangulation, [flipper.kernel.PLFunction([f, g], [f_inv, g_inv])])
	
	def encode_puncture_triangles(self, to_puncture):
		''' Returns an encoding from this triangulation to one in which each triangle
		on the list to_puncture has been punctured, that is the triangulation obtained
		by applying 1-->3 Pachner moves to the given triangles. '''
		# We label real punctures 0, 1, ... and fake ones -1, -2, ... .
		
		old_zeta = self.zeta
		M = flipper.kernel.Id_Matrix(old_zeta) * 2
		
		zeta = self.zeta
		triangles = []
		num_new_vertices = 0
		for triangle in self:
			A, B, C = triangle.indices
			if triangle in to_puncture:
				x, y, z = triangle.vertices
				num_new_vertices += 1
				w = AbstractVertex(-num_new_vertices)
				p, q, r = triangle.edges
				s, t, u = [AbstractEdge(w, x, zeta), AbstractEdge(w, y, zeta+1), AbstractEdge(w, z, zeta+2)]
				triangles.append(AbstractTriangle([p, ~u, t]))
				triangles.append(AbstractTriangle([q, ~s, u]))
				triangles.append(AbstractTriangle([r, ~t, s]))
				
				X = flipper.kernel.Zero_Matrix(old_zeta, 3).tweak([(0, B), (0, C), (1, A), (1, C), (2, A), (2, B)], [(0, A), (1, B), (2, C)])
				M = M.join(X)
				
				zeta += 3
			else:
				triangles.append(triangle)
		
		T = flipper.kernel.AbstractTriangulation(triangles)
		return flipper.kernel.Encoding(self, T, [flipper.kernel.PLFunction([flipper.kernel.PartialFunction(M)])])

def abstract_triangulation(all_labels):
	# We should assert a load of stuff here first. !?!
	zeta = len(all_labels) * 3 // 2
	
	def finder(value):
		for labels in all_labels:
			for i in range(3):
				if labels[i] == value:
					return (labels, i)
	
	unused = [i for i in range(zeta)] + [~i for i in range(zeta)]
	vertex_classes = []
	while unused:
		new_vertex = [unused.pop()]
		while True:
			label, i = finder(new_vertex[-1])
			neighbour = ~label[(i+2) % 3]
			if neighbour in unused:
				new_vertex.append(neighbour)
				unused.remove(neighbour)
			else:
				break
		
		vertex_classes.append(new_vertex)
	
	num_vertices = len(vertex_classes)
	vertices = [AbstractVertex(i) for i in range(num_vertices)]
	
	def vertexer(value):
		for vertex, cls in zip(vertices, vertex_classes):
			if value in cls:
				return vertex
	
	edges_map = dict((i, AbstractEdge(vertexer(i), vertexer(~i), i)) for i in range(zeta))
	for i in range(zeta):
		edges_map[~i] = ~edges_map[i]
	
	triangles = [AbstractTriangle([edges_map[label] for label in labels]) for labels in all_labels]
	
	return AbstractTriangulation(triangles)

