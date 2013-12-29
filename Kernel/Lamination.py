
# We can also produce Laminations using:
#	1) empty_laminaiton(triangulation),
#	2) regular_neighbourhood(triangulation, edge_index),
#	3) key_curves(triangulation), and
#	4) invariant_lamination(encoding)

from itertools import product, combinations

from Flipper.Kernel.AbstractTriangulation import Abstract_Triangulation
from Flipper.Kernel.Matrix import nonnegative, nonnegative_image, nontrivial
from Flipper.Kernel.Isometry import Isometry, all_isometries
from Flipper.Kernel.Error import AbortError, ComputationError, AssumptionError, ApproximationError
from Flipper.Kernel.SymbolicComputation import Perron_Frobenius_eigen, minimal_polynomial_coefficients, algebraic_simplify, algebraic_string, algebraic_type, symbolic_degree, symbolic_height
from Flipper.Kernel.AlgebraicApproximation import algebraic_approximation_from_symbolic
from Flipper.Kernel.NumberSystem import number_system_basis

# The common denominator to switch Algebraic_Approximations to before hashing.
HASH_DENOMINATOR = 5

class Lamination:
	def __init__(self, abstract_triangulation, vector):
		self.abstract_triangulation = abstract_triangulation
		self.zeta = self.abstract_triangulation.zeta
		self.vector = [algebraic_simplify(v) for v in vector]
		self.labels = [algebraic_string(v) for v in self.vector]
	
	def copy(self):
		return Lamination(self.abstract_triangulation, list(self.vector))
	
	def __repr__(self):
		return '[' + ', '.join(self.labels) + ']'
	
	def __iter__(self):
		return iter(self.vector)
	
	def __getitem__(self, index):
		return self.vector[index]
	
	def __rmul__(self, other):
		if isinstance(other, Isometry) and other.source_triangulation == self.abstract_triangulation:
			return Lamination(other.target_triangulation, [self[j] for i in range(self.zeta) for j in range(self.zeta) if i == other.edge_map[j]])
		else:
			return NotImplemented
	
	def __eq__(self, other):
		return self.abstract_triangulation == other.abstract_triangulation and all(bool(v == w) for v, w in zip(self, other))
	
	def weight(self):
		return algebraic_simplify(sum(self.vector))
	
	def is_multicurve(self):
		if not all(v == int(v) for v in self.vector): return False  # Redundant?
		if not nontrivial(self.vector): return False
		if not nonnegative(self.vector): return False
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
	
	def is_good_curve(self):
		# This is based off of Source.Encoding.encode_twist(). See the documentation there as to why this works.
		if not self.is_multicurve(): return False
		
		lamination = self.copy()
		
		time_since_last_weight_loss = 0
		old_weight = lamination.weight()
		while lamination.weight() > 2:
			edge_index = min([i for i in range(lamination.zeta) if lamination[i] > 0 and lamination.abstract_triangulation.edge_is_flippable(i)], key=lambda i: lamination.weight_difference_flip_edge(i))
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
	
	def is_pants_boundary(self):
		# This is based off of Source.Encoding.encode_halftwist(). See the documentation there as to why this works.
		if not self.is_good_curve(): return False
		
		lamination = self.copy()
		
		while lamination.weight() > 2:
			edge_index = min([i for i in range(lamination.zeta) if lamination[i] > 0], key=lambda i: lamination.weight_difference_flip_edge(i))
			lamination = lamination.flip_edge(edge_index)
		
		e1, e2 = [edge_index for edge_index in range(lamination.zeta) if lamination[edge_index] > 0]
		x, y = [edge_indices for edge_indices in lamination.abstract_triangulation.find_indicies_of_square_about_edge(e1) if edge_indices != e2]
		for triangle in lamination.abstract_triangulation:
			if (x in triangle or y in triangle) and len(set(triangle)) == 2:
				return True
		
		return False
	
	def weight_difference_flip_edge(self, edge_index):
		a, b, c, d = self.abstract_triangulation.find_indicies_of_square_about_edge(edge_index)
		return max(self[a] + self[c], self[b] + self[d]) - self[edge_index] - self[edge_index]
	
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
	
	# @profile
	def splitting_sequence(self):
		# Assumes that self is a filling lamination. If not, it will discover this along the way and throw an 
		# AssumptionError
		# We assume that self is given as a list of algebraic numbers. 
		# We continually use SymbolicComputation.algebraic_simplify() just to be safe.
		# This assumes that the edges are labelled 0, ..., abstract_triangulation.zeta-1, this is a very sane labelling system.
		
		def projective_weights(x):
			s = algebraic_simplify(1 / sum(x))
			return tuple([algebraic_simplify(v * s) for v in x])
		
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
			
			# Check if it (projectively) matches a lamination we've already seen.
			target = hash_lamination(lamination)
			current_triangulation = lamination.abstract_triangulation
			current_projective_weights = projective_weights(lamination)
			if target in seen:
				for index, old_lamination, old_projective_weights in seen[target]:
					old_triangulation = old_lamination.abstract_triangulation
					isometries = []
					for isometry in all_isometries(current_triangulation, old_triangulation):
						permuted_old_projective_weights = tuple([old_projective_weights[isometry.edge_map[i]] for i in range(lamination.zeta)])
						if current_projective_weights == permuted_old_projective_weights:
							# Return: the pre-periodic part, the periodic part, the dilatation.
							isometries.append(isometry)
					if len(isometries) > 0:
						return flipped[:index], flipped[index:], algebraic_simplify(old_lamination[isometry.edge_map[0]] / lamination[0]), old_lamination, isometries
				seen[target].append([len(flipped), lamination, current_projective_weights])
			else:
				seen[target] = [[len(flipped), lamination, current_projective_weights]]
	
	# @profile
	def splitting_sequence2(self):
		# Assumes that self is a filling lamination. If not, it will discover this along the way and throw an 
		# AssumptionError
		# We assume that self is given as a list of algebraic numbers. 
		# We continually use SymbolicComputation.algebraic_simplify() just to be safe.
		# This assumes that the edges are labelled 0, ..., abstract_triangulation.zeta-1, this is a very sane labelling system.
		
		def projectively_equal(v1, v2):
			return all(v1[i] * v2[0] == v2[i] * v1[0] for i in range(1, len(v1)))
		
		def projective_weights(x):
			s = x.weight()
			return tuple(v / s for v in lamination)
		
		def hash_lamination(x):
			return tuple(sorted([v.interval.change_denominator(HASH_DENOMINATOR) for v in projective_weights(x)], key=lambda a: a.lower))
		
		# Check if vector is obviously reducible.
		if any(v == 0 for v in self.vector):
			raise AssumptionError('Lamination is not filling.')
		
		initial_lamination = self.puncture_trigons()  # Puncture out all trigon regions.
		
		# Replace the lamination with a close approximation.
		
		w = initial_lamination.weight()
		places = 10
		while True:
			try:
				lamination = Lamination(initial_lamination.abstract_triangulation, [algebraic_approximation_from_symbolic(algebraic_simplify(x / w), places) for x in initial_lamination])
				
				flipped = []
				seen = [lamination]
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
					
					# Check if it (projectively) matches a lamination we've already seen.
					current_triangulation = lamination.abstract_triangulation
					for index, old_lamination in enumerate(seen):
						old_triangulation = old_lamination.abstract_triangulation
						isometries = []
						for isometry in all_isometries(current_triangulation, old_triangulation):
							if projectively_equal((isometry * lamination).vector, old_lamination.vector):
								isometries.append(isometry)
						if len(isometries) > 0:
							# return flipped[:index], flipped[index:], algebraic_simplify(old_lamination[isometry.edge_map[0]] / lamination[0]), old_lamination, isometries
							return flipped[:index], flipped[index:], 1, old_lamination, isometries
					else:
						seen.append(lamination)
			except ApproximationError:
				# We just needed more precision.
				print('Calculations failed when using %d places.' % places)
				places = places * 2
	
	# @profile
	def splitting_sequence3(self):
		# Assumes that self is a filling lamination. If not, it will discover this along the way and throw an 
		# AssumptionError
		# We assume that self is given as a list of algebraic numbers. 
		# We continually use SymbolicComputation.algebraic_simplify() just to be safe.
		# This assumes that the edges are labelled 0, ..., abstract_triangulation.zeta-1, this is a very sane labelling system.
		
		def projectively_equal(v1, v2):
			for i in range(1, len(v1)):
				print(v1[i] * v2[0])
				print(v2[i] * v1[0])
			return all(v1[i] * v2[0] == v2[i] * v1[0] for i in range(1, len(v1)))
		
		def hash_lamination(x):
			s = x.weight()
			return tuple(sorted([(v / s).interval.change_denominator(HASH_DENOMINATOR).tuple() for v in x]))
		
		# Check if vector is obviously reducible.
		if any(v == 0 for v in self.vector):
			raise AssumptionError('Lamination is not filling.')
		
		initial_lamination = self.puncture_trigons()  # Puncture out all trigon regions.
		
		# Replace the lamination with a close approximation.
		
		w = initial_lamination.weight()
		places = 10
		while True:
			try:
				# Start by taking an approximation of the initial lamination which is correct to places decimal places.
				lamination = Lamination(initial_lamination.abstract_triangulation, [algebraic_approximation_from_symbolic(algebraic_simplify(x / w), places) for x in initial_lamination])
				
				flipped = []
				seen = {hash_lamination(lamination):[(0, lamination)]}
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
					
					# Check if it (projectively) matches a lamination we've already seen.
					target = hash_lamination(lamination)
					if target in seen:
						for index, old_lamination in seen[target]:
							isometries = [isometry for isometry in all_isometries(lamination.abstract_triangulation, old_lamination.abstract_triangulation) if projectively_equal((isometry * lamination).vector, old_lamination.vector)]
							if len(isometries) > 0:
								return flipped[:index], flipped[index:], old_lamination[isometries[0].edge_map[0]] / lamination[0], old_lamination, isometries
						seen[target].append((len(flipped), lamination))
					else:
						seen[target] = [(len(flipped), lamination)]
				
			except ApproximationError:
				# We just needed more precision.
				print('Calculations failed after %d steps when using %d places.' % (len(flipped), places))
				places = places * 2
	
	# @profile
	def splitting_sequence4(self):
		# Assumes that self is a filling lamination. If not, it will discover this along the way and throw an 
		# AssumptionError
		# We assume that self is given as a list of algebraic numbers. 
		# We continually use SymbolicComputation.algebraic_simplify() just to be safe.
		# This assumes that the edges are labelled 0, ..., abstract_triangulation.zeta-1, this is a very sane labelling system.
		
		def projectively_equal(v1, v2):
			return all(v1[i].algebraic_approximation(factor=2) * v2[0].algebraic_approximation(factor=2) == v2[i].algebraic_approximation(factor=2) * v1[0].algebraic_approximation(factor=2) for i in range(1, len(v1)))
		
		def hash_lamination(x):
			s = x.weight().algebraic_approximation(factor=2)
			return tuple(sorted([(v.algebraic_approximation(factor=2) / s).interval.change_denominator(HASH_DENOMINATOR).tuple() for v in x]))
		
		# Check if vector is obviously reducible.
		if any(v == 0 for v in self.vector):
			raise AssumptionError('Lamination is not filling.')
		
		initial_lamination = self.puncture_trigons()  # Puncture out all trigon regions.
		
		w = initial_lamination.weight()
		lamination = Lamination(initial_lamination.abstract_triangulation, number_system_basis([algebraic_simplify(v / w) for v in initial_lamination]))
		
		flipped = []
		seen = {hash_lamination(lamination):[(0, lamination)]}
		while True:
			edge_index = max(range(lamination.zeta), key=lambda i: lamination[i])  # Find the index of the largest entry
			lamination = lamination.flip_edge(edge_index)
			
			if lamination[edge_index].algebraic_approximation() == 0:
				try:
					# If this fails it's because the lamination isn't filling.
					lamination = lamination.collapse_trivial_weight(edge_index)
				except AssumptionError:
					raise AssumptionError('Lamination is not filling.')
			
			flipped.append(edge_index)
			
			# Check if it (projectively) matches a lamination we've already seen.
			target = hash_lamination(lamination)
			if target in seen:
				for index, old_lamination in seen[target]:
					isometries = [isometry for isometry in all_isometries(lamination.abstract_triangulation, old_lamination.abstract_triangulation) if projectively_equal((isometry * lamination).vector, old_lamination.vector)]
					if len(isometries) > 0:
						return flipped[:index], flipped[index:], old_lamination[isometries[0].edge_map[0]].algebraic_approximation(factor=2) / lamination[0].algebraic_approximation(factor=2), old_lamination, isometries
				seen[target].append((len(flipped), lamination))
			else:
				seen[target] = [(len(flipped), lamination)]
	
	def is_filling(self):
		try:
			self.splitting_sequence()
		except AssumptionError:
			return False
		else:
			return True

#### Some special Laminations we know how to build.

def empty_lamination(triangulation):
	return Lamination(triangulation, [0] * triangulation.zeta)

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
	# If exact is set to True then this uses SymbolicComputation.Perron_Frobenius_eigen() to return the exact 
	# projectively invariant lamination along with the exact dilatation (as an algebraic_type). Again, if a good
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

