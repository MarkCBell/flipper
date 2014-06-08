
from functools import reduce

import flipper
import flipper.application

NT_TYPE_PERIODIC = 'Periodic'
NT_TYPE_REDUCIBLE = 'Reducible'
NT_TYPE_PSEUDO_ANOSOV = 'Pseudo-Anosov'

class PartialFunction(object):
	''' This represents a linear function from a subset of RR^m to RR^n. '''
	def __init__(self, action, condition=None):
		''' This represents a partial linear function from RR^m to RR^n.
		The function is defined on the subset where condition*vector >= 0, or everywhere if condition
		is None. Attempting to apply the function to a point not in the domain will raise a TypeError. '''
		self.action = action
		self.condition = condition if condition is not None else flipper.kernel.Empty_Matrix()
	
	def __str__(self):
		return '%s\n%s' % (self.action, self.condition)
	
	def __call__(self, other):
		if self.condition.nonnegative_image(other):
			return self.action * other
		
		raise TypeError('Object is not in domain.')

class PLFunction(object):
	''' This represent the piecewise-linear map from RR^m to RR^n. '''
	def __init__(self, partial_functions, inverse_partial_functions=None):
		self.partial_functions = partial_functions
		assert(len(self.partial_functions) > 0)
		self.inverse_partial_functions = inverse_partial_functions if inverse_partial_functions is not None else []
	
	def __iter__(self):
		return iter(self.partial_functions)
	def __str__(self):
		return '\n'.join(str(function) for function in self.partial_functions)
	def __len__(self):
		return len(self.partial_functions)
	def __getitem__(self, index):
		return self.partial_functions[index]
	def __call__(self, other):
		for function in self.partial_functions:
			try:
				return function(other)
			except TypeError:
				pass
		raise TypeError('Object is not in domain.')
	def copy(self):
		return PLFunction([f.copy() for f in self.partial_functions], [f.copy() for f in self.inverse_partial_functions])
	def inverse(self):
		if not self.inverse_partial_functions:
			raise TypeError('Function is not invertible.')
		
		return PLFunction(self.inverse_partial_functions, self.partial_functions)
	def applied_index(self, lamination):
		# Returns the index of the partial function that would be applied to this lamination.
		for index, function in enumerate(self.partial_functions):
			try:
				function(lamination)
				return index
			except TypeError:
				pass
		
		raise TypeError('Object is not in domain.')

class Encoding(object):
	''' This represents a map between two AbstractTriagulations. '''
	def __init__(self, source_triangulation, target_triangulation, sequence):
		''' This represents a map between two AbstractTriagulations. It is given by a sequence
		of PLFunctions whose composition is the action on the edge weights. '''
		self.sequence = sequence
		assert(all(isinstance(x, PLFunction) for x in self.sequence))
		
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.zeta = self.source_triangulation.zeta
	
	def is_mapping_class(self):
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
		elif isinstance(key, flipper.kernel.Integer_Type):
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
		# return self * other
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
			# !?! Could do something like:
			# return flipper.kernel.utilities.product(list(self) + [other.copy()])
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
		return Encoding(self.target_triangulation, self.source_triangulation, [A.inverse() for A in reversed(self)])
	
	def applied_function(self, lamination):
		''' Returns the partial function that will be applied to the lamination. '''
		
		vector = lamination.vector
		indices = []
		for A in reversed(self):
			indices.append(A.applied_index(vector))
			vector = A(vector)
		
		return self.expand_indices(indices)
	
	def expand_indices(self, indices):
		''' Given indices = [a_0, ..., a_k] this returns the partial function of
		choice[a_k] * ... * choice[a_0]. Be careful about the order in which you give the indices. '''
		
		As = flipper.kernel.Id_Matrix(self.zeta)
		Cs = flipper.kernel.Empty_Matrix()
		for E, i in zip(reversed(self), indices):
			Cs = Cs.join(E[i].condition * As)
			As = E[i].action * As
		
		return PartialFunction(As, Cs)
	
	def order(self):
		''' Returns the order of this mapping class. If this has infinite order then returns 0. '''
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
		order = self.order()
		return 'Infinite' if order == 0 else str(order)
	
	def is_identity(self):
		return self == self.source_triangulation.id_encoding()
	
	def is_periodic(self):
		return self.order() > 0
	
	def is_reducible(self, log_progress=None):
		''' This determines if the induced action of self on V the space of laminations on T
		has a fixed point satisfying:
			face_matrix.v >= 0 and marking_matrix.v >= 0 
		for some marking_matrix in marking_matrices. '''
		# We now use Ben's branch and bound approach. It's much better.
		assert(self.is_mapping_class())
		
		# We first create two little functions to increment the list of indices to the next point that
		# we are interested in. The first jumps from our current location to the next subtree, the second
		# advances to the next index according to the lex ordering.
		
		sizes = [len(encoding) for encoding in self][::-1]
		sizes_mul = [reduce(lambda x, y: x*y, sizes[i:], 1) for i in range(len(sizes))]
		total = sum((scale-1) * scale_prod for scale, scale_prod in zip(sizes, sizes_mul))
		
		def jump_index(indices):
			indices = list(indices)
			while len(indices) > 0 and indices[-1] == len(self[len(self)-len(indices)])-1:
				indices.pop()
			if len(indices) > 0: indices[-1] += 1
			return indices
		
		def next_index(indices):
			indices = list(indices)
			if len(indices) < len(self):
				return indices + [0]
			elif len(indices) == len(self):
				return jump_index(indices)
			else:
				raise IndexError
		
		face_matrix, marking_matrices = self.source_triangulation.face_matrix(), self.source_triangulation.marking_matrices()
		
		M4 = face_matrix
		M6 = flipper.kernel.Id_Matrix(self.zeta)
		indices = [0]
		while indices != []:
			partial_function = self.expand_indices(indices)
			As, Cs = partial_function.action, partial_function.condition
			if log_progress is not None:
				# Log how far we've gotten.
				progression = float(sum(index * scale for index, scale in zip(indices, sizes_mul))) / total
				log_progress(progression)
			
			if len(indices) < len(self):
				# Remember to always add the Id matrix as empty matrices always
				# define trivial polytopes.
				indices = next_index(indices) if Cs.join(M6).nontrivial_polytope() else jump_index(indices)
			else:
				for i in range(len(marking_matrices)):
					M1 = Cs
					M2 = As - M6  # As - flipper.kernel.Id_Matrix.
					M3 = M6 - As  # flipper.kernel.Id_Matrix - As.
					M5 = marking_matrices[i]
					
					# M4 = face_matrix  # These have been precomputed.
					# M6 = flipper.kernel.Id_Matrix(self.zeta)
					P = M4.join(M5).join(M2).join(M3).join(M1)  # A better order.
					if P.nontrivial_polytope():
						# We could just return True here but we'll repeat some work
						# just to make sure everything went ok.
						certificate = self.source_triangulation.lamination([2*i for i in P.find_edge_vector()])
						assert(self.check_fixedpoint(certificate))
						return True
				indices = jump_index(indices)
		
		return False
	
	def check_fixedpoint(self, certificate):
		assert(self.is_mapping_class())
		return certificate.is_multicurve() and self(certificate) == certificate
	
	def NT_type_alternate(self, log_progress=None):
		assert(self.is_mapping_class())
		if self.is_periodic():
			return NT_TYPE_PERIODIC
		elif self.is_reducible(log_progress=log_progress):
			return NT_TYPE_REDUCIBLE
		else:
			return NT_TYPE_PSEUDO_ANOSOV
	
	def invariant_lamination(self):
		''' Returns a lamination (with entries in a NumberField) which is projectively invariant
		under this mapping class. If it cannot find one then it raises a ComputationError.
		Assumes that the mapping class is pseudo-Anosov. If it is periodic it will discover this
		if it is reducible it may discover this.
		
		The process starts with a curve on the surface and repeatedly applies the map until
		it appear to be projectively similar to a previous iteration. Finally it uses:
			flipper.kernel.symboliccomputation.Perron_Frobenius_eigen()
		to find the nearby projective fixed point.
		
		Note: In most pseudo-Anosov cases < 15 iterations are needed, if it fails to converge after
		100 iterations and a ComputationError is thrown then it's actually extremely likely that the
		map was not pseudo-Anosov. '''
		
		# Suppose that f_1, ..., f_m, g_1, ..., g_n, t_1, ..., t_k, p is the Thurston decomposition of self.
		# That is: f_i are pA on subsurfaces, g_i are periodic on subsurfaces, t_i are Dehn twist along the curve of
		# the canonical curve system and p is a permutation of the subsurfaces.
		# Additionally, let S_i be the subsurface corresponding to f_i, P_i correspond to g_i and A_i correspond to t_i.
		# Finally, let x be a curve on the surface and define x_0 := x and x_i := self(x_{i-1}).
		#
		# The algorithm covers 3 cases:  (Note we reorder the subsurfaces for ease of notation.)
		#  1) x meets at S_1, ..., S_m',
		#  2) x meets no S_i but meets A_1, ..., A_k', and
		#  3) x meets no S_i or A_i, that is x is contained in a P_1.
		#
		# In the first case, x_i will converge exponentially to the stable laminations of f_1, ..., f_m'.
		# Here the convergence is so fast we need only a few iterations.
		#
		# In the second case x_i will converge linearly to c, the cores of A_1, ..., A_k'. To speed this up
		# we note that x_i = i*c + O(1), so rescale x_i by 1/i, round and check if this is c.
		#
		# Finally, the third case happens if and only if x_i is periodic. In this case self must be
		# periodic or reducible. We test for periodicity at the begining hence if we ever find a curve
		# fixed by a power of self then we must reducible.
		
		assert(self.is_mapping_class())
		if self.is_periodic():  # This is not needed but it provides a fast test.
			raise flipper.AssumptionError('Mapping class is periodic.')
		triangulation = self.source_triangulation
		
		curves = [triangulation.key_curves()[0]]
		
		def projective_difference(A, B, error_reciprocal):
			# Returns True iff the projective difference between A and B is less than 1 / error_reciprocal.
			A_sum, B_sum = sum(A), sum(B)
			return max(abs((p * B_sum) - q * A_sum) for p, q in zip(A, B)) * error_reciprocal < A_sum * B_sum
		
		for i in range(50):
			new_curve = self(curves[-1])
			
			# Check if we have seen this curve before.
			if new_curve in curves:  # self**(i-j)(curve) == curve, so self is reducible.
				raise flipper.AssumptionError('Mapping class is reducible.')
			
			for j in range(1, min(triangulation.max_order, len(curves))+1):
				old_curve = curves[-j]
				if projective_difference(new_curve, old_curve, 1000):
					average_curve = sum(curves[-j:])
					partial_function = self.applied_function(average_curve)
					action_matrix, condition_matrix = partial_function.action, partial_function.condition
					try:
						eigenvector = flipper.kernel.symboliccomputation.Perron_Frobenius_eigen(action_matrix, average_curve)
					except flipper.AssumptionError:
						pass  # Largest eigenvalue was not real.
					else:
						# Test if the vector we found lies in the cone given by the condition matrix.
						if condition_matrix.nonnegative_image(eigenvector):
							# If it does then we have a projectively invariant lamintation.
							invariant_lamination = triangulation.lamination(eigenvector, remove_peripheral=True)
							if not invariant_lamination.is_empty():
								# print('###', i, j, '-', '%0.3f' % eigenvector[0].number_field.lmbda)
								if invariant_lamination[0].number_field.lmbda == 1:
									# print('###', i, j, '-', '%0.3f' % eigenvector[0].number_field.lmbda)
									raise flipper.AssumptionError('Mapping class is reducible.')
								else:
									return invariant_lamination
			
			denominator = i+1
			vector = [int(round(float(x) / denominator, 0)) for x in new_curve]
			new_curve = small_curve = triangulation.lamination(vector, remove_peripheral=True)
			if not small_curve.is_empty():
				for j in range(1, triangulation.max_order+1):
					new_curve = self(new_curve)
					if new_curve == small_curve:
						# print('###', i, j, small_curve, '%0.3f' % 1)
						raise flipper.AssumptionError('Mapping class is reducible.')
			
			curves.append(new_curve)
		
		raise flipper.ComputationError('Could not estimate invariant lamination.')
	
	def NT_type(self):
		assert(self.is_mapping_class())
		if self.is_periodic():
			return NT_TYPE_PERIODIC
		else:
			try:
				lamination = self.invariant_lamination()
			except flipper.AssumptionError:
				return NT_TYPE_REDUCIBLE
			# This can also fail with a flipper.ComputationError if self.invariant_lamination()
			# fails to find an invariant lamination.
			if lamination.is_filling():
				return NT_TYPE_PSEUDO_ANOSOV
			else:
				return NT_TYPE_REDUCIBLE
	
	def dilatation(self, lamination):
		''' Returns the dilatation of this mapping class on the given lamination.
		
		Assumes that the given lamination is projectively invariant. If not then
		it will discover this. '''
		
		assert(self.is_mapping_class())
		new_lamination = self(lamination)
		if not lamination.projectively_equal(new_lamination):
			raise flipper.AssumptionError('Lamination is not projectively invariant.')
		
		return float(new_lamination.weight()) / float(lamination.weight())
	
	def splitting_sequence(self):
		''' Returns the (unique) splitting sequence associated to this mapping class.
		
		If the mapping class is not on S_{1,1} or S_{0,4} then then splitting
		sequence will have a unique closing isometry set. To do this the algorithm may
		occasionally need to perform a second round of lamination.splitting_sequence().
		However this is only done when the mapping class has a symmetry and its
		stable lamination has fewer singularities than we could initally see.
		
		Assumes that the mapping class is pseudo-Anosov. If not then it will
		discover this. '''
		
		assert(self.is_mapping_class())
		if self.is_periodic():  # Actually this test is redundant but it is faster to test it now.
			raise flipper.AssumptionError('Mapping class is not pseudo-Anosov.')
		lamination = self.invariant_lamination()  # This could fail with a flipper.ComputationError.
		dilatation = lamination[0].number_field.lmbda
		try:
			splitting = lamination.splitting_sequence(target_dilatation=dilatation)
		except flipper.AssumptionError:  # Lamination is not filling.
			raise flipper.AssumptionError('Mapping class is not pseudo-Anosov.')
		else:
			# We might need to do more work to get the closing isometry.
			#if splitting.closing_isometry is None:
			if False:
				# If we installed too many punctures by default then
				# the preperiodic encoding wont make it through.
				print('Finding closer')
				if splitting.preperiodic is None:
					print('RECOMPUTING')
					# So we have to do it again with fewer.
					initial_triangulation = splitting.laminations[0].triangulation
					surviving_punctures = set([label for triangle in initial_triangulation for label in triangle.corner_labels])
					tripods = lamination.tripod_regions()
					real_tripods = [tripods[i-1] for i in surviving_punctures if i > 0]
					print(len(tripods), surviving_punctures)
					puncture_encoding = lamination.triangulation.encode_puncture_triangles(real_tripods)
					lamination = puncture_encoding(lamination)
					remove_tripods = lamination.remove_tripod_regions()
					lamination = remove_tripods(lamination)
					splitting = lamination.splitting_sequence(target_dilatation=dilatation) # , puncture_first=real_tripods)
					print(splitting.flips)
				
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
				preperiodic, periodic = splitting.preperiodic, splitting.periodic
				preperiodic = preperiodic * remove_tripods * puncture_encoding
				
			#	for curve in self.source_triangulation.key_curves():
			#		print(curve)
			#		print((preperiodic * self.inverse()**100 * curve).weight())
			#		for isom in splitting.closing_isometries:
			#			print(((isom.encode() * periodic)**100 * preperiodic * curve).weight())
			#		
			#		print('####')
				for isom in splitting.closing_isometries:
					# Note: Until algebraic intersection numbers are done, this equality 
					# isn't strong enought if the underlying surface is S_1_1 or S_0_4.
					if preperiodic * self.inverse() == isom.encode() * periodic * preperiodic:
						splitting.closing_isometry = isom
						break
				else:
					print('FAILED')
					
			#		print(dilatation)
			#		print(self.dilatation(lamination))
			#		for isom in splitting.closing_isometries:
			#			print(isom.permutation())
			#			print(1 / (isom.encode() * periodic).dilatation(conj_lamination))
			#		for isom in self.source_triangulation.all_isometries(self.source_triangulation):
			#			print(isom.permutation())
			#		assert(False)  # There was no way to close the square!?
			return splitting

