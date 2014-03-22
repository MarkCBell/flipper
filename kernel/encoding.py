from functools import reduce
from itertools import product

import Flipper

NT_TYPE_PERIODIC = 'Periodic'
NT_TYPE_REDUCIBLE = 'Reducible'
NT_TYPE_PSEUDO_ANOSOV = 'Pseudo-Anosov'

# Represents a linear function defined on a piece of the space of laminations on source_triangulation.
# If condition is not set the no condition is assumed, that is the function is defined on the 
# entirety of the space.
class PartialFunction(object):
	def __init__(self, source_triangulation, target_triangulation, action, condition=None):
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.action = action
		if condition is None: condition = Flipper.kernel.Empty_Matrix()
		self.condition = condition
	
	def __str__(self):
		return str(self.action) + '\n' + str(self.condition)
	
	def __call__(self, other):
		return self * other
	
	def __mul__(self, other):
		if isinstance(other, Flipper.kernel.Lamination) and other.abstract_triangulation == self.source_triangulation:
			if self.condition.nonnegative_image(other.vector):
				return self.target_triangulation.lamination(self.action * other.vector)
		
		raise TypeError('Object is not in domain.')

# These represent the piecewise-linear maps between the coordinates systems of various abstract triangulations.

class Encoding(object):
	def __init__(self, partial_functions, inverse_partial_functions=None, name=None):
		self.partial_functions = partial_functions
		assert(len(self.partial_functions) > 0)
		self.source_triangulation = self.partial_functions[0].source_triangulation
		self.target_triangulation = self.partial_functions[0].target_triangulation
		assert(all(f.source_triangulation == self.source_triangulation for f in self.partial_functions))
		if inverse_partial_functions is None: inverse_partial_functions = []
		self.inverse_partial_functions = inverse_partial_functions
		assert(all(f.target_triangulation == self.target_triangulation for f in self.partial_functions))
		
		self.name = name
	
	def __iter__(self):
		return iter(self.partial_functions)
	def __str__(self):
		return '\n'.join(str(function) for function in self.partial_functions)
	def __len__(self):
		return len(self.partial_functions)
	def __getitem__(self, index):
		return self.partial_functions[index]
	def __eq__(self, other):
		all(self * curve == other * curve for curve in self.source_triangulation.key_curves())
		return self.source_triangulation == other.source_triangulation and \
			self.target_triangulation == other.target_triangulation and \
			all(self * curve == other * curve for curve in self.source_triangulation.key_curves())
	def __hash__(self):
		return hash(tuple(self.partial_functions + self.inverse_partial_functions))
	def __call__(self, other):
		return self * other
	def __mul__(self, other):
		if isinstance(other, Encoding):
			return EncodingSequence([self, other])
		elif isinstance(other, EncodingSequence):
			return EncodingSequence([self] + other.sequence)
		elif isinstance(other, Flipper.kernel.Lamination):
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
			return EncodingSequence([self] * n)
		elif n == 0:
			return self.source_triangulation.Id_Encoding()
		elif n < 0:
			return self.inverse()**abs(n)
	def copy(self):
		return Encoding([f.copy() for f in self.partial_functions], [f.copy() for f in self.inverse_partial_functions], self.name)
	def inverse(self):
		if not self.inverse_partial_functions:
			raise TypeError('Function is not invertible.')
		
		return Encoding(self.inverse_partial_functions, self.partial_functions)
	def applied_index(self, lamination):
		# Returns the index of the partial function that would be applied to this lamination.
		for index, function in enumerate(self.partial_functions):
			try:
				function(lamination)
				return index
			except TypeError:
				pass
		
		raise TypeError('Object is not in domain.')

class EncodingSequence(object):
	def __init__(self, sequence, name=None):
		self.sequence = sequence
		assert(all(isinstance(x, Encoding) for x in self.sequence))
		assert(all(x.source_triangulation == y.target_triangulation for x, y in zip(self.sequence, self.sequence[1:])))
		
		self.source_triangulation = self.sequence[-1].source_triangulation
		self.target_triangulation = self.sequence[0].target_triangulation
		self.zeta = self.source_triangulation.zeta
		self.name = name
	
	def __len__(self):
		return len(self.sequence)
	def __str__(self):
		return '\n###\n'.join(str(A) for A in self.sequence)
	def __iter__(self):
		return iter(self.sequence)
	def __getitem__(self, key):
		if isinstance(key, slice):
			return EncodingSequence(self.sequence[key])
		elif isinstance(key, Flipper.kernel.Integer_Type):
			return self.sequence[key]
		else:
			raise TypeError('Invalid argument type.')
	def __eq__(self, other):
		return self.source_triangulation == other.source_triangulation and \
			self.target_triangulation == other.target_triangulation and \
			all(self * curve == other * curve for curve in self.source_triangulation.key_curves())
	def __hash__(self):
		return hash(tuple(self.sequence))
	def __call__(self, other):
		return self * other
	def __mul__(self, other):
		if isinstance(other, EncodingSequence):
			return EncodingSequence(self.sequence + other.sequence)
		elif isinstance(other, Encoding):
			return EncodingSequence(self.sequence + [other])
		else:
			other = other.copy()
			for A in reversed(self.sequence):
				other = A * other
			return other
	def __pow__(self, k):
		assert(self.source_triangulation == self.target_triangulation)
		if k == 0:
			return self.source_triangulation.Id_EncodingSequence()
		elif k > 0:
			return EncodingSequence(self.sequence * k)
		else:
			return self.inverse()**abs(k)
	
	def inverse(self):
		return EncodingSequence([A.inverse() for A in reversed(self)])
	
	def applied_function(self, lamination):
		''' Returns the partial function that will be applied to the lamination. '''
		indices = []
		for A in reversed(self):
			indices.append(A.applied_index(lamination))
			lamination = A * lamination
		
		return self.expand_indices(indices)
	
	def expand_indices(self, indices):
		''' Given indices = [a_0, ..., a_k] this returns the partial function of
		choice[a_k] * ... * choice[a_0]. Be careful about the order in which you give the indices. '''
		
		As = Flipper.kernel.Id_Matrix(self.zeta)
		Cs = Flipper.kernel.Empty_Matrix()
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
		curves = self.source_triangulation.key_curves()
		max_order = self.source_triangulation.max_order
		id_map = self.source_triangulation.Id_EncodingSequence()
		for i in range(self.source_triangulation.max_order):
			if self**(i+1) == id_map:
				return i+1
		
		return 0
	
	def is_identity(self):
		return self == self.source_triangulation.Id_EncodingSequence()
	
	def is_periodic(self):
		return self.order() > 0
	
	def is_reducible(self, progression=None):
		''' This determines if the induced action of self on V has a fixed point satisfying:
		face_matrix.v >= 0 and marking_matrix.v >= 0 for some marking_matrix in marking_matrices. '''
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
			return float(sum(index * scale for index, scale in zip(indices, sizes_mul))) / total
		
		face_matrix, marking_matrices = self.source_triangulation.face_matrix(), self.source_triangulation.marking_matrices()
		
		M4 = face_matrix
		M6 = Flipper.kernel.Id_Matrix(self.zeta)
		indices = [0]
		while indices != []:
			partial_function = self.expand_indices(indices)
			As, Cs = partial_function.action, partial_function.condition
			if progression is not None: progression(progress(indices))
			if len(indices) < len(self):
				indices = next(indices) if Cs.nontrivial_polytope() else jump(indices)
			else:
				for i in range(len(marking_matrices)):
					M1 = Cs
					M2 = As - M6  # As - Flipper.kernel.Id_Matrix.
					M3 = M6 - As  # Flipper.kernel.Id_Matrix - As.
					M5 = marking_matrices[i]
					
					# M4 = face_matrix  # These have been precomputed.
					# M6 = Flipper.kernel.Id_Matrix(self.zeta)
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
	
	def NT_type(self, progression=None):
		if self.is_periodic():
			return NT_TYPE_PERIODIC
		elif self.is_reducible(progression=progression):
			return NT_TYPE_REDUCIBLE
		else:
			return NT_TYPE_PSEUDO_ANOSOV
	
	def NT_type_alternate(self):
		if self.is_periodic():
			return NT_TYPE_PERIODIC
		else:
			# This can also fail with a Flipper.ComputationError if self.invariant_lamination()
			# fails to find an invariant lamination.
			try:
				self.splitting_sequence()
				return NT_TYPE_PSEUDO_ANOSOV
			except Flipper.AssumptionError:
				return NT_TYPE_REDUCIBLE
	
	def invariant_lamination(self):
		# This uses Flipper.kernel.symboliccomputation.Perron_Frobenius_eigen() to return a lamination
		# (with entries of algebraic_type) which is projectively invariant under this mapping class. 
		#
		# This is designed to be called only with pseudo-Anosov mapping classes and so assumes that 
		# the mapping class is not periodic. If not an AssumptionError is thrown.
		# If the mapping class is:
		#	periodic then an AssumptionError will be thrown,
		#	reducible then an AssumptionError or ComputationError might be thrown or an invariant lamination will be returned, or
		#	pseudo-Anosov then a ComputationError might be thrown or an invariant lamination will be returned.
		#
		# The process starts with several curves on the surface and repeatedly applies the map until 
		# they appear to projectively converge. Finally Flipper.kernel.symboliccomputation.Perron_Frobenius_eigen() 
		# is used to find the nearby projective fixed point. Technically if we are in the reducible case we
		# might need to solve some LP problem over QQbar, but we don't know how to do this (quickly) so we
		# raise an AssumptionError - signifying that our mapping class is not pseudo-Anosov.
		#
		# If these curves do not appear to converge, this is detected and a ComputationError thrown. 
		#
		# Note: in most pseudo-Anosov cases < 15 iterations are needed, if it fails to converge after
		# 100 iterations and a ComputationError is thrown then it's actually extremely likely that the 
		# map was not pseudo-Anosov.
		
		assert(self.source_triangulation == self.target_triangulation)
		if self.is_periodic():
			raise Flipper.AssumptionError('Mapping class is periodic.')
		
		curves = self.source_triangulation.key_curves()
		
		def projective_difference(A, B, error_reciprocal):
			# Returns True iff the projective difference between A and B is less than 1 / error_reciprocal.
			A_sum, B_sum = sum(A), sum(B)
			return max(abs((p * B_sum) - q * A_sum) for p, q in zip(A, B)) * error_reciprocal < A_sum * B_sum 
		
		new_curves = [self * curve for curve in curves]
		for i in range(100):
			new_curves, curves = [self * new_curve for new_curve in new_curves], new_curves
			if i > 3:  # Make sure to do at least 4 iterations.
				for new_curve, curve in zip(new_curves, curves):
					if projective_difference(new_curve, curve, 1000):
						if curve == new_curve:
							return self.source_triangulation.lamination(Flipper.kernel.numberfield.number_field_from_integers(curve))
						else:
							partial_function = self.applied_function(curve)
							action_matrix, condition_matrix = partial_function.action, partial_function.condition
							try:
								eigenvector = Flipper.kernel.symboliccomputation.Perron_Frobenius_eigen(action_matrix)
								# If we actually found an invariant lamination then return it.
								if condition_matrix.nonnegative_image(eigenvector):
									return self.source_triangulation.lamination(eigenvector)
							except Flipper.AssumptionError:
								pass  # Didn't go far enough.
		
		raise Flipper.ComputationError('Could not estimate invariant lamination.')
	
	def dilatation(self, lamination):
		# Returns the dilatation of this mapping class on the given lamination.
		# This only makes sense if the lamination is projectively invariant.
		
		new_lamination = self * lamination
		if not lamination.projectively_equal(new_lamination):
			raise Flipper.AssumptionError('Lamination is not projectively invariant.')
		
		return new_lamination.weight() / lamination.weight()
	
	def splitting_sequence(self):
		lamination = self.invariant_lamination()
		# dilatation = self.dilatation(lamination)
		dilatation = lamination.vector[0].number_field.lmbda
		splitting = lamination.splitting_sequence(target_dilatation=dilatation, name=self.name)
		# new_dilatation = splitting.dilatation()
		return splitting
