
''' A module for representing a triangulation of a punctured surface.

Provides five classes: Vertex, Edge, Triangle, Corner and Triangulation.
	An Vertex is a singleton.
	An Edge is an ordered pair of Vertices.
	An Triangle is an ordered triple of Edges.
	A Corner is a Triangle with a chosen side.
	An Triangulation is a collection of Triangles.

There is also a helper function: create_triangulation. '''

import flipper

from random import choice
from itertools import product
import string
from math import log

INFTY = float('inf')

def norm(value):
	''' A map taking an edges label to its index.
	
	That is, x and ~x should map to the same thing. '''
	
	return max(value, ~value)

class Vertex(object):
	''' This represents a vertex, labelled with an integer. '''
	def __init__(self, label, filled=False):
		assert(isinstance(label, flipper.IntegerType))
		assert(isinstance(filled, bool))
		self.label = label
		self.filled = filled
	
	def __repr__(self):
		return str(self)
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
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return ('' if self.is_positive() else '~') + str(self.index)
	
	def __invert__(self):
		return self.reverse()
	
	def is_positive(self):
		''' Return if this edge is the positively oriented one. '''
		
		return self.label == self.index
	
	def sign(self):
		''' Return the sign (+/-1) of this edge. '''
		
		return +1 if self.is_positive() else -1
	
	def reverse(self):
		''' Return this edge but with reversed orientation. '''
		
		return self.reversed_edge

class Triangle(object):
	''' This represents a triangle.
	
	It is specified by a list of three edges, ordered anticlockwise.
	It builds its corners automatically. '''
	def __init__(self, edges):
		assert(isinstance(edges, (list, tuple)))
		assert(all(isinstance(edge, Edge) for edge in edges))
		assert(len(edges) == 3)
		
		# Edges are ordered anti-clockwise. We will cyclically permute
		# these to a canonical ordering, the one where the edges are ordered
		# minimally by label.
		self.edges = min([edges[i:] + edges[:i] for i in range(3)], key=lambda t: [e.label for e in t])
		self.labels = [edge.label for edge in self]
		self.indices = [edge.index for edge in self]
		self.vertices = [self.edges[1].target_vertex, self.edges[2].target_vertex, self.edges[0].target_vertex]
		self.corners = [Corner(self, i) for i in range(3)]
	
	def __repr__(self):
		return str(self)
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
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return str((self.triangle, self.side))

# Remark: In other places in the code you will often see L(triangulation). This is the space
# of laminations on triangulation with the coordinate system induced by the triangulation.

class Triangulation(object):
	''' This represents a triangulation of a punctured surface.
	
	It is specified by a list of Triangles. Its edges must be
	numbered 0, 1, ... and its vertices must be numbered 0, 1, ... '''
	def __init__(self, triangles):
		assert(isinstance(triangles, (list, tuple)))
		assert(all(isinstance(triangle, Triangle) for triangle in triangles))
		
		# We will sort the triangles into a canonical ordering, the one where the edges are ordered
		# minimally by label. This allows for fast comparisons.
		self.triangles = sorted(triangles, key=lambda t: [e.label for e in t])
		
		self.edges = [edge for triangle in self for edge in triangle.edges]
		self.oriented_edges = [edge for edge in self.edges if edge.is_positive()]
		self.vertices = sorted(set(vertex for triangle in self for vertex in triangle.vertices), key=lambda vertex: vertex.label)
		assert(not all(vertex.filled for vertex in self.vertices))
		self.corners = [corner for triangle in self for corner in triangle.corners]
		
		self.num_triangles = len(self.triangles)
		self.zeta = len(self.oriented_edges)
		assert(self.zeta == self.num_triangles * 3 // 2)
		self.num_vertices = len(self.vertices)
		self.num_filled_vertices = len([vertex for vertex in self.vertices if vertex.filled])
		self.num_unfilled_vertices = self.num_vertices - self.num_filled_vertices
		assert(set([vertex.label for vertex in self.vertices]) == set(range(self.num_vertices)))
		assert(set(edge.label for edge in self.edges) == set([i for i in range(self.zeta)] + [~i for i in range(self.zeta)]))
		
		self.triangle_lookup = dict((edge.label, triangle) for triangle in self for edge in triangle.edges)
		self.edge_lookup = dict((edge.label, edge) for edge in self.edges)
		self.corner_lookup = dict((corner.label, corner) for corner in self.corners)
		self.vertex_lookup = dict((corner.label, corner.vertex) for corner in self.corners)
		
		# This appears to be one of the slowest bits when there is a high degree vertex.
		def order_corner_class(corner_class):
			''' Return the given corner_class but reorderd so that corners occur anti-clockwise about the vertex. '''
			
			corner_class = list(corner_class)
			lookup = dict((corner.edges[2], corner) for corner in corner_class)
			ordered_class = [corner_class[0]]  # Get one corner to start at.
			# Perhaps this should be chosen in some canonical way. Smallest labelled one?
			# This isn't totally safe: it doesn't check that there aren't multiple cycles.
			for i in range(len(corner_class)-1):
				try:
					ordered_class.append(lookup[~ordered_class[i].edges[1]])
				except KeyError:
					raise ValueError('Corners do not close up about vertex.')
			
			if ordered_class[0].edges[2] != ~ordered_class[-1].edges[1]:
				raise ValueError('Corners do not close up about vertex.')
			
			return ordered_class
		self.corner_classes = [order_corner_class([corner for corner in self.corners if corner.vertex == vertex]) for vertex in self.vertices]
		
		self.euler_characteristic = self.num_filled_vertices - self.zeta + self.num_triangles  # V - E + F.
		self.genus = (2 - self.euler_characteristic - self.num_unfilled_vertices) // 2
		
		# The maximum order of a periodic mapping class.
		# These bounds follow from the 4g + 4 bound on the closed surface [Primer reference]
		# and the Riemann removable singularity theorem which allows us to cap off the
		# punctures when the genus > 1 without affecting this bound.
		if self.genus > 1:
			self.max_order = 4 * self.genus + 2
		elif self.genus == 1:
			self.max_order = max(self.num_unfilled_vertices, 6)
		else:
			self.max_order = self.num_unfilled_vertices
		
		# Two triangualtions are the same if and only if they have the same signature.
		self.signature = [e.label for t in self for e in t]
	
	def __repr__(self):
		return str(self)
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
	def __reduce__(self):
		# Triangulations are already pickleable but this results in a smaller pickle.
		return (self.__class__, (self.triangles,))
	def __eq__(self, other):
		return self.signature == other.signature
	def __ne__(self, other):
		return not(self == other)
	
	def vertices_of_edge(self, edge_label):
		''' Return the two vertices at the ends of the given edge. '''
		
		# Refactor out?
		return [self.edge_lookup[edge_label].source_vertex, self.edge_lookup[~edge_label].source_vertex]
	
	def triangles_of_edge(self, edge_label):
		''' Return the two triangles containing the given edge. '''
		
		# Refactor out?
		return [self.triangle_lookup[edge_label], self.triangle_lookup[~edge_label]]
	
	def corner_of_edge(self, edge_label):
		''' Return the corner opposite the given edge. '''
		assert(isinstance(edge_label, flipper.IntegerType))
		
		# Refactor out?
		return self.corner_lookup[edge_label]
	
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
	
	def iso_sig(self, start_points=None):
		''' Return the isomorphism signature of this triangulation. '''
		
		perm_lookup = dict((perm, index) for index, perm in enumerate(flipper.kernel.permutation.all_permutations(3)))
		transition_perm_lookup = {
			(0, 0): flipper.kernel.Permutation([0, 2, 1]),
			(0, 1): flipper.kernel.Permutation([1, 0, 2]),
			(0, 2): flipper.kernel.Permutation([2, 1, 0]),
			(1, 0): flipper.kernel.Permutation([1, 0, 2]),
			(1, 1): flipper.kernel.Permutation([2, 1, 0]),
			(1, 2): flipper.kernel.Permutation([0, 2, 1]),
			(2, 0): flipper.kernel.Permutation([2, 1, 0]),
			(2, 1): flipper.kernel.Permutation([0, 2, 1]),
			(2, 2): flipper.kernel.Permutation([1, 0, 2])
			}
		
		best = ([INFTY], [INFTY], [INFTY])
		num_tri = self.num_triangles
		
		if start_points is None:
			start_points = product(self, flipper.kernel.permutation.all_permutations(3))
		
		for start_triangle, start_perm in start_points:
			type_sequence = []
			target_sequence = []
			permutation_sequence = []
			
			queue = [start_triangle]
			triangle_labels = {start_triangle: (0, start_perm)}
			
			for i in range(num_tri):
				triangle = queue[i]
				_, perm = triangle_labels[triangle]
				perm_inv = perm.inverse()
				
				for j in range(3):
					side = perm_inv(j)
					target_corner = self.corner_of_edge(~triangle.labels[side])
					target_triangle = target_corner.triangle
					target_side = target_corner.side
					if target_triangle not in triangle_labels:
						target_perm = perm * transition_perm_lookup[(target_side, side)]
						triangle_labels[target_triangle] = (len(queue), target_perm)
						queue.append(target_triangle)
						
						type_sequence.append(1)
						# We don't need to record the follow as they are implied.
						# target_sequence.append(len(queue))
						# permutation_sequence.append(perm_lookup[id_perm])
					else:
						target_index, target_perm = triangle_labels[target_triangle]
						k = target_perm(target_side)
						if target_index > i or (target_index == i and k > j):  # We've not done this gluing yet.
							transition_perm = target_perm * transition_perm_lookup[(side, target_side)] * perm_inv
							
							type_sequence.append(2)
							target_sequence.append(target_index)
							permutation_sequence.append(perm_lookup[transition_perm])
			
			best = min((type_sequence, target_sequence, permutation_sequence), best)
		
		char = string.ascii_lowercase + string.ascii_uppercase + string.digits + '+-'
		
		type_sequence, target_sequence, permutation_sequence = best
		type_sequence = type_sequence + [0] * (len(type_sequence) % 3)
		char_type = ''.join(char[type_sequence[i] + 4 * type_sequence[i+1] + 16 * type_sequence[i+2]] for i in range(0, len(type_sequence), 3))
		char_perm = ''.join(char[p] for p in permutation_sequence)
		if num_tri < 63:
			char_start = char[num_tri]
			char_target = ''.join(char[target] for target in target_sequence)
		else:
			digits = int(log(num_tri) / log(64)) + 1
			char_start = char[63] + char[digits] + ''.join(char[(num_tri // 64**i) % 64] for i in range(digits))
			char_target = ''.join(char[(target // 64**i) % 64] for target in target_sequence for i in range(digits))
		
		return char_start + char_type + char_target  + char_perm
	
	def is_flippable(self, edge_label):
		''' Return if the given edge is flippable.
		
		An edge is flippable if and only if it lies in two distinct triangles. '''
		
		return self.triangle_lookup[edge_label] != self.triangle_lookup[~edge_label]
	
	def flippable_edges(self):
		''' Return this list of flippable edges of this triangulation. '''
		
		return [i for i in range(self.zeta) if self.is_flippable(i)]
	
	def nonflippable_boundary(self, edge_label):
		''' Return the label of the edge bounding the once-punctured monogon containing edge_label.
		
		The given edge must not be flippable. '''
		
		assert(not self.is_flippable(edge_label))
		
		# As edge_label is not flippable the triangle containing it must be (edge_label, ~edge_label, x).
		[boundary_edge] = [label for label in self.triangle_lookup[edge_label].labels if label != edge_label and label != ~edge_label]
		return boundary_edge
	
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
	
	def flip_edge(self, edge_label):
		''' Return a new triangulation obtained by flipping the given edge.
		
		The chosen edge must be flippable. '''
		
		assert(self.is_flippable(edge_label))
		
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
		
		a, b, c, d = self.square_about_edge(edge_label)
		new_edge = Edge(a.target_vertex, c.target_vertex, edge_label)
		
		triangle_A2 = Triangle([new_edge, d, a])
		triangle_B2 = Triangle([~new_edge, b, c])
		
		unchanged_triangles = [triangle for triangle in self if edge_label not in triangle.labels and ~edge_label not in triangle]
		return Triangulation(unchanged_triangles + [triangle_A2, triangle_B2])
	
	def tree_and_dual_tree(self, respect_fillings=False):
		''' Return a maximal tree in the 1--skeleton of this triangulation and a
		maximal tree in 1--skeleton of the dual of this triangulation.
		
		These are given as lists of Booleans signaling if each edge is in the tree.
		No edge is used in both the tree and the dual tree. '''
		
		tree = [False] * self.zeta
		vertices_used = dict((vertex, False) for vertex in self.vertices)
		# Get some starting vertices.
		for vertex in self.vertices:
			if not vertex.filled:
				vertices_used[vertex] = True
				if not respect_fillings:
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
	
	def find_isometry(self, other, edge_from_label, edge_to_label, respect_fillings=True):
		''' Return the isometry from this triangulation to other that sends edge_from_label to
		to edge_to_label.
		
		Assumes (and checks) that such an isometry exists and is unique. '''
		assert(isinstance(other, Triangulation))
		assert(isinstance(edge_from_label, flipper.IntegerType))
		assert(isinstance(edge_to_label, flipper.IntegerType))
		assert(isinstance(respect_fillings, bool))
		
		source_corner = self.corner_of_edge(edge_from_label)
		target_corner = other.corner_of_edge(edge_to_label)
		# We do a depth first search extending the corner map across the triangulation.
		corner_map = {source_corner: target_corner}
		# This is a stack of triangles that may still have consequences.
		to_process = [(source_corner, target_corner)]
		while to_process:
			from_corner, to_corner = to_process.pop()
			new_from_corner, new_to_corner = self.opposite_corner(from_corner), other.opposite_corner(to_corner)
			if new_from_corner in corner_map:
				if new_to_corner != corner_map[new_from_corner]:
					# Map does not extend to a consistent isometry.
					raise flipper.AssumptionError('edge_from_label and edge_to_label do not determine an isometry.')
			else:
				corner_map[new_from_corner] = new_to_corner
				to_process.append((new_from_corner, new_to_corner))
			
			new_from_corner, new_to_corner = self.rotate_corner(from_corner), other.rotate_corner(to_corner)
			if new_from_corner in corner_map:
				if new_to_corner != corner_map[new_from_corner]:
					# Map does not extend to a consistent isometry.
					raise flipper.AssumptionError('edge_from_label and edge_to_label do not determine an isometry.')
			else:
				corner_map[new_from_corner] = new_to_corner
				to_process.append((new_from_corner, new_to_corner))
		
		
		isometry = flipper.kernel.Isometry(self, other, corner_map)
		if respect_fillings and any(vertex.filled != isometry(vertex).filled for vertex in self.vertices):  #pylint: disable=maybe-no-member
			raise flipper.AssumptionError('Isometry does not respect fillings.')
		
		return isometry
	
	def isometries_to(self, other, respect_fillings=True):
		''' Return a list of all isometries from this triangulation to other. '''
		
		assert(isinstance(other, Triangulation))
		assert(isinstance(respect_fillings, bool))
		
		# Isometries are determined by where a single triangle is sent.
		# We take a corner of smallest degree.
		source_cc = min(self.corner_classes, key=len)
		source_corner = source_cc[0]
		# And find all the places where it could be sent so there are as few as possible to check.
		target_corners = [corner for target_cc in other.corner_classes for corner in target_cc if len(target_cc) == len(source_cc)]
		
		isometries = []
		for target_corner in target_corners:
			try:
				isometries.append(self.find_isometry(other, source_corner.label, target_corner.label, respect_fillings))
			except flipper.AssumptionError:
				pass
		
		return isometries
	
	def self_isometries(self):
		''' Returns a list of isometries taking this triangulation to itself. '''
		
		return self.isometries_to(self)
	
	def is_isometric_to(self, other):
		''' Return if there are any orientation preserving isometries from this triangulation to other. '''
		
		assert(isinstance(other, Triangulation))
		
		return len(self.isometries_to(other)) > 0
	
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
				if all(entry % 2 == 0 for entry in geometric):
					geometric = [entry // 2 for entry in geometric]
		
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
		''' Return a list of curves which fill the underlying surface and include a basis for H_1(S).
		
		As these fill, by Alexander's trick a mapping class is the identity
		if and only if it fixes all of them, including orientation. '''
		
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
					boundary_edge = norm(self.nonflippable_boundary(edge_index))
					geometric[boundary_edge] = 0
					algebraic[boundary_edge] = 0
				
				curves.append(self.lamination(geometric, algebraic))
		
		# Now add in paths to make sure we have the homology basis covered.
		for path in self.homology_basis():
			geometric = [0] * self.zeta
			algebraic = [0] * self.zeta
			for step in path:
				geometric[norm(step)] += 1
				algebraic[norm(step)] += +1 if norm(step) == step else -1
			curves.append(self.lamination(geometric, algebraic))
		
		# Filter out any empty laminations that we get.
		return [curve for curve in curves if not curve.is_empty()]
	
	def id_isometry(self):
		''' Return the isometry representing the identity map. '''
		
		return flipper.kernel.Isometry(self, self, dict((corner, corner) for corner in self.corners))
	
	def id_encoding(self):
		''' Return an encoding of the identity map on this triangulation. '''
		
		return self.id_isometry().encode()
	
	def encode_flip(self, edge_label):
		''' Return an encoding of the effect of flipping the given edge.
		
		The given edge must be flippable. '''
		
		assert(self.is_flippable(edge_label))
		
		new_triangulation = self.flip_edge(edge_label)
		
		return flipper.kernel.EdgeFlip(self, new_triangulation, edge_label).encode()
	
	def encode_flips(self, edge_labels):
		''' Return an encoding of the effect of flipping the given sequences of edges. '''
		
		h = self.id_encoding()
		for edge_label in edge_labels:
			h = h.target_triangulation.encode_flip(edge_label) * h
		return h
	
	def encode_flips_and_close(self, edge_labels, edge_from_label, edge_to_label):
		''' Return an encoding of the effect of flipping the given sequences of edges followed by an isometry.
		
		The isometry used is the one taking edge_from_label to edge_to_label. '''
		
		assert(isinstance(edge_labels, (list, tuple)))
		assert(all(isinstance(label, flipper.IntegerType) for label in edge_labels))
		assert(isinstance(edge_from_label, flipper.IntegerType))
		assert(isinstance(edge_to_label, flipper.IntegerType))
		
		E = self.encode_flips(edge_labels)
		return E.target_triangulation.find_isometry(self, edge_from_label, edge_to_label).encode() * E
	
	def all_flips(self, depth, prefix=None):
		''' Return all flip sequences of at most the given number of flips. '''
		
		assert(isinstance(depth, flipper.IntegerType))
		
		def generator(T, d, flippable):
			''' Return the sequences of at most d flips from this triangulation where only the specified edges are flippable. '''
			for i in flippable:
				yield [i]
				if d > 1:
					T2 = T.flip_edge(i)
					square = [edge.index for edge in T.square_about_edge(i)]
					new_flippable = [j for j in T2.flippable_edges() if (j > i and j in flippable) or j in square]
					for suffix in generator(T.flip_edge(i), d-1, new_flippable):
						yield [i] + suffix
		
		prefix = [] if prefix is None else list(prefix)
		
		flippable = self.flippable_edges()
		T = self
		for item in prefix:
			square = [edge.index for edge in T.square_about_edge(item)]
			T = T.flip_edge(item)
			flippable = [j for j in T.flippable_edges() if (j > item and j in flippable) or j in square]
		
		for sequence in generator(T, depth - len(prefix), flippable):
			yield prefix + sequence
	
	def all_encodings(self, depth, prefix=None):
		''' Return all encodings that can be defined by at most the given number of flips. '''
		
		prefix = [] if prefix is None else list(prefix)
		
		for sequence in self.all_flips(depth, prefix):
			yield self.encode_flips(prefix + sequence)
	
	def all_mapping_classes(self, depth, prefix=None):
		''' Return all mapping classes that can be defined by at most the given number of flips followed by one isometry. '''
		
		assert(isinstance(depth, flipper.IntegerType))
		
		for encoding in self.all_encodings(depth, prefix):
			for isom in encoding.closing_isometries():
				yield isom.encode() * encoding


#######################################################
#### Some helper functions for building triangulations.

def create_triangulation(all_labels):
	''' Return an Triangulation from a list of triples of edge labels.
	
	Let T be an ideal triangulaton of the punctured (oriented) surface S. Orient
	and edge e of T and assign an index i(e) in 0, ..., zeta-1. Now to each
	triangle t of T associate the triple (j(e_1), j(e_2), j(e_3)) where:
		- e_1, e_2, e_3 are the edges of t, ordered acording to the orientation of t, and
		- j(e) = {  i(e) if the orientation of e agrees with that of t, and
		         { ~i(e) otherwise.
		    Here ~x := -1 - x, the two's complement of x.
	
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
		raise flipper.FatalError('Label now missing.')
	
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


def triangulation_from_iso_sig(signature):
	''' Return the triangulation described by the given isomorphism signature.
	
	See the appendix of:
		Simplification paths in the Pachner graphs of closed orientable
		3-manifold triangulations
	for a more detailed description of this construction. '''
	
	# We will specialise this function for loading isomorphism signatures
	# of closed 2--manifolds only. This will enable us to remove a lot of
	# variables and simplify proceedings.
	
	assert(isinstance(signature, flipper.StringType))
	
	char = string.ascii_lowercase + string.ascii_uppercase + string.digits + '+-'
	char_lookup = dict((letter, index) for index, letter in enumerate(char))
	perm_lookup = flipper.kernel.permutation.all_permutations(3)
	
	def debase(digits, base=64):
		''' Return the decimal corresponding to a base64 sequence of digits. '''
		
		return sum(digit * base**index for index, digit in enumerate(digits))
	
	values = [char_lookup[letter] for letter in signature]
	
	if values[0] < 63:
		num_chars = 1
		num_tri = values[0]
		start = 1
	else:
		num_chars = values[1]  # This must be > 1.
		num_tri = debase(values[1:num_chars])
		start = 1 + num_chars
	
	assert(num_chars > 0)
	assert(num_tri > 0)
	
	start2 = start + num_tri // 2  # Type sequence is [start:start2].
	start3 = start2 + num_chars * (1 + num_tri // 2)  # Destination sequence is [start2:start3].
	start4 = start3 + (1 + num_tri // 2)  # Permutation sequence is [start3:start4].
	assert(start4 == len(values))
	
	type_sequence = [t for value in values[start:start2] for t in [value % 4, (value // 4) % 4, (value // 16) % 4]]
	destination_sequence = [debase(values[i:i+num_chars]) for i in range(start2, start3, num_chars)]
	permutation_sequence = [perm_lookup[value] for value in values[start3:start4]]
	
	zeta = 0
	num_tri_used = 1
	type_index, destination_index, permutation_index = 0, 0, 0
	edge_labels = [[None, None, None] for _ in range(num_tri)]
	triangle_reversed = [None] * num_tri
	triangle_reversed[0] = False
	for i in range(num_tri):
		for j in range(3):
			if edge_labels[i][j] is None:  # Otherwise we have filled in this entry from the other side.
				try:
					# We could also do type 0 in order to handle triangulations with boundary.
					if type_sequence[type_index] == 1:
						target, gluing = num_tri_used, perm_lookup[0]
						triangle_reversed[target] = not triangle_reversed[i]
						
						num_tri_used += 1
					elif type_sequence[type_index] == 2:
						target, gluing = destination_sequence[destination_index], permutation_sequence[permutation_index]
						
						destination_index += 1
						permutation_index += 1
					else:
						raise TypeError('Each gluing must be type 1 or 2 to give a closed triangulation.')
				except IndexError:
					raise ValueError('String does not correspond to a isomorphism signature.')
				type_index += 1
				
				edge_labels[i][j] = zeta
				edge_labels[target][gluing(j)] = ~zeta
				zeta += 1
	
	assert(num_tri_used == num_tri)
	# Check there are no unglued edges.
	assert(all(all(entry is not None for entry in row) for row in edge_labels))
	
	edge_labels = [edge_labels[i] if triangle_reversed[i] else edge_labels[i][::-1] for i in range(num_tri)]
	
	return create_triangulation(edge_labels)

