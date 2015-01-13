
''' A module for representing a triangulation of a punctured surface.

Provides five classes: Vertex, Edge, Triangle, Corner and Triangulation.
	An Vertex is a singleton.
	An Edge is an ordered pair of Vertices.
	An Triangle is an ordered triple of Edges.
	A Corner is a Triangle with a chosen side.
	An Triangulation is a collection of Triangles.

There is also a helper function: create_triangulation. '''

from random import choice

import flipper

def norm(value):
	''' A map taking an edges label to its index.
	
	That is, x and ~x should map to the same thing. '''
	
	return max(value, ~value)

class Vertex(object):
	''' This represents a vertex, labelled with an integer. '''
	def __init__(self, label):
		assert(isinstance(label, flipper.IntegerType))
		self.label = label
	
	def __str__(self):
		return str(self.label)

class Edge(object):
	''' This represents an oriented edge, labelled with an integer.
	
	It is specified by the vertices that it connects from / to.
	Its inverse edge is created automatically and is labelled with ~its label. '''
	def __init__(self, source_vertex, target_vertex, label, reversed_edge=None):
		assert(isinstance(source_vertex, Vertex))
		assert(isinstance(target_vertex, Vertex))
		assert(isinstance(label, flipper.IntegerType))
		assert(reversed_edge is None or isinstance(reversed_edge, Edge))
		
		self.source_vertex = source_vertex
		self.target_vertex = target_vertex
		self.label = label
		self.index = norm(self.label)
		if reversed_edge is None: reversed_edge = Edge(self.target_vertex, self.source_vertex, ~self.label, self)
		self.reversed_edge = reversed_edge
	
	def __str__(self):
		return ('' if self.is_positive() else '~') + str(self.index)
	
	def __invert__(self):
		return self.reverse()
	
	def is_positive(self):
		''' Return if this edge is the positively oriented one. '''
		
		return self.label == self.index
	
	def reverse(self):
		''' Return this edge but with reversed orientation. '''
		
		return self.reversed_edge

class Triangle(object):
	''' This represents a triangle.
	
	It is specified by a list of three edges, ordered anticlockwise. '''
	def __init__(self, edges):
		assert(isinstance(edges, (list, tuple)))
		assert(all(isinstance(edge, Edge) for edge in edges))
		assert(len(edges) == 3)
		
		# Edges are ordered anti-clockwise.
		self.edges = edges
		self.labels = [edge.label for edge in self]
		self.indices = [edge.index for edge in self]
		self.vertices = [self.edges[1].target_vertex, self.edges[2].target_vertex, self.edges[0].target_vertex]
		self.corners = [Corner(self, i) for i in range(3)]
	
	def __str__(self):
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
		elif isinstance(item, Edge):
			return item in self.edges
		elif isinstance(item, Vertex):
			return item in self.vertices
		elif isinstance(item, Corner):
			return item in self.corners
		else:
			return NotImplemented

class Corner(object):
	''' This represents a corner of a triangulation
	
	It is a triangle along with a side number (the side opposite this corner). '''
	def __init__(self, triangle, side):
		assert(isinstance(triangle, Triangle))
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
	
	def __str__(self):
		return str((self.triangle, self.side))

# Remark: In other places in the code you will often see L(triangulation). This is the space
# of laminations on triangulation with the coordinate system induced by the triangulation.

class Triangulation(object):
	''' This represents a triangulation of a punctured surface.
	
	 It is specified by a list of Triangles. It builds its own
	 corners automatically. '''
	def __init__(self, triangles):
		assert(isinstance(triangles, (list, tuple)))
		assert(all(isinstance(triangle, Triangle) for triangle in triangles))
		
		self.triangles = triangles
		
		self.edges = [edge for triangle in self for edge in triangle.edges]
		self.oriented_edges = [edge for edge in self.edges if edge.is_positive()]
		self.vertices = list(set(vertex for triangle in self for vertex in triangle.vertices))
		self.corners = [corner for triangle in self for corner in triangle.corners]
		
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
	
	def __str__(self):
		return str(list(self))
	def __iter__(self):
		return iter(self.triangles)
	def __getitem__(self, index):
		return self.triangles[index]
	def __contains__(self, item):
		if isinstance(item, Vertex):
			return item in self.vertices
		elif isinstance(item, Edge):
			return item in self.edges
		elif isinstance(item, Triangle):
			return item in self.triangles
		elif isinstance(item, Corner):
			return item in self.corners
		else:
			return NotImplemented
	
	def copy(self):
		''' Return a new copy of this Triangulation.
		
		Note: This preserves both vertex and edge labels. '''
		
		new_vertices = dict((vertex, Vertex(vertex.label)) for vertex in self.vertices)
		new_edges = dict((edge, Edge(new_vertices[edge.source_vertex], new_vertices[edge.target_vertex], edge.label)) for edge in self.oriented_edges)
		for edge in self.oriented_edges:
			new_edges[~edge] = ~new_edges[edge]
		new_triangles = [Triangle([new_edges[edge] for edge in triangle]) for triangle in self]
		return Triangulation(new_triangles)
	
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
	
	def is_flippable(self, edge_label):
		''' Return if the given edge is flippable.
		
		An edge is flippable if and only if it lies in two distinct triangles. '''
		
		return self.triangle_lookup[edge_label] != self.triangle_lookup[~edge_label]
	
	def flippable_edges(self):
		''' Return this list of flippable edges of this triangulation. '''
		
		return [i for i in range(self.zeta) if self.is_flippable(i)]
	
	def square_about_edge(self, edge_label):
		''' Return the four edges around the given edge.
		
		The chosen edge must be flippable. '''
		
		assert(self.is_flippable(edge_label))
		
		# Given the label e, return the edges a, b, c, d in order.
		#
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
		
		corner_A, corner_B = self.corner_of_edge(edge_label), self.corner_of_edge(~edge_label)
		return [corner_A.edges[1], corner_A.edges[2], corner_B.edges[1], corner_B.edges[2]]
	
	def flip_edge(self, edge_index):
		''' Return a new triangulation obtained by flipping the given edge.
		
		The chosen edge must be flippable. '''
		
		assert(self.is_flippable(edge_index))
		
		# Use the following for reference:
		# #<----------#     #-----------#
		# |     a    ^^     |\          |
		# |         / |     | \         |
		# |  A     /  |     |  \     A2 |
		# |       /   |     |   \       |
		# |b    e/   d| --> |    \e'    |
		# |     /     |     |     \     |
		# |    /      |     |      \    |
		# |   /       |     |       \   |
		# |  /     B  |     | B2     \  |
		# | /         |     |         \ |
		# V/    c     |     |          V|
		# #---------->#     #-----------#
		
		a, b, c, d = self.square_about_edge(edge_index)
		new_edge = Edge(a.target_vertex, c.target_vertex, edge_index)
		
		triangle_A2 = Triangle([new_edge, d, a])
		triangle_B2 = Triangle([~new_edge, b, c])
		
		unchanged_triangles = [triangle for triangle in self if edge_index not in triangle.labels and ~edge_index not in triangle]
		return Triangulation(unchanged_triangles + [triangle_A2, triangle_B2])
	
	def tree_and_dual_tree(self, respect_vertex_labels=False):
		''' Return a maximal tree in the 1--skeleton of this triangulation and a
		maximal tree in 1--skeleton of the dual of this triangulation.
		
		These are given as lists of Booleans signaling if each edge is in the tree.
		No edge is used in both the tree and the dual tree. '''
		
		tree = [False] * self.zeta
		vertices_used = dict((vertex, False) for vertex in self.vertices)
		# Get some starting vertices.
		for vertex in self.vertices:
			if vertex.label >= 0:
				vertices_used[vertex] = True
				if not respect_vertex_labels:
					# Stop as soon as we've marked one.
					break
		
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
		
		Each element is given as a path in the dual 1--skeleton and corrsponds
		to a good curve. Each path will meet each edge at most once.
		
		Each pair of paths is guaranteed to meet at most once. '''
		
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
		
		assert(isinstance(other_triangulation, Triangulation))
		
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
		
		if respect_vertex_labels:
			isometries = [isom for isom in isometries if all((vertex.label >= 0) == (isom.vertex_map[vertex].label >= 0) for vertex in self.vertices)]
		return isometries
	
	def self_isometries(self):
		''' Returns a list of isometries taking this triangulation to itself. '''
		
		return self.isometries_to(self)
	
	def is_isometric_to(self, other_triangulation):
		''' Return if there are any orientation preserving isometries from this triangulation to other_triangulation. '''
		
		assert(isinstance(other_triangulation, Triangulation))
		
		return len(self.isometries_to(other_triangulation)) > 0
	
	def find_isometry(self, other_triangulation, edge_from_label, edge_to_label):
		''' Return the isometry from this triangulation to other_triangulation that sends edge_from_label to
		to edge_to_label.
		
		Assumes (and checks) that such an isometry exists and is unique. '''
		
		try:
			[isometry] = [isom for isom in self.isometries_to(other_triangulation) if isom(edge_from_label) == edge_to_label]
		except ValueError:
			raise flipper.AssumptionError('edge_from_label and edge_to_label do not determine a unique isometry.')
		else:
			return isometry
	
	# Laminations we can build on this triangulation.
	def lamination(self, geometric, algebraic=None, remove_peripheral=True):
		''' Return a new lamination on this surface assigning the specified weight to each edge. '''
		
		if remove_peripheral:
			# Compute how much peripheral component there is on each corner class.
			# This will also check that the triangle inequalities are satisfied. When
			# they fail one of peripheral.values() is negative, which is non-zero and
			# so triggers the correction.
			def dual_weight(corner):
				''' Return double the weight of normal arc corresponding to the given corner. '''
				
				return geometric[corner.indices[1]] + geometric[corner.indices[2]] - geometric[corner.index]
			
			peripheral = dict((vertex, min(dual_weight(corner) for corner in self.corner_class_of_vertex(vertex))) for vertex in self.vertices)
			if any(peripheral.values()):  # Is there any to add / remove?
				# Really should be geometric[i] - sum(peripheral[v]) / 2 but we can't do division in a ring.
				geometric = [2*geometric[i] - sum(peripheral[v] for v in self.vertices_of_edge(i)) for i in range(self.zeta)]
		
		if algebraic is not None:
			return flipper.kernel.Lamination(self, geometric, algebraic)
		else:
			lamination = flipper.kernel.Lamination(self, geometric, [0] * self.zeta)
			# If we have a curve we should compute the algebraic intersection numbers.
			# Note that if the curve is not twistable then its algebraic intersection numbers
			# are all zero and so we can just return lamination.
			if lamination.is_curve() and lamination.is_twistable():
				conjugation = lamination.conjugate_short()
				short_lamination = conjugation(lamination)
				triangulation = short_lamination.triangulation
				
				# Grab the indices of the two edges we meet.
				e1, e2 = [edge_index for edge_index in range(short_lamination.zeta) if short_lamination[edge_index] > 0]
				
				a, b, c, d = triangulation.square_about_edge(e1)
				# If the curve is going vertically through the square then ...
				if short_lamination[a] == 1 and short_lamination[c] == 1:
					# swap the labels round so it goes horizontally.
					e1, e2 = e2, e1
					a, b, c, d = triangulation.square_about_edge(e1)
				elif short_lamination[b] == 1 and short_lamination[d] == 1:
					pass
				
				# Currently short_lamination.algebraic == [0, 0, ..., 0].
				short_lamination.algebraic[e1] = +1
				short_lamination.algebraic[b.index] = -1 if b.is_positive() else +1
				
				return conjugation.inverse()(short_lamination)
			else:
				return lamination
	
	def empty_lamination(self):
		''' Return an empty lamination on this surface. '''
		
		return self.lamination([0] * self.zeta, [0] * self.zeta)
	
	def random_curve(self, num_flips):
		''' Return a random curve on this surface. '''
		
		h = self.id_encoding()
		for _ in range(num_flips):
			T = h.target_triangulation
			h = T.encode_flip(choice(T.flippable_edges())) * h
		
		c = h.target_triangulation.key_curves()[0]
		return h.inverse()(c)
	
	def key_curves(self):
		''' Return a list of curves which fill the underlying surface.
		
		As these fill, by Alexander's trick a mapping class is the identity
		if and only if it fixes all of them. '''
		
		curves = []
		
		for edge_index in range(self.zeta):
	 		# Build the curve which is the boundary of a regular neighbourhood of this edge.
			endpoints = self.vertices_of_edge(edge_index)
			
			# If the given edge actually forms a loop then we will build two curves, one for
			# each side of the regular neighbourhood.
			if len(set(endpoints)) == 1:
				left = False
				geometric = [[0] * self.zeta, [0] * self.zeta]
				algebraic = [[0] * self.zeta, [0] * self.zeta]
				for corner in self.corner_class_of_vertex(endpoints[0]):  # They are the same so it doesn't matter which we take.
					index = corner.indices[2]
					if index == edge_index:
						left = not left
					else:
						geometric[0 if left else 1][index] += 1
						algebraic[0 if left else 1][index] += 1 if index == corner.labels[2] else -1
				
				curves.append(self.lamination(geometric[0], algebraic[0]))
				curves.append(self.lamination(geometric[1], algebraic[1]))
			else:
				geometric = [0] * self.zeta
				algebraic = [0] * self.zeta
				for vertex in endpoints:
					for corner in self.corner_class_of_vertex(vertex):
						index = corner.indices[2]
						geometric[index] += 1
						algebraic[index] += 1 if index == corner.labels[2] else -1
				
				geometric[edge_index] = 0
				algebraic[edge_index] = 0
				if not self.is_flippable(edge_index):
					# We also need to zero out the curve enclosing this edge.
					[boundary_edge] = [index for index in self.corner_of_edge(edge_index).indices if index != edge_index]
					geometric[boundary_edge] = 0
					algebraic[boundary_edge] = 0
				
				curves.append(self.lamination(geometric, algebraic))
		
		# Filter out any empty laminations that we get.
		return [curve for curve in curves if not curve.is_empty()]
	
	def id_encoding(self):
		''' Return an encoding of the identity map on this triangulation. '''
		
		return flipper.kernel.Encoding(self, self, flipper.kernel.id_pl_function(self.zeta), flipper.kernel.id_l_function(self.zeta))
	
	def encode_flip(self, edge_index):
		''' Return an encoding of the effect of flipping the given edge.
		
		The given edge must be flippable. '''
		
		assert(self.is_flippable(edge_index))
		
		new_triangulation = self.flip_edge(edge_index)
		
		I = flipper.kernel.id_matrix(self.zeta)
		Z = flipper.kernel.zero_matrix(self.zeta, 1)
		
		a, b, c, d = [edge.index for edge in self.square_about_edge(edge_index)]
		e = norm(edge_index)  # Give it a shorter name.
		A1 = I.tweak([(e, a), (e, c)], [(e, e), (e, e)])
		C1 = Z.tweak([(0, a), (0, c)], [(0, b), (0, d)])
		
		A2 = I.tweak([(e, b), (e, d)], [(e, e), (e, e)])
		C2 = Z.tweak([(0, b), (0, d)], [(0, a), (0, c)])
		
		# These functions are their own inverses.
		f = f_inv = flipper.kernel.PartialFunction(A1, C1)
		g = g_inv = flipper.kernel.PartialFunction(A2, C2)
		
		w, x, y, z = [edge.label for edge in self.square_about_edge(edge_index)]
		A = I.tweak([(e, norm(i)) for i in [x, y] if norm(i) == i], [(e, norm(i)) for i in [x, y] if norm(i) != i] + [(e, e)])
		B = I.tweak([(e, norm(i)) for i in [y, z] if norm(i) == i], [(e, norm(i)) for i in [y, z] if norm(i) != i] + [(e, e)])
		# Note that B is not A.inverse() as there are some relations in homology().
		
		return flipper.kernel.Encoding(self, new_triangulation,
			flipper.kernel.PLFunction([flipper.kernel.BasicPLFunction([f, g], [f_inv, g_inv])]),
			flipper.kernel.LFunction(A, B))
	
	def encode_flips(self, edge_indices):
		''' Return an encoding of the effect of flipping the given sequences of edges. '''
		
		h = self.id_encoding()
		for edge_index in edge_indices:
			h = h.target_triangulation.encode_flip(edge_index) * h
		return h
	
	def encode_flips_and_close(self, edge_indices, edge_from_label, edge_to_label):
		''' Return an encoding of the effect of flipping the given sequences of edges followed by an isometry.
		
		The isometry used is the one taking edge_from_label to edge_to_label. '''
		
		E = self.encode_flips(edge_indices)
		return E.target_triangulation.find_isometry(self, edge_from_label, edge_to_label).encode() * E


def create_triangulation(all_labels):
	''' Return an Triangulation from a list of triples of edge labels.
	
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
	vertices = [Vertex(i) for i in range(num_vertices)]
	
	def vertexer(edge_label):
		''' Return the vertex opposite the given edge label. '''
		
		for vertex, cls in zip(vertices, vertex_classes):
			if edge_label in cls:
				return vertex
	
	edges_map = dict((i, Edge(vertexer(i), vertexer(~i), i)) for i in range(zeta))
	for i in range(zeta):
		edges_map[~i] = ~edges_map[i]
	
	triangles = [Triangle([edges_map[label] for label in labels]) for labels in all_labels]
	
	return Triangulation(triangles)

