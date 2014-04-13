
from functools import reduce
from itertools import product

import flipper

NT_TYPE_PERIODIC = 'Periodic'
NT_TYPE_REDUCIBLE = 'Reducible'
NT_TYPE_PSEUDO_ANOSOV = 'Pseudo-Anosov'

class PartialFunction(object):
	''' This represents a linear function defined between the spaces of laminations on two AbstractTriangulations. '''
	def __init__(self, source_triangulation, target_triangulation, action, condition=None):
		''' This represents a partial linear function from L(source_triangulation) to L(target_triangulation).
		The function is defined on the subset where condition*lamination >= 0, or everywhere if condition
		is None. Attempting to apply the function to a point not in the domain will raise a TypeError. '''
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.action = action
		if condition is None: condition = flipper.kernel.Empty_Matrix()
		self.condition = condition
	
	def __str__(self):
		return str(self.action) + '\n' + str(self.condition)
	
	def __call__(self, other):
		return self * other
	
	def __mul__(self, other):
		if isinstance(other, flipper.kernel.Lamination) and other.abstract_triangulation == self.source_triangulation:
			if self.condition.nonnegative_image(other.vector):
				return self.target_triangulation.lamination(self.action * other.vector)
		
		raise TypeError('Object is not in domain.')

class PLFunction(object):
	''' This represent the piecewise-linear map between the spaces of laminations on two AbstractTriangulations. '''
	def __init__(self, partial_functions, inverse_partial_functions=None):
		self.partial_functions = partial_functions
		assert(len(self.partial_functions) > 0)
		self.source_triangulation = self.partial_functions[0].source_triangulation
		self.target_triangulation = self.partial_functions[0].target_triangulation
		assert(all(f.source_triangulation == self.source_triangulation for f in self.partial_functions))
		if inverse_partial_functions is None: inverse_partial_functions = []
		self.inverse_partial_functions = inverse_partial_functions
		assert(all(f.target_triangulation == self.target_triangulation for f in self.partial_functions))
	
	def __iter__(self):
		return iter(self.partial_functions)
	def __str__(self):
		return '\n'.join(str(function) for function in self.partial_functions)
	def __repr__(self):
		return 'PLfunction: %s --> %s' % (self.source_triangulation, self.target_triangulation)
	def __len__(self):
		return len(self.partial_functions)
	def __getitem__(self, index):
		return self.partial_functions[index]
	def __eq__(self, other):
		return isinstance(other, PLFunction) and \
			self.source_triangulation == other.source_triangulation and \
			self.target_triangulation == other.target_triangulation and \
			all(self * curve == other * curve for curve in self.source_triangulation.key_curves())
	def __hash__(self):
		return hash(tuple(self.partial_functions + self.inverse_partial_functions))
	def __call__(self, other):
		return self * other
	def __mul__(self, other):
		if isinstance(other, PLFunction):
			return Encoding([self, other])
		elif isinstance(other, Encoding):
			return Encoding([self] + other.sequence)
		elif isinstance(other, flipper.kernel.Lamination):
			for function in self.partial_functions:
				try:
					return function(other)
				except TypeError:
					pass
			raise TypeError('Object is not in domain.')
		else:
			return NotImplemented
	def __pow__(self, n):
		assert(self.source_triangulation == self.target_triangulation)
		if n > 0:
			return Encoding([self] * n)
		elif n == 0:
			return self.source_triangulation.Id_Encoding()
		elif n < 0:
			return self.inverse()**abs(n)
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
	def __init__(self, sequence):
		''' This represents the composition of several PLFunction. '''
		# Try and make a shorter sequence.
		#seq = []
		#for f in sequence:
		#	if seq and seq[-1] == f.inverse():
		#		seq.pop()
		#	else:
		#		seq.append(f)
		#sequence = seq
		
		self.sequence = sequence
		assert(all(isinstance(x, PLFunction) for x in self.sequence))
		assert(all(x.source_triangulation == y.target_triangulation for x, y in zip(self.sequence, self.sequence[1:])))
		
		self.source_triangulation = self.sequence[-1].source_triangulation
		self.target_triangulation = self.sequence[0].target_triangulation
		self.zeta = self.source_triangulation.zeta
	
	def __len__(self):
		return len(self.sequence)
	#def __str__(self):
	#	return '\n###\n'.join(str(A) for A in self.sequence)
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
			all(self * curve == other * curve for curve in self.source_triangulation.key_curves())
	def __hash__(self):
		return hash(tuple(self.sequence))
	def __call__(self, other):
		return self * other
	def __mul__(self, other):
		if isinstance(other, Encoding):
			return Encoding(self.sequence + other.sequence)
		elif isinstance(other, PLFunction):
			return Encoding(self.sequence + [other])
		else:
			other = other.copy()
			for A in reversed(self.sequence):
				other = A * other
			return other
	def __pow__(self, k):
		assert(self.source_triangulation == self.target_triangulation)
		if k == 0:
			return self.source_triangulation.Id_Encoding()
		elif k > 0:
			return Encoding(self.sequence * k)
		else:
			return self.inverse()**abs(k)
	
	def inverse(self):
		return Encoding([A.inverse() for A in reversed(self)])
	
	def name_indices(self, lamination):
		indices = []
		for A in reversed(self):
			indices.append(A.applied_index(lamination))
			lamination = A * lamination
		
		return indices
	
	def applied_function(self, lamination):
		''' Returns the partial function that will be applied to the lamination. '''
		
		return self.expand_indices(self.name_indices(lamination))
	
	def expand_indices(self, indices):
		''' Given indices = [a_0, ..., a_k] this returns the partial function of
		choice[a_k] * ... * choice[a_0]. Be careful about the order in which you give the indices. '''
		
		As = flipper.kernel.Id_Matrix(self.zeta)
		Cs = flipper.kernel.Empty_Matrix()
		source_triangulation = self.source_triangulation
		target_triangulation = self.source_triangulation
		for E, i in zip(reversed(self), indices):
			Cs = Cs.join(E[i].condition * As)
			As = E[i].action * As
			target_triangulation = E.target_triangulation
		
		return PartialFunction(source_triangulation, target_triangulation, As, Cs)
	
	def order(self):
		''' Returns the order of this mapping class. If this has infinite order then returns 0. '''
		assert(self.source_triangulation == self.target_triangulation)
		curve_images = curves = self.source_triangulation.key_curves()
		# We could do:
		# id_map = self.source_triangulation.Id_Encoding()
		# for i in range(self.source_triangulation.max_order):
		#	if self**(i+1) == id_map:
		#		return i+1
		# But this is quadratic in the order so instead we do:
		possible_orders = set(range(1, self.source_triangulation.max_order+1))
		for curve in curves:
			curve_image = curve
			for i in range(1, max(possible_orders)+1):
				curve_image = self * curve_image
				if curve_image != curve:
					possible_orders.discard(i)
					if not possible_orders: return 0  # No finite orders remain so we are infinite order.
		
		return min(possible_orders)
	
	def order_string(self):
		order = self.order()
		return 'Infinite' if order == 0 else str(order)
	
	def is_identity(self):
		return self == self.source_triangulation.Id_Encoding()
	
	def is_periodic(self):
		return self.order() > 0
	
	def is_reducible(self, log_progress=None):
		''' This determines if the induced action of self on V the space of laminations on T
		has a fixed point satisfying:
			face_matrix.v >= 0 and marking_matrix.v >= 0 
		for some marking_matrix in marking_matrices. '''
		# We now use Ben's branch and bound approach. It's much better.
		assert(self.source_triangulation == self.target_triangulation)
		
		# We first create two little functions to increment the list of indices to the next point that 
		# we are interested in. The first jumps from our current location to the next subtree, the second
		# advances to the next index according to the lex ordering.
		
		sizes = [len(encoding) for encoding in self][::-1]
		sizes_mul = [reduce(lambda x, y: x*y, sizes[i:], 1) for i in range(len(sizes))]
		total = sum((scale-1) * scale_prod for scale, scale_prod in zip(sizes, sizes_mul))
		
		def jump(indices):
			indices = list(indices)
			while len(indices) > 0 and indices[-1] == len(self[len(self)-len(indices)])-1:
				indices.pop()
			if len(indices) > 0: indices[-1] += 1
			return indices
		
		def next(indices):
			indices = list(indices)
			if len(indices) < len(self):
				return indices + [0]
			elif len(indices) == len(self):
				return jump(indices)
			else:
				raise IndexError
		
		def progress(indices):
			return 
		
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
				indices = next(indices) if Cs.join(M6).nontrivial_polytope() else jump(indices)
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
				indices = jump(indices)
		
		return False
	
	def check_fixedpoint(self, certificate):
		assert(self.source_triangulation == self.target_triangulation)
		return certificate.is_multicurve() and self * certificate == certificate
	
	def NT_type(self, log_progress=None):
		assert(self.source_triangulation == self.target_triangulation)
		if self.is_periodic():
			return NT_TYPE_PERIODIC
		elif self.is_reducible(log_progress=log_progress):
			return NT_TYPE_REDUCIBLE
		else:
			return NT_TYPE_PSEUDO_ANOSOV
	
	def NT_type_alternate(self):
		assert(self.source_triangulation == self.target_triangulation)
		if self.is_periodic():
			return NT_TYPE_PERIODIC
		else:
			# This can also fail with a flipper.ComputationError if self.invariant_lamination()
			# fails to find an invariant lamination.
			try:
				self.splitting_sequence()
				return NT_TYPE_PSEUDO_ANOSOV
			except flipper.AssumptionError:
				return NT_TYPE_REDUCIBLE
	
	def invariant_lamination(self):
		''' Returns a lamination (with entries in a NumberField) which is projectively invariant
		under this mapping class. If it cannot find one then it raises a ComputationError.
		
		The process starts with several curves on the surface and repeatedly applies the map until
		they appear to projectively similar to a previous iteration. Finally it uses:
			flipper.kernel.symboliccomputation.Perron_Frobenius_eigen()
		to find the nearby projective fixed point.
		
		Note: In most pseudo-Anosov cases < 15 iterations are needed, if it fails to converge after
		100 iterations and a ComputationError is thrown then it's actually extremely likely that the
		map was not pseudo-Anosov. '''
		
		assert(self.source_triangulation == self.target_triangulation)
		triangulation = self.source_triangulation
		
		curves = self.source_triangulation.key_curves()
		# We will need the number field QQ for constructing small invariant curves.
		QQ = flipper.kernel.NumberField()
		
		def projective_difference(A, B, error_reciprocal):
			# Returns True iff the projective difference between A and B is less than 1 / error_reciprocal.
			A_sum, B_sum = sum(A), sum(B)
			return max(abs((p * B_sum) - q * A_sum) for p, q in zip(A, B)) * error_reciprocal < A_sum * B_sum 
		
		curves = [[self * curve for curve in curves]]
		for i in range(50):
			# Differnt schemes for taking steps.
			new_curves = [self**(1) * curve for curve in curves[-1]]  # Constant.
			# new_curves = [self**(i+1) * curve for curve in curvesi[-1]]  # Linear.
			# new_curves = [self**(2**1) * curve for curve in curvesi[-1]]  # Exponential.
			
			for j in range(1, min(1, triangulation.max_order, len(curves))+1):  # Remove the 1??
				for new_curve, curve in zip(new_curves, curves[-j]):
					if projective_difference(new_curve, curve, 1000):
						partial_function = (self**j).applied_function(curve)
						action_matrix, condition_matrix = partial_function.action, partial_function.condition
						try:
							eigenvector = flipper.kernel.symboliccomputation.Perron_Frobenius_eigen(action_matrix, curve)
						except flipper.AssumptionError:
							pass  # Largest eigenvalue was not real.
						else:
							# If we actually found an invariant lamination then return it.
							if condition_matrix.nonnegative_image(eigenvector):
								invariant_lamination = triangulation.lamination(eigenvector)
								invariant_lamination = sum([self**(k+1) * invariant_lamination for k in range(j)])
								if not invariant_lamination.is_empty():
									return invariant_lamination
			
			for curve in new_curves:
				denominator = max(min(x for x in curve if x > 0), i+1)
				vector = [QQ.element([int(round(float(x) / denominator, 0))]) for x in curve]
				small_curve = triangulation.lamination(vector, remove_peripheral=True)
				if self * small_curve == small_curve:
					return small_curve
			
			curves.append(new_curves)
		
		raise flipper.ComputationError('Could not estimate invariant lamination.')
	
	def dilatation(self, lamination):
		''' Returns the dilatation of this mapping class on the given lamination.
		
		Assumes that the given lamination is projectively invariant. If not then
		it will discover this. '''
		
		assert(self.source_triangulation == self.target_triangulation)
		new_lamination = self * lamination
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
		
		assert(self.source_triangulation == self.target_triangulation)
		if self.is_periodic():  # Actually this test is redundant but it is faster to test it now.
			raise flipper.AssumptionError('Mapping class is not pseudo-Anosov.')
		lamination = self.invariant_lamination()
		# dilatation = self.dilatation(lamination)
		dilatation = lamination.vector[0].number_field.lmbda
		try:
			splitting = lamination.splitting_sequence(target_dilatation=dilatation)
		except flipper.AssumptionError:  # lamination is not filling.
			raise flipper.AssumptionError('Mapping class is not pseudo-Anosov.')
		# new_dilatation = splitting.dilatation()
		return splitting
	
	def decompose(self, other_encodings):
		''' Returns this mapping class as a composition of the given others. '''
		search_radius = 2
		all_words = [''.join(x) for x in product(other_encodings.keys(), repeat=search_radius)]
		
		curves = self.source_triangulation.key_curves()
		images = [self * curve for curve in curves]
		score = lambda imgs: max(curve.weight()**2 for curve in imgs)
		
		while score(images) > score(curves):
			best_word, best_score = None, score(images)
			for word in all_words:
				imgs = list(curve.copy() for curve in images)
				for letter in word:
					imgs = [other_encodings[letter] * curve for curve in imgs]
				if score(imgs) <= best_score:
					best_word = word
					best_score = score(imgs)
			
			images = [other_encodings[best_word[0]] * curve for curve in images]
		
		return True

