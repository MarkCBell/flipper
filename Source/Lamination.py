
# We can also produce Laminations using:
#	1) key_curves(triangulation), and
#	2) invariant_lamination(encoding)

from itertools import product, combinations
try:
	from Source.AbstractTriangulation import Abstract_Triangulation
	from Source.Matrix import Matrix, Id_Matrix, Empty_Matrix, Permutation_Matrix, nonnegative, nontrivial, nonnegative_image
	from Source.Isometry import all_isometries
	from Source.Error import AbortError, ComputationError, AssumptionError
	from Source.Symbolic_Computation import Perron_Frobenius_eigen, minimal_polynomial_coefficients, simplify, algebraic_type
except ImportError:
	from AbstractTriangulation import Abstract_Triangulation
	from Matrix import Matrix, Id_Matrix, Empty_Matrix, Permutation_Matrix, nonnegative, nontrivial, nonnegative_image
	from Isometry import all_isometries
	from Error import AbortError, ComputationError, AssumptionError
	from Symbolic_Computation import Perron_Frobenius_eigen, minimal_polynomial_coefficients, simplify, algebraic_type

class Lamination:
	def __init__(self, abstract_triangulation, vector):
		self.abstract_triangulation = abstract_triangulation
		self.vector = [simplify(v) if isinstance(v, algebraic_type) else v for v in vector]
		self.zeta = self.abstract_triangulation.zeta
	
	def copy(self):
		return Lamination(self.abstract_triangulation, list(self.vector))
	
	def __repr__(self):
		if isinstance(self.vector[0], algebraic_type):
			return '[' + ', '.join('%0.4f' % float(v) for v in self.vector) + ']'
		else:
			return '[' + ', '.join('%d' % v for v in self.vector) + ']'
	
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
		if not all(v == int(v) for v in self.vector): return False
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
		
		lamination = self.copy()
		
		time_since_last_weight_loss = 0
		old_weight = lamination.weight()
		while lamination.weight() > 2:
			edge_index = min([i for i in range(lamination.zeta) if lamination[i] > 0], key=lambda i: lamination.weight_difference_flip_edge(i))
			lamination = lamination.flip_edge(edge_index)
			
			if lamination.weight() < old_weight:
				time_since_last_weight_loss = 0
				old_weight = lamination.weight()
			else:
				time_since_last_weight_loss += 1
			
			# If we ever fail to make progress more than once it is because our curve was really a multicurve.
			if time_since_last_weight_loss > 1:
				return False
		
		return True
	
	def weight_difference_flip_edge(self, edge_index):
		a, b, c, d = self.abstract_triangulation.find_indicies_of_square_about_edge(edge_index)
		return max(self.vector[a] + self.vector[c], self.vector[b] + self.vector[d]) - self.vector[edge_index] - self.vector[edge_index]
	
	def flip_edge(self, edge_index):
		a, b, c, d = self.abstract_triangulation.find_indicies_of_square_about_edge(edge_index)
		new_vector = list(self.vector)
		new_vector[edge_index] = max(self[a] + self[c], self[b] + self[d]) - self[edge_index]
		return Lamination(self.abstract_triangulation.flip_edge(edge_index), new_vector)
	
	def puncture_trigons(self):
		# We label real punctures with a 0 and fake ones created by this process with a 1.
		new_labels = []
		new_corner_labels = []
		new_vector = list(self.vector)
		zeta = self.zeta
		for triangle in self.abstract_triangulation:
			a, b, c = triangle.edge_indices
			if new_vector[a] + new_vector[b] > new_vector[c] and new_vector[b] + new_vector[c] > new_vector[a] and new_vector[c] + new_vector[a] > new_vector[b]:
				x, y, z = zeta, zeta+1, zeta+2
				new_labels.append([a,z,y])
				new_labels.append([b,x,z])
				new_labels.append([c,y,x])
				new_corner_labels.append([1,0,0])
				new_corner_labels.append([1,0,0])
				new_corner_labels.append([1,0,0])
				new_vector.append((new_vector[b] + new_vector[c] - new_vector[a]) / 2)
				new_vector.append((new_vector[c] + new_vector[a] - new_vector[b]) / 2)
				new_vector.append((new_vector[a] + new_vector[b] - new_vector[c]) / 2)
				zeta = zeta + 3
			else:
				new_labels.append([a,b,c])
				new_corner_labels.append([0,0,0])
		
		return Lamination(Abstract_Triangulation(new_labels, new_corner_labels), new_vector)
	
	def collapse_trivial_weight(self, edge_index):
		# Assumes that abstract_triangulation is not S_{0,3}. Assumes that the given 
		# edge does not connect between two real vertices, that is vertices with 
		# label 0. Assumes that edge_index is the only edge of weight 0.
		# If any of these assumptions are not met an AssumptionError is thrown.
		
		assert(self[edge_index] == 0)
		
		a, b, c, d = self.abstract_triangulation.find_indicies_of_square_about_edge(edge_index)  # Get the square about it.
		
		# We'll first deal with some bad cases that con occur when some of the sides of the square are in fact the same.
		if a == b or c == d:
			# This means that self[a] (respectively self[c] == 0).
			raise AssumptionError('Additional weightless edge.')
		
		# There is at most one duplicated pair.
		if a == d and b == c:
			# We're on S_{0,3}.
			raise AssumptionError('Underlying surface is S_{0,3}.')
		
		if a == c and a == d:
			# We're on the square torus, there's only one vertex so both endpoints of this edge must be labelled 0.
			raise AssumptionError('Edge connects between two vertices labelled 0.')
		
		# We'll first compute the new corner labels. This way we can check if our assumption is False early and so save some work.
		base_triangle, base_side = self.abstract_triangulation.find_edge(edge_index)[0]
		corner_A_label = base_triangle.corner_labels[(base_side + 1) % 3]
		corner_B_label = base_triangle.corner_labels[(base_side + 2) % 3]
		if corner_A_label == 0 and corner_B_label == 0:
			raise AssumptionError('Edge connects between two vertices labelled 0.')
		
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
		
		return Lamination(Abstract_Triangulation(new_edge_labels, new_corner_labels), new_vector)
	
	def splitting_sequence(self, split_all_edges=False):
		# Assumes that self is a filling lamination. If not, it will discover this along the way and throw an 
		# AssumptionError
		# We assume that self is given as a list of algebraic numbers. 
		# We continually use Symbolic_Computation.simplify() just to be safe.
		# This assumes that the edges are labelled 0, ..., abstract_triangulation.zeta-1, this is a very sane labelling system.
		
		def projective_weights(x):
			s = simplify(1 / sum(x))
			return tuple([simplify(v * s) for v in x])
		
		# We use this function to hash the number down. It MUST be (projectively) invariant under isometries of the triangulation.
		# We take the coefficients of the minimal polynomial of each entry and sort them. This has the nice property that there is a
		# uniform bound on the number of collisions.
		def hash_lamination(x):
			return tuple(sorted(([minimal_polynomial_coefficients(v) for v in projective_weights(x)])))
		
		# Check if vector is obviously reducible.
		if any(v == 0 for v in self.vector):
			raise AssumptionError('Lamination is not filling.')
		
		lamination = self.puncture_trigons()  # Puncture out all trigon regions.
		flipped = []
		seen = {hash_lamination(lamination):[[0, lamination, projective_weights(lamination)]]}
		while True:
			edge_index = max(range(lamination.zeta), key=lambda i: lamination[i])  # Find the index of the largest entry
			lamination = lamination.flip_edge(edge_index)
			
			if lamination[edge_index] == 0:
				try:
					# If this fails it's because the lamination isn't filling.
					lamination = lamination.collapse_trivial_weight(edge_index)
				except AssumptionError:
					raise AssumptionError('Lamination is not filling.')
			
			flipped.append(edge_index)
			
			# if len(flipped) % 20 == 0: print(flipped[-20:])  # Every once in a while show how we're progressing.
			
			# Check if it (projectively) matches a lamination we've already seen.
			target = hash_lamination(lamination)
			current_triangulation = lamination.abstract_triangulation
			current_projective_weights = projective_weights(lamination)
			if target in seen:
				for index, old_lamination, old_projective_weights in seen[target]:
					old_triangulation = old_lamination.abstract_triangulation
					for isometry in all_isometries(current_triangulation, old_triangulation):
						permuted_old_projective_weights = tuple([old_projective_weights[isometry.edge_map[i]] for i in range(lamination.zeta)])
						if current_projective_weights == permuted_old_projective_weights:
							if not split_all_edges or all(i in flipped[index:] for i in range(lamination.zeta)):
								# Return: the pre-periodic part, the periodic part, the dilatation.
								return flipped[:index], flipped[index:], simplify(old_lamination[isometry.edge_map[0]] / lamination[0]), old_lamination, isometry
				seen[target].append([len(flipped), lamination, current_projective_weights])
			else:
				seen[target] = [[len(flipped), lamination, current_projective_weights]]
	
	def is_filling(self):
		try:
			self.splitting_sequence()
		except AssumptionError:
			return False
		else:
			return True

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

def invariant_lamination(encoding, exact=False):
	# Attempts to find an curve which is almost (projectively) invariant under given encoding and a
	# (floating point) estimate of the dilatation. If one cannot be found this a ComputationError is thrown. 
	# This is designed to be called only with pseudo-Anosov mapping classes and so assumes that the 
	# mapping class is not periodic. If not an AssumptionError is thrown.
	# If exact is set to True then this uses Symbolic_Computation.Perron_Frobenius_eigen() to return the exact 
	# invariant lamination along with the exact dilatation (as an algebraic_type). Again, if a good
	# enough approximation cannot be found to start the exact calculations with, this is detected and a
	# ComputationError thrown. Note: in most pseudo-Anosov cases < 15 iterations are needed, if it fails to
	# converge after 1000 iterations it's actually extremely likely that the map was not pseudo-Anosov.
	
	assert(encoding.source_triangulation == encoding.target_triangulation)
	if encoding.is_periodic():
		raise AssumptionError('Mapping class is periodic.')
	curves = key_curves(encoding.source_triangulation)
	
	def projective_difference(A, B, error_reciprocal):
		# Returns True iff the projective difference between A and B is less than 1 / error_reciprocal.
		A_sum, B_sum = sum(A), sum(B)
		return max(abs((p * B_sum) - q * A_sum) for p, q in zip(A, B)) * error_reciprocal < A_sum * B_sum 
	
	new_curves = [encoding * curve for curve in curves]
	for i in range(1000):
		new_curves, curves = [encoding * new_curve for new_curve in new_curves], new_curves
		if i > 3:  # Make sure to do at least n==4 iterations.
			for new_curve, curve in zip(new_curves, curves):
				if projective_difference(new_curve, curve, 1000000000):
					if curve == new_curve:
						return Lamination(encoding.source_triangulation, curve), 1
					elif exact:
						action_matrix, condition_matrix = encoding.applied_matrix(curve)
						try:
							eigenvector, eigenvalue = Perron_Frobenius_eigen(action_matrix)
						except AssumptionError:  # action_matrix was not Perron-Frobenius.
							raise ComputationError('Could not estimate invariant lamination.')
						if nonnegative_image(condition_matrix, eigenvector):  # Check that the projective fixed point is actually in this cell. 
							return Lamination(encoding.source_triangulation, eigenvector), eigenvalue
						else:
							raise ComputationError('Could not estimate invariant lamination.')  # If not then the curve failed to get close enough to the invariant lamination.
					else:
						return Lamination(encoding.source_triangulation, curve), float((encoding * curve).weight()) / curve.weight()
	else:
		raise ComputationError('Could not estimate invariant lamination.')

###########################################################################
# Some Tests #
###########################################################################

def determine_type(mapping_class):
	from Error import ComputationError, AssumptionError
	from time import time
	
	start_time = time()
	if mapping_class.is_periodic():
		print(' -- Periodic.')
	else:
		try:
			# We know the map cannot be periodic.
			# If this computation fails it will throw a ComputationError - the map was probably reducible.
			# In theory it could also fail by throwing an AssumptionError but we have already checked that the map is not periodic.
			lamination, dilatation = invariant_lamination(mapping_class, exact=True)
			# If this computation fails it will throw an AssumptionError - the map _is_ reducible.
			preperiodic, periodic, new_dilatation, lamination, isometry = lamination.splitting_sequence()
			print(' -- Pseudo-Anosov.')
		except ComputationError:
			print(' ~~ Probably reducible.')
		except AssumptionError:
			print(' -- Reducible.')
	print('      (Time: %0.4fs)' % (time() - start_time))
	return time() - start_time

def random_test(Example, word=None, num_trials=50):
	from time import time
	from Encoding import Id_Encoding_Sequence
	from Examples import build_example_mapping_class
	
	print('Start')
	
	times = []
	for k in range(num_trials):
		word, mapping_class = build_example_mapping_class(Example)
		print(word)
		times.append(determine_type(mapping_class))
	
	print('Times over %d trials: Average %0.4fs, Max %0.4fs' % (num_trials, sum(times) / len(times), max(times)))

if __name__ == '__main__':
	# from Examples import Example_24 as Example
	# T, twists = Example()
	# h = (twists['a']*twists['B']*twists['B']*twists['a']*twists['p'])**3
	# print('Lamination')
	# lamination, dilatation = h.stable_lamination(exact=True)
	# print('Splitting')
	# preperiodic, periodic, new_dilatation = compute_splitting_sequence(lamination)
	# print(len(preperiodic), len(periodic), compute_powers(dilatation, new_dilatation))
	
	# from Examples import Example_S_1_1 as Example
	from Examples import Example_S_1_2 as Example
	random_test(Example)
	# random_test(Example, 'aBC')
	# random_test(Example, 'aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa', num_trials=1)
	# cProfile.run('random_test(Example, 'aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa', num_trials=1)', sort='cumtime')
