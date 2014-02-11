
import Flipper

class Lamination:
	def __init__(self, AbstractTriangulation, vector):
		self.AbstractTriangulation = AbstractTriangulation
		self.zeta = self.AbstractTriangulation.zeta
		self.vector = list(vector)
		self.labels = [str(v) for v in self.vector]
	
	def copy(self):
		return Lamination(self.AbstractTriangulation, list(self.vector))
	
	def __repr__(self):
		return '[' + ', '.join(self.labels) + ']'
	
	def __iter__(self):
		return iter(self.vector)
	
	def __getitem__(self, index):
		return self.vector[index]
	
	def __rmul__(self, other):
		if isinstance(other, Flipper.kernel.isometry.Isometry) and other.source_triangulation == self.AbstractTriangulation:
			return Lamination(other.target_triangulation, [self[j] for i in range(self.zeta) for j in range(self.zeta) if i == other.edge_map[j]])
		else:
			return NotImplemented
	
	def __eq__(self, other):
		return self.AbstractTriangulation == other.AbstractTriangulation and all(bool(v == w) for v, w in zip(self, other))
	
	def weight(self):
		return sum(self.vector)
	
	def is_multicurve(self):
		if not Flipper.kernel.matrix.nontrivial(self.vector): return False
		if not Flipper.kernel.matrix.nonnegative(self.vector): return False
		if not self.AbstractTriangulation.face_matrix().nonnegative_image(self.vector): return False
		
		for vertex in self.AbstractTriangulation.corner_classes:
			for triangle, side in vertex:
				weights = [self.vector[index] for index in triangle]
				dual_weights_doubled = [weights[1] + weights[2] - weights[0], weights[2] + weights[0] - weights[1], weights[0] + weights[1] - weights[2]]
				for i in range(3):
					if dual_weights_doubled[i] % 2 != 0:  # Is odd.
						return False
				if dual_weights_doubled[side] == 0:
					break
			else:
				return False
		
		return True
	
	def is_good_curve(self):
		# This is based off of Source.Encoding.encode_twist(). See the documentation there as to why this works.
		if not self.is_multicurve(): return False
		
		lamination = self.copy()
		
		time_since_last_weight_loss = 0
		old_weight = lamination.weight()
		while lamination.weight() > 2:
			edge_index = min([i for i in range(lamination.zeta) if lamination[i] > 0 and lamination.AbstractTriangulation.edge_is_flippable(i)], key=lambda i: lamination.weight_difference_flip_edge(i))
			lamination = lamination.flip_edge(edge_index)
			new_weight = lamination.weight()
			
			if new_weight < old_weight:
				time_since_last_weight_loss = 0
				old_weight = new_weight
			else:
				time_since_last_weight_loss += 1
			
			# If we ever fail to make progress more than once it is because our curve was really a multicurve.
			if time_since_last_weight_loss > 1:
				return False
		
		return True
	
	def is_pants_boundary(self):
		# This is based off of Source.Encoding.encode_halftwist(). See the documentation there as to why this works.
		if not self.is_good_curve(): return False
		
		lamination = self.copy()
		
		while lamination.weight() > 2:
			edge_index = min([i for i in range(lamination.zeta) if lamination[i] > 0], key=lambda i: lamination.weight_difference_flip_edge(i))
			lamination = lamination.flip_edge(edge_index)
		
		e1, e2 = [edge_index for edge_index in range(lamination.zeta) if lamination[edge_index] > 0]
		x, y = [edge_indices for edge_indices in lamination.AbstractTriangulation.find_indicies_of_square_about_edge(e1) if edge_indices != e2]
		for triangle in lamination.AbstractTriangulation:
			if (x in triangle or y in triangle) and len(set(triangle)) == 2:
				return True
		
		return False
	
	def weight_difference_flip_edge(self, edge_index):
		a, b, c, d = self.AbstractTriangulation.find_indicies_of_square_about_edge(edge_index)
		return max(self[a] + self[c], self[b] + self[d]) - self[edge_index] - self[edge_index]
	
	def flip_edge(self, edge_index):
		a, b, c, d = self.AbstractTriangulation.find_indicies_of_square_about_edge(edge_index)
		new_vector = list(self.vector)
		new_vector[edge_index] = max(self[a] + self[c], self[b] + self[d]) - self[edge_index]
		return Lamination(self.AbstractTriangulation.flip_edge(edge_index), new_vector)
	
	def puncture_trigons(self):
		# We label real punctures with a 0 and fake ones created by this process with a 1.
		new_labels = []
		new_corner_labels = []
		new_vector = [2*x for x in self.vector]
		zeta = self.zeta
		for triangle in self.AbstractTriangulation:
			a, b, c = triangle.edge_indices
			if new_vector[a] + new_vector[b] > new_vector[c] and new_vector[b] + new_vector[c] > new_vector[a] and new_vector[c] + new_vector[a] > new_vector[b]:
				x, y, z = zeta, zeta+1, zeta+2
				new_labels.append([a,z,y])
				new_labels.append([b,x,z])
				new_labels.append([c,y,x])
				new_corner_labels.append([1,0,0])
				new_corner_labels.append([1,0,0])
				new_corner_labels.append([1,0,0])
				new_vector.append(self[b] + self[c] - self[a])
				new_vector.append(self[c] + self[a] - self[b])
				new_vector.append(self[a] + self[b] - self[c])
				zeta = zeta + 3
			else:
				new_labels.append([a,b,c])
				new_corner_labels.append([0,0,0])
		
		return Lamination(Flipper.kernel.abstracttriangulation.AbstractTriangulation(new_labels, new_corner_labels), new_vector)
	
	def collapse_trivial_weight(self, edge_index):
		# Assumes that AbstractTriangulation is not S_{0,3}. Assumes that the given 
		# edge does not connect between two real vertices, that is vertices with 
		# label 0. Assumes that edge_index is the only edge of weight 0.
		# If any of these assumptions are not met an AssumptionError is thrown.
		
		assert(self[edge_index] == 0)
		
		a, b, c, d = self.AbstractTriangulation.find_indicies_of_square_about_edge(edge_index)  # Get the square about it.
		
		# We'll first deal with some bad cases that con occur when some of the sides of the square are in fact the same.
		if a == b or c == d:
			# This means that self[a] (respectively self[c]) == 0.
			raise Flipper.kernel.error.AssumptionError('Additional weightless edge.')
		
		# There is at most one duplicated pair.
		if a == d and b == c:
			# We're on S_{0,3}.
			raise Flipper.kernel.error.AssumptionError('Underlying surface is S_{0,3}.')
		
		if a == c and a == d:
			# We're on the square torus, there's only one vertex so both endpoints of this edge must be labelled 0.
			raise Flipper.kernel.error.AssumptionError('Edge connects between two vertices labelled 0.')
		
		# We'll first compute the new corner labels. This way we can check if our assumption is False early and so save some work.
		base_triangle, base_side = self.AbstractTriangulation.find_edge(edge_index)[0]
		corner_A_label = base_triangle.corner_labels[(base_side + 1) % 3]
		corner_B_label = base_triangle.corner_labels[(base_side + 2) % 3]
		if corner_A_label == 0 and corner_B_label == 0:
			raise Flipper.kernel.error.AssumptionError('Edge connects between two vertices labelled 0.')
		
		# We'll replace the labels on the corner class with higher labels with the label from the lower
		good_corner_label = min(corner_A_label, corner_B_label)
		if corner_A_label < corner_B_label:
			bad_corner_class = self.AbstractTriangulation.find_corner_class(base_triangle, (base_side+2) % 3)
		else:
			bad_corner_class = self.AbstractTriangulation.find_corner_class(base_triangle, (base_side+1) % 3)
		
		# replacement is a map sending the old edge_indices to the new edge indices. We already know what it does on edges far away from edge_index.
		replacement = dict(zip([i for i in range(self.zeta) if i not in [edge_index, a, b, c, d]], range(self.zeta)))
		zeta = len(replacement)
		if a == c:
			replacement[a] = replacement[b] = replacement[c] = replacement[d] = zeta
			zeta += 1
		elif a == d:
			# Must make sure to update the vertex which is not in the interior of the bigon.
			bad_corner_class = self.AbstractTriangulation.find_corner_class(base_triangle, (base_side+1) % 3)
			
			replacement[a] = replacement[b] = replacement[c] = replacement[d] = zeta
			zeta += 1
		elif b == c:
			# Must make sure to update the vertex which is not in the interior of the bigon.
			bad_corner_class = self.AbstractTriangulation.find_corner_class(base_triangle, (base_side+2) % 3)
			
			replacement[a] = replacement[b] = replacement[c] = replacement[d] = zeta
			zeta += 1
		elif b == d:
			replacement[a] = replacement[b] = replacement[c] = replacement[d] = zeta
			zeta += 1
		else:
			replacement[a] = replacement[b] = zeta
			replacement[c] = replacement[d] = zeta + 1
			zeta += 2
		
		new_edge_labels = [[replacement[i] for i in triangle] for triangle in self.AbstractTriangulation if edge_index not in triangle]
		new_vector = [[self[j] for j in range(self.zeta) if j != edge_index and replacement[j] == i][0] for i in range(zeta)]
		new_corner_labels = [[triangle.corner_labels[side] if (triangle, side) not in bad_corner_class else good_corner_label for side in range(3)] for triangle in self.AbstractTriangulation if edge_index not in triangle]
		
		return Lamination(Flipper.kernel.abstracttriangulation.AbstractTriangulation(new_edge_labels, new_corner_labels), new_vector)
	
	def splitting_sequence(self, exact=False):
		# Computes the splitting sequence of this lamination where each of the entries an AlgebraicType.
		
		# Assumes that self is a filling lamination. If not, it will discover this along the way and throw an AssumptionFlipper.kernel.error.
		# We assume that self is given as a list of algebraic numbers.
		
		# If exact is set to False then an NumberSystem is created to how sufficiently good AlgebraicApproximations of the
		# algebraic numbers involved. If at any point the precision would drop below what is required to maintain exactness 
		# then the NumberSystem automatically requests a more accurate approximation from the symbolic library. This is much 
		# faster than even sage.
		#
		# Note that when exact is False we require far less from the symbolic library. For example, we do not need:
		#	addition, subtraction, division, comparison and equality (+, -, /, <, ==) with integers or other algebraic_types.
		
		def projectively_equal(lamination1, lamination2):
			return all(lamination1[i] * lamination2[0] == lamination2[i] * lamination1[0] for i in range(1, lamination1.zeta))
		
		# We use this function to hash the number down. It NEEDS be (projectively) invariant under isometries of the triangulation
		# so we achieve this by sorting the hash values.
		def projectively_hash_lamination(lamination1):
			s = lamination1.weight()
			return tuple(sorted([v.algebraic_hash_ratio(s) for v in lamination1]))
		
		if exact:
			initial_lamination = self
		else:
			initial_lamination = Lamination(self.AbstractTriangulation, Flipper.kernel.numbersystem.NumberSystem_basis(self.vector, self.zeta))
		
		# Check if vector is obviously reducible.
		if any(v == 0 for v in initial_lamination.vector):
			raise Flipper.kernel.error.AssumptionError('Lamination is not filling.')
		
		# Puncture out all trigon regions.
		lamination = initial_lamination.puncture_trigons()
		
		flipped = []
		seen = {projectively_hash_lamination(lamination):[(0, lamination)]}
		while True:
			edge_index = max(range(lamination.zeta), key=lambda i: lamination[i])  # Find the index of the largest entry.
			lamination = lamination.flip_edge(edge_index)
			
			if lamination[edge_index] == 0:
				try:
					# If this fails it's because the lamination isn't filling.
					lamination = lamination.collapse_trivial_weight(edge_index)
				except Flipper.kernel.error.AssumptionError:
					raise Flipper.kernel.error.AssumptionError('Lamination is not filling.')
			
			flipped.append(edge_index)
			
			# Check if it (projectively) matches a lamination we've already seen.
			target = projectively_hash_lamination(lamination)
			if target in seen:
				for index, old_lamination in seen[target]:
					isometries = [isometry for isometry in lamination.AbstractTriangulation.all_isometries(old_lamination.AbstractTriangulation) if projectively_equal(isometry * lamination, old_lamination)]
					if len(isometries) > 0:
						return flipped[:index], flipped[index:], old_lamination[isometries[0].edge_map[0]] / lamination[0], old_lamination, isometries
				seen[target].append((len(flipped), lamination))
			else:
				seen[target] = [(len(flipped), lamination)]
	
	def is_filling(self):
		try:
			self.splitting_sequence()
		except Flipper.kernel.error.AssumptionError:
			return False
		else:
			return True
	
	def encode_twist(self, k=1):
		''' Returns an Encoding of a left Dehn twist about this lamination raised to the power k.
		If k is zero this will return None, which can be used as the identity Encoding. If k is negative this 
		will return an Encoding of a right Dehn twist about this lamination raised to the power -k.
		Assumes that this lamination is a curve, if not an AssumptionError is thrown. '''
		if not self.is_good_curve():
			raise Flipper.kernel.error.AssumptionError('Not a good curve.')
		
		if k == 0: return self.AbstractTriangulation.Id_EncodingSequence()
		
		lamination = self.copy()
		
		# We'll keep track of what we have conjugated by as well as it's inverse
		# we could compute this at the end by doing:
		#   conjugation_inverse = conjugation.inverse()
		# but this is much faster as we don't need to invert a load of matrices.
		conjugation = lamination.AbstractTriangulation.Id_EncodingSequence()
		conjugation_inverse = lamination.AbstractTriangulation.Id_EncodingSequence()
		
		while lamination.weight() > 2:
			# Find the edge which decreases our weight the most.
			# If none exist then it doesn't matter which edge we flip, so long as it meets the curve.
			# By Lee Mosher's work there is a complexity that we will reduce to by doing this and eventually we will reach weight 2.
			edge_index = min([i for i in range(lamination.zeta) if lamination[i] > 0 and lamination.AbstractTriangulation.edge_is_flippable(i)], key=lambda i: lamination.weight_difference_flip_edge(i))
			
			forwards, backwards = lamination.AbstractTriangulation.encode_flip(edge_index)
			conjugation = forwards * conjugation
			conjugation_inverse = conjugation_inverse * backwards
			lamination = forwards * lamination
		
		triangulation = lamination.AbstractTriangulation
		# Grab the indices of the two edges we meet.
		e1, e2 = [edge_index for edge_index in range(lamination.zeta) if lamination[edge_index] > 0]
		# We might need to swap these edge indices so we have a good frame of reference.
		containing_triangles = triangulation.find_edge(e1)
		if containing_triangles[0][0][containing_triangles[0][1] + 2] != e2: e1, e2 = e2, e1
		# But to do a right twist we'll need to switch framing again.
		if k < 0: e1, e2 = e2, e1
		
		# Finally we can encode the twist.
		forwards, backwards = lamination.AbstractTriangulation.encode_flip(e1)
		lamination = forwards * lamination
		new_triangulation = lamination.AbstractTriangulation
		
		# Find the correct isometry to take us back.
		map_back = [isom for isom in new_triangulation.all_isometries(triangulation) if isom.edge_map[e1] == e2 and isom.edge_map[e2] == e1 and all(isom.edge_map[x] == x for x in range(triangulation.zeta) if x not in [e1, e2])][0].encode_isometry()
		T = map_back * forwards
		
		return conjugation_inverse * T**abs(k) * conjugation
	
	def encode_halftwist(self, k=1):
		''' Returns an Encoding of a left Dehn twist about this lamination raised to the power k.
		If k is zero this will return None, which can be used as the identity Encoding. If k is negative this 
		will return an Encoding of a right Dehn twist about this lamination raised to the power -k.
		Assumes that this lamination is a curve, if not an AssumptionError is thrown. '''
		if not self.is_pants_boundary():
			raise Flipper.kernel.error.AssumptionError('Not a boundary of a pair of pants.')
		
		if k == 0: return self.AbstractTriangulation.Id_EncodingSequence()
		
		lamination = self.copy()
		
		# We'll keep track of what we have conjugated by as well as it's inverse
		# we could compute this at the end by doing:
		#   conjugation_inverse = conjugation.inverse()
		# but this is much faster as we don't need to invert a load of matrices.
		conjugation = lamination.AbstractTriangulation.Id_EncodingSequence()
		conjugation_inverse = lamination.AbstractTriangulation.Id_EncodingSequence()
		
		while lamination.weight() > 2:
			# Find the edge which decreases our weight the most.
			# If none exist then it doesn't matter which edge we flip, so long as it meets the curve.
			# By Lee Mosher's work there is a complexity that we will reduce to by doing this and eventually we will reach weight 2.
			edge_index = min([i for i in range(lamination.zeta) if lamination[i] > 0 and lamination.AbstractTriangulation.edge_is_flippable(i)], key=lambda i: lamination.weight_difference_flip_edge(i))
			
			forwards, backwards = lamination.AbstractTriangulation.encode_flip(edge_index)
			conjugation = forwards * conjugation
			conjugation_inverse = conjugation_inverse * backwards
			lamination = forwards * lamination
		
		triangulation = lamination.AbstractTriangulation
		# Grab the indices of the two edges we meet.
		e1, e2 = [edge_index for edge_index in range(lamination.zeta) if lamination[edge_index] > 0]
		# We might need to swap these edge indices so we have a good frame of reference.
		containing_triangles = triangulation.find_edge(e1)
		if containing_triangles[0][0][containing_triangles[0][1] + 2] != e2: e1, e2 = e2, e1
		# But to do a right twist we'll need to switch framing again.
		if k < 0: e1, e2 = e2, e1
		
		x, y = [edge_indices for edge_indices in triangulation.find_indicies_of_square_about_edge(e1) if edge_indices != e2]
		for triangle in triangulation:
			if (x in triangle or y in triangle) and len(set(triangle)) == 2:
				bottom = x if x in triangle else y
				other = triangle[0] if triangle[0] != bottom else triangle[1]
		
		# Finally we can encode the twist.
		forwards, backwards = lamination.AbstractTriangulation.encode_flip(bottom)
		lamination = forwards * lamination
		
		forwards2, backwards2 = lamination.AbstractTriangulation.encode_flip(e1)
		lamination = forwards2 * lamination
		
		forwards3, backwards3 = lamination.AbstractTriangulation.encode_flip(e2)
		lamination = forwards3 * lamination
		
		new_triangulation = lamination.AbstractTriangulation
		
		# Find the correct isometry to take us back.
		map_back = [isom for isom in new_triangulation.all_isometries(triangulation) if isom.edge_map[e1] == e2 and isom.edge_map[e2] == bottom and isom.edge_map[bottom] == e1 and all(isom.edge_map[x] == x for x in range(triangulation.zeta) if x not in [e1, e2, bottom])][0].encode_isometry()
		T = map_back * forwards3 * forwards2 * forwards
		
		return conjugation_inverse * T**abs(k) * conjugation