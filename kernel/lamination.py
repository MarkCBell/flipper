
import Flipper

class Lamination(object):
	def __init__(self, abstract_triangulation, vector):
		self.abstract_triangulation = abstract_triangulation
		self.zeta = self.abstract_triangulation.zeta
		self.vector = list(vector)
		self.labels = [str(v) for v in self.vector]
		if not self.is_lamination():
			raise Flipper.AssumptionError('Not a lamination.')
	
	def copy(self):
		return Lamination(self.abstract_triangulation, list(self.vector))
	
	def __repr__(self):
		return str(self.labels)
	
	def __iter__(self):
		return iter(self.vector)
	
	def __getitem__(self, index):
		return self.vector[index]
	
	def __eq__(self, other):
		return self.abstract_triangulation == other.abstract_triangulation and all(bool(v == w) for v, w in zip(self, other))
	def __ne__(self, other):
		return not self == other
	
	def __hash__(self):
		# This should be done better.
		return hash(tuple(self.vector))
	
	def all_isometries(self, other):
		return [isometry for isometry in self.abstract_triangulation.all_isometries(other.abstract_triangulation) if other == isometry * self]
	
	def all_projective_isometries(self, other):
		return [isometry for isometry in self.abstract_triangulation.all_isometries(other.abstract_triangulation) if other.projectively_equal(isometry * self)]
	
	def projectively_equal(self, other):
		w1, w2 = self.weight(), other.weight()
		return all(x * w2 == y * w1 for x, y in zip(self, other))
	
	def projective_hash(self):
		# We use this function to hash the number down. It NEEDS be (projectively) invariant under isometries of the triangulation
		# so we achieve this by sorting the hash values.
		w = self.weight()
		return tuple(sorted([x.algebraic_hash_ratio(w) for x in self]))
	
	def weight(self):
		return sum(self.vector)
	
	def is_lamination(self):
		if not Flipper.kernel.matrix.nonnegative(self.vector): return False
		for vertex in self.abstract_triangulation.corner_classes:
			for triangle, side in vertex:
				weights = [self.vector[index] for index in triangle]
				if weights[(side+1)%3] + weights[(side+2)%3] - weights[(side+0)%3] == 0:
					break
			else:
				return False
		
		return True
	
	def is_multicurve(self):
		if not self.is_lamination(): return False
		if self == self.abstract_triangulation.empty_lamination(): return False
		
		for vertex in self.abstract_triangulation.corner_classes:
			for triangle, side in vertex:
				weights = [self.vector[index] for index in triangle]
				dual_weights_doubled = [weights[1] + weights[2] - weights[0], weights[2] + weights[0] - weights[1], weights[0] + weights[1] - weights[2]]
				for i in range(3):
					if not isinstance(dual_weights_doubled[i], Flipper.kernel.types.Integer_Type):
						return False
					
					if dual_weights_doubled[i] % 2 != 0:  # Is odd.
						return False
		
		return True
	
	def conjugate_short(self):
		# Repeatedly flip to reduce the weight of this lamination as much as 
		# possible. Assumes that self is a multicurve.
		#
		# If this lamination is a curve then this will conjugate it to
		# a curve which meets each edge either:
		#	once (in which case it meets exactly 2 of them), or
		#	0 or 2 times.
		# The latter case happens iff a component of S - \gamma has no punctures.
		
		if not self.is_multicurve():
			raise Flipper.AssumptionError('Can only conjugate multicurves to be short.')
		
		lamination = self.copy()
		best_conjugation = conjugation = lamination.abstract_triangulation.Id_EncodingSequence()
		
		time_since_last_weight_loss = 0
		old_weight = lamination.weight()
		# If we ever fail to make progress more than once then the curve is as short as it's going to get.
		while time_since_last_weight_loss < 2:
			# Find the edge which decreases our weight the most.
			# If none exist then it doesn't matter which edge we flip, so long as it meets the curve.
			# By Lee Mosher's work there is a complexity that we will reduce to by doing this. 
			edge_index = min([i for i in range(lamination.zeta) if lamination[i] > 0 and lamination.abstract_triangulation.edge_is_flippable(i)], key=lamination.weight_difference_flip_edge)
			
			forwards = lamination.abstract_triangulation.encode_flip(edge_index)
			backwards = forwards.inverse()
			conjugation = forwards * conjugation
			lamination = forwards * lamination
			new_weight = lamination.weight()
			
			if new_weight < old_weight:
				time_since_last_weight_loss = 0
				old_weight = new_weight
				best_conjugation = conjugation
			else:
				time_since_last_weight_loss += 1
		
		return best_conjugation
	
	def is_curve(self):
		if not self.is_multicurve(): return False
		
		conjugation = self.conjugate_short()
		short_lamination = conjugation * self
		
		if short_lamination.weight() == 2: return True
		
		# See the conditions on conjugate_short as to why this works.
		if any(weight not in [0, 2] for weight in short_lamination): return False
		
		# If we have a longer curve then all vertices must be on one side of it.
		# So if we collapse the edges with weight 0 we must end up with a
		# one vertex triangulation.
		triangulation = short_lamination.abstract_triangulation
		corner_class_numbers = dict(zip(list(triangulation.corner_classes), range(len(triangulation.corner_classes))))
		for edge_index in range(triangulation.zeta):
			if self[edge_index] == 0:
				c1, c2 = triangulation.find_edge_corner_classes(edge_index)
				a, b = corner_class_numbers[c1], corner_class_numbers[c2]
				if a != b:
					x, y = max(a, b), min(a, b)
					for c in corner_class_numbers:
						if corner_class_numbers[c] == x: corner_class_numbers[c] = y
		
		# If any corner class is numbered > 0 then we don't have a one vertex triangulation.
		if any(corner_class_numbers.values()): return False
		
		# So either we have a single curve or we have a multicurve with two parallel components.
		# We can test for the latter by seeing if the halved curve is still a multicurve.
		if triangulation.lamination([v // 2 for v in short_lamination]).is_multicurve():
			return False
		
		return True
	
	def is_twistable(self):
		# This is based off of self.encode_twist(). See the documentation there as to why this works.
		if not self.is_curve(): return False
		
		conjugation = self.conjugate_short()
		short_lamination = conjugation * self
		
		return short_lamination.weight() == 2
	
	def is_halftwistable(self):
		# This is based off of self.encode_halftwist(). See the documentation there as to why this works.
		if not self.is_twistable(): return False
		
		conjugation = self.conjugate_short()
		short_lamination = conjugation * self
		
		e1, e2 = [edge_index for edge_index in range(short_lamination.zeta) if short_lamination[edge_index] > 0]
		x, y = [edge_indices for edge_indices in short_lamination.abstract_triangulation.find_indicies_of_square_about_edge(e1) if edge_indices != e2]
		for triangle in short_lamination.abstract_triangulation:
			if (x in triangle or y in triangle) and len(set(triangle)) == 2:
				return True
		
		return False
	
	def weight_difference_flip_edge(self, edge_index):
		# Returns how much the weight would change by if this flip was done.
		a, b, c, d = self.abstract_triangulation.find_indicies_of_square_about_edge(edge_index)
		return max(self[a] + self[c], self[b] + self[d]) - self[edge_index] - self[edge_index]
	
	def encode_puncture_trigons(self):
		# We label real punctures with a 0 and fake ones created by this process with a 1.
		
		zeta1 = self.abstract_triangulation.zeta
		M = Flipper.kernel.Id_Matrix(zeta1) * 2
		
		new_labels = []
		new_corner_labels = []
		zeta = self.zeta
		for triangle in self.abstract_triangulation:
			a, b, c = triangle.edge_indices
			if self[a] + self[b] > self[c] and self[b] + self[c] > self[a] and self[c] + self[a] > self[b]:
				x, y, z = zeta, zeta+1, zeta+2
				new_labels.append([a, z, y])
				new_labels.append([b, x, z])
				new_labels.append([c, y, x])
				new_corner_labels.append([1, 0, 0])
				new_corner_labels.append([1, 0, 0])
				new_corner_labels.append([1, 0, 0])
				
				M = M.join(Flipper.kernel.matrix.tweak_matrix(Flipper.kernel.Zero_Matrix(zeta1, 3), [(0, b), (0, c), (1, c), (1, a), (2, a), (2, b)], [(0, a), (1, b), (2, c)]))
				
				zeta = zeta + 3
			else:
				new_labels.append([a, b, c])
				new_corner_labels.append([0, 0, 0])
		
		T = Flipper.AbstractTriangulation(new_labels, new_corner_labels)
		return Flipper.kernel.Encoding([Flipper.kernel.PartialFunction(self.abstract_triangulation, T, M)])
	
	def collapse_trivial_weight(self, edge_index):
		# Assumes that AbstractTriangulation is not S_{0,3}. Assumes that the given 
		# edge does not connect between two real vertices, that is vertices with 
		# label 0. Assumes that edge_index is the only edge of weight 0.
		# If any of these assumptions are not met an AssumptionError is thrown.
		
		assert(self[edge_index] == 0)
		
		a, b, c, d = self.abstract_triangulation.find_indicies_of_square_about_edge(edge_index)  # Get the square about it.
		
		# We'll first deal with some bad cases that con occur when some of the sides of the square are in fact the same.
		if a == b or c == d:
			# This means that self[a] (respectively self[c]) == 0.
			raise Flipper.AssumptionError('Additional weightless edge.')
		
		# There is at most one duplicated pair.
		if a == d and b == c:
			# We're on S_{0,3}.
			raise Flipper.AssumptionError('Underlying surface is S_{0,3}.')
		
		if a == c and a == d:
			# We're on the square torus, there's only one vertex so both endpoints of this edge must be labelled 0.
			raise Flipper.AssumptionError('Edge connects between two vertices labelled 0.')
		
		# We'll first compute the new corner labels. This way we can check if our assumption is False early and so save some work.
		base_triangle, base_side = self.abstract_triangulation.find_edge(edge_index)[0]
		corner_A_label = base_triangle.corner_labels[(base_side + 1) % 3]
		corner_B_label = base_triangle.corner_labels[(base_side + 2) % 3]
		if corner_A_label == 0 and corner_B_label == 0:
			raise Flipper.AssumptionError('Edge connects between two vertices labelled 0.')
		
		# We'll replace the labels on the corner class with higher labels with the label from the lower
		good_corner_label = min(corner_A_label, corner_B_label)
		if corner_A_label < corner_B_label:
			bad_corner_class = self.abstract_triangulation.find_corner_class(base_triangle, (base_side+2) % 3)
		else:
			bad_corner_class = self.abstract_triangulation.find_corner_class(base_triangle, (base_side+1) % 3)
		
		# replacement is a map sending the old edge_indices to the new edge indices. We already know what it does on edges far away from edge_index.
		replacement = dict(zip([i for i in range(self.zeta) if i not in [edge_index, a, b, c, d]], range(self.zeta)))
		zeta = len(replacement)
		if a == c:
			replacement[a] = replacement[b] = replacement[c] = replacement[d] = zeta
			zeta += 1
		elif a == d:
			# Must make sure to update the vertex which is not in the interior of the bigon.
			bad_corner_class = self.abstract_triangulation.find_corner_class(base_triangle, (base_side+1) % 3)
			
			replacement[a] = replacement[b] = replacement[c] = replacement[d] = zeta
			zeta += 1
		elif b == c:
			# Must make sure to update the vertex which is not in the interior of the bigon.
			bad_corner_class = self.abstract_triangulation.find_corner_class(base_triangle, (base_side+2) % 3)
			
			replacement[a] = replacement[b] = replacement[c] = replacement[d] = zeta
			zeta += 1
		elif b == d:
			replacement[a] = replacement[b] = replacement[c] = replacement[d] = zeta
			zeta += 1
		else:
			replacement[a] = replacement[b] = zeta
			replacement[c] = replacement[d] = zeta + 1
			zeta += 2
		
		new_edge_labels = [[replacement[i] for i in triangle] for triangle in self.abstract_triangulation if edge_index not in triangle]
		new_vector = [[self[j] for j in range(self.zeta) if j != edge_index and replacement[j] == i][0] for i in range(zeta)]
		new_corner_labels = [[triangle.corner_labels[side] if (triangle, side) not in bad_corner_class else good_corner_label for side in range(3)] for triangle in self.abstract_triangulation if edge_index not in triangle]
		
		return Lamination(Flipper.AbstractTriangulation(new_edge_labels, new_corner_labels), new_vector)
	
	def splitting_sequence(self, target_dilatation=None, name=''):
		# Computes the splitting sequence of this lamination until we reach a periodic sequence (with the
		# required dilatation if given).
		# We assume that each entry is a NumberFieldElement and that this is a filling lamination. 
		# If not, it will discover this along the way and throw an AssumptionFlipper.
		
		# Check if vector is obviously reducible.
		if any(v == 0 for v in self.vector):
			raise Flipper.AssumptionError('Lamination is not filling.')
		
		# Puncture out all trigon regions.
		lamination = self.encode_puncture_trigons() * self
		
		laminations = [lamination]
		flips = []
		encodings = []
		seen = {lamination.projective_hash():[0]}
		while True:
			edge_index = max(range(lamination.zeta), key=lambda i: lamination[i])  # Find the index of the largest entry.
			E = lamination.abstract_triangulation.encode_flip(edge_index)
			lamination = E * lamination
			encodings.append(E)
			laminations.append(lamination)
			flips.append(edge_index)
			
			if lamination[edge_index] == 0:
				try:
					# If this fails it's because the lamination isn't filling.
					lamination = lamination.collapse_trivial_weight(edge_index)
				except Flipper.AssumptionError:
					raise Flipper.AssumptionError('Lamination is not filling.')
			
			# Check if it (projectively) matches a lamination we've already seen.
			target = lamination.projective_hash()
			if target in seen:
				for index in seen[target]:
					old_lamination = laminations[index]
					if len(lamination.all_projective_isometries(old_lamination)) > 0:
						if target_dilatation is None or old_lamination.weight() == target_dilatation * lamination.weight():
							return Flipper.kernel.SplittingSequence(self, None, laminations[index:], flips[index:], encodings, name=name)
				seen[target].append(len(laminations)-1)
			else:
				seen[target] = [len(laminations)-1]
	
	def is_filling(self):
		try:
			self.splitting_sequence()
		except Flipper.AssumptionError:
			return False
		else:
			return True
	
	def encode_twist(self, k=1):
		''' Returns an Encoding of a left Dehn twist about this lamination raised to the power k.
		If k is zero this will return None, which can be used as the identity Encoding. If k is negative this 
		will return an Encoding of a right Dehn twist about this lamination raised to the power -k.
		Assumes that this lamination is a curve, if not an AssumptionError is thrown. '''
		if not self.is_twistable():
			raise Flipper.AssumptionError('Not a good curve.')
		
		if k == 0: return self.abstract_triangulation.Id_EncodingSequence()
		
		conjugation = self.conjugate_short()
		short_lamination = conjugation * self
		
		triangulation = short_lamination.abstract_triangulation
		# Grab the indices of the two edges we meet.
		e1, e2 = [edge_index for edge_index in range(short_lamination.zeta) if short_lamination[edge_index] > 0]
		# We might need to swap these edge indices so we have a good frame of reference.
		containing_triangles = triangulation.find_edge(e1)
		if containing_triangles[0][0][containing_triangles[0][1] + 2] != e2: e1, e2 = e2, e1
		# But to do a right twist we'll need to switch framing again.
		if k < 0: e1, e2 = e2, e1
		
		# Finally we can encode the twist.
		forwards = short_lamination.abstract_triangulation.encode_flip(e1)
		short_lamination = forwards * short_lamination
		
		# Find the correct isometry to take us back.
		map_back = [isom for isom in short_lamination.abstract_triangulation.all_isometries(triangulation) if isom.edge_map[e1] == e2 and isom.edge_map[e2] == e1 and all(isom.edge_map[x] == x for x in range(triangulation.zeta) if x not in [e1, e2])][0].encode_isometry()
		T = map_back * forwards
		
		return conjugation.inverse() * T**abs(k) * conjugation
	
	def encode_halftwist(self, k=1):
		''' Returns an Encoding of a left Dehn twist about this lamination raised to the power k.
		If k is zero this will return None, which can be used as the identity Encoding. If k is negative this 
		will return an Encoding of a right Dehn twist about this lamination raised to the power -k.
		Assumes that this lamination is a curve, if not an AssumptionError is thrown. '''
		if not self.is_halftwistable():
			raise Flipper.AssumptionError('Not a boundary of a pair of pants.')
		
		if k == 0: return self.abstract_triangulation.Id_EncodingSequence()
		
		conjugation = self.conjugate_short()
		short_lamination = conjugation * self
		
		triangulation = short_lamination.abstract_triangulation
		# Grab the indices of the two edges we meet.
		e1, e2 = [edge_index for edge_index in range(short_lamination.zeta) if short_lamination[edge_index] > 0]
		# We might need to swap these edge indices so we have a good frame of reference.
		containing_triangles = triangulation.find_edge(e1)
		if containing_triangles[0][0][containing_triangles[0][1] + 2] != e2: e1, e2 = e2, e1
		# But to do a right twist we'll need to switch framing again.
		if k < 0: e1, e2 = e2, e1
		
		x, y = [edge_indices for edge_indices in triangulation.find_indicies_of_square_about_edge(e1) if edge_indices != e2]
		for triangle in triangulation:
			if (x in triangle or y in triangle) and len(set(triangle)) == 2:
				bottom = x if x in triangle else y
		
		# Finally we can encode the twist.
		forwards = short_lamination.abstract_triangulation.encode_flip(bottom)
		short_lamination = forwards * short_lamination
		
		forwards2 = short_lamination.abstract_triangulation.encode_flip(e1)
		short_lamination = forwards2 * short_lamination
		
		forwards3 = short_lamination.abstract_triangulation.encode_flip(e2)
		short_lamination = forwards3 * short_lamination
		
		new_triangulation = short_lamination.abstract_triangulation
		
		# Find the correct isometry to take us back.
		map_back = [isom for isom in new_triangulation.all_isometries(triangulation) if isom.edge_map[e1] == e2 and isom.edge_map[e2] == bottom and isom.edge_map[bottom] == e1 and all(isom.edge_map[x] == x for x in range(triangulation.zeta) if x not in [e1, e2, bottom])][0].encode_isometry()
		T = map_back * forwards3 * forwards2 * forwards
		
		return conjugation.inverse() * T**abs(k) * conjugation
