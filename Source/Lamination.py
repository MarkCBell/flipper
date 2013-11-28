
# We can also produce Laminations using:
#	1) key_curves(triangulation), and
#	2) stable_lamination(encoding)

from itertools import product, combinations
try:
	from Source.Matrix import Matrix, Id_Matrix, Empty_Matrix, Permutation_Matrix, nonnegative, nontrivial, nonnegative_image
	from Source.Error import AbortError, ComputationError, AssumptionError
	from Source.Symbolic_Computation import Perron_Frobenius_eigen
except ImportError:
	from Matrix import Matrix, Id_Matrix, Empty_Matrix, Permutation_Matrix, nonnegative, nontrivial, nonnegative_image
	from Error import AbortError, ComputationError, AssumptionError
	from Symbolic_Computation import Perron_Frobenius_eigen

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
		# This is based off of Source.Encoding.encode_twist(). See the documentation there as to why this works.
		if not self.is_multicurve(): return False
		
		lamination_copy = self.copy()
		
		time_since_last_weight_loss = 0
		old_weight = lamination_copy.weight()
		while lamination_copy.weight() > 2:
			edge_index = min([i for i in range(lamination_copy.zeta) if lamination_copy[i] > 0], key=lambda i: lamination_copy.weight_difference_flip_edge(i))
			
			a, b, c, d = lamination_copy.abstract_triangulation.find_indicies_of_square_about_edge(edge_index)
			new_vector = list(lamination_copy.vector)
			new_vector[edge_index] = max(lamination_copy[a] + lamination_copy[c], lamination_copy[b] + lamination_copy[d]) - lamination_copy[edge_index]
			lamination_copy = Lamination(lamination_copy.abstract_triangulation.flip_edge(edge_index), new_vector)
			
			if lamination_copy.weight() < old_weight:
				time_since_last_weight_loss = 0
				old_weight = lamination_copy.weight()
			else:
				time_since_last_weight_loss += 1
			
			# If we ever fail to make progress more than once it is because our curve was really a multicurve.
			if time_since_last_weight_loss > 1:
				return False
		
		return True
	
	def weight_difference_flip_edge(self, edge_index):
		a, b, c, d = self.abstract_triangulation.find_indicies_of_square_about_edge(edge_index)
		return max(self.vector[a] + self.vector[c], self.vector[b] + self.vector[d]) - self.vector[edge_index] - self.vector[edge_index]

#### Some special Laminations we know how to build.

def regular_neighbourhood(triangulation, edge_index):
	vector = [0] * triangulation.zeta
	(t1, s1), (t2, s2) = triangulation.find_edge(edge_index)
	corner_classes = [corner_class for corner_class in triangulation.corner_classes if (t1, (s1+1) % 3) in corner_class or (t2, (s2+1) % 3) in corner_class]
	for corner_class in corner_classes:
		for triangle, side in corner_class:
			if triangle[side+2] != edge_index:
				vector[triangle[side+2]] += 1
	return Lamination(triangulation, vector)

def key_curves(triangulation):
	return [regular_neighbourhood(triangulation, edge_index) for edge_index in range(triangulation.zeta)]

def stable_lamination(encoding, exact=False):
	# If this is an encoding of a pseudo-Anosov mapping class then this returns a curve that is 
	# quite (very) close to its stable lamination and a (floating point) estimate of the dilatation. 
	# If one cannot be found this a ComputationError is thrown. If exact is set to True then this uses 
	# Symbolic_Computation.Perron_Frobenius_eigen() to return the exact stable lamination (as a list of
	# algebraic numbers) along with the exact dilatation (again as an algebraic number). Again, if a good
	# enough approximation cannot be found to start the exact calculations with, this is detected and a
	# ComputationError thrown. Note: in most pseudo-Anosov cases < 15 iterations are needed, if it fails to
	# converge after 1000 iterations it's actually extremely likely that the map was not pseudo-Anosov.
	
	assert(encoding.source_triangulation == encoding.target_triangulation)
	curves = key_curves(encoding.source_triangulation)
	
	def projective_difference(A, B, error_reciprocal):
		# Returns True iff the projective difference between A and B is less than 1 / error_reciprocal.
		A_sum, B_sum = sum(A), sum(B)
		return max(abs((p * B_sum) - q * A_sum) for p, q in zip(A, B)) * error_reciprocal < A_sum * B_sum 
	
	for i in range(1000):
		curves = [encoding * curve for curve in curves]
		if i > 3 and all(projective_difference(curve_A, curve_B, 1000000000) for curve_A, curve_B in combinations(curves, 2)):  # Make sure to apply at least 4 iterations.
			break
	else:
		if not exact: raise ComputationError('Could not estimate stable lamination.')
	
	curve = curves[0]  # They're all pretty much the same so just get this one.
	
	if exact:
		action_matrix, condition_matrix = encoding.applied_matrix(curve)
		try:
			eigenvector, eigenvalue = Perron_Frobenius_eigen(action_matrix)
		except AssumptionError:  # action_matrix was not Perron-Frobenius.
			raise ComputationError('Could not estimate stable lamination.')
		if nonnegative_image(condition_matrix, eigenvector):  # Check that the projective fixed point is actually in this cell. 
			return Lamination(encoding.source_triangulation, eigenvector), eigenvalue
		else:
			raise ComputationError('Could not estimate stable lamination.')  # If not then the curve failed to get close enough to the stable lamination.
	else:
		return Lamination(encoding.source_triangulation, curve), float((encoding * curve)[0]) / curve[0]
