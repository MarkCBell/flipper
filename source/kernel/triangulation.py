''' A module for representing a triangulation of a punctured surface.

Provides five classes: Vertex, Edge, Triangle, Corner and Triangulation.
	A Vertex is a singleton.
	An Edge is an ordered pair of Vertices.
	A Triangle is an ordered triple of Edges.
	A Corner is a Triangle with a chosen side.
	A Triangulation is a collection of Triangles. '''

import flipper

try:
	from Queue import Queue
except ImportError:
	from queue import Queue
from random import choice
from itertools import groupby
import string
from math import log

INFTY = float('inf')

def norm(value):
	''' A map taking an edges label to its index.
	
	That is, x and ~x should map to the same thing. '''
	
	return max(value, ~value)

class Vertex(object):
	''' This represents a vertex, labelled with an integer. '''
	
	# Warning: This needs to be updated if the interals of this class ever change.
	__slots__ = ['label', 'filled']
	
	def __init__(self, label, filled=False):
		assert(isinstance(label, flipper.IntegerType))
		assert(isinstance(filled, bool))
		self.label = label
		self.filled = filled
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return ('Singularity ' if self.filled else 'Puncture ') + str(self.label)
	def __hash__(self):
		return hash(self.label)
	def __eq__(self, other):
		if isinstance(other, Vertex):
			return self.label == other.label
		else:
			return NotImplemented

class Edge(object):
	''' This represents an oriented edge, labelled with an integer.
	
	It is specified by the vertices that it connects from / to.
	Its inverse edge is created automatically and is labelled with ~its label. '''
	
	# Warning: This needs to be updated if the interals of this class ever change.
	__slots__ = ['source_vertex', 'target_vertex', 'label', 'index', 'reversed_edge']
	
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
	def __hash__(self):
		return hash(self.label)
	def __eq__(self, other):
		if isinstance(other, Edge):
			return self.label == other.label
		else:
			return NotImplemented
	
	def __invert__(self):
		''' Return this edge but with reversed orientation. '''
		
		return self.reversed_edge
	
	def is_positive(self):
		''' Return if this edge is the positively oriented one. '''
		
		return self.label == self.index
	
	def sign(self):
		''' Return the sign (+/-1) of this edge. '''
		
		return +1 if self.is_positive() else -1

class Triangle(object):
	''' This represents a triangle.
	
	It is specified by a list of three edges, ordered anticlockwise.
	It builds its corners automatically. '''
	
	# Warning: This needs to be updated if the interals of this class ever change.
	__slots__ = ['edges', 'labels', 'indices', 'vertices', 'corners']
	
	def __init__(self, edges):
		assert(isinstance(edges, (list, tuple)))
		assert(all(isinstance(edge, Edge) for edge in edges))
		assert(len(edges) == 3)
		
		# Edges are ordered anti-clockwise. We will cyclically permute
		# these to a canonical ordering, the one where the edges are ordered
		# minimally by label.
		best_index = min(range(3), key=lambda i: edges[i].label)
		
		self.edges = edges[best_index:] + edges[:best_index]
		self.labels = [edge.label for edge in self]
		self.indices = [edge.index for edge in self]
		self.vertices = [self.edges[1].target_vertex, self.edges[2].target_vertex, self.edges[0].target_vertex]
		self.corners = [Corner(self, i) for i in range(3)]
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return str(tuple(self.edges))
	def __hash__(self):
		return hash(tuple(self.labels))
	def __eq__(self, other):
		if isinstance(other, Triangle):
			return self.labels == other.labels
		else:
			return NotImplemented
	
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
	
	# Warning: This needs to be updated if the interals of this class ever change.
	__slots__ = ['triangle', 'side', 'edges', 'labels', 'indices', 'vertices', 'label', 'index', 'vertex', 'edge']
	
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
		self.positive_edges = [edge for edge in self.edges if edge.is_positive()]
		self.labels = sorted([edge.label for edge in self.edges])
		self.indices = sorted([edge.index for edge in self.positive_edges])
		self.vertices = sorted(set(vertex for triangle in self for vertex in triangle.vertices), key=lambda vertex: vertex.label)
		assert(not all(vertex.filled for vertex in self.vertices))
		self.corners = [corner for triangle in self for corner in triangle.corners]
		
		self.num_triangles = len(self.triangles)
		self.zeta = len(self.positive_edges)
		assert(self.zeta == self.num_triangles * 3 // 2)
		self.num_vertices = len(self.vertices)
		self.num_filled_vertices = len([vertex for vertex in self.vertices if vertex.filled])
		self.num_unfilled_vertices = self.num_vertices - self.num_filled_vertices
		# Check that the vertices are labelled 0, ..., num_vertices-1.
		assert(set(vertex.label for vertex in self.vertices) == set(range(self.num_vertices)))
		# Check that the edges have indices 0, ..., zeta-1.
		assert(set(self.labels) == set([i for i in range(self.zeta)] + [~i for i in range(self.zeta)]))
		
		self.triangle_lookup = dict((edge.label, triangle) for triangle in self for edge in triangle.edges)
		self.edge_lookup = dict((edge.label, edge) for edge in self.edges)
		self.corner_lookup = dict((corner.label, corner) for corner in self.corners)
		self.vertex_lookup = dict((corner.label, corner.vertex) for corner in self.corners)
		
		# This appears to be one of the slowest bits when there is a high degree vertex.
		def order_corner_class(corner_class):
			''' Return the given corner_class but reorderd so that corners occur anti-clockwise about the vertex. '''
			
			corner_class = list(corner_class)
			lookup = dict((corner.edges[2], corner) for corner in corner_class)
			ordered_class = [None] * len(corner_class)
			ordered_class[0] = corner_class[0]  # Get one corner to start at.
			# Perhaps this should be chosen in some canonical way. Smallest labelled one?
			# This isn't totally safe: it doesn't check that there aren't multiple cycles.
			for i in range(len(corner_class)-1):
				try:
					ordered_class[i+1] = lookup[~ordered_class[i].edges[1]]
				except KeyError:
					raise ValueError('Corners do not close up about vertex.')
			
			if ordered_class[0].edges[2] != ~ordered_class[-1].edges[1]:
				raise ValueError('Corners do not close up about vertex.')
			
			return ordered_class
		
		# We want to sort by the vertices so groupby will gather them but this would require adding
		# orderings to the Vertex class so we'll just sort / group by the vertex label. This should
		# uniquely determine the vertex.
		vertexer = lambda corner: corner.vertex.label
		self.corner_classes = [order_corner_class(g) for _, g in groupby(sorted(self.corners, key=vertexer), key=vertexer)]
		
		self.euler_characteristic = self.num_filled_vertices - self.zeta + self.num_triangles  # V - E + F.
		# NOTE: This assumes connected.
		self.genus = (2 - self.euler_characteristic - self.num_unfilled_vertices) // 2
		
		# The maximum order of a periodic mapping class.
		# These bounds follow from the 4g + 4 bound on the closed surface [Primer reference]
		# and the Riemann removable singularity theorem which allows us to cap off the
		# punctures when the genus > 1 without affecting this bound.
		# NOTE: This assumes connected.
		if self.genus > 1:
			self.max_order = 4 * self.genus + 2
		elif self.genus == 1:
			self.max_order = max(self.num_unfilled_vertices, 6)
		else:
			self.max_order = self.num_unfilled_vertices
		
		# Two triangualtions are the same if and only if they have the same signature.
		self.signature = [e.label for t in self for e in t]
	
	@classmethod
	def from_tuple(cls, edge_labels, vertex_labels=None, vertex_states=None):
		''' Return an Triangulation from a list of triples of edge labels.
		
		Let T be an ideal triangulaton of the punctured (oriented) surface S. Orient
		and edge e of T and assign an index i(e) in 0, ..., zeta-1. Now to each
		triangle t of T associate the triple j)t) := (j(e_1), j(e_2), j(e_3)) where:
			- e_1, e_2, e_3 are the edges of t, ordered acording to the orientation of t, and
			- j(e) = {  i(e) if the orientation of e agrees with that of t, and
					 { ~i(e) otherwise.
				Here ~x := -1 - x, the two's complement of x.
		
		We may describe T by the list [j(t) for t in T]. This function reconstructs
		T from such a list.
		
		edge_labels must be a list of triples of integers and each of
		0, ..., zeta-1, ~0, ..., ~(zeta-1) must occur exactly once.
		
		Two optional arguments allow the states of vertices to be specified. These
		are intended to only really be used by pickling methods.
		
		Firstly, if given, vertex_labels is a dictionary taking x to the label of the
		vertex opposite edge x. Vertices can be labelled by anything but using something
		like 0, ..., num_vertices-1 is sensible.
		
		Secondly, if given, vertex_states is a dict, list or tuple of Boolean flags such that
		the vertex labelled i is filled iff vertex_states[i] == True. '''
		
		assert(isinstance(edge_labels, (list, tuple)))
		assert(all(isinstance(labels, (list, tuple)) for labels in edge_labels))
		assert(all(len(labels) == 3 for labels in edge_labels))
		assert(vertex_labels is None or isinstance(vertex_labels, dict))
		assert(vertex_states is None or isinstance(vertex_states, (list, tuple, dict)))
		assert(len(edge_labels) > 0)
		
		zeta = len(edge_labels) * 3 // 2
		
		# Check that each of 0, ..., zeta-1, ~0, ..., ~(zeta-1) occurs exactly once.
		flattened = [label for labels in edge_labels for label in labels]
		for i in range(zeta):
			if i not in flattened:
				raise TypeError('Missing label %d' % i)
			if ~i not in flattened:
				raise TypeError('Missing label ~%d' % i)
		
		def finder(edge_label):
			''' Return the label and position of the given edge_label. '''
			
			for labels in edge_labels:
				for i in range(3):
					if labels[i] == edge_label:
						return (labels, i)
			raise flipper.FatalError('Label now missing.')
		
		def rotate(edge_label):
			''' Return the edge label one click round from edge_label. '''
			
			label, i = finder(edge_label)
			return label[(i+1) % 3]
		
		# Group the edges into vertex classes. Here two edges are in the same
		# class iff they have the same tail.
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
		
		# Build the vertex_labels if not given.
		if vertex_labels is None:
			vertex_labels = dict()
			# We will label the vertices 0, ..., num_vertices-1 in some order.
			for index, vertex_class in enumerate(vertex_classes):
				for edge_label in vertex_class:
					vertex_labels[rotate(edge_label)] = index
		
		# Sanity check vertex_labels now.
		# All edges should have a label.
		# Edges should have the same label iff they are opposite the same vertex.
		
		for edge_label in [i for i in range(zeta)] + [~i for i in range(zeta)]:
			if edge_label not in vertex_labels:
				raise TypeError('Missing vertex label for edge %d.' % edge_label)
		
		for vertex_class in vertex_classes:
			for edge_label in vertex_class:
				if vertex_labels[rotate(edge_label)] != vertex_labels[rotate(vertex_class[0])]:
					raise TypeError('Edges %d and %d should not have different vertex labels.' % (rotate(edge_label), rotate(vertex_class[0])))
		
		X = set(vertex_labels.values())
		# Check we have the right number of labels. This also checks that distinct vertex_classes have distinct labels.
		if len(X) != num_vertices:
			raise TypeError('There are %d vertices but %d vertex labels were given.' % (num_vertices, len(X)))
		
		# Build the vertex_states if not given.
		if vertex_states is None:
			vertex_states = {label: False for label in X}
		
		# Check we have a state for each vertex.
		for label in X:
			if label not in vertex_states:
				raise TypeError('No state given for vertex %s.' % label)
		
		# Build the vertices.
		vertices = [Vertex(label, filled=vertex_states[label]) for label in X]
		
		def vertexer(edge_label):
			''' Return the vertex at the tail of the given edge label. '''
			
			return vertices[vertex_labels[rotate(edge_label)]]
		
		# Build the Edges.
		edges_map = dict((i, Edge(vertexer(i), vertexer(~i), i)) for i in range(zeta))
		for i in range(zeta):
			edges_map[~i] = ~edges_map[i]
		
		triangles = [Triangle([edges_map[label] for label in labels]) for labels in edge_labels]
		
		return cls(triangles)
	
	@classmethod
	def from_string(cls, signature):
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
		
		try:
			values = [char_lookup[letter] for letter in signature]
		except KeyError:
			raise ValueError('Signature must be a string matching [a-zA-Z0-9+-]*')
		
		if values[0] < 63:
			num_chars = 1
			num_tri = values[0]
			start = 1
		else:
			num_chars = values[1]  # This must be > 1.
			num_tri = debase(values[1:num_chars])
			start = 1 + num_chars
		
		if num_chars == 0:
			raise ValueError('Signature must specify a character length > 0.')
			
		if num_tri == 0:
			raise ValueError('Signature must specify at least one triangle.')
		
		start2 = start + num_tri // 2  # Type sequence is [start:start2].
		start3 = start2 + num_chars * (1 + num_tri // 2)  # Destination sequence is [start2:start3].
		start4 = start3 + (1 + num_tri // 2)  # Permutation sequence is [start3:start4].
		if start4 != len(values):
			raise ValueError('Signature must specify permutations for each triangle.')
		
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
						if type_sequence[type_index] == 0:
							# We cannot yet handle triangulations with boundary.
							raise ValueError('Triangulations must be closed and so gluing must not be type 0.')
						elif type_sequence[type_index] == 1:
							target, gluing = num_tri_used, perm_lookup[0]
							triangle_reversed[target] = not triangle_reversed[i]
							
							num_tri_used += 1
						elif type_sequence[type_index] == 2:
							target, gluing = destination_sequence[destination_index], permutation_sequence[permutation_index]
							
							destination_index += 1
							permutation_index += 1
						else:
							raise ValueError('Each gluing must be type 0, 1 or 2.')
					except IndexError:
						raise ValueError('String does not correspond to a isomorphism signature.')
					type_index += 1
					
					edge_labels[i][j] = zeta
					edge_labels[target][gluing(j)] = ~zeta
					zeta += 1
		
		if num_tri_used != num_tri:
			raise ValueError('Unused triangles. String does not correspond to a isomorphism signature.')
		# Check there are no unglued edges.
		if not all(all(entry is not None for entry in row) for row in edge_labels):
			raise ValueError('Unused edges. String does not correspond to a isomorphism signature.')
		
		edge_labels = [edge_labels[i] if triangle_reversed[i] else edge_labels[i][::-1] for i in range(num_tri)]
		
		return cls.from_tuple(edge_labels)
	
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
	def package(self):
		''' Return a small amount of info that create_triagulation can use to reconstruct this triangulation. '''
		return (
			[t.labels for t in self],
			{corner.label: corner.vertex.label for corner in self.corners},
			{vertex.label: vertex.filled for vertex in self.vertices}
			)
	def __reduce__(self):
		# Triangulations are already pickleable but this results in a much smaller pickle.
		return (create_triangulation, (self.__class__,) + self.package())
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
	
	def iso_sig(self, preserve_orientation=False, skip=None, start_points=None):
		''' Return the isomorphism signature of this triangulation as described by Ben Burton.
		
		This is a string such that two triangulations have the same signature
		if and only if there is a homeomorphism taking one to the other.
		
		If skip is not None then it must be an iterable containing the labels
		of edges to treat as boundary. If preserve_orientation is True then
		this identifying homeomorphism must be orientation preserving.
		
		
		If start_points is not None then it must be an iterable containing pairs:
		(edge_lable, oriented) which specifies a corner to start with and whether
		to orient this corner to match the orientation of the triangle. This can
		be used to generate signatures relative to a fixed boundary by specify
		an edge on that boundary (and True) as the only starting point. '''
		
		best = ([INFTY], [INFTY], [INFTY])
		skip = set() if skip is None else set(skip)
		
		perm_inverse = flipper.kernel.permutation.PERM3_INVERSE
		perm_lookup = flipper.kernel.permutation.PERM3_LOOKUP
		transition_perm_lookup = flipper.kernel.permutation.TRANSITION_PERM3_LOOKUP
		perm_reverse = flipper.kernel.Permutation([0, 2, 1])
		
		# Set up the starting points.
		if start_points is None:
			# If we want to preserve the orientation on the surface we should only use the positive
			# permutations. So we should set the orientation to True.
			if preserve_orientation:
				start_points = [(label, True) for label in self.labels]
			else:
				start_points = [(label, orientation) for label in self.labels for orientation in [True, False]]
		
		for start_edge, start_orientation in start_points:
			start_corner = self.corner_lookup[start_edge]
			start_triangle = start_corner.triangle
			
			if not all(label in skip for label in start_triangle.labels):
				start_perm = flipper.kernel.permutation.cyclic_permutation(start_corner.side, 3).inverse()
				if not start_orientation:
					start_perm = start_perm * perm_reverse
				
				type_sequence = []
				target_sequence = []
				permutation_sequence = []
				
				good = True
				queue = Queue()
				queue.put(start_triangle)
				triangle_labels = {start_triangle: (0, start_perm)}
				num_triangles_seen = 1
				
				while not queue.empty() and good:
					triangle = queue.get()
					_, perm = triangle_labels[triangle]
					perm_inv = perm_inverse[perm]
					
					for j in range(3):
						side = perm_inv(j)
						target_corner = self.corner_of_edge(~triangle.labels[side])
						target_triangle = target_corner.triangle
						target_side = target_corner.side
						if ~triangle.labels[side] in skip:
							# This edge was really a boundary edge.
							type_sequence.append(0)
						elif target_triangle not in triangle_labels:
							target_perm = perm * transition_perm_lookup[(target_side, side)]
							triangle_labels[target_triangle] = (num_triangles_seen, target_perm)
							queue.put(target_triangle)
							num_triangles_seen += 1
							
							type_sequence.append(1)
							# We don't need to record the follow as they are implied.
							# target_sequence.append(len(queue))
							# permutation_sequence.append(perm_lookup[id_perm])
						else:
							triangle_index, _ = triangle_labels[triangle]
							target_index, target_perm = triangle_labels[target_triangle]
							k = target_perm(target_side)
							if target_index > triangle_index or (target_index == triangle_index and k > j):
								# We've not done this gluing yet.
								transition_perm = target_perm * transition_perm_lookup[(side, target_side)] * perm_inv
								
								type_sequence.append(2)
								target_sequence.append(target_index)
								permutation_sequence.append(perm_lookup[transition_perm])
						# We can give up early if we've built something bigger than best.
						if type_sequence > best[0]:
							good = False
							break
				
				if good:
					best = min((type_sequence, target_sequence, permutation_sequence), best)
		
		char = string.ascii_lowercase + string.ascii_uppercase + string.digits + '+-'
		
		type_sequence, target_sequence, permutation_sequence = best
		# Pad the type_sequence with 0's so that its length is a multiple of 3.
		type_sequence = type_sequence + [0] * (-len(type_sequence) % 3)
		char_type = ''.join(char[type_sequence[i] + 4 * type_sequence[i+1] + 16 * type_sequence[i+2]] for i in range(0, len(type_sequence), 3))
		char_perm = ''.join(char[perm] for perm in permutation_sequence)
		
		# Get the number of triangles that we encoutered.
		num_tri = type_sequence.count(1) + 1
		
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
		
		return [i for i in self.indices if self.is_flippable(i)]
	
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
		
		vertex_map = dict()
		for vertex in self.vertices:
			vertex_map[vertex] = flipper.kernel.Vertex(vertex.label, filled=vertex.filled)
		
		edge_map = dict()
		# Far away edges should go to an exact copy of themselves.
		for edge in self.positive_edges:
			edge_map[edge] = flipper.kernel.Edge(vertex_map[edge.source_vertex], vertex_map[edge.target_vertex], edge.label)
			edge_map[~edge] = ~edge_map[edge]
		
		a, b, c, d = self.square_about_edge(edge_label)
		# We need to label new_edge with norm(edge_label) so that self.flip_edge(i).flip_edge(~i) == self.
		new_edge = Edge(vertex_map[a.target_vertex], vertex_map[c.target_vertex], norm(edge_label))
		
		triangle_A2 = Triangle([new_edge, edge_map[d], edge_map[a]])
		triangle_B2 = Triangle([~new_edge, edge_map[b], edge_map[c]])
		
		triangles = [flipper.kernel.Triangle([edge_map[edge] for edge in triangle]) for triangle in self if edge_label not in triangle.labels and ~edge_label not in triangle]
		
		return Triangulation(triangles + [triangle_A2, triangle_B2])
	
	def relabel_edges(self, label_map):
		''' Return a new triangulation obtained by relabelling the edges according to label_map. '''
		
		if isinstance(label_map, (list, tuple)):
			label_map = dict(enumerate(label_map))
		else:
			label_map = dict(label_map)
		
		# Build any missing labels.
		for i in self.indices:
			if i in label_map and ~i in label_map:
				pass
			elif i not in label_map and ~i in label_map:
				label_map[i] = ~label_map[~i]
			elif i in label_map and ~i not in label_map:
				label_map[~i] = ~label_map[i]
			else:
				raise flipper.AssumptionError('Missing new label for %d.' % i)
		
		vertex_map = dict()
		for vertex in self.vertices:
			vertex_map[vertex] = flipper.kernel.Vertex(vertex.label, filled=vertex.filled)
		
		edge_map = dict()
		# Far away edges should go to an exact copy of themselves.
		for edge in self.positive_edges:
			edge_map[edge] = flipper.kernel.Edge(vertex_map[edge.source_vertex], vertex_map[edge.target_vertex], label_map[edge.label])
			edge_map[~edge] = ~edge_map[edge]
		
		triangles = [flipper.kernel.Triangle([edge_map[edge] for edge in triangle]) for triangle in self]
		return Triangulation(triangles)
	
	def tree_and_dual_tree(self, respect_fillings=False):
		''' Return a maximal tree in the 1--skeleton of this triangulation and a
		maximal tree in 1--skeleton of the dual of this triangulation.
		
		These are given as lists of Booleans signaling if each edge is in the tree.
		No edge is used in both the tree and the dual tree. Note that when this surface
		is disconnected this tree is actually a forest. '''
		
		components = self.components()
		
		tree = [False] * self.zeta
		vertices_used = dict((vertex, False) for vertex in self.vertices)
		# Get some starting vertices.
		if respect_fillings:
			for vertex in self.vertices:
				if not vertex.filled:
					vertices_used[vertex] = True
		else:
			for component in components:
				for edge_label in component:
					vertex = self.edge_lookup[edge_label].source_vertex
					if not vertex.filled:
						vertices_used[vertex] = True
						break
		
		if False:
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
		for component in components:
			faces_used[self.triangle_lookup[component[0]]] = True
		
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
	
	def find_isometry(self, other, label_map, respect_fillings=True):
		''' Return the isometry from this triangulation to other defined by label_map.
		
		label_map must be a dictionary mapping self.labels to other.labels. Labels may
		be omitted if they are determined by other given ones and these will be found
		automatically.
		
		Assumes (and checks) that such an isometry exists and is unique. '''
		
		assert(isinstance(label_map, dict))
		
		# Make a local copy as we may need to make a lot of changes.
		label_map = dict(label_map)
		
		source_orders = dict([(corner.label, len(corner_class)) for corner_class in self.corner_classes for corner in corner_class])
		target_orders = dict([(corner.label, len(corner_class)) for corner_class in other.corner_classes for corner in corner_class])
		# We do a depth first search extending the corner map across the triangulation.
		# This is a stack of labels that may still have consequences to check.
		to_process = [(edge_from_label, label_map[edge_from_label]) for edge_from_label in label_map]
		while to_process:
			from_label, to_label = to_process.pop()
			
			neighbours = [
				(~from_label, ~to_label),
				(self.corner_lookup[from_label].labels[1], other.corner_lookup[to_label].labels[1])
				]
			for new_from_label, new_to_label in neighbours:
				if new_from_label in label_map:
					# Check that this map is still consistent.
					if new_to_label != label_map[new_from_label]:
						raise flipper.AssumptionError('This label_map does not extend to an isometry.')
				else:
					# Extend the map.
					if source_orders[new_from_label] != target_orders[new_to_label] or \
						respect_fillings and self.vertex_lookup[new_from_label].filled != other.vertex_lookup[new_to_label].filled:
						raise flipper.AssumptionError('This label_map does not extend to an isometry.')
					label_map[new_from_label] = new_to_label
					to_process.append((new_from_label, new_to_label))
		
		if any(i not in label_map for i in self.labels):
			raise flipper.AssumptionError('This label_map cannot be extended to an isometry.')
		
		return flipper.kernel.Isometry(self, other, label_map)
	
	def isometries_to(self, other, respect_fillings=True):
		''' Return a list of all isometries from this triangulation to other. '''
		
		assert(isinstance(other, Triangulation))
		assert(isinstance(respect_fillings, bool))
		
		if self.zeta != other.zeta:
			return []
		
		# !?! This needs to be modified to work on disconnected surfaces.
		
		# Isometries are determined by where a single triangle is sent.
		# We take a corner of smallest degree.
		source_cc = min(self.corner_classes, key=len)
		source_corner = source_cc[0]
		# And find all the places where it could be sent so there are as few as possible to check.
		target_corners = [corner for target_cc in other.corner_classes for corner in target_cc if len(target_cc) == len(source_cc)]
		
		isometries = []
		for target_corner in target_corners:
			try:
				isometries.append(self.find_isometry(other, {source_corner.label: target_corner.label}, respect_fillings))
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
				e1, e2 = [edge_index for edge_index in range(short_lamination.zeta) if short_lamination(edge_index) > 0]
				
				a, b, c, d = triangulation.square_about_edge(e1)
				# If the curve is going vertically through the square then ...
				if short_lamination(a) == 1 and short_lamination(c) == 1:
					# swap the labels round so it goes horizontally.
					e1, e2 = e2, e1
					a, b, c, d = triangulation.square_about_edge(e1)
				elif short_lamination(b) == 1 and short_lamination(d) == 1:
					pass
				
				# Currently short_lamination.algebraic == [0, 0, ..., 0].
				# So we need to build a new short_lamination with the correct algebraic intersection numbers.
				geometric = short_lamination.geometric
				algebraic = [1 if i == e1 else -b.sign() if i == b.index else 0 for i in range(self.zeta)]
				
				new_short_lamination = flipper.kernel.Lamination(triangulation, geometric, algebraic)
				return conjugation.inverse()(new_short_lamination)
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
		
		for edge_index in self.indices:
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
		
		return flipper.kernel.Isometry(self, self, dict((i, i) for i in self.labels))
	
	def id_encoding(self):
		''' Return an encoding of the identity map on this triangulation. '''
		
		return self.id_isometry().encode()
	
	def encode_flip(self, edge_label):
		''' Return an encoding of the effect of flipping the given edge.
		
		The given edge must be flippable. '''
		
		assert(self.is_flippable(edge_label))
		
		new_triangulation = self.flip_edge(edge_label)
		
		return flipper.kernel.EdgeFlip(self, new_triangulation, edge_label).encode()
	
	def encode_spiral(self, edge_label, power):
		''' Return an encoding of the effect of spiraling about the given edge.
		
		The given edge must be spiralable. '''
		
		return flipper.kernel.Spiral(self, self, edge_label, power).encode()
	
	def encode_relabel_edges(self, label_map):
		''' Return an encoding of the effect of flipping the given edge. '''
		
		if isinstance(label_map, (list, tuple)):
			label_map = dict(enumerate(label_map))
		else:
			label_map = dict(label_map)
		
		# Build any missing labels.
		for i in self.indices:
			if i in label_map and ~i in label_map:
				pass
			elif i not in label_map and ~i in label_map:
				label_map[i] = ~label_map[~i]
			elif i in label_map and ~i not in label_map:
				label_map[~i] = ~label_map[i]
			else:
				raise flipper.AssumptionError('Missing new label for %d.' % i)
		
		new_triangulation = self.relabel_edges(label_map)
		
		return flipper.kernel.Isometry(self, new_triangulation, label_map).encode()
	
	def encode(self, sequence, _cache=None):
		''' Return the encoding given by sequence.
		
		This consists of EdgeFlips, Isometries and LinearTransformations. Furthermore there are
		several conventions that allow these to be specified by a smaller amount of information.
		 - An integer x represents EdgeFlip(..., edge_label=x)
		 - A dictionary which has i or ~i as a key (for every i) represents a relabelling.
		 - A dictionary which is missing i and ~i (for some i) represents an isometry back to this triangulation.
		 - None represents the identity isometry.
		
		This sequence is read in reverse in order respect composition. For example:
			self.encode([1, {1: ~2}, 2, 3, ~4])
		is the mapping class which: flips edge ~4, then 3, then 2, then relabels
		back to the starting triangulation via the isometry which takes 1 to ~2 and
		then finally flips edge 1. '''
		
		assert(isinstance(sequence, (list, tuple)))
		
		h = None
		for item in reversed(sequence):
			if isinstance(item, flipper.IntegerType):  # Flip.
				if h is None:
					h = self.encode_flip(item)
				else:
					h = h.target_triangulation.encode_flip(item) * h
			elif isinstance(item, dict):  # Isometry.
				if h is None:
					h = self.encode_relabel_edges(item)
				elif all(i in item or ~i in item for i in self.indices):
					h = h.target_triangulation.encode_relabel_edges(item) * h
				else:  # If some edges are missing then we assume that we must be mapping back to this triangulation.
					h = h.target_triangulation.find_isometry(self, item).encode() * h
			elif item is None:  # Identity isometry.
				if h is None:
					h = self.id_encoding()
				else:
					h = h.target_triangulation.id_encoding() * h
			elif isinstance(item, tuple) and len(item) == 2:  # Spiral
				if h is None:
					h = self.encode_spiral(item[0], item[1])
				else:
					h = h.target_triangulation.encode_spiral(item[0], item[1]) * h
			elif isinstance(item, flipper.kernel.Encoding):  # Encoding.
				if h is None:
					h = item
				else:
					h = item * h
			elif isinstance(item, flipper.kernel.Move):  # Move.
				if h is None:
					h = item.encode()
				else:
					h = item.encode() * h
			else:  # Other.
				if h is None:
					h = item.encode()
				else:
					h = item.encode() * h
		
		# Install a cache if we were given one.
		if _cache is not None: h._cache = _cache
		
		return h
	
	def encode_flips_and_close(self, edge_labels, edge_from_label, edge_to_label):
		''' DEPRECIATED: Return an encoding of the effect of flipping the given sequences of edges followed by an isometry.
		
		The isometry used is the one taking edge_from_label to edge_to_label.
		
		This function has been depreciated in favour of self.encode() and is equivalent to:
			self.encode([{edge_from_label: edge_to_label}] + list(reversed(edge_labels)))
		Note that edge_labels needs to be reversed in order to match the order of
		composition used in self.encode(). '''
		
		assert(isinstance(edge_labels, (list, tuple)))
		assert(all(isinstance(label, flipper.IntegerType) for label in edge_labels))
		assert(isinstance(edge_from_label, flipper.IntegerType))
		assert(isinstance(edge_to_label, flipper.IntegerType))
		
		E = self.encode(list(reversed(edge_labels)))
		return E.target_triangulation.find_isometry(self, {edge_from_label: edge_to_label}).encode() * E
	
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
			yield self.encode(list(reversed(sequence)) + list(reversed(prefix)))
	
	def all_mapping_classes(self, depth, prefix=None):
		''' Return all mapping classes that can be defined by at most the given number of flips followed by one isometry. '''
		
		assert(isinstance(depth, flipper.IntegerType))
		
		for encoding in self.all_encodings(depth, prefix):
			for isom in encoding.closing_isometries():
				yield isom.encode() * encoding
	
	def components(self):
		''' Return a list of pairs (connected component of self, embedding). '''
		
		remaining_labels = set(self.labels)
		components = []
		while remaining_labels:
			to_process = [remaining_labels.pop()]
			component = set(to_process)
			while to_process:
				label = to_process.pop()
				neighbours = [~label, self.corner_lookup[label].labels[1]]
				for new_label in neighbours:
					if new_label not in component:
						remaining_labels.remove(new_label)
						component.add(new_label)
						to_process.append(new_label)
			
			components.append(list(component))
		
		return components

def create_triangulation(cls, edge_labels, vertex_labels=None, vertex_states=None):
	''' A helper function for pickling. '''
	
	return cls.from_tuple(edge_labels, vertex_labels, vertex_states)

