
''' A module for representing laminations on Triangulations.

Provides one class: Lamination. '''

import flipper

class Lamination(object):
	''' This represents a lamination on an triangulation.
	
	It is given by a list of its geometric intersection numbers and a
	list of its algebraic intersection numbers with the (oriented) edges
	of underlying triangulation. Note that:
	     ^L
	     |
	-----|------> e
	     |
	has algebraic intersection +1.
	
	Users should use Triangulation.lamination() to create laminations with,
	when the lamination is a curve, its algebraic intersection computed
	automatically.
	
	If remove_peripheral is True then the Lamination is allowed to rescale
	its weights (by a factor of 2) in order to remove any peripheral
	components / satifsy the triangle inequalities. '''
	def __init__(self, triangulation, geometric, algebraic):
		assert(isinstance(triangulation, flipper.kernel.Triangulation))
		assert(all(isinstance(entry, object) for entry in geometric))
		assert(flipper.kernel.matrix.nonnegative(geometric))
		# We should check that algebraic satisfies reasonable relations too.
		
		self.triangulation = triangulation
		self.zeta = self.triangulation.zeta
		self.geometric = list(geometric)
		self.algebraic = algebraic
		
		self._cache = {}  # For caching hard to compute results.
	
	def copy(self):
		''' Return a copy of this lamination. '''
		
		return Lamination(self.triangulation, list(self.geometric), list(self.algebraic))
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return str(self.geometric)
	
	def projective_string(self):
		''' Return a string describing this lamination in PML. '''
		
		w = float(self.weight())
		return str([float(x) / w for x in self])
	
	def __iter__(self):
		return iter(self.geometric)
	
	def __getitem__(self, item):
		if isinstance(item, flipper.IntegerType):
			return self.geometric[flipper.kernel.norm(item)]
		elif isinstance(item, flipper.kernel.Edge):
			return self.geometric[item.index]
		else:
			return NotImplemented
	
	def __len__(self):
		return self.zeta
	
	def __eq__(self, other):
		return self.triangulation == other.triangulation and \
			all(v == w for v, w in zip(self, other)) and \
			all(v == w for v, w in zip(self.algebraic, other.algebraic))
	def __ne__(self, other):
		return not (self == other)
	
	def __hash__(self):
		# This should be done better.
		return hash(tuple(self.geometric))
	
	def __add__(self, other):
		if isinstance(other, Lamination):
			if other.triangulation != self.triangulation:
				raise ValueError('Laminations must be on the same triangulation to add them.')
			
			geometric = [x + y for x, y in zip(self, other)]
			algebraic = [x + y for x, y in zip(self.algebraic, other.algebraic)]
			return Lamination(self.triangulation, geometric, algebraic)
		else:
			if other == 0:  # So we can use sum.
				return self
			else:
				return NotImplemented
	def __radd__(self, other):
		return self + other
	
	def __mul__(self, other):
		geometric = [other * x for x in self]
		algebraic = [other * x for x in self.algebraic]
		return Lamination(self.triangulation, geometric, algebraic)
	def __rmul__(self, other):
		return self * other
	
	def is_empty(self):
		''' Return if this lamination is equal to the empty lamination. '''
		
		return not any(self)
	
	def isometries_to(self, other_lamination):
		''' Return a list of isometries taking this lamination to other_lamination. '''
		
		assert(isinstance(other_lamination, Lamination))
		
		# We used to just test other_lamination == isom.encode()(self) but this is much faster.
		return [isom for isom in self.triangulation.isometries_to(other_lamination.triangulation) if all(other_lamination[isom.index_map[i]] == self[i] for i in range(self.zeta))]
	
	def self_isometries(self):
		''' Returns a list of isometries taking this lamination to itself. '''
		
		return self.isometries_to(self)
	
	def all_projective_isometries(self, other_lamination):
		''' Return a list of isometries taking this lamination projectively to other_lamination. '''
		
		assert(isinstance(other_lamination, Lamination))
		
		return [isometry for isometry in self.triangulation.isometries_to(other_lamination.triangulation) if other_lamination.projectively_equal(isometry.encode()(self))]
	
	def projectively_equal(self, other_lamination):
		''' Return if this lamination is projectively equal to other_lamination.
		
		other_lamination must be on the same Triangulation as this lamination. '''
		
		assert(isinstance(other_lamination, Lamination))
		assert(other_lamination.triangulation == self.triangulation)
		
		# We can't do division so we have to cross multiply.
		return self * other_lamination.weight() == other_lamination * self.weight()
	
	def projective_hash(self):
		''' Return a hashable object that is invariant under isometries and rescaling. '''
		
		# Normalise so that it is invaiant under rescaling and sort to make it invariant under isometries.
		w = self.weight()
		return tuple(sorted([x.algebraic_hash_ratio(w) for x in self]))
	
	def weight(self):
		''' Return the sum of the geometric of this lamination. '''
		
		return sum(self.geometric)
	
	def is_multicurve(self):
		''' Return if this lamination is a multicurve. '''
		
		if self == self.triangulation.empty_lamination(): return False
		
		# This isn't quite right. We should allow NumberFieldElements too.
		if not all(isinstance(entry, flipper.IntegerType) for entry in self): return False
		
		for corner_class in self.triangulation.corner_classes:
			for corner in corner_class:
				weights = [self[edge] for edge in corner.triangle]
				dual_weights_doubled = [weights[1] + weights[2] - weights[0],
					weights[2] + weights[0] - weights[1],
					weights[0] + weights[1] - weights[2]]
				if any(dual_weight % 2 != 0 for dual_weight in dual_weights_doubled): return False
		
		return True
	
	def conjugate_short(self):
		''' Return an encoding which maps this lamination to a lamination with as little weight as possible.
		
		This lamination must be a multicurve. '''
		
		# Repeatedly flip to reduce the weight of this lamination as much as possible.
		# Let [v_i] := f(self), where f is the encoding returned by this method.
		#
		# Self is a curve and each component of S - self has a puncture if and only if:
		#  v_i \in {0, 1} and all-bar-two v_i's are 0.
		#
		# Self is a curve and a component of S - self has no punctures if and only if:
		#  v_i \in {0, 2} and [v_i // 2] does not correspond to a (multi)curve.
		#
		# Otherwise, self is a multicurve.
		
		assert(self.is_multicurve())
		
		lamination = self.copy()
		best_conjugation = conjugation = lamination.triangulation.id_encoding()
		
		time_since_last_weight_loss = 0
		old_weight = lamination.weight()
		# If we ever fail to make progress more than once then the curve is as short as it's going to get.
		while time_since_last_weight_loss < 2 and old_weight > 2:
			# Find the edge which decreases our weight the most.
			# If none exist then it doesn't matter which edge we flip, so long as it meets the curve.
			edge_index = min([i for i in lamination.triangulation.flippable_edges() if lamination[i] > 0], key=lamination.weight_difference_flip_edge)
			
			forwards = lamination.triangulation.encode_flip(edge_index)
			conjugation = forwards * conjugation
			lamination = forwards(lamination)
			new_weight = lamination.weight()
			
			if new_weight < old_weight:
				time_since_last_weight_loss = 0
				old_weight = new_weight
				best_conjugation = conjugation
			else:
				time_since_last_weight_loss += 1
		
		return best_conjugation
	
	def is_curve(self):
		''' Return if this lamination is a curve. '''
		
		if not self.is_multicurve(): return False
		
		conjugation = self.conjugate_short()
		short_lamination = conjugation(self)
		
		if short_lamination.weight() == 2: return True
		
		# See the conditions on conjugate_short as to why this works.
		if any(weight not in [0, 2] for weight in short_lamination): return False
		
		# If we have a longer curve then all vertices must be on one side of it.
		# So if we collapse the edges with weight 0 we must end up with a
		# one vertex triangulation.
		triangulation = short_lamination.triangulation
		vertex_numbers = dict(zip(list(triangulation.vertices), range(len(triangulation.vertices))))
		for edge_index in range(triangulation.zeta):
			if self[edge_index] == 0:
				c1, c2 = triangulation.vertices_of_edge(edge_index)
				a, b = vertex_numbers[c1], vertex_numbers[c2]
				if a != b:
					x, y = max(a, b), min(a, b)
					for c in vertex_numbers:
						if vertex_numbers[c] == x: vertex_numbers[c] = y
		
		# If any corner class is numbered > 0 then we don't have a one vertex triangulation.
		if any(vertex_numbers.values()): return False
		
		# So either we have a single curve or we have a multicurve with two parallel components.
		# We can test for the latter by seeing if the halved curve has the correct weight.
		if triangulation.lamination([v // 2 for v in short_lamination]).weight() == short_lamination.weight() // 2:
			return False
		
		return True
	
	def is_twistable(self):
		''' Return if this lamination is a twistable curve. '''
		
		# This is based off of self.encode_twist(). See the documentation there as to why this works.
		if not self.is_curve(): return False
		
		conjugation = self.conjugate_short()
		short_lamination = conjugation(self)
		
		return short_lamination.weight() == 2
	
	def is_halftwistable(self):
		''' Return if this lamination is a half twistable curve. '''
		
		# This is based off of self.encode_halftwist(). See the documentation there as to why this works.
		if not self.is_twistable(): return False
		
		conjugation = self.conjugate_short()
		short_lamination = conjugation(self)
		triangulation = short_lamination.triangulation
		
		e1, e2 = [edge_index for edge_index in range(short_lamination.zeta) if short_lamination[edge_index] > 0]
		
		a, b, c, d = triangulation.square_about_edge(e1)
		if short_lamination[a] == 1 and short_lamination[c] == 1:
			e1, e2 = e2, e1
			a, b, c, d = triangulation.square_about_edge(e1)
		elif short_lamination[b] == 1 and short_lamination[d] == 1:
			pass
		
		_, _, z, w = triangulation.square_about_edge(a.label)
		_, _, x, y = triangulation.square_about_edge(c.label)
		
		return z.index == w.index or x.index == y.index
	
	def weight_difference_flip_edge(self, edge_index):
		''' Return how much the weight would change by if this flip was done. '''
		
		a, b, c, d = self.triangulation.square_about_edge(edge_index)
		return max(self[a] + self[c], self[b] + self[d]) - 2 * self[edge_index]
	
	def stratum(self):
		''' Return a dictionary mapping each vertex of the underlying triangulation to the number of stratum exiting it.
		
		This is the number of bipods incident to the vertex. '''
		
		triangulation = self.triangulation
		return dict((vertex, sum(1 for corner in triangulation.corner_class_of_vertex(vertex) if self.is_bipod(corner))) for vertex in triangulation.vertices)
	
	def is_bipod(self, corner):
		''' Return if the lamination looks like a bipod with respect to the given corner. '''
		
		return self[corner.indices[1]] + self[corner.indices[2]] == self[corner.indices[0]]
	
	def is_tripod(self, triangle):
		''' Return if the lamination looks like a tripod in this triangle. '''
		
		weights = [self[edge] for edge in triangle]
		dual_weights_doubled = [weights[1] + weights[2] - weights[0],
					weights[2] + weights[0] - weights[1],
					weights[0] + weights[1] - weights[2]]
		return all(dual_weight > 0 for dual_weight in dual_weights_doubled)
	
	def tripod_regions(self):
		''' Return a list of all triangles in which this lamination looks like a tripod. '''
		
		return [triangle for triangle in self.triangulation if self.is_tripod(triangle)]
	
	def puncture_tripods(self):
		''' Return the encoding corresponding to puncturing the tripods of this lamination. '''
		
		# We label real punctures 0, 1, ... and fake ones -1, -2, ... .
		
		to_puncture = self.tripod_regions()
		geometric = 2 * flipper.kernel.id_matrix(self.zeta)
		algebraic = flipper.kernel.id_matrix(self.zeta)
		
		zeta = self.zeta
		triangles = []
		num_new_vertices = 0
		for triangle in self.triangulation:
			a, b, c = triangle.labels
			A, B, C = triangle.indices
			if triangle in to_puncture:
				x, y, z = triangle.vertices
				num_new_vertices += 1
				w = flipper.kernel.Vertex(-num_new_vertices)
				p, q, r = triangle.edges
				s, t, u = [flipper.kernel.Edge(w, x, zeta), flipper.kernel.Edge(w, y, zeta+1), flipper.kernel.Edge(w, z, zeta+2)]
				triangles.append(flipper.kernel.Triangle([p, ~u, t]))
				triangles.append(flipper.kernel.Triangle([q, ~s, u]))
				triangles.append(flipper.kernel.Triangle([r, ~t, s]))
				
				geometric = geometric.join(flipper.kernel.zero_matrix(self.zeta, 1).tweak([(0, B), (0, C)], [(0, A)]))
				geometric = geometric.join(flipper.kernel.zero_matrix(self.zeta, 1).tweak([(0, C), (0, A)], [(0, B)]))
				geometric = geometric.join(flipper.kernel.zero_matrix(self.zeta, 1).tweak([(0, A), (0, B)], [(0, C)]))
				
				algebraic = algebraic.join(flipper.kernel.zero_matrix(self.zeta, 1))
				if c == C:
					algebraic = algebraic.join(flipper.kernel.zero_matrix(self.zeta, 1).tweak([(0, C)], []))
				else:
					algebraic = algebraic.join(flipper.kernel.zero_matrix(self.zeta, 1).tweak([], [(0, C)]))
				if b != B:
					algebraic = algebraic.join(flipper.kernel.zero_matrix(self.zeta, 1).tweak([(0, B)], []))
				else:
					algebraic = algebraic.join(flipper.kernel.zero_matrix(self.zeta, 1).tweak([], [(0, B)]))
				
				zeta += 3
			else:
				triangles.append(triangle)
		
		l = flipper.kernel.LFunction(algebraic, flipper.kernel.zero_matrix(zeta, self.zeta))
		partial = flipper.kernel.PartialFunction(geometric)
		pl = flipper.kernel.PLFunction([flipper.kernel.BasicPLFunction([partial])])
		
		T = flipper.kernel.Triangulation(triangles)
		return flipper.kernel.Encoding(self.triangulation, T, pl, l)
	
	def collapse_trivial_weight(self, edge_index):
		''' Return this lamination on the triangulation obtained by collapsing edge edge_index
		and an encoding which is at least algebraically correct.
		
		Assumes (and checks) that:
			- self.triangulation is not S_{0,3},
			- the given edge does not connect between two real vertices, (with non-negative label), and
			- edge_index is the only edge of weight 0. '''
		
		if self[edge_index] != 0:
			raise flipper.AssumptionError('Lamination does not have weight 0 on edge to collapse.')
		
		# This relies on knowing how squares are returned.
		a, b, c, d = self.triangulation.square_about_edge(edge_index)  # Get the square about it.
		e = self.triangulation.edge_lookup[edge_index]
		
		# We'll first deal with some bad cases that con occur when some of the sides of the square are in fact the same.
		if a == ~b or c == ~d:
			# This implies that self[a] (respectively self[c]) == 0.
			raise flipper.AssumptionError('Additional weightless edge.')
		
		# There is at most one duplicated pair.
		if a == ~d and b == ~c:
			# This implies that the underlying surface is S_{0,3}.
			raise flipper.AssumptionError('Underlying surface is S_{0,3}.')
		
		if a == ~c and a == ~d:
			# This implies the underlying surface is S_{1,1}. As there is
			# only one vertex, both endpoints of this edge must be labelled 0.
			raise flipper.AssumptionError('Lamination is not filling.')
		
		# Now the only remaining possibilities are:
		#   a == ~c, b == ~d, a == ~d, b == ~c, or no relations.
		
		# We'll replace the labels on the corner class with lower labels with the label from the higher.
		# This ensures that any non-negative vertex survives.
		bad_vertex, good_vertex = [e.source_vertex, e.target_vertex] if e.source_vertex.label < 0 else [e.target_vertex, e.source_vertex]
		
		# We'll first compute the vertex labels. This way we can check if our assumption is False early and so save some work.
		# If we collapse together two real vertices (or a vertex with itself) then there is a loop
		# dijoint to this lamination and so this is not filling.
		if (good_vertex.label >= 0 and bad_vertex.label >= 0) or good_vertex == bad_vertex:
			raise flipper.AssumptionError('Lamination is not filling.')
		
		# Figure out how the vertices should be mapped.
		vertex_map = dict()
		for vertex in self.triangulation.vertices:
			if vertex != good_vertex and vertex != bad_vertex:
				vertex_map[vertex] = flipper.kernel.Vertex(vertex.label)
		vertex_map[good_vertex] = flipper.kernel.Vertex(good_vertex.label)
		vertex_map[bad_vertex] = vertex_map[good_vertex]
		
		# Now figure out how the edges should be mapped.
		edge_count = 0
		edge_map = dict()
		for edge in self.triangulation.edges:
			if edge.is_positive() and edge not in [a, b, c, d, e, ~a, ~b, ~c, ~d, ~e]:
				edge_map[edge] = flipper.kernel.Edge(vertex_map[edge.source_vertex], vertex_map[edge.target_vertex], edge_count)
				edge_map[~edge] = ~edge_map[edge]
				edge_count += 1
		
		if a == ~c:  # Collapsing an annulus.
			edge_map[~b] = flipper.kernel.Edge(vertex_map[b.target_vertex], vertex_map[b.source_vertex], edge_count)
			edge_map[~d] = ~edge_map[~b]
			edge_count += 1
		elif b == ~d:  # An annulus in the other direction.
			edge_map[~a] = flipper.kernel.Edge(vertex_map[a.target_vertex], vertex_map[a.source_vertex], edge_count)
			edge_map[~c] = ~edge_map[~a]
			edge_count += 1
		elif a == ~d:  # Collapsing a bigon.
			edge_map[~b] = flipper.kernel.Edge(vertex_map[b.target_vertex], vertex_map[b.source_vertex], edge_count)
			edge_map[~c] = ~edge_map[~b]
			edge_count += 1
		elif b == ~c:  # A bigon in the other direction.
			edge_map[~a] = flipper.kernel.Edge(vertex_map[a.target_vertex], vertex_map[a.source_vertex], edge_count)
			edge_map[~d] = ~edge_map[~a]
			edge_count += 1
		else:  # No identification.
			edge_map[~a] = flipper.kernel.Edge(vertex_map[a.target_vertex], vertex_map[a.source_vertex], edge_count)
			edge_map[~b] = ~edge_map[~a]
			edge_count += 1
			edge_map[~c] = flipper.kernel.Edge(vertex_map[c.target_vertex], vertex_map[c.source_vertex], edge_count)
			edge_map[~d] = ~edge_map[~c]
			edge_count += 1
		
		triples = [[edge_map[edge] for edge in triangle] for triangle in self.triangulation if e not in triangle and ~e not in triangle]
		new_triangles = [flipper.kernel.Triangle(triple) for triple in triples]
		T = flipper.kernel.Triangulation(new_triangles)
		
		bad_edges = [a, b, c, d, e, ~e]  # These are the edges for which edge_map is not defined.
		geometric = [[self[edge] for edge in self.triangulation.edges if edge not in bad_edges and edge_map[edge].index == i][0] for i in range(edge_count)]
		algebraic = [0] * edge_count
		lamination = Lamination(T, geometric, algebraic)
		
		# Now compute the encoding describing this. We will only bother to get the algebraic part correct
		# as the geometric part is not a PL function with only finitely many pieces.
		matrix = flipper.kernel.id_matrix(self.zeta)
		for edge in self.triangulation.edges:
			if edge != e and edge != ~e and edge.source_vertex == bad_vertex and edge.target_vertex != bad_vertex:
				matrix = matrix.elementary(edge.index, edge_index, +1 if edge.is_positive() != (e.source_vertex == bad_vertex) else -1)
		
		matrix2 = flipper.kernel.zero_matrix(self.zeta, edge_count)
		for edge in self.triangulation.edges:
			if edge not in bad_edges:
				target_edge = edge_map[edge]
				if not any(matrix2[target_edge.index]):
					matrix2[target_edge.index][edge.index] = +1 if edge.is_positive() == target_edge.is_positive() else -1
		
		algebraic_matrix = matrix2 * matrix
		algebraic_action = flipper.kernel.LFunction(algebraic_matrix, flipper.kernel.zero_matrix(edge_count, self.zeta))
		geometric_action = flipper.kernel.zero_pl_function(self.zeta, edge_count)
		
		encoding = flipper.kernel.Encoding(self.triangulation, T, geometric_action, algebraic_action)
		
		return lamination, encoding
	
	def splitting_sequences_uncached(self, target_dilatation=None):
		''' Return a list of splitting sequence associated to this lamination.
		
		Assumes (and checks) that this lamination is filling.
		
		This is the flips the edges of maximal weight until you reach a
		projectively periodic sequence (with required dilatation if given).
		
		This requires the entries of self.geometric to be NumberFieldElements
		(over the same NumberField) or AlgebraicNumbers. '''
		
		# Check if the lamination is obviously non-filling.
		if any(v == 0 for v in self):
			raise flipper.AssumptionError('Lamination is not filling.')
		
		if all(isinstance(v, flipper.IntegerType) for v in self):
			raise flipper.AssumptionError('Lamination is not filling.')
		
		# Puncture all the triangles where the lamination is a tripod.
		E = self.puncture_tripods()
		lamination = E(self)
		
		encodings = [(None, E)]
		laminations = [self, lamination]
		num_isometries = [len(lamination.self_isometries())]
		seen = {lamination.projective_hash(): [1]}
		# We start indexing at 1 to help keep the indices aligned.
		# We don't want to include self as the first lamination just incase
		# it is already on the axis and the puncture_tripods does nothing,
		# misaligning the indices.
		while True:
			# Find the index of the largest entry.
			edge_index = max(range(lamination.zeta), key=lambda i: lamination[i])
			E = lamination.triangulation.encode_flip(edge_index)
			encodings.append((edge_index, E))
			lamination = E(lamination)
			laminations.append(lamination)
			num_isometries.append(len(lamination.self_isometries()))
			
			# Check if we have created any edges of weight 0.
			# It is enough to just check edge_index.
			if lamination[edge_index] == 0:
				try:
					# If this fails it's because the lamination isn't filling.
					lamination, E2 = lamination.collapse_trivial_weight(edge_index)
					# We cannot provide the encoding or flip so we'll just stick in a None.
					encodings.append((None, E2))
					laminations.append(lamination)
					num_isometries.append(len(lamination.self_isometries()))
				except flipper.AssumptionError:
					raise flipper.AssumptionError('Lamination is not filling.')
			
			# Check if it (projectively) matches a lamination we've already seen.
			target = lamination.projective_hash()
			if target in seen:
				for index in seen[target]:
					old_lamination = laminations[index]
					isometries = lamination.all_projective_isometries(old_lamination)
					if len(isometries) > 0:
						if target_dilatation is None or old_lamination.weight() == target_dilatation * lamination.weight():
							# We might need to keep going a little bit more, we need to stop at the point with maximal symmetry.
							if num_isometries[-1] == max(num_isometries[index:]):
								return [flipper.kernel.SplittingSequence(laminations, encodings, isom, index) for isom in isometries]
						elif target_dilatation is not None and old_lamination.weight() > target_dilatation * lamination.weight():
							assert(False)
				seen[target].append(len(laminations)-1)
			else:
				seen[target] = [len(laminations)-1]
	
	def splitting_sequences(self, target_dilatation=None):
		''' A version of self.splitting_sequences_uncached with caching. '''
		
		if 'splitting_sequences' not in self._cache:
			self._cache['splitting_sequences'] = {}
		
		if target_dilatation not in self._cache['splitting_sequences']:
			try:
				self._cache['splitting_sequences'][target_dilatation] = self.splitting_sequences_uncached(target_dilatation)
			except (flipper.AssumptionError) as error:
				self._cache['splitting_sequences'][target_dilatation] = error
		
		if isinstance(self._cache['splitting_sequences'][target_dilatation], Exception):
			raise self._cache['splitting_sequences'][target_dilatation]
		else:
			return self._cache['splitting_sequences'][target_dilatation]
	
	def encode_twist(self, k=1):
		''' Return an Encoding of a left Dehn twist about this lamination raised to the power k.
		
		This lamination must be a twistable curve. '''
		
		assert(self.is_twistable())
		
		if k == 0: return self.triangulation.id_encoding()
		
		conjugation = self.conjugate_short()
		short_lamination = conjugation(self)
		
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
		
		# We now have:
		# #<----------#
		# |     a    ^^
		# |         / |
		# |---->------|
		# |       /   |
		# |b    e/   d|
		# |     /     |
		# |    /      |
		# |   /       |
		# |  /        |
		# | /         |
		# V/    c     |
		# #---------->#
		# And e.index = e1 and b.index = d.index = e2.
		
		T = triangulation.encode_flips_and_close([e1], a, a)
		
		return conjugation.inverse() * T**k * conjugation
	
	def encode_halftwist(self, k=1):
		''' Return an Encoding of a left half twist about this lamination raised to the power k.
		
		This lamination must be a half-twistable curve. '''
		
		assert(self.is_halftwistable())
		
		# This first section is the same as in self.encode_flip.
		if k == 0: return self.triangulation.id_encoding()
		
		conjugation = self.conjugate_short()
		short_lamination = conjugation(self)
		
		triangulation = short_lamination.triangulation
		e1, e2 = [edge_index for edge_index in range(short_lamination.zeta) if short_lamination[edge_index] > 0]
		
		a, b, c, d = triangulation.square_about_edge(e1)
		# If the curve is going vertically through the square then ...
		if short_lamination[a] == 1 and short_lamination[c] == 1:
			# swap the labels round so it goes horizontally.
			e1, e2 = e2, e1
			a, b, c, d = triangulation.square_about_edge(e1)
		elif short_lamination[b] == 1 and short_lamination[d] == 1:
			pass
		
		# Get some more edges.
		_, _, z, w = triangulation.square_about_edge(a.label)
		_, _, x, y = triangulation.square_about_edge(c.label)
		
		# But now we have to go one further and worry about a, b, c, d Vs. c, d, a, b.
		# We want it so that x == ~y.
		if z.index == w.index:
			a, b, c, d = c, d, a, b
			w, x, y, z = y, z, w, x
		
		# So we now have:
		#       #
		#      / ^
		#     /   \
		#    /w   z\
		#   /       \
		#  V         \
		# #<----------#
		# |     a    ^^
		# |         / |
		# |---->------|
		# |       /   |
		# |b    e/   d|
		# |     /     |
		# |    /      |
		# |   /       |
		# |  /        |
		# | /         |
		# V/    c     |
		# #---------->#
		#  \         ^
		#   \       /
		#    \x   y/
		#     \   /
		#      V /
		#       #
		# Where e.index = e1 and b.index = d.index = e2,
		# and additionally x.index = y.index.
		
		T = triangulation.encode_flips_and_close([c.index, e1, e2], a, a)
		
		return conjugation.inverse() * T**k * conjugation
	
	def geometric_intersection(self, lamination):
		''' Return the geometric intersection number between this lamination and the given one.
		
		Assumes (and checks) that this is a twistable lamination. '''
		
		assert(isinstance(lamination, Lamination))
		assert(lamination.triangulation == self.triangulation)
		
		if not self.is_twistable():
			raise flipper.AssumptionError('Can only compute geometric intersection number between a twistable curve and a lamination.')
		
		conjugator = self.conjugate_short()
		
		short = conjugator(self)
		short_lamination = conjugator(lamination)
		
		triangulation = short.triangulation
		e1, e2 = [edge_index for edge_index in range(triangulation.zeta) if short[edge_index] > 0]
		# We might need to swap these edge indices so we have a good frame of reference.
		if triangulation.corner_of_edge(e1).indices[2] != e2: e1, e2 = e2, e1
		
		a, b, c, d = triangulation.square_about_edge(e1)
		e = e1
		
		x = (short_lamination[a] + short_lamination[b] - short_lamination[e]) // 2
		y = (short_lamination[b] + short_lamination[e] - short_lamination[a]) // 2
		z = (short_lamination[e] + short_lamination[a] - short_lamination[b]) // 2
		x2 = (short_lamination[c] + short_lamination[d] - short_lamination[e]) // 2
		y2 = (short_lamination[d] + short_lamination[e] - short_lamination[c]) // 2
		z2 = (short_lamination[e] + short_lamination[c] - short_lamination[d]) // 2
		
		intersection_number = short_lamination[a] - 2 * min(x, y2, z)
		assert(intersection_number == short_lamination[c] - 2 * min(x2, y, z2))
		
		return intersection_number
	
	def is_homologous_to(self, lamination, relative_boundary=False):
		''' Return if this lamination is homologous to the given one.
		
		The the homology class is computed relative to the fake punctures, unless relative_boundary
		is set to True in which case it is done relative to all vertices.
		
		This lamination and the given one must be defined on the same triangulation. '''
		
		assert(isinstance(lamination, Lamination))
		assert(self.triangulation == lamination.triangulation)
		
		matrix = flipper.kernel.id_matrix(self.zeta)
		
		triangulation = self.triangulation
		tree, dual_tree = triangulation.tree_and_dual_tree(not relative_boundary)
		vertices_used = dict((vertex, False) for vertex in triangulation.vertices)
		# Get some starting vertices.
		for vertex in triangulation.vertices:
			if vertex.label >= 0:
				vertices_used[vertex] = True
				if relative_boundary:
					# Stop as soon as we've marked one.
					break
		
		while True:
			for edge in triangulation.edges:
				if tree[edge.index]:
					source, target = edge.source_vertex, edge.target_vertex
					if vertices_used[source] and not vertices_used[target]:
						vertices_used[target] = True
						for edge2 in triangulation.edges:
							if edge2 != edge and edge2 != ~edge and edge2.source_vertex == target and edge2.target_vertex != target:
								matrix = matrix.elementary(edge2.index, edge.index, +1 if edge2.is_positive() == edge.is_positive() else -1)
						break
			else:
				break  # If there are no more to add then we've dealt with every edge.
		
		M = flipper.kernel.Matrix([matrix[i] for i in range(self.zeta) if not tree[i] and not dual_tree[i]])
		return M(self.algebraic) == M(lamination.algebraic)

