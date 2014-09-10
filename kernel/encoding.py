
''' A module for representing and manipulating maps between AbstractTriangulations.

Provides two classes: PartialFunction, PLFunction and Encoding. '''

import flipper

from itertools import product

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
	''' This represents a map between two AbstractTriagulations.
	
	It is given by a sequence of PLFunctions whose composition is the action on the edge weights.'''
	def __init__(self, source_triangulation, target_triangulation, sequence):
		assert(isinstance(source_triangulation, flipper.kernel.AbstractTriangulation))
		assert(isinstance(target_triangulation, flipper.kernel.AbstractTriangulation))
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
	
	def is_mapping_class(self):
		''' Return if this encoding is a mapping class.
		
		That is, if it maps to the AbstractTriangulation it came from. '''
		
		return self.source_triangulation == self.target_triangulation
	
	def __len__(self):
		return len(self.sequence)
	def __repr__(self):
		return 'PLfunction (comp): %s --> %s' % (self.source_triangulation, self.target_triangulation)
	def __iter__(self):
		return iter(self.sequence)
	def __getitem__(self, key):
		if isinstance(key, slice):
			return Encoding(self.sequence[key])
		elif isinstance(key, flipper.Integer_Type):
			return self.sequence[key]
		else:
			raise TypeError('Invalid argument type.')
	def __eq__(self, other):
		return isinstance(other, Encoding) and \
			self.source_triangulation == other.source_triangulation and \
			self.target_triangulation == other.target_triangulation and \
			all(self(curve) == other(curve) for curve in self.source_triangulation.key_curves())
	def __hash__(self):
		return hash(tuple(self.sequence))
	def __call__(self, other):
		if isinstance(other, flipper.kernel.Lamination):
			if self.source_triangulation != other.triangulation:
				raise ValueError('Cannot apply an Encoding to a Lamination on a triangulation other than source_triangulation.')
			vector = other.vector
			for A in reversed(self):
				vector = A(vector)
			return self.target_triangulation.lamination(vector)
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
		
		return flipper.kernel.utilities.change_base(int(''.join(str(x) for x in self.find_indices(lamination, count_all=False)), 2))
	
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
		
		If this has infinite order then returns 0.
		
		This encoding must be a mapping class. '''
		
		assert(self.is_mapping_class())
		
		# We could do:
		# for i in range(self.source_triangulation.max_order):
		#	if (self**(i+1)).is_identity():
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
	
	def order_string(self):
		''' Return the order of this mapping class as a string.
		
		This encoding must be a mapping class. '''
		
		order = self.order()
		return 'Infinite' if order == 0 else str(order)
	
	def is_identity(self):
		''' Return if this mapping class is the identity. '''
		
		return self == self.source_triangulation.id_encoding()
	
	def is_periodic(self):
		''' Return if this encoding has finite order.
		
		This encoding must be a mapping class. '''
		
		return self.order() > 0
	
	def is_reducible(self, log_progress=None):
		''' Return if this encoding is reducible.
		
		This determines if the induced action of self on V the space of laminations on T.
		To do this, for each Marking matrix and (Action, Condition) matrix pair we check
		if there is a non-negative, non-trivial solution to:
			( Condition )
			(Action - Id)
			(Id - Action) x >= 0
			(    Id     )
			(   Face    )
			(  Marking  )
		
		Such a solution corresponds to an essential invariant (multi)curve. See section ?? of:
			http://arxiv.org/pdf/1403.2997.pdf
		for more information.
		
		This only uses integer arithmetic but there may be exponentially many LP problems to
		check. Hence this is not advisable to use.
		
		This encoding must be a mapping class. '''
		
		assert(self.is_mapping_class())
		
		# We now use Ben's branch and bound approach. It's much better.
		
		# To do this we create two little functions to increment the list of indices to the next point that
		# we are interested in. The first jumps from our current location to the next subtree, the second
		# advances to the next index according to the lex ordering.
		
		sizes = [len(encoding) for encoding in self][::-1]
		sizes_mul = [flipper.kernel.product(sizes[i:]) for i in range(len(sizes))]
		total = sum((scale-1) * scale_prod for scale, scale_prod in zip(sizes, sizes_mul))
		
		def jump_index(indices):
			''' Return the next indices at this level of the tree. '''
			
			indices = list(indices)
			while len(indices) > 0 and indices[-1] == len(self[len(self)-len(indices)])-1:
				indices.pop()
			if len(indices) > 0: indices[-1] += 1
			return indices
		
		def next_index(indices):
			''' Return the next indices of the tree. '''
			
			indices = list(indices)
			if len(indices) < len(self):
				return indices + [0]
			elif len(indices) == len(self):
				return jump_index(indices)
			else:
				raise IndexError
		
		face_matrix, marking_matrices = self.source_triangulation.face_matrix(), self.source_triangulation.marking_matrices()
		
		M4 = face_matrix
		M6 = flipper.kernel.id_matrix(self.zeta)
		indices = [0]
		while indices != []:
			partial_function = self.expand_indices(indices)
			As, Cs = partial_function.action, partial_function.condition
			
			if log_progress is not None:  # Log how far we've gotten.
				progression = float(sum(index * scale for index, scale in zip(indices, sizes_mul))) / total
				log_progress(progression)
			
			if len(indices) < len(self):
				# Remember to always add the Id matrix as empty matrices always define trivial polytopes.
				indices = next_index(indices) if Cs.join(M6).nontrivial_polytope() else jump_index(indices)
			else:
				for i in range(len(marking_matrices)):
					M1 = Cs
					M2 = As - M6  # As - flipper.kernel.id_matrix.
					M3 = M6 - As  # flipper.kernel.id_matrix - As.
					M5 = marking_matrices[i]
					
					# M4 = face_matrix  # These have been precomputed.
					# M6 = flipper.kernel.id_matrix(self.zeta)
					P = M4.join(M5).join(M2).join(M3).join(M1)  # A better order.
					if P.nontrivial_polytope():
						return True
				indices = jump_index(indices)
		
		return False
	
	def invariant_lamination(self):
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
		
		if self.is_periodic():  # This is not needed but it provides a fast test.
			raise flipper.AssumptionError('Mapping class is periodic.')
		
		triangulation = self.source_triangulation
		
		curves = [triangulation.key_curves()[0]]
		
		def projective_difference(A, B, error_reciprocal):
			''' Return if the projective difference between A and B is less than 1 / error_reciprocal. '''
			
			A_sum, B_sum = sum(A), sum(B)
			return max(abs((p * B_sum) - (q * A_sum)) for p, q in zip(A, B)) * error_reciprocal < A_sum * B_sum
		
		# We will remember the cells we've tested to avoid recalculating their eigenvectors again.
		tested_cells = []
		for i in range(50):
			new_curve = self(curves[-1])
			
			# Check if we have seen this curve before.
			if new_curve in curves:  # self**(i-j)(curve) == curve, so self is reducible.
				raise flipper.AssumptionError('Mapping class is reducible.')
			
			curves.append(new_curve)
			for j in range(1, min(triangulation.max_order, len(curves))):
				old_curve = curves[-j-1]
				if projective_difference(new_curve, old_curve, 100):
					average_curve = sum(curves[-j:])
					# print('%s - %d' % (self.find_indices_compressed(average_curve), i))
					partial_function = (self**j).applied_function(average_curve)
					if partial_function not in tested_cells:
						tested_cells.append(partial_function)
						action_matrix, condition_matrix = partial_function.action, partial_function.condition
						try:
							eigenvalue, eigenvector = flipper.kernel.symboliccomputation.perron_frobenius_eigen(action_matrix, average_curve)
						except flipper.AssumptionError:
							pass  # Largest eigenvalue was not real.
						else:
							# Test if the vector we found lies in the cone given by the condition matrix.
							# We could also use: invariant_lamination.projectively_equal(self(invariant_lamination))
							# but this is much faster.
							if flipper.kernel.matrix.nonnegative(eigenvector) and condition_matrix.nonnegative_image(eigenvector):
								# If it does then we have a projectively invariant lamination.
								invariant_lamination = triangulation.lamination(eigenvector, remove_peripheral=True)
								if not invariant_lamination.is_empty():
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
			
			denominators = [min(new_curve) + 1, i + 1]  # Other strategies: (i // triangulation.max_order) + 1
			for denominator in denominators:
				vector = [int(round(float(x) / denominator, 0)) for x in new_curve]
				new_small_curve = small_curve = triangulation.lamination(vector, remove_peripheral=True)
				if not small_curve.is_empty():
					for j in range(1, triangulation.max_order+1):
						new_small_curve = self(new_small_curve)
						if new_small_curve == small_curve:
							raise flipper.AssumptionError('Mapping class is reducible.')
		
		raise flipper.ComputationError('Could not estimate invariant lamination.')
	
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
		else:
			# There might be more work to do here. We should choose only one of the splittings.
			if False:
				c = 0
				for splitting in splittings:
					# If we installed too many punctures by default then the preperiodic encoding wont make it through.
					if splitting.preperiodic is None:
						print('COULDNT CHECK')
						c = -1
						# !?! TO DO.
					else:
						# Find the correct isometry (isom) which completes the square (pentagon?).
						# Remember: The periodic goes in the _opposite_ direction to self so the
						# diagram looks like this:
						#
						#   T ------------ self^{-1} ------------> T
						#    \                                      \
						#  preperiodic                            preperiodic
						#      \                                      \
						#       V                                      V
						#       T' --- periodic ---> T'' --- isom ---> T'
						#
						preperiodic, periodic, isom = splitting.preperiodic, splitting.periodic, splitting.isometry.encode()
						
						curves = self.source_triangulation.key_curves()
						print('#########################')
						for c1, c2 in product(curves, curves):
							top1 = self(c1)
							top2 = c2
							bottom1 = isom(periodic(preperiodic(c1)))
							bottom2 = preperiodic(c2)
							i1 = top1.geometric_intersection(top2)
							i2 = bottom1.geometric_intersection(bottom2)
							print(i1 == i2)
							if i1 != i2:
								break
						
						print('???????????????????')
						print(len(self))
						print(preperiodic.target_triangulation)
						for curve in self.source_triangulation.key_curves():
							print(curve)
							print((preperiodic * self.inverse())(curve))
							print((isom * periodic * preperiodic)(curve))
							print('####')
						if preperiodic * self.inverse() == isom * periodic * preperiodic:
							c += 1
				print('!!! %d closers' % c)
				if c == 0:
					print ('!!!!!!!!!!!!!!!!!!!')
					print ('!!!!!!!!!!!!!!!!!!!')
					print ('!!!!!!!!!!!!!!!!!!!')
					print ('!!!!!!!!!!!!!!!!!!!')
					print ('!!!!!!!!!!!!!!!!!!!')
					
				assert(c != 0)
			return splittings
