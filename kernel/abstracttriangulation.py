
''' A module for representing an abstract triangulation of a punctured surface.

Provides five classes: AbstractVertex, AbstractEdge, AbstractTriangle, AbstractCorner and AbstractTriangulation.
	An AbstractVertex is a singleton.
	An AbstractEdge is an ordered pair of AbstractVertices.
	An AbstractTriangle is an ordered triple of AbstractEdges
	An AbstractTriangulation is a collection of AbstractTriangles.

There is also a helper function: abstract_triangulation. '''

import flipper

def norm(value):
	''' A map taking an edges label to its index.
	
	That is, x and ~x should map to the same thing. '''
	
	return max(value, ~value)

class AbstractVertex(object):
	''' This represents a vertex, labelled with an integer. '''
	def __init__(self, label):
		assert(isinstance(label, flipper.IntegerType))
		self.label = label
	
	def __repr__(self):
		return str(self.label)

class AbstractEdge(object):
	''' This represents an oriented edge, labelled with an integer.
	
	It is specified by the vertices that it connects from / to.
	Its inverse edge is created automatically and is labelled with ~its label. '''
	def __init__(self, source_vertex, target_vertex, label, reversed_edge=None):
		assert(isinstance(source_vertex, AbstractVertex))
		assert(isinstance(target_vertex, AbstractVertex))
		assert(isinstance(label, flipper.IntegerType))
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
		''' Return if this edge is the positively oriented one. '''
		
		return self.label == self.index
	
	def reverse(self):
		''' Return this edge but with reversed orientation. '''
		
		return self.reversed_edge

class AbstractTriangle(object):
	''' This represents a triangle.
	
	It is specified by a list of three edges, ordered anticlockwise. '''
	def __init__(self, edges):
		assert(isinstance(edges, (list, tuple)))
		assert(all(isinstance(edge, AbstractEdge) for edge in edges))
		assert(len(edges) == 3)
		
		# Edges are ordered anti-clockwise.
		self.edges = edges
		self.labels = [edge.label for edge in self]
		self.indices = [edge.index for edge in self]
		self.vertices = [self.edges[1].target_vertex, self.edges[2].target_vertex, self.edges[0].target_vertex]
	
	def __repr__(self):
		return str(tuple(self.edges))
	
	# Note that this is NOT the same convention as used in pieces.
	# There iterating and index accesses return vertices.
	def __iter__(self):
		return iter(self.edges)
	
	def __getitem__(self, index):
		return self.edges[index]
	
	def __contains__(self, item):
		if isinstance(item, flipper.IntegerType):
			return item in self.labels
		elif isinstance(item, AbstractEdge):
			return item in self.edges
		elif isinstance(item, AbstractVertex):
			return item in self.vertices
		else:
			return NotImplemented

class AbstractCorner(object):
	''' This represents a corner of a triangulation
	
	It is a triangle along with a side number (the side opposite this corner). '''
	def __init__(self, triangle, side):
		assert(isinstance(triangle, AbstractTriangle))
		assert(isinstance(side, flipper.IntegerType))
		
		self.triangle = triangle
		self.side = side
		
		self.edges = self.triangle.edges[self.side:] + self.triangle.edges[:self.side]
		self.labels = self.triangle.labels[self.side:] + self.triangle.labels[:self.side]
		self.indices = self.triangle.indices[self.side:] + self.triangle.indices[:self.side]
		self.vertices = self.triangle.vertices[self.side:] + self.triangle.vertices[:self.side]
		
		self.label = self.labels[0]
		self.index = self.indices[0]
		self.vertex = self.vertices[0]
		self.edge = self.edges[0]
	
	def __repr__(self):
		return str((self.triangle, self.side))

# Remark: In other places in the code you will often see L(abstract_triangulation). This is the space
# of laminations on abstract_triangulation with the coordinate system induced by the triangulation.

class AbstractTriangulation(object):
	''' This represents a triangulation of a punctured surface.
	
	 It is specified by a list of AbstractTriangles. It builds its own
	 corners automatically. '''
	def __init__(self, triangles):
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
		
		def order_corner_class(corner_class):
			''' Return the given corner_class but reorderd so that corners occur anti-clockwise about the vertex. '''
			
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
		
		self.euler_characteristic = 0 - self.zeta + self.num_triangles  # 0 - E + F as we have no vertices.
		self.genus = (2 - self.euler_characteristic - self.num_vertices) // 2
		self.max_order = 6 - 4 * self.euler_characteristic  # The maximum order of a periodic mapping class.
	
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
		''' Return a new copy of this AbstractTriangulation.
		
		Note: This preserves both vertex and edge labels. '''
		
		new_vertices = dict((vertex, AbstractVertex(vertex.label)) for vertex in self.vertices)
		new_edges = dict((edge, AbstractEdge(new_vertices[edge.source_vertex], new_vertices[edge.target_vertex], edge.label)) for edge in self.oriented_edges)
		for edge in self.oriented_edges:
			new_edges[~edge] = ~new_edges[edge]
		new_triangles = [AbstractTriangle([new_edges[edge] for edge in triangle]) for triangle in self]
		return AbstractTriangulation(new_triangles)
	
	def vertices_of_edge(self, edge_index):
		''' Return the two vertices at the ends of the given edge. '''
		
		# Refactor out?
		return [self.edge_lookup[edge_index].source_vertex, self.edge_lookup[~edge_index].source_vertex]
	
	def triangles_of_edge(self, edge_index):
		''' Return the two triangles containing the given edge. '''
		
		# Refactor out?
		return [self.triangle_lookup[edge_index], self.triangle_lookup[~edge_index]]
	
	def corner_of_edge(self, edge_index):
		''' Return the corner opposite the given edge. '''
		
		# Refactor out?
		return self.corner_lookup[edge_index]
	
	def corner_class_of_vertex(self, vertex):
		''' Return the corner class containing the given vertex. '''
		
		# Refactor out?
		for cc in self.corner_classes:
			if cc[0].vertex == vertex:
				return cc
		raise ValueError('Given vertex does not correspond to a corner class.')
	
	def opposite_corner(self, corner):
		''' Return the corner opposite the given corner. '''
		
		return self.corner_of_edge(~(corner.label))
	
	def rotate_corner(self, corner):
		''' Return the corner obtained by rotating the given corner one click anti-clockwise. '''
		
		return self.corner_of_edge(corner.labels[1])
	
	def is_flippable(self, edge_index):
		''' Return if the given edge is flippable.
		
		An edge is flippable if and only if it lies in two distinct triangles. '''
		
		return self.triangle_lookup[edge_index] != self.triangle_lookup[~edge_index]
	
	def square_about_edge(self, edge_index):
		''' Return the four edges around the given edge.
		
		The chosen edge must be flippable. '''
		
		assert(self.is_flippable(edge_index))
		
		# #<----------#
		# |     a    ^^
		# |         / |
		# |  A     /  |
		# |       /   |
		# |b    e/   d|
		# |     /     |
		# |    /      |
		# |   /       |
		# |  /     B  |
		# | /         |
		# V/    c     |
		# #---------->#
		
		corner_A, corner_B = self.corner_of_edge(edge_index), self.corner_of_edge(~edge_index)
		return [corner_A.edges[1], corner_A.edges[2], corner_B.edges[1], corner_B.edges[2]]
	
	def flip_edge(self, edge_index):
		''' Return a new triangulation obtained by flipping the given edge.
		
		The chosen edge must be flippable. '''
		
		assert(self.is_flippable(edge_index))
		
		# Use the following for reference:
		# #<----------#     #-----------#
		# |     a    ^^     |\          |
		# |         / |     | \         |
		# |  A     /  |     |  \        |
		# |       /   |     |   \       |
		# |b    e/   d| --> |    \e'    |
		# |     /     |     |     \     |
		# |    /      |     |      \    |
		# |   /       |     |       \   |
		# |  /     B  |     |        \  |
		# | /         |     |         \ |
		# V/    c     |     |          V|
		# #---------->#     #-----------#
		
		a, b, c, d = self.square_about_edge(edge_index)
		new_edge = AbstractEdge(a.target_vertex, c.target_vertex, edge_index)
		
		triangle_A2 = AbstractTriangle([new_edge, d, a])
		triangle_B2 = AbstractTriangle([~new_edge, b, c])
		
		unchanged_triangles = [triangle for triangle in self if edge_index not in triangle.labels and ~edge_index not in triangle]
		return AbstractTriangulation(unchanged_triangles + [triangle_A2, triangle_B2])
	
	def tree_and_dual_tree(self):
		''' Return a maximal tree in the 1--skeleton of this triangulation and a
		maximal tree in 1--skeleton of the dual of this triangulation.
		
		These are given as lists of Booleans signaling if each edge is in the tree.
		No edge is used in both the tree and the dual tree. '''
		
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
				break  # If there are no more to add then our tree is maximal.
		
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
				break  # If there are no more to add then our dual tree is maximal.
		
		return tree, dual_tree
	
	def homology_basis(self):
		''' Return a basis for H_1 of the underlying punctured surface.
		
		Each element is given as a path in the dual 1--skeleton and each pair of
		paths is guaranteed to meet at most once. '''
		
		# Construct a maximal spanning tree in the 1--skeleton of the triangulation.
		# and a maximal spanning tree in the complement of the tree in the 1--skeleton of the dual triangulation.
		tree, dual_tree = self.tree_and_dual_tree()
		
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
				# each point to be self.num_triangles+1 which we know is larger than
				# any possible distance.
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
	
	def isometries_to(self, other_triangulation, respect_vertex_labels=True):
		''' Return a list of all isometries from this triangulation to other_triangulation. '''
		
		assert(isinstance(other_triangulation, AbstractTriangulation))
		
		# Isometries are determined by where a single triangle is sent.
		# We take a corner of smallest degree.
		source_cc = min(self.corner_classes, key=len)
		source_corner = source_cc[0]
		# And find all the places where it could be sent so there are as few as possible to check.
		target_corners = [corner for target_cc in other_triangulation.corner_classes for corner in target_cc if len(target_cc) == len(source_cc)]
		
		isometries = []
		for target_corner in target_corners:
			# We do a depth first search extending the corner map across the triangulation.
			corner_map = {source_corner: target_corner}
			# This is a stack of triangles that may still have consequences.
			to_process = [(source_corner, target_corner)]
			while to_process:
				from_corner, to_corner = to_process.pop()
				new_from_corner, new_to_corner = self.opposite_corner(from_corner), other_triangulation.opposite_corner(to_corner)
				if new_from_corner in corner_map:
					if new_to_corner != corner_map[new_from_corner]:
						break  # Map does not extend to a consistent isometry.
				else:
					corner_map[new_from_corner] = new_to_corner
					to_process.append((new_from_corner, new_to_corner))
				
				new_from_corner, new_to_corner = self.rotate_corner(from_corner), other_triangulation.rotate_corner(to_corner)
				if new_from_corner in corner_map:
					if new_to_corner != corner_map[new_from_corner]:
						break  # Map does not extend to a consistent isometry.
				else:
					corner_map[new_from_corner] = new_to_corner
					to_process.append((new_from_corner, new_to_corner))
			else:
				isometries.append(flipper.kernel.Isometry(self, other_triangulation, corner_map))
		
		if respect_vertex_labels: isometries = [isom for isom in isometries if all((vertex.label >= 0) == (isom.vertex_map[vertex].label >= 0) for vertex in self.vertices)]
		return isometries
	
	def self_isometries(self):
		''' Returns a list of isometries taking this triangulation to itself. '''
		
		return self.isometries_to(self)
	
	def is_isometric_to(self, other_triangulation):
		''' Return if there are any orientation preserving isometries from this triangulation to other_triangulation. '''
		
		assert(isinstance(other_triangulation, AbstractTriangulation))
		
		return len(self.isometries_to(other_triangulation)) > 0
	
	def find_isometry(self, other_triangulation, edge_from_label, edge_to_label):
		''' Return the isometry from this triangulation to other_triangulation that sends edge_from_label to
		to edge_to_label.
		
		Assumes that such an isometry exists and is unique. '''
		
		try:
			[isometry] = [isom for isom in self.isometries_to(other_triangulation) if isom.label_map[edge_from_label] == edge_to_label]
		except ValueError:
			raise flipper.AssumptionError('edge_from_label and edge_to_label do not determine a unique isometry.')
		else:
			return isometry
	
	# Laminations we can build on the triangulation.
	def lamination(self, vector, remove_peripheral=False):
		''' Return a new lamination on this surface assigning the specified weight to each edge. '''
		
		return flipper.kernel.Lamination(self, vector, remove_peripheral)
	
	def empty_lamination(self):
		''' Return an empty lamination on this surface. '''
		
		return self.lamination([0] * self.zeta)
	
	def regular_neighbourhood(self, edge_index):
		''' Return the lamination which is the boundary of a regular neighbourhood of the chosen edge. '''
		
		vector = [0] * self.zeta
		for vertex in set(self.vertices_of_edge(edge_index)):
			for corner in self.corner_class_of_vertex(vertex):
				vector[corner.indices[2]] += 1
		vector[norm(edge_index)] = 0
		return self.lamination(vector)
	
	def key_curves(self):
		''' Return a list of all boundaries of regular neighbourhoods of edges.
		
		These curves fill so if they are all fixed by a mapping class then it is
		the identity (or possibly the hyperelliptic if we are on S_{0, 4} or
		S_{1, 1}). '''
		
		return [self.regular_neighbourhood(edge_index) for edge_index in range(self.zeta)]
	
	def id_encoding(self):
		''' Return an encoding of the identity map on this triangulation. '''
		
		f = b = [flipper.kernel.PartialFunction(flipper.kernel.id_matrix(self.zeta))]
		return flipper.kernel.Encoding(self, self, [flipper.kernel.PLFunction(f, b)])
	
	def encode_flip(self, edge_index):
		''' Return an encoding of the effect of flipping the given edge.
		
		The given edge must be flippable. '''
		
		assert(self.is_flippable(edge_index))
		
		new_triangulation = self.flip_edge(edge_index)
		
		a, b, c, d = [edge.index for edge in self.square_about_edge(edge_index)]
		e = norm(edge_index)  # Give it a shorter name.
		A1 = flipper.kernel.id_matrix(self.zeta).tweak([(e, a), (e, c)], [(e, e), (e, e)])
		C1 = flipper.kernel.zero_matrix(self.zeta, 1).tweak([(0, a), (0, c)], [(0, b), (0, d)])
		
		A2 = flipper.kernel.id_matrix(self.zeta).tweak([(e, b), (e, d)], [(e, e), (e, e)])
		C2 = flipper.kernel.zero_matrix(self.zeta, 1).tweak([(0, b), (0, d)], [(0, a), (0, c)])
		
		f = flipper.kernel.PartialFunction(A1, C1)
		g = flipper.kernel.PartialFunction(A2, C2)
		
		f_inv = flipper.kernel.PartialFunction(A1, C1)
		g_inv = flipper.kernel.PartialFunction(A2, C2)
		
		return flipper.kernel.Encoding(self, new_triangulation, [flipper.kernel.PLFunction([f, g], [f_inv, g_inv])])
	
	def encode_flips(self, edge_indices):
		''' Return an encoding of the effect of flipping the given sequences of edges. '''
		
		h = self.id_encoding()
		for edge_index in edge_indices:
			h = h.target_triangulation.encode_flip(edge_index) * h
		return h
	
	def encode_flips_and_close(self, edge_indices, edge_from_label, edge_to_label):
		''' Return an encoding of the effect of flipping the given sequences of edges followed by the isometry taking edge_from_label to edge_to_label. '''
		
		E = self.encode_flips(edge_indices)
		return E.target_triangulation.find_isometry(self, edge_from_label, edge_to_label).encode() * E
	
	def encode_puncture_triangles(self, to_puncture):
		''' Return an encoding from this triangulation to one in which each triangle
		on the list to_puncture has been punctured, that is the triangulation obtained
		by applying 1-->3 Pachner moves to the given triangles. '''
		
		# We label real punctures 0, 1, ... and fake ones -1, -2, ... .
		
		old_zeta = self.zeta
		M = flipper.kernel.id_matrix(old_zeta) * 2
		
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
				
				X = flipper.kernel.zero_matrix(old_zeta, 3).tweak([(0, B), (0, C), (1, A), (1, C), (2, A), (2, B)], [(0, A), (1, B), (2, C)])
				M = M.join(X)
				
				zeta += 3
			else:
				triangles.append(triangle)
		
		T = flipper.kernel.AbstractTriangulation(triangles)
		E = flipper.kernel.Encoding(self, T, [flipper.kernel.PLFunction([flipper.kernel.PartialFunction(M)])])
		
		return E

def abstract_triangulation(all_labels):
	''' Return an AbstractTriangulation from a list of triples of edge labels.
	
	Let T be an ideal triangulaton of the punctured (oriented) surface S. Orient
	and edge e of T and assign an index i(e) in 0, ..., zeta-1. Now to each
	triangle t of T associate the triple (j(e_1), j(e_2), j(e_3)) where:
		- e_1, e_2, e_3 are the edges of t, ordered acording to the orientation of t, and
		- j(e) = {  i(e) if the orientation of e agrees with that of t, and
		         { ~i(e) otherwise.
		    Here ~x = -1 - x, the two's complement of x.
	
	We may describe T by the list [j(t) for t in T]. This function reconstructs
	T from such a list.
	
	all_labels must be a list of triples of integers and each of
	0, ..., zeta-1, ~0, ..., ~(zeta-1) must occur exactly once. '''
	
	assert(isinstance(all_labels, (list, tuple)))
	assert(all(isinstance(labels, (list, tuple)) for labels in all_labels))
	assert(all(len(labels) == 3 for labels in all_labels))
	
	zeta = len(all_labels) * 3 // 2
	
	# Check that each of 0, ..., zeta-1, ~0, ..., ~(zeta-1) occurs exactly once.
	flattened = [label for labels in all_labels for label in labels]
	for i in range(zeta):
		if i not in flattened:
			raise TypeError('Missing label %d' % i)
		if ~i not in flattened:
			raise TypeError('Missing label ~%d' % i)
	
	def finder(edge_label):
		''' Return the label and position of the given edge_label. '''
		
		for labels in all_labels:
			for i in range(3):
				if labels[i] == edge_label:
					return (labels, i)
		assert(False)
	
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
	
	def vertexer(edge_label):
		''' Return the vertex opposite the given edge label. '''
		
		for vertex, cls in zip(vertices, vertex_classes):
			if edge_label in cls:
				return vertex
	
	edges_map = dict((i, AbstractEdge(vertexer(i), vertexer(~i), i)) for i in range(zeta))
	for i in range(zeta):
		edges_map[~i] = ~edges_map[i]
	
	triangles = [AbstractTriangle([edges_map[label] for label in labels]) for labels in all_labels]
	
	return AbstractTriangulation(triangles)

