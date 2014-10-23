
''' A module for representing and manipulating maps between Triangulations.

Provides two classes: PartialFunction, PLFunction and Encoding. '''

import flipper

NT_TYPE_PERIODIC = 'Periodic'
NT_TYPE_REDUCIBLE = 'Reducible'
NT_TYPE_PSEUDO_ANOSOV = 'Pseudo-Anosov'

class PartialFunction(object):
	''' This represents a linear function from a subset of RR^m to RR^n.
	
	The function is defined on the subset where self.condition * vector >= 0,
	or everywhere if self.condition is None. Attempting to apply the function
	to a point not in the domain will raise a TypeError. '''
	def __init__(self, action, condition=None):
		assert(isinstance(action, flipper.kernel.Matrix))
		assert(condition is None or isinstance(condition, flipper.kernel.Matrix))
		
		self.action = action
		self.condition = condition if condition is not None else flipper.kernel.empty_matrix()
	
	def __str__(self):
		return '%s\n%s' % (self.action, self.condition)
	
	def __eq__(self, other):
		if isinstance(other, PartialFunction):
			return self.action == other.action and self.condition == other.condition
		else:
			return NotImplemented
	def __ne__(self, other):
		return not (self == other)
	
	def __mul__(self, other):
		if isinstance(other, PartialFunction):
			return PartialFunction(self.action * other.action, other.condition.join(self.condition * other.action))
		else:
			return NotImplemented
	
	def __call__(self, other):
		if self.condition.nonnegative_image(other):
			return self.action * other
		
		raise TypeError('Object is not in domain.')

class PLFunction(object):
	''' This represent the piecewise-linear map from RR^m to RR^n. '''
	def __init__(self, partial_functions, inverse_partial_functions=None):
		assert(all(isinstance(function, PartialFunction) for function in partial_functions))
		assert(inverse_partial_functions is None or all(isinstance(function, PartialFunction) for function in inverse_partial_functions))
		assert(len(partial_functions) > 0)
		
		self.partial_functions = partial_functions
		self.inverse_partial_functions = inverse_partial_functions if inverse_partial_functions is not None else []
	
	def __iter__(self):
		return iter(self.partial_functions)
	def __str__(self):
		return '\n'.join(str(function) for function in self.partial_functions)
	def __len__(self):
		return len(self.partial_functions)
	def __getitem__(self, index):
		return self.partial_functions[index]
	
	def __mul__(self, other):
		if isinstance(other, PLFunction):
			partial_functions = [func1 * func2 for func1 in self for func2 in other]
			inverse_partial_functions = [func2 * func1 for func1 in self.inverse_partial_functions for func2 in other.inverse_partial_functions]
			return PLFunction(partial_functions, inverse_partial_functions)
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
		
		if not self.inverse_partial_functions:
			raise TypeError('Function is not invertible.')
		
		return PLFunction(self.inverse_partial_functions, self.partial_functions)
	def applied_index(self, vector):
		''' Return the index of the partial function that would be applied to this vector. '''
		
		for index, function in enumerate(self.partial_functions):
			try:
				function(vector)
				return index
			except TypeError:
				pass
		
		raise TypeError('Point is not in domain.')

class Encoding(object):
	''' This represents a map between two Triagulations.
	
	If it maps to and from the same triangulation then it represents
	a mapping class. This can be checked using self.is_mapping_class().
	
	The map is given by a sequence of PLFunctions whose composition is
	the action on the edge weights. '''
	def __init__(self, source_triangulation, target_triangulation, sequence):
		assert(isinstance(source_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(target_triangulation, flipper.kernel.Triangulation))
		assert(all(isinstance(function, PLFunction) for function in sequence))
		
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
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.zeta = self.source_triangulation.zeta
		
		self._cache = {}  # For caching hard to compute results.
	
	def is_mapping_class(self):
		''' Return if this encoding is a mapping class.
		
		That is, if it maps to the triangulation it came from. '''
		
		return self.source_triangulation == self.target_triangulation
	
	def __len__(self):
		return len(self.sequence)
	def __repr__(self):
		return 'PLfunction (%d flips)' % len(self)
	def __iter__(self):
		return iter(self.sequence)
	def __getitem__(self, key):
		if isinstance(key, slice):
			return Encoding(self.sequence[key])
		elif isinstance(key, flipper.IntegerType):
			return self.sequence[key]
		else:
			raise TypeError('Invalid argument type.')
	def __eq__(self, other):
		if isinstance(other, Encoding):
			if self.source_triangulation != other.source_triangulation or \
				self.target_triangulation != other.target_triangulation:
				raise ValueError('Cannot compare Encodings between different triangulations.')
			
			return all(self(curve) == other(curve) for curve in self.source_triangulation.key_curves())
		else:
			return NotImplemented
	def __hash__(self):
		return hash(tuple(self.sequence))
	def __call__(self, other):
		if isinstance(other, flipper.kernel.Lamination):
			if self.source_triangulation != other.triangulation:
				raise ValueError('Cannot apply an Encoding to a Lamination on a triangulation other than source_triangulation.')
			vector = other.vector
			for A in reversed(self):
				vector = A(vector)
			# If other has no peripheral components then self(other) does too.
			# Hence we can skip this check and save ~25% of the work.
			return self.target_triangulation.lamination(vector, remove_peripheral=False)
		else:
			return NotImplemented
	def __mul__(self, other):
		if isinstance(other, Encoding):
			if self.source_triangulation != other.target_triangulation:
				raise ValueError('Cannot compose Encodings over different triangulations.')
			return Encoding(other.source_triangulation, self.target_triangulation, self.sequence + other.sequence)
		else:
			return NotImplemented
	def __pow__(self, k):
		assert(self.is_mapping_class())
		if k == 0:
			return self.source_triangulation.id_encoding()
		elif k > 0:
			return Encoding(self.source_triangulation, self.target_triangulation, self.sequence * k)
		else:
			return self.inverse()**abs(k)
	
	def inverse(self):
		''' Return the inverse of this encoding. '''
		
		return Encoding(self.target_triangulation, self.source_triangulation, [A.inverse() for A in reversed(self)])
	
	def closing_isometries(self):
		''' Return all the possible isometries from self.target_triangulation to self.source_triangulation.
		
		These are the maps that can be used to close this into a mapping class. '''
		
		return self.target_triangulation.isometries_to(self.source_triangulation)
	
	def find_indices(self, lamination, count_all=True):
		''' Return the list of indices describing the cell this lamination lies in. '''
		
		vector = lamination.vector
		indices = []
		for A in reversed(self):
			if count_all or len(A) > 1: indices.append(A.applied_index(vector))  # We might not record ones with no choice.
			vector = A(vector)
		
		return indices
	
	def find_indices_compressed(self, lamination):
		''' Return the list of indices describing the cell this lamination lies in as a base64 string. '''
		
		return flipper.kernel.utilities.encode_binary(self.find_indices(lamination, count_all=False))
	
	def applied_function(self, lamination):
		''' Return the partial function that will be applied to the lamination. '''
		
		return self.expand_indices(self.find_indices(lamination))
	
	
	def expand_indices(self, indices):
		''' Return the partial function corresponding to the given list of indices.
		
		Note: Given indices = [a_0, ..., a_k] this returns choice[a_k] * ... * choice[a_0].
		Be careful about the order in which you give the indices. '''
		
		As = flipper.kernel.id_matrix(self.zeta)
		Cs = flipper.kernel.empty_matrix()
		for E, i in zip(reversed(self), indices):
			Cs = Cs.join(E[i].condition * As)
			As = E[i].action * As
		
		return PartialFunction(As, Cs)
	
	def order(self):
		''' Return the order of this mapping class.
		
		If this has infinite order then returns 0. Note: if the
		underlying surface is S_0_4 or S_1_1 then this might be
		off by a factor of 2 due to the hyperelliptic. Eventuallly,
		when algebraic intersection numbers are implemented, this
		problem will be solved.
		
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
			for j in range(1, min(triangulation.max_order, len(curves))):
				old_curve = curves[-j-1]
				if projective_difference(new_curve, old_curve, 100):
					average_curve = sum(curves[-j:])
					# print('%s - %d, %d' % (self.find_indices_compressed(average_curve), i, j))
					partial_function = (self**j).applied_function(average_curve)
					if partial_function not in tested_cells:
						tested_cells.append(partial_function)
						action_matrix, condition_matrix = partial_function.action, partial_function.condition
						try:
							eigenvalue, eigenvector = flipper.kernel.symboliccomputation.directed_eigenvector(action_matrix, condition_matrix, average_curve)
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
										if eigenvalue == 1:
											raise flipper.AssumptionError('Mapping class is reducible.')
										else:
											return eigenvalue, invariant_lamination
									else:
										if not invariant_lamination.projectively_equal(self(invariant_lamination)):
											raise flipper.AssumptionError('Mapping class is reducible.')
										else:
											# We possibly could reconstruct something here but all the numbers are
											# in the wrong number field. It's easier to just keep going.
											pass
					break
			
			denominators = [min(new_curve) + 1, i + 1, (i // 2) + 1]  # Other strategies: (i // triangulation.max_order) + 1
			for denominator in denominators:
				vector = [int(round(float(x) / denominator, 0)) for x in new_curve]
				new_small_curve = small_curve = triangulation.lamination(vector)
				if not small_curve.is_empty():
					for j in range(1, triangulation.max_order+1):
						new_small_curve = self(new_small_curve)
						if new_small_curve == small_curve:
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
	
	def nielsen_thurston_type(self):
		''' Return the Nielsen--Thurston type of this encoding.
		
		This encoding must be a mapping class. '''
		
		assert(self.is_mapping_class())
		
		# We used to do:
		# if self.is_periodic():
		#	return NT_TYPE_PERIODIC
		# elif self.is_reducible(log_progress=log_progress):
		#	return NT_TYPE_REDUCIBLE
		# else:
		#	return NT_TYPE_PSEUDO_ANOSOV
		# but this uses self.is_reducible() and so took exponential time.
		
		if self.is_periodic():
			return NT_TYPE_PERIODIC
		else:
			try:
				# This can also fail with a flipper.ComputationError if
				# self.invariant_lamination() fails to find an invariant lamination.
				_, lamination = self.invariant_lamination()
			except flipper.AssumptionError:
				return NT_TYPE_REDUCIBLE
			else:
				if lamination.is_filling():
					return NT_TYPE_PSEUDO_ANOSOV
				else:
					return NT_TYPE_REDUCIBLE
	
	def is_conjugate_to(self, other):
		''' Return if this mapping class is conjugate to other.
		
		Assumes that both encodings are pseudo-Anosov mapping classes. '''
		
		assert(self.is_mapping_class())
		assert(isinstance(other, Encoding))
		assert(other.is_mapping_class())
		
		splitting1 = self.splitting_sequences()[0]
		splitting2 = other.splitting_sequences()[0]
		
		source_lamination = splitting1.initial_lamination
		target_lamination = splitting2.initial_lamination
		for edge_index in splitting2.periodic_flips:
			try:
				if source_lamination.all_projective_isometries(target_lamination):
					return True
			except TypeError:  # We cannot do arithmetic with these numbers because they lie in different fields.
				return False
			
			f = target_lamination.triangulation.encode_flip(edge_index)
			target_lamination = f(target_lamination)
		
		return False
	
	def dilatation(self, lamination):
		''' Return the dilatation of this mapping class on the given lamination.
		
		Assumes (and checks) that the given lamination is projectively invariant.
		
		This encoding must be a mapping class. '''
		
		assert(self.is_mapping_class())
		
		new_lamination = self(lamination)
		if not lamination.projectively_equal(new_lamination):
			raise flipper.AssumptionError('Lamination is not projectively invariant.')
		
		return float(new_lamination.weight()) / float(lamination.weight())
	
	def splitting_sequences(self, take_roots=False):
		''' Return a list of splitting sequences associated to this mapping class.
		
		Eventually this should return the unique splitting sequence associated, in which
		case the name might change.
		
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
		
		# Eventually we should choose only one of the splittings.
		return splittings

