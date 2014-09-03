
import flipper

class Lamination(object):
	''' This represents a lamination on an abstract triangluation. You shouldn't create laminations directly
	but instead should use AbstractTriangulation.lamination() which creates a lamination on that triangulation.
	If remove_peripheral is True then the Lamination is allowed to rescale its weights (by a factor of 2) in order
	to remove any peripheral components. '''
	def __init__(self, triangulation, vector, remove_peripheral=False):
		assert(isinstance(triangulation, flipper.kernel.AbstractTriangulation))
		assert(all(isinstance(entry, object) for entry in vector))
		assert(isinstance(remove_peripheral, bool))
		assert(flipper.kernel.matrix.nonnegative(vector))
		
		self.triangulation = triangulation
		self.zeta = self.triangulation.zeta
		if remove_peripheral:
			# Compute how much peripheral component there is on each corner class.
			peripheral = dict((vertex, min(vector[corner.indices[1]] + vector[corner.indices[2]] - vector[corner.index] for corner in self.triangulation.corner_class_of_vertex(vertex))) for vertex in self.triangulation.vertices)
			# If there is any remove it.
			if any(peripheral.values()):
				vector = [2*vector[i] - sum(peripheral[x] for x in self.triangulation.vertices_of_edge(i)) for i in range(self.zeta)]
		self.vector = list(vector)
	
	def copy(self):
		return Lamination(self.triangulation, list(self.vector))
	
	def __repr__(self):
		return str(self.vector)
	
	def projective_string(self):
		w = float(self.weight())
		return str([float(x) / w for x in self])
	
	def __iter__(self):
		return iter(self.vector)
	
	def __getitem__(self, item):
		if isinstance(item, flipper.Integer_Type):
			return self.vector[flipper.kernel.norm(item)]
		elif isinstance(item, flipper.kernel.AbstractEdge):
			return self.vector[item.index]
		else:
			return NotImplemented
	
	def __len__(self):
		return self.zeta
	
	def __eq__(self, other):
		return self.triangulation == other.triangulation and all(bool(v == w) for v, w in zip(self, other))
	def __ne__(self, other):
		return not self == other
	
	def __hash__(self):
		# This should be done better.
		return hash(tuple(self.vector))
	
	def __add__(self, other):
		if isinstance(other, Lamination):
			if other.triangulation == self.triangulation:
				return self.triangulation.lamination([x + y for x, y in zip(self, other)], remove_peripheral=True)
			else:
				raise ValueError('Laminations must be on the same triangulation to add them.')
		else:
			return self.triangulation.lamination([x + other for x in self])
	def __radd__(self, other):
		return self + other
	
	def __mul__(self, other):
		return self.triangulation.lamination([other * x for x in self])
	def __rmul__(self, other):
		return self * other
	
	def is_empty(self):
		return not any(self)
	
	def all_isometries(self, other):
		assert(isinstance(other, Lamination))
		return [isometry for isometry in self.triangulation.all_isometries(other.triangulation) if other == isometry.encode()(self)]
	
	def all_projective_isometries(self, other):
		assert(isinstance(other, Lamination))
		return [isometry for isometry in self.triangulation.all_isometries(other.triangulation) if other.projectively_equal(isometry.encode()(self))]
	
	def projectively_equal(self, other):
		assert(isinstance(other, Lamination))
		# We can't do division so we have to cross multiply.
		return self * other.weight() == other * self.weight()
	
	def projective_hash(self):
		# We use this function to hash the number down. It NEEDS be (projectively) invariant under isometries of the triangulation
		# so we achieve this by sorting the hash values.
		w = self.weight()
		return tuple(sorted([x.algebraic_hash_ratio(w) for x in self]))
	
	def weight(self):
		return sum(self.vector)
	
	def is_multicurve(self):
		''' Decides if this lamination is a multicurve. '''
		if self == self.triangulation.empty_lamination(): return False
		
		# This isn't quite right. We should allow NumberFieldElements too.
		if not all(isinstance(entry, flipper.Integer_Type) for entry in self): return False
		
		for corner_class in self.triangulation.corner_classes:
			for corner in corner_class:
				weights = [self[edge] for edge in corner.triangle]
				dual_weights_doubled = [weights[1] + weights[2] - weights[0],
					weights[2] + weights[0] - weights[1],
					weights[0] + weights[1] - weights[2]]
				if any(dual_weight % 2 != 0 for dual_weight in dual_weights_doubled): return False
		
		return True
	
	def conjugate_short(self):
		# Repeatedly flip to reduce the weight of this lamination as much as
		# possible. Assumes that self is a multicurve.
		#
		# If this lamination is a curve then this will conjugate it to
		# a curve which meets each edge either:
		#	once (in which case it meets exactly 2 of them), or
		#	0 or 2 times.
		# The latter case happens if and only if a component of S - \gamma has no punctures.
		
		if not self.is_multicurve():
			raise flipper.AssumptionError('Can only conjugate multicurves to be short.')
		
		lamination = self.copy()
		best_conjugation = conjugation = lamination.triangulation.id_encoding()
		
		time_since_last_weight_loss = 0
		old_weight = lamination.weight()
		# If we ever fail to make progress more than once then the curve is as short as it's going to get.
		while time_since_last_weight_loss < 2:
			# Find the edge which decreases our weight the most.
			# If none exist then it doesn't matter which edge we flip, so long as it meets the curve.
			# By Lee Mosher's work there is a complexity that we will reduce to by doing this.
			edge_index = min([i for i in range(lamination.zeta) if lamination[i] > 0 and lamination.triangulation.is_flippable(i)], key=lamination.weight_difference_flip_edge)
			
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
		''' Decides if this lamination is a curve. '''
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
		# We can test for the latter by seeing if the halved curve is still a multicurve.
		if triangulation.lamination([v // 2 for v in short_lamination]).is_multicurve():
			return False
		
		return True
	
	def is_twistable(self):
		''' Decides if this lamination is a twistable. '''
		# This is based off of self.encode_twist(). See the documentation there as to why this works.
		if not self.is_curve(): return False
		
		conjugation = self.conjugate_short()
		short_lamination = conjugation(self)
		
		return short_lamination.weight() == 2
	
	def is_halftwistable(self):
		''' Decides if this lamination is a half twistable. '''
		# This is based off of self.encode_halftwist(). See the documentation there as to why this works.
		if not self.is_twistable(): return False
		
		conjugation = self.conjugate_short()
		short_lamination = conjugation(self)
		
		e1, e2 = [edge_index for edge_index in range(short_lamination.zeta) if short_lamination[edge_index] > 0]
		x, y = [edge_indices for edge_indices in short_lamination.triangulation.find_indicies_of_square_about_edge(e1) if edge_indices != e2]
		for triangle in short_lamination.triangulation:
			if (x in triangle or y in triangle) and len(set(triangle)) == 2:
				return True
		
		return False
	
	def weight_difference_flip_edge(self, edge_index):
		''' Returns how much the weight would change by if this flip was done. '''
		a, b, c, d = self.triangulation.find_indicies_of_square_about_edge(edge_index)
		return max(self[a] + self[c], self[b] + self[d]) - 2 * self[edge_index]
	
	def puncture_stratum_orders(self):
		''' Returns a list of the number of stratum exiting each cusp. This is the
		number of bipods incident to the cusp. '''
		return [sum(1 for corner in vertex if self.is_bipod(corner)) for vertex in self.triangulation.vertices]
	
	def is_bipod(self, corner):
		''' Returns if the lamination looks like a bipod with respect to this corner. '''
		return self[corner.indices[1]] + self[corner.indices[2]] == self[corner.indices[0]]
	
	def open_bipod(self, corner):
		''' Returns an encoding flipping the edge opposite this corner along with a new corner class. '''
		assert(self.is_bipod(corner))
		assert(self.triangulation.is_flippable(corner.label))
		# #-----------#     #-----------#
		# |c    l    /|     |\C2       A|
		# |         / |     | \         |
		# |        /  |     |C1\        |
		# |       /   |     |   \       |
		# |r    e/    | --> |    \e'    |
		# |     /     |     |     \     |
		# |    /      |     |      \    |
		# |   /       |     |       \   |
		# |  /        |     |        \  |
		# | /         |     |         \ |
		# |/          |     |B         \|
		# #-----------#     #-----------#
		
		edge = corner.label
		left, right = corner.labels[1], corner.labels[2]
		encoding = self.triangulation.encode_flip(edge)
		new_lamination = encoding(self)
		new_triangulation = new_lamination.triangulation
		for corner in [new_triangulation.corner_of_edge(edge), new_triangulation.corner_of_edge(~edge)]:
			for side in range(3):
				if corner.labels[side] == left and new_lamination.is_bipod(corner.rotate(-1)):
					return encoding, corner.rotate(-1)
				if corner.labels[side] == right and new_lamination.is_bipod(corner.rotate(1)):
					return encoding, corner.rotate(1)
		
		return encoding, None
	
	def repeatedly_open_bipod(self, corner):
		encoding = self.triangulation.id_encoding()
		lamination = self
		while corner is not None:
			open_encoding, corner = lamination.open_bipod(corner)
			encoding = open_encoding * encoding
			lamination = open_encoding(lamination)
		
		return encoding
	
	def is_tripod(self, triangle):
		''' Returns if the lamination looks like a tripod in this triangle. '''
		weights = [self[edge] for edge in triangle]
		dual_weights_doubled = [weights[1] + weights[2] - weights[0],
					weights[2] + weights[0] - weights[1],
					weights[0] + weights[1] - weights[2]]
		return all(dual_weight > 0 for dual_weight in dual_weights_doubled)
	
	def tripod_regions(self):
		''' Returns a list of all triangles in which this lamination looks like a tripod. '''
		return [triangle for triangle in self.triangulation if self.is_tripod(triangle)]
	
	def is_tripod_free(self):
		return not any(self.tripod_regions())
	
	def remove_tripod_regions(self):
		lamination = self
		encodings = []
		while not lamination.is_tripod_free():
			bipod_edges = [triangle[side] for triangle, side in lamination.triangulation.corners if lamination.is_bipod((triangle, side))]
			edge_index = max(bipod_edges, key=lambda i: lamination[i])
			edge_index = int(raw_input('Edge to flip'))
			
			E = lamination.triangulation.encode_flip(edge_index)
			lamination = E(lamination)
			encodings.append(E)
		
		return flipper.kernel.product(encodings)
	
	def collapse_trivial_weight(self, edge_index):
		''' Returns this lamination on the triangulation obtained by collapsing edge edge_index.
		Assumes that:
			- self.triangulation is not S_{0,3},
			- the given edge does not connect between two real vertices, (with non-negative label), and
			- edge_index is the only edge of weight 0. '''
		
		if self[edge_index] != 0:
			raise flipper.AssumptionError('Lamination does not have weight 0 on edge to collapse.')
		
		# This relies on knowing how squares are returned.
		a, b, c, d = self.triangulation.find_edges_of_square_about_edge(edge_index)  # Get the square about it.
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
		
		# We'll first compute the vertex labels. This way we can check if our assumption is False early and so save some work.
		near_vertices = e.source_vertex, e.target_vertex
		
		# We'll replace the labels on the corner class with lower labels with the label from the higher.
		# This ensures that any non-negative vertex survives.
		if near_vertices[0].label <= near_vertices[1].label:
			good_vertex, bad_vertex = near_vertices[1], near_vertices[0]
		else:
			good_vertex, bad_vertex = near_vertices[0], near_vertices[1]
		
		# If we collapse together two real vertices (or a vertex with itself) then there is a loop
		# dijoint to this lamination and so this is not filling.
		if (good_vertex.label >= 0 and bad_vertex.label >= 0) or good_vertex == bad_vertex:
			raise flipper.AssumptionError('Lamination is not filling.')
		
		# Figure out how the vertices should be mapped.
		vertex_map = dict()
		for vertex in self.triangulation.vertices:
			if vertex != good_vertex and vertex != bad_vertex:
				vertex_map[vertex] = flipper.kernel.AbstractVertex(vertex.label)
		vertex_map[good_vertex] = flipper.kernel.AbstractVertex(good_vertex.label)
		vertex_map[bad_vertex] = vertex_map[good_vertex]
		
		# Now figure out how the edges should be mapped.
		edge_count = 0
		edge_map = dict()
		for edge in self.triangulation.edges:
			if edge.is_positive() and edge not in [a, b, c, d, e, ~a, ~b, ~c, ~d, ~e]:
				edge_map[edge] = flipper.kernel.AbstractEdge(vertex_map[edge.source_vertex], vertex_map[edge.target_vertex], edge_count)
				edge_map[~edge] = ~edge_map[edge]
				edge_count += 1
		
		if a == ~c:  # Collapsing an annulus.
			edge_map[~b] = flipper.kernel.AbstractEdge(vertex_map[b.target_vertex], vertex_map[b.source_vertex], edge_count)
			edge_map[~d] = ~edge_map[~b]
			edge_count += 1
		elif b == ~d:  # An annulus in the other direction.
			edge_map[~a] = flipper.kernel.AbstractEdge(vertex_map[a.target_vertex], vertex_map[a.source_vertex], edge_count)
			edge_map[~c] = ~edge_map[~a]
			edge_count += 1
		elif a == ~d:  #Collapsing a bigon.
			edge_map[~b] = flipper.kernel.AbstractEdge(vertex_map[b.target_vertex], vertex_map[b.source_vertex], edge_count)
			edge_map[~c] = ~edge_map[~b]
			edge_count += 1
		elif b == ~c:  # A bigon in the other direction.
			edge_map[~a] = flipper.kernel.AbstractEdge(vertex_map[a.target_vertex], vertex_map[a.source_vertex], edge_count)
			edge_map[~d] = ~edge_map[~a]
			edge_count += 1
		else:  # No identification.
			edge_map[~a] = flipper.kernel.AbstractEdge(vertex_map[a.target_vertex], vertex_map[a.source_vertex], edge_count)
			edge_map[~b] = ~edge_map[~a]
			edge_count += 1
			edge_map[~c] = flipper.kernel.AbstractEdge(vertex_map[c.target_vertex], vertex_map[c.source_vertex], edge_count)
			edge_map[~d] = ~edge_map[~c]
			edge_count += 1
		
		triples = [[edge_map[edge] for edge in triangle] for triangle in self.triangulation if e not in triangle and ~e not in triangle]
		new_triangles = [flipper.kernel.AbstractTriangle(triple) for triple in triples]
		
		bad_edges = [a, b, c, d, e, ~e]  # These are the edges for which edge_map is not defined.
		new_vector = [[self[edge] for edge in self.triangulation.edges if edge not in bad_edges and edge_map[edge].index == i][0] for i in range(edge_count)]
		
		return flipper.kernel.AbstractTriangulation(new_triangles).lamination(new_vector)
	
	def splitting_sequence(self, target_dilatation=None):
		''' Returns the splitting sequence associated to this laminations.
		This is the list of edges of maximal weight until you reach a
		periodic sequence (with required dilatation if given).
		
		The splitting sequence will have self.preperiodic_encoding set to
		None iff an edge collapse occurs. This is because we don't (yet)
		know how to describe this by a PLFunction but only happens because
		we punctured too many triangles to begin with.
		
		This requires the entries to be NumberFieldElements (over the same
		NumberField) or AlgebraicNumbers.
		
		This assumes that the lamination is filling. If not then it will
		discover this. '''
		
		# Check if the lamination is obviously non-filling.
		if any(v == 0 for v in self):
			raise flipper.AssumptionError('Lamination is not filling.')
		
		# If not given, puncture all the triangles where the lamination is a tripod.
		puncture_encoding = self.triangulation.encode_puncture_triangles(self.tripod_regions())
		lamination = puncture_encoding(self)
		
		laminations = [lamination]
		flips = []
		encodings = [puncture_encoding]
		seen = {lamination.projective_hash(): [0]}
		while True:
			# Find the index of the largest entry.
			edge_index = max(range(lamination.zeta), key=lambda i: lamination[i])
			E = lamination.triangulation.encode_flip(edge_index)
			lamination = E(lamination)
			encodings.append(E)
			laminations.append(lamination)
			flips.append(edge_index)
			
			# Check if we have created any edges of weight 0.
			# It is enough to just check edge_index.
			if lamination[edge_index] == 0:
				lamination.collapse_trivial_weight(edge_index)
				try:
					# If this fails it's because the lamination isn't filling.
					lamination = lamination.collapse_trivial_weight(edge_index)
					# We cannot provide the encoding or flip so we'll just stick in a None.
					encodings.append(None)
					laminations.append(lamination)
					flips.append(None)
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
							if None in encodings:
								pp_encoding = None
							else:
								pp_encoding = flipper.kernel.product(encodings[:index+1], start=self.triangulation.id_encoding())
								assert(pp_encoding.source_triangulation == self.triangulation)
								assert(pp_encoding.target_triangulation == old_lamination.triangulation)
							p_encoding = flipper.kernel.product(encodings[index+1:], start=old_lamination.triangulation.id_encoding())
							p_flips = flips[index:]
							
							assert(p_encoding.source_triangulation == old_lamination.triangulation)
							assert(p_encoding.target_triangulation == lamination.triangulation)
							assert(all(isom.source_triangulation == lamination.triangulation for isom in isometries))
							assert(all(isom.target_triangulation == old_lamination.triangulation for isom in isometries))
							
							return flipper.kernel.SplittingSequence(self, pp_encoding, p_encoding, isometries, p_flips)
						elif target_dilatation is not None and old_lamination.weight() > target_dilatation * lamination.weight():
							assert(False)
				seen[target].append(len(laminations)-1)
			else:
				seen[target] = [len(laminations)-1]
	
	def is_filling(self):
		try:
			self.splitting_sequence()
		except flipper.AssumptionError:
			return False
		else:
			return True
	
	def encode_twist(self, k=1):
		''' Returns an Encoding of a left Dehn twist about this lamination raised to the power k.
		If k is zero this will return the identity encoding. If k is negative this
		will return an Encoding of a right Dehn twist about this lamination raised to the power -k.
		Assumes that this lamination is a twistable curve. '''
		if not self.is_twistable():
			raise flipper.AssumptionError('Not a good curve.')
		
		if k == 0: return self.triangulation.id_encoding()
		
		conjugation = self.conjugate_short()
		short_lamination = conjugation(self)
		
		triangulation = short_lamination.triangulation
		# Grab the indices of the two edges we meet.
		e1, e2 = [edge_index for edge_index in range(short_lamination.zeta) if short_lamination[edge_index] > 0]
		# We might need to swap these edge indices so we have a good frame of reference.
		if triangulation.corner_of_edge(e1).indices[2] != e2: e1, e2 = e2, e1
		# But to do a right twist we'll need to switch framing again.
		if k < 0: e1, e2 = e2, e1
		
		# Finally we can encode the twist.
		forwards = short_lamination.triangulation.encode_flip(e1)
		short_lamination = forwards(short_lamination)
		
		# Find the correct isometry to take us back.
		# !?! TO DO.
		map_back = [isom for isom in short_lamination.triangulation.all_isometries(triangulation) if isom.index_map[e1] == e2 and isom.index_map[e2] == e1 and all(isom.index_map[x] == x for x in range(triangulation.zeta) if x not in [e1, e2])][0].encode()
		T = map_back * forwards
		
		return conjugation.inverse() * T**abs(k) * conjugation
	
	def encode_halftwist(self, k=1):
		''' Returns an Encoding of a left Dehn twist about this lamination raised to the power k.
		If k is zero this will return the identity encoding. If k is negative this
		will return an Encoding of a right Dehn twist about this lamination raised to the power -k.
		Assumes that this lamination is a half twistable curve. '''
		# !?! TOTALLY REDO.
		if not self.is_halftwistable():
			raise flipper.AssumptionError('Not a boundary of a pair of pants.')
		
		if k == 0: return self.triangulation.id_encoding()
		
		conjugation = self.conjugate_short()
		short_lamination = conjugation(self)
		
		triangulation = short_lamination.triangulation
		# Grab the indices of the two edges we meet.
		e1, e2 = [edge_index for edge_index in range(short_lamination.zeta) if short_lamination[edge_index] > 0]
		# We might need to swap these edge indices so we have a good frame of reference.
		if triangulation.corner_of_edge(e1).indices[2] != e2: e1, e2 = e2, e1
		# But to do a right twist we'll need to switch framing again.
		if k < 0: e1, e2 = e2, e1
		
		x, y = [edge_indices for edge_indices in triangulation.find_indicies_of_square_about_edge(e1) if edge_indices != e2]
		for triangle in triangulation:
			if (x in triangle or y in triangle) and len(set(triangle)) == 2:
				bottom = x if x in triangle else y
		
		# Finally we can encode the twist.
		forwards = short_lamination.triangulation.encode_flip(bottom)
		short_lamination = forwards(short_lamination)
		
		forwards2 = short_lamination.triangulation.encode_flip(e1)
		short_lamination = forwards2(short_lamination)
		
		forwards3 = short_lamination.triangulation.encode_flip(e2)
		short_lamination = forwards3(short_lamination)
		
		new_triangulation = short_lamination.triangulation
		
		# Find the correct isometry to take us back.
		map_back = [isom for isom in new_triangulation.all_isometries(triangulation) if isom.index_map[e1] == e2 and isom.index_map[e2] == bottom and isom.index_map[bottom] == e1 and all(isom.index_map[x] == x for x in range(triangulation.zeta) if x not in [e1, e2, bottom])][0].encode()
		T = map_back * forwards3 * forwards2 * forwards
		
		return conjugation.inverse() * T**abs(k) * conjugation

