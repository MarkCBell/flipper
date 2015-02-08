
''' A module for representing and manipulating maps between Triangulations.

Provides four classes: PartialFunction, BasicPLFunction, PLFunction and Encoding. '''

import flipper

NT_TYPE_PERIODIC = 'Periodic'
NT_TYPE_REDUCIBLE = 'Reducible'
NT_TYPE_PSEUDO_ANOSOV = 'Pseudo-Anosov'

class LFunction(object):
	''' Represents an invertible linear function from RR^m to RR^n. '''
	def __init__(self, action, inverse_action):
		self.action = action
		self.inverse_action = inverse_action
	def __call__(self, other):
		return self.action(other)
	def __mul__(self, other):
		return LFunction(self.action * other.action, other.inverse_action * self.inverse_action)
	def __pow__(self, power):
		return LFunction(self.action**power, self.inverse_action**power)
	def inverse(self):
		''' Return the inverse of this L function. '''
		
		return LFunction(self.inverse_action, self.action)

class PartialFunction(object):
	''' This represents a linear function from a subset of RR^m to RR^n.
	
	The function is defined on the subset where self.condition * vector >= 0,
	or everywhere if self.condition is None. Attempting to apply the function
	to a point not in the domain will raise a TypeError. '''
	def __init__(self, action, condition=None):
		assert(isinstance(action, flipper.kernel.Matrix))
		assert(condition is None or isinstance(condition, flipper.kernel.Matrix))
		
		self.action = action
		self.condition = condition if condition is not None else flipper.kernel.zero_matrix(self.action.width)
	
	def __mul__(self, other):
		if isinstance(other, PartialFunction):
			return PartialFunction(self.action * other.action, other.condition.join(self.condition * other.action))
		else:
			return NotImplemented
	
	def __call__(self, other):
		if self.condition.nonnegative_image(other):
			return self.action(other)
		
		raise TypeError('Object is not in domain.')

class BasicPLFunction(object):
	''' This represent the piecewise-linear map from RR^m to RR^n. '''
	def __init__(self, partial_functions, inverse_partial_functions=None):
		assert(all(isinstance(function, PartialFunction) for function in partial_functions))
		assert(inverse_partial_functions is None or all(isinstance(function, PartialFunction) for function in inverse_partial_functions))
		assert(len(partial_functions) > 0)
		
		self.partial_functions = partial_functions
		self.inverse_partial_functions = inverse_partial_functions if inverse_partial_functions is not None else []
		self.zeta = self.partial_functions[0].action.width
	
	def __iter__(self):
		return iter(self.partial_functions)
	def __len__(self):
		return len(self.partial_functions)
	def __getitem__(self, index):
		return self.partial_functions[index]
	
	def __mul__(self, other):
		if isinstance(other, BasicPLFunction):
			partial_functions = [func1 * func2 for func1 in self for func2 in other]
			inverse_partial_functions = [func2 * func1 for func1 in self.inverse_partial_functions for func2 in other.inverse_partial_functions]
			return BasicPLFunction(partial_functions, inverse_partial_functions)
		else:
			return NotImplemented
	
	def __call__(self, other):
		for function in self.partial_functions:
			try:
				return function(other)
			except TypeError:
				pass
		raise TypeError('Object is not in domain.')
	
	def inverse(self):
		''' Return the inverse of this PL function. '''
		
		if self.inverse_partial_functions is None:
			raise TypeError('Function is not invertible.')
		
		return BasicPLFunction(self.inverse_partial_functions, self.partial_functions)
	def applied_index(self, vector):
		''' Return the index of the partial function that would be applied to this vector. '''
		
		for index, function in enumerate(self.partial_functions):
			try:
				function(vector)
				return index
			except TypeError:
				pass
		
		raise TypeError('Point is not in domain.')

class PLFunction(object):
	''' This represents the composition of a sequence of BasicPLFunctions. '''
	def __init__(self, sequence):
		assert(isinstance(sequence, (list, tuple)))
		assert(all(isinstance(element, BasicPLFunction) for element in sequence))
		
		# Collapse away the PLFunctions of length 1 (the ones with no branching).
		new_sequence = []
		current = None
		for function in sequence:
			if current is None:
				current = function
			else:
				current = current * function
			if len(current) > 1:
				new_sequence.append(current)
				current = None
		if current is not None:
			new_sequence.append(current)
		sequence = new_sequence
		
		self.sequence = sequence
		self.zeta = self.sequence[0].zeta
	
	def __len__(self):
		return len(self.sequence)
	def __iter__(self):
		return iter(self.sequence)
	def __getitem__(self, key):
		return self.sequence[key]
	def __hash__(self):
		return hash(tuple(self.sequence))
	def __call__(self, vector):
		for A in reversed(self):
			vector = A(vector)
		return vector
	def __mul__(self, other):
		if isinstance(other, PLFunction):
			return PLFunction(self.sequence + other.sequence)
		else:
			return NotImplemented
	def __pow__(self, power):
		if power == 0:
			return self * self.inverse()  # Just to make sure we remember the dimensions.
		elif power > 0:
			return PLFunction(self.sequence * power)
		else:
			return PLFunction(self.sequence * abs(power)).inverse()
	
	def inverse(self):
		''' Return the inverse of this encoding. '''
		
		return PLFunction([A.inverse() for A in reversed(self)])
	
	def find_indices(self, vector, count_all=True):
		''' Return the list of indices describing the cell this lamination lies in. '''
		
		indices = []
		for A in reversed(self):
			if count_all or len(A) > 1: indices.append(A.applied_index(vector))  # We might not record ones with no choice.
			vector = A(vector)
		
		return indices
	
	def find_indices_compressed(self, vector):
		''' Return the list of indices describing the cell this lamination lies in as a base64 string. '''
		
		return flipper.kernel.utilities.encode_binary(self.find_indices(vector, count_all=False))
	
	def applied_function(self, vector):
		''' Return the partial function that will be applied to the lamination. '''
		
		return self.expand_indices(self.find_indices(vector))
	
	
	def expand_indices(self, indices):
		''' Return the partial function corresponding to the given list of indices.
		
		Note: Given indices = [a_0, ..., a_k] this returns choice[a_k] * ... * choice[a_0].
		Be careful about the order in which you give the indices. '''
		
		As = flipper.kernel.id_matrix(self.zeta)
		Cs = flipper.kernel.zero_matrix(self.zeta, 1)
		for E, i in zip(reversed(self), indices):
			Cs = Cs.join(E[i].condition * As)
			As = E[i].action * As
		
		return PartialFunction(As, Cs)

class Encoding(object):
	''' This represents a map between two Triagulations.
	
	If it maps to and from the same triangulation then it represents
	a mapping class. This can be checked using self.is_mapping_class().
	
	The map is given by a sequence of PLFunctions whose composition is
	the action on the edge weights. '''
	def __init__(self, source_triangulation, target_triangulation, geometric, algebraic, name=None):
		assert(isinstance(source_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(target_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(geometric, PLFunction))
		assert(isinstance(algebraic, LFunction))
		assert(name is None or isinstance(name, flipper.StringType))
		
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.geometric = geometric
		self.algebraic = algebraic
		self.name = name
		self.zeta = self.source_triangulation.zeta
		
		self._cache = {}  # For caching hard to compute results.
	
	def is_mapping_class(self):
		''' Return if this encoding is a mapping class.
		
		That is, if it maps to the triangulation it came from. '''
		
		return self.source_triangulation == self.target_triangulation
	
	def __len__(self):
		return len(self.geometric)
	def __repr__(self):
		return str(self)
	def __str__(self):
		return self.name
	
	def __eq__(self, other):
		if isinstance(other, Encoding):
			if self.source_triangulation != other.source_triangulation or \
				self.target_triangulation != other.target_triangulation:
				raise ValueError('Cannot compare Encodings between different triangulations.')
			
			return all(self(curve) == other(curve) for curve in self.source_triangulation.key_curves())
		else:
			return NotImplemented
	def __ne__(self, other):
		return not (self == other)
	def is_homologous_to(self, other):
		''' Return if this encoding and other induce the same map from
		H_1(source_triangulation) to H_1(target_triangulation). '''
		
		if isinstance(other, Encoding):
			if self.source_triangulation != other.source_triangulation or \
				self.target_triangulation != other.target_triangulation:
				raise ValueError('Cannot compare Encodings between different triangulations.')
			
			return all(self(curve).is_homologous_to(other(curve)) for curve in self.source_triangulation.key_curves())
		else:
			return NotImplemented
	
	def __call__(self, other):
		if isinstance(other, flipper.kernel.Lamination):
			if self.source_triangulation != other.triangulation:
				raise ValueError('Cannot apply an Encoding to a Lamination on a triangulation other than source_triangulation.')
			geometric = self.geometric(other.geometric)
			algebraic = self.algebraic(other.algebraic)
			# If other has no peripheral components then neither does self(other).
			# Hence we can skip this check and save ~25% of the work.
			return self.target_triangulation.lamination(geometric, algebraic, remove_peripheral=False)
		else:
			return NotImplemented
	def __mul__(self, other):
		if isinstance(other, Encoding):
			if self.source_triangulation != other.target_triangulation:
				raise ValueError('Cannot compose Encodings over different triangulations.')
			return Encoding(other.source_triangulation, self.target_triangulation,
				self.geometric * other.geometric, self.algebraic * other.algebraic,
				other.name + '.' + self.name if self.name is not None and other.name is not None else None)
		else:
			return NotImplemented
	def __pow__(self, k):
		assert(self.is_mapping_class())
		if k == 0:
			return self.source_triangulation.id_encoding()
		elif k > 0:
			return Encoding(self.source_triangulation, self.target_triangulation, self.geometric**k, self.algebraic**k)
		else:
			return self.inverse()**abs(k)
	
	def inverse(self):
		''' Return the inverse of this encoding. '''
		
		return Encoding(self.target_triangulation, self.source_triangulation, self.geometric.inverse(), self.algebraic.inverse())
	
	def closing_isometries(self):
		''' Return all the possible isometries from self.target_triangulation to self.source_triangulation.
		
		These are the maps that can be used to close this into a mapping class. '''
		
		return self.target_triangulation.isometries_to(self.source_triangulation)
	
	def order(self):
		''' Return the order of this mapping class.
		
		If this has infinite order then return 0.
		
		This encoding must be a mapping class. '''
		
		assert(self.is_mapping_class())
		
		# We could do:
		# for i in range(self.source_triangulation.max_order):
		#	if self**(i+1) == self.source_triangulation.id_encoding():
		#		return i+1
		# But this is quadratic in the order so instead we do:
		curves = self.source_triangulation.key_curves()
		possible_orders = set(range(1, self.source_triangulation.max_order+1))
		for curve in curves:
			curve_image = curve
			for i in range(1, max(possible_orders)+1):
				curve_image = self(curve_image)
				if curve_image != curve:
					possible_orders.discard(i)
					if not possible_orders: return 0  # No finite orders remain so we are infinite order.
		
		return min(possible_orders)
	
	def is_periodic(self):
		''' Return if this encoding has finite order.
		
		This encoding must be a mapping class. '''
		
		return self.order() > 0
	
	def invariant_lamination_uncached(self):
		''' Return a rescaling constant and projectively invariant lamination.
		
		Assumes that the mapping class is pseudo-Anosov.
		
		To find this we start with a curve on the surface and repeatedly apply
		the map until it appear to be projectively similar to a previous iteration.
		Finally it uses:
			flipper.kernel.symboliccomputation.perron_frobenius_eigen()
		to find the nearby projective fixed point. If it cannot find one then it
		raises a ComputationError.
		
		Note: In most pseudo-Anosov cases < 15 iterations are needed, if it fails
		to converge after many iterations and a ComputationError is thrown then it
		is extremely likely that the mapping class was not pseudo-Anosov.
		
		This encoding must be a mapping class. '''
		
		# Suppose that f_1, ..., f_m, g_1, ..., g_n, t_1, ..., t_k, p is the Thurston decomposition of self.
		# That is: f_i are pA on subsurfaces, g_i are periodic on subsurfaces, t_i are Dehn twist along the curve of
		# the canonical curve system and p is a permutation of the subsurfaces.
		# Additionally, let S_i be the subsurface corresponding to f_i, P_i correspond to g_i and A_i correspond to t_i.
		# Finally, let x_0 be a curve on the surface and define x_i := self(x_{i-1}).
		#
		# The algorithm covers 3 cases:  (Note we reorder the subsurfaces for ease of notation.)
		#  1) x_0 meets at S_1, ..., S_m',
		#  2) x_0 meets no S_i but meets A_1, ..., A_k', and
		#  3) x_0 meets no S_i or A_i, that is x_0 is contained in a P_1.
		#
		# In the first case, x_i will converge exponentially to the stable laminations of f_1, ..., f_m'.
		# Here the convergence is so fast we need only a few iterations.
		#
		# In the second case x_i will converge linearly to c, the cores of A_1, ..., A_k'. To speed this up
		# we note that x_i = i*c + O(1), so rescale x_i by 1/i, round and check if this is c.
		#
		# Finally, the third case happens if and only if x_i is periodic. In this case self must be
		# periodic or reducible. We test for periodicity at the beginning hence if we ever find a curve
		# fixed by a power of self then we must reducible.
		
		assert(self.is_mapping_class())
		
		# We start with a fast test for periodicity.
		# This isn't needed but it means that if we ever discover that
		# self is not pA then it must be reducible.
		if self.is_periodic():
			raise flipper.AssumptionError('Mapping class is periodic.')
		
		triangulation = self.source_triangulation
		max_order = triangulation.max_order
		curves = [triangulation.key_curves()[0]]
		
		# A little helper function to determine how much two vectors differ by.
		def projective_difference(A, B, error_reciprocal):
			''' Return if the projective difference between A and B is less than 1 / error_reciprocal. '''
			
			A_sum, B_sum = sum(A), sum(B)
			return max(abs((p * B_sum) - (q * A_sum)) for p, q in zip(A, B)) * error_reciprocal < A_sum * B_sum
		
		# We will remember the cells we've tested to avoid recalculating their eigenvectors again.
		tested_cells = []
		for i in range(100):
			new_curve = self(curves[-1])
			# print(new_curve)
			
			# Check if we have seen this curve before.
			if new_curve in curves:  # self**(i-j)(curve) == curve, so self is reducible.
				raise flipper.AssumptionError('Mapping class is reducible.')
			
			curves.append(new_curve)
			for j in range(1, min(max_order, len(curves))):
				old_curve = curves[-j-1]
				if projective_difference(new_curve, old_curve, 100):
					average_curve = sum(curves[-j:])
					partial_function = (self**j).geometric.applied_function(average_curve.geometric)
					if partial_function not in tested_cells:
						tested_cells.append(partial_function)
						action_matrix, condition_matrix = partial_function.action, partial_function.condition
						try:
							eigenvalue, eigenvector = flipper.kernel.symboliccomputation.directed_eigenvector(
								action_matrix, condition_matrix, average_curve)
						except flipper.ComputationError:
							pass  # Could not find an eigenvector in the cone.
						except flipper.AssumptionError:
							raise flipper.AssumptionError('Mapping class is reducible.')
						else:
							# Test if the vector we found lies in the cone given by the condition matrix.
							# We could also use: invariant_lamination.projectively_equal(self(invariant_lamination))
							# but this is much faster.
							if flipper.kernel.matrix.nonnegative(eigenvector) and condition_matrix.nonnegative_image(eigenvector):
								# If it does then we have a projectively invariant lamination.
								invariant_lamination = triangulation.lamination(eigenvector)
								if not invariant_lamination.is_empty():  # But it might have been entirely peripheral.
									if j == 1:
										# We could raise an AssumptionError as this actually shows that self is reducible.
										return eigenvalue, invariant_lamination
									else:
										if not invariant_lamination.projectively_equal(self(invariant_lamination)):
											raise flipper.AssumptionError('Mapping class is reducible.')
										else:
											# We possibly could reconstruct something here but all the numbers are
											# in the wrong number field. It's easier to just keep going.
											pass
					break
			
			# See if we are close to an invariant curve.
			# Build some different vectors which are good candidates for reducing curves.
			vectors = [[x - y for x, y in zip(new_curve, old_curve)] for old_curve in curves[max(len(curves) - max_order, 0):]]
			
			for vector in vectors:
				new_small_curve = small_curve = triangulation.lamination(vector, algebraic=[0] * self.zeta)
				if not small_curve.is_empty():
					for j in range(1, max_order+1):
						new_small_curve = self(new_small_curve)
						if new_small_curve == small_curve:
							if j == 1:
								# We could raise an AssumptionError in this case too as this also shows that self is reducible.
								return 1, small_curve
							else:
								raise flipper.AssumptionError('Mapping class is reducible.')
		
		raise flipper.ComputationError('Could not estimate invariant lamination.')
	
	def invariant_lamination(self):
		''' A version of self.invariant_lamination_uncached with caching. '''
		
		if 'invariant_lamination' not in self._cache:
			try:
				self._cache['invariant_lamination'] = self.invariant_lamination_uncached()
			except (flipper.AssumptionError, flipper.ComputationError) as error:
				self._cache['invariant_lamination'] = error
		
		if isinstance(self._cache['invariant_lamination'], Exception):
			raise self._cache['invariant_lamination']
		else:
			return self._cache['invariant_lamination']
	
	def splitting_sequences(self, take_roots=False):
		''' Return a list of splitting sequences associated to this mapping class.
		
		Assumes (and checks) that the mapping class is pseudo-Anosov.
		
		This encoding must be a mapping class. '''
		
		assert(self.is_mapping_class())
		
		if self.is_periodic():  # Actually this test is redundant but it is faster to test it now.
			raise flipper.AssumptionError('Mapping class is not pseudo-Anosov.')
		
		dilatation, lamination = self.invariant_lamination()  # This could fail with a flipper.ComputationError.
		try:
			splittings = lamination.splitting_sequences(target_dilatation=None if take_roots else dilatation)
		except flipper.AssumptionError:  # Lamination is not filling.
			raise flipper.AssumptionError('Mapping class is not pseudo-Anosov.')
		
		return splittings
	
	def splitting_sequence(self):
		''' Return the splitting sequence associated to this mapping class.
		
		Assumes (and checks) that the mapping class is pseudo-Anosov.
		
		This encoding must be a mapping class. '''
		
		# We get a list of all possible splitting sequences from
		# self.splitting_sequences(). From there we use the fact that each
		# of these differ by a periodic mapping class, which cannot be in the
		# Torelli subgroup and so acts non-trivially on H_1(S).
		# Thus we look for the map whose action on H_1(S) is conjugate to self
		# via splitting.preperiodic.
		
		# To do this we take sufficiently many curves (the key_curves() of the
		# underlying triangulation) and look for the splitting sequence in which
		# they are mapped to homologous curves by:
		#	preperiodic . self^{-1} and periodic . preperiodic.
		# Note that we must use self.inverse().
		
		for splitting in self.splitting_sequences():
			if (splitting.preperiodic * self.inverse()).is_homologous_to(splitting.mapping_class * splitting.preperiodic):
				return splitting
	
	def nielsen_thurston_type(self):
		''' Return the Nielsen--Thurston type of this encoding.
		
		This encoding must be a mapping class. '''
		
		assert(self.is_mapping_class())
		
		if self.is_periodic():
			return NT_TYPE_PERIODIC
		
		try:
			# This can also fail with a flipper.ComputationError if
			# self.invariant_lamination() fails to find an invariant lamination.
			self.splitting_sequence()
		except flipper.AssumptionError:
			return NT_TYPE_REDUCIBLE
		
		return NT_TYPE_PSEUDO_ANOSOV
	
	def is_Abelian(self):
		''' Return if this mapping class corresponds to an Abelian differential.
		
		This is an Abelian differential (rather than a quadratic differential) if and
		only if its stable lamination is orientable.
		
		Assumes (and checks) that the mapping class is pseudo-Anosov.
		
		This encoding must be a mapping class. '''
		
		# Because the lamination meets each triangle in a bipod, it is orientable
		# if and only if each singularity of the lamination has an even number of prongs.
		
		stratum = self.stratum()
		return all(stratum[singularity] % 2 == 0 for singularity in stratum)
	
	def dilatation(self):
		''' Return the dilatation of this mapping class.
		
		This encoding must be a mapping class. '''
		
		assert(self.is_mapping_class())
		
		if self.nielsen_thurston_type() != NT_TYPE_PSEUDO_ANOSOV:
			return 0
		else:
			lmbda, _ = self.invariant_lamination()
			return lmbda
	
	def is_conjugate_to(self, other):
		''' Return if this mapping class is conjugate to other.
		
		It would also be straightforward to check if self^i ~~ other^j
		for some i, j.
		
		Both encodings must be mapping classes.
		
		Assumes that both mapping classes are pseudo-Anosov. '''
		
		assert(self.is_mapping_class())
		assert(isinstance(other, Encoding))
		assert(other.is_mapping_class())
		
		# Nielsen-Thurston type is a conjugacy invariant.
		if self.nielsen_thurston_type() != other.nielsen_thurston_type():
			return False
		
		if self.nielsen_thurston_type() == NT_TYPE_PERIODIC:
			if self.order() != other.order():
				return False
			
			# We could also use action on H_1(S) as a conjugacy invaraiant.
			
			raise flipper.AssumptionError('Mapping class is periodic.')
		elif self.nielsen_thurston_type() == NT_TYPE_REDUCIBLE:
			# There's more to do here.
			
			raise flipper.AssumptionError('Mapping class is reducible.')
		elif self.nielsen_thurston_type() == NT_TYPE_PSEUDO_ANOSOV:
			splitting1 = self.splitting_sequence()
			splitting2 = other.splitting_sequence()
			
			mapping_class1 = splitting1.mapping_class
			
			# The product of these is mapping_class2 = splitting2.mapping_class.
			encodings2 = splitting2.encodings[splitting2.index:] + [splitting2.isometry.encode()]
			for i in range(len(encodings2)):
				mapping_class2 = flipper.kernel.product(encodings2[i:] + encodings2[:i])
				
				# Would could get away with only looking at those that projectively preserve the
				# lamination but that involves comparing algebraic numbers and so is generally
				# slower in practice.
				for isom in mapping_class1.source_triangulation.isometries_to(mapping_class2.source_triangulation):
					if isom.encode() * mapping_class1 == mapping_class2 * isom.encode():
						return True
			
			return False
	
	def stratum(self):
		''' Return a dictionary mapping each singularity to its stratum order.
		
		This is the number of bipods incident to the vertex.
		
		Assumes (and checks) that this mapping class is pseudo-Anosov.
		
		This encoding must be a mapping class. '''
		
		assert(self.is_mapping_class())
		
		# This can fail with an flipper.AssumptionError.
		return self.splitting_sequence().lamination.stratum()
	
	def bundle(self):
		''' Return the bundle associated to this mapping class.
		
		Assumes (and checks) that this mapping class is pseudo-Anosov.
		
		This encoding must be a mapping class. '''
		
		assert(self.is_mapping_class())
		
		# This can fail with an flipper.AssumptionError.
		return self.splitting_sequence().bundle()


def id_l_function(dim):
	''' Return the identity linear function on RR^dim. '''
	
	id_matrix = flipper.kernel.id_matrix(dim)
	return LFunction(id_matrix, id_matrix)

def id_pl_function(dim):
	''' Return the identity piecewise-linear function on RR^dim. '''
	
	id_partial = PartialFunction(flipper.kernel.id_matrix(dim))
	f = BasicPLFunction([id_partial], [id_partial])
	return PLFunction([f])

def zero_pl_function(width, height=None):
	''' Return the zero piecewise-linear function from RR^width to RR^height. '''
	
	if height is None: height = width
	zero_partial = PartialFunction(flipper.kernel.zero_matrix(width, height))
	zero_partial_inverse = PartialFunction(flipper.kernel.zero_matrix(height, width))
	f = BasicPLFunction([zero_partial], [zero_partial_inverse])
	return PLFunction([f])

