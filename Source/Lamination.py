
try:
	# from Source.AbstractTriangulation import Abstract_Triangulation
	from Source.Matrix import Matrix, Id_Matrix, Empty_Matrix, Permutation_Matrix, nonnegative, nontrivial, nonnegative_image
	from Source.Error import AbortError, ComputationError, AssumptionError
except ImportError:
	# from AbstractTriangulation import Abstract_Triangulation
	from Matrix import Matrix, Id_Matrix, Empty_Matrix, Permutation_Matrix, nonnegative, nontrivial, nonnegative_image
	from Error import AbortError, ComputationError, AssumptionError

class Lamination:
	def __init__(self, abstract_triangulation, vector):
		self.abstract_triangulation = abstract_triangulation
		self.vector = vector
		self.zeta = self.abstract_triangulation.zeta
	
	def copy(self):
		return Lamination(self.abstract_triangulation, self.vector)
	
	def __repr__(self):
		return str(self.vector)
	
	def __iter__(self):
		return iter(self.vector)
	
	def __getitem__(self, index):
		return self.vector[index]
	
	def __rmul__(self, other):
		try:
			return Lamination(other.target_triangulation, other * self.vector)
		except TypeError:
			return NotImplemented
	
	def __eq__(self, other):
		return self.abstract_triangulation == other.abstract_triangulation and all(bool(v == w) for v, w in zip(self, other))
	
	def weight(self):
		return sum(self.vector)
	
	def is_multicurve(self):
		# Need to test if integral?
		
		if not nonnegative(self.vector): return False
		if self.vector == [0] * self.zeta: return False
		
		if not nonnegative_image(self.abstract_triangulation.face_matrix(), self.vector): return False
		
		for vertex in self.abstract_triangulation.corner_classes:
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
	
	def is_curve(self):
		# This is based off of Lamination.encode_twist(). See the documentation there as to why this works.
		if not self.is_multicurve(): return False
		
		lamination_copy = self.copy()
		
		time_since_last_weight_loss = 0
		old_weight = lamination_copy.weight()
		while lamination_copy.weight() > 2:
			edge_index = min([i for i in range(lamination_copy.zeta) if lamination_copy[i] > 0], key=lambda i: lamination_copy.weight_difference_flip_edge(i))
			lamination_copy = lamination_copy.flip_edge(edge_index)
			
			if lamination_copy.weight() < old_weight:
				time_since_last_weight_loss = 0
				old_weight = lamination_copy.weight()
			else:
				time_since_last_weight_loss += 1
			
			# If we ever fail to make progress more than once it is because our curve was really a multicurve.
			if time_since_last_weight_loss > 1:
				return False
		
		return True
	
	def flip_edge(self, edge_index, encoding=False):
		# Returns a new triangulation obtained by flipping the edge of index edge_index.
		# If encoding is set to True then it also returns the encodings from the old triangulation
		# to the new and vice versa.
		assert(self.abstract_triangulation.edge_is_flippable(edge_index))
		
		forwards, backwards = self.abstract_triangulation.encode_flip_edge(edge_index)
		if encoding:
			return (forwards * self), forwards, backwards
		else:
			return forwards * self
	
	def weight_difference_flip_edge(self, edge_index):
		a, b, c, d = self.abstract_triangulation.find_indicies_of_square_about_edge(edge_index)
		return max(self.vector[a] + self.vector[c], self.vector[b] + self.vector[d]) - self.vector[edge_index] - self.vector[edge_index]
	
	def encode_twist(self, k=1):
		''' Returns an Encoding of a left Dehn twist about this lamination raised to the power k.
		If k is zero this will return None, which can be used as the identity Encoding. If k is negative this 
		will return an Encoding of a right Dehn twist about this lamination raised to the power -k.
		Assumes that this lamination is a curve, if not an AssumptionError is thrown. '''
		if not self.is_curve():
			raise AssumptionError('Not a curve.')
		
		if k == 0: return None
		
		lamination_copy = self.copy()
		
		# We'll keep track of what we have conjugated by as well as it's inverse
		# we could compute this at the end by doing:
		#   conjugation_inverse = conjugation.inverse()
		# but this is much faster as we don't need to invert a load of matrices.
		conjugation = None
		conjugation_inverse = None
		
		while lamination_copy.weight() > 2:
			# Find the edge which decreases our weight the most.
			# If none exist then it doesn't matter which edge we flip, so long as it meets the curve.
			# By Lee Mosher's work there is a complexity that we will reduce to by doing this and eventually we will reach weight 2.
			edge_index = min([i for i in range(lamination_copy.zeta) if lamination_copy[i] > 0], key=lambda i: lamination_copy.weight_difference_flip_edge(i))
			
			lamination_copy, forwards, backwards = lamination_copy.flip_edge(edge_index, encoding=True)
			conjugation = forwards * conjugation
			conjugation_inverse = conjugation_inverse * backwards
		
		triangulation = lamination_copy.abstract_triangulation
		# Grab the indices of the two edges we meet.
		e1, e2 = [edge_index for edge_index in range(self.zeta) if lamination_copy[edge_index] > 0]
		# We might need to swap these edge indices so we have a good frame of reference.
		containing_triangles = triangulation.find_edge(e1)
		if containing_triangles[0][0][containing_triangles[0][1] + 2] != e2: e1, e2 = e2, e1
		# But to do a right twist we'll need to switch framing again.
		if k < 0: e1, e2 = e2, e1
		
		# Finally we can encode the twist.
		lamination_copy, forwards, backwards = lamination_copy.flip_edge(e1, encoding=True)
		new_triangulation = lamination_copy.abstract_triangulation
		
		# Find the correct isometry to take us back.
		map_back = [isom for isom in new_triangulation.all_isometries(triangulation) if isom.edge_map[e1] == e2 and isom.edge_map[e2] == e1 and all(isom.edge_map[x] ==  x for x in range(new_triangulation.zeta) if x not in [e1, e2])][0].encoding()
		T = map_back * forwards
		
		return conjugation_inverse * T**abs(k) * conjugation
