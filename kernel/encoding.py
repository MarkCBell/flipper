
from functools import reduce
from itertools import product

import Flipper

# These represent the piecewise-linear maps between the coordinates systems of various abstract triangulations.

class Encoding:
	def __init__(self, actions, conditions, source_triangulation, target_triangulation, as_latex=None):
		assert(len(actions) > 0)
		zeta = source_triangulation.zeta
		zeta2 = target_triangulation.zeta
		assert(len(actions) == len(conditions))
		assert(all(len(M) == zeta2 for M in actions))
		assert(all(len(row) == zeta for M in actions for row in M))
		assert(all(len(row) == zeta for M in conditions for row in M))
		# assert(all(abs(M.determinant()) == 1 for M in actions))
		
		self.size = len(actions)
		self.action_matrices = actions
		self.condition_matrices = conditions
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.zeta = zeta
		self.as_latex = as_latex
	
	def __str__(self):
		return '\n'.join(str(self.action_matrices[i]) + '\n' + str(self.condition_matrices[i]) for i in range(self.size))
	def latex_string(self):
		if len(self) == 1: return '%s(\\underline{x}) &= (' + ','.join(self.action_matrices[0].latex_string()) + ')'
		if self.as_latex is not None: return self.as_latex
		
		actions = ['(' + ','.join(action_matrix.latex_string()) + ')' for action_matrix in self.action_matrices]
		conditions = [' \\wedge '.join(condition_matrix.latex_string()) for condition_matrix in self.condition_matrices]
		return '%s(\\underline{x}) &= \n\t\\begin{cases} \n' + ' \\\\ \n'.join('\t\t%s &\\mbox{if } %s \\geq 0' % (a, c) for a,c in zip(actions, conditions)) + '\n\t\\end{cases}'
	def __len__(self):
		return self.size
	def __eq__(self, other):
		if self.size != other.size: return False
		if self.zeta != other.zeta: return False
		for i in range(self.size):
			if all(self.action_matrices[i] != other.action_matrices[j] or not self.condition_matrices[i].equivalent(other.condition_matrices[j]) for j in range(other.size)):
				return False
		return True
	def __call__(self, other):
		return self * other
	def __mul__(self, other):
		# Should have some more asserts here to check we're going between matching triangulations.
		if isinstance(other, EncodingSequence):
			return EncodingSequence([self] + other.sequence, other.source_triangulation, self.target_triangulation)
		elif isinstance(other, Encoding):
			return EncodingSequence([self, other], other.source_triangulation, self.target_triangulation)
		elif isinstance(other, Flipper.Lamination):
			return Flipper.Lamination(self.target_triangulation, self * other.vector)
		elif isinstance(other, list):
			for i in range(self.size):
				if self.condition_matrices[i].nonnegative_image(other):
					return self.action_matrices[i] * other
			raise IndexError
		elif other is None:
			return EncodingSequence([self], self.source_triangulation, self.target_triangulation)
		else:
			return NotImplemented
	def __rmul__(self, other):
		if other is None:
			return EncodingSequence([self], self.source_triangulation, self.target_triangulation)
		else:
			return NotImplemented
	def __pow__(self, n):
		assert(self.source_triangulation == self.target_triangulation)
		if n == 0:
			return self.source_triangulation.Id_Encoding()
		if n == 1:
			return self
		if n > 1:
			return reduce(lambda x, y: x * y, [self] * n, self.source_triangulation.Id_Encoding())
		if n == -1:
			return self.inverse()
		if n < -1:
			inv = self.inverse()
			return reduce(lambda x, y: x * y, [inv] * n, self.source_triangulation.Id_Encoding())
	def copy(self):
		return Encoding([matrix.copy() for matrix in self.action_matrices], [matrix.copy() for matrix in self.condition_matrices], self.source_triangulation, self.target_triangulation)
	def inverse(self):
		# Assumes that the matrices are invertible square.
		assert(source_triangulation.zeta == target_triangulation.zeta)
		X = [self.action_matrices[i].inverse() for i in range(self.size)]  # This is the very slow bit.
		Y = [self.condition_matrices[i] * X[i] for i in range(self.size)]
		return Encoding(X, Y, self.target_triangulation, self.source_triangulation)

class EncodingSequence:
	def __init__(self, L, source_triangulation, target_triangulation):
		# Should make sure the triangulations of the encodings in L chain together.
		assert(source_triangulation.zeta == target_triangulation.zeta)
		assert(all(isinstance(x, Encoding) for x in L))
		
		self.sequence = L
		self.zeta = source_triangulation.zeta
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		
		self.size = len(self.sequence)
	def __call__(self, other):
		return self * other
	def __mul__(self, other):
		if isinstance(other, EncodingSequence):
			assert(self.source_triangulation == other.target_triangulation)
			return EncodingSequence(self.sequence + other.sequence, other.source_triangulation, self.target_triangulation)
		elif isinstance(other, Encoding):
			assert(self.source_triangulation == other.target_triangulation)
			return EncodingSequence(self.sequence + [other], other.source_triangulation, self.target_triangulation)
		elif other is None:
			return self
		else:
			other = other.copy()
			for A in reversed(self.sequence):
				other = A * other
			return other
	def __rmul__(self, other):
		if other is None:
			return self
		else:
			return NotImplemented
	def __pow__(self, k):
		assert(self.source_triangulation == self.target_triangulation)
		if k == 0:
			return self.source_triangulation.Id_EncodingSequence()
		elif k > 0:
			return EncodingSequence(self.sequence * k, self.source_triangulation, self.target_triangulation)
		else:
			return EncodingSequence([A.inverse() for A in reversed(self.sequence)] * abs(k), self.source_triangulation, self.target_triangulation)
	def __len__(self):
		return self.size
	def __str__(self):
		return '\n###\n'.join(str(A) for A in self.sequence)
	def latex_string(self):
		s = ''
		if len(self) == 1:
			s += '\\[ f_1 \\]\n'
		elif len(self) == 2:
			s += '\\[ f_2 \\circ f_1 \\]\n'
		elif len(self) > 2:
			s += '\\[ f_{%d} \\circ \\cdots \\circ f_{1} \\]\n' % len(self)
		s += 'where if $\\underline{x} = (x_1, \\ldots, x_{%d})$ and $\\underline{x}[i] = x_i$ then:\n' % self.zeta  # This is always >= 3.
		s += '\\begin{align*} \n' + ' \\\\ \n'.join(encoding.latex_string() % ('f_{%d}' % (index+1)) for index, encoding in enumerate(self.sequence)) + '\n\\end{align*}\n'
		s += 'and $f_i[j](\\underline{x}) = \\underline{x}[j]$ otherwise. \n'
		return s
	def __iter__(self):
		return iter(self.sequence)
	def __getitem__(self, key):
		if isinstance(key, slice):
			return EncodingSequence(self.sequence[key], self.sequence[key.end].source_triangulation, self.sequence[key.start].target_triangulation)
		elif isinstance(key, Flipper.kernel.types.Integer_Type):
			return self.sequence[key]
		else:
			raise TypeError('Invalid argument type.')
	
	def compactify(self):
		''' Returns an EncodingSequence which acts equivalently to this one but which has no Encoding of size 1. '''
		# !?! Broken!
		X = []
		for encoding in self:
			if len(X) > 0 and len(encoding) == 1:
				X[-1] = X[-1] * encoding
			else:
				X.append(encoding.copy())
		
		if len(X) > 1 and len(X[0]) == 1:
			X[1] = X[0] * X[1]
			X = X[1:]
		
		return EncodingSequence(X, self.source_triangulation, self.target_triangulation)
	
	def applied_matrix(self, vector):
		''' Returns the matrix that will be applied to the vector and the condition matrix the vector must satisfy. '''
		vector2 = list(vector)
		indices = []
		for A in reversed(self):
			for i in range(A.size):
				if A.condition_matrices[i].nonnegative_image(vector2):
					indices.append(i)
					vector2 = A.action_matrices[i] * vector2
					break
		
		return self.expand_indices(indices)
	
	def inverse(self):
		return EncodingSequence([A.inverse() for A in reversed(self)], self.target_triangulation, self.source_triangulation)
	
	def expand_indices(self, indices):
		''' Given indices = [a_0, ..., a_k] this returns the action and condition matrix of
		choice[a_k] * ... * choice[a_0]. Be careful about the order in which you give the indices. '''
		
		As = Flipper.kernel.matrix.Id_Matrix(self.zeta)
		Cs = Flipper.kernel.matrix.Empty_Matrix(self.zeta)
		for E, i in zip(reversed(self), indices):
			Cs = Cs.join(E.condition_matrices[i] * As)
			As = E.action_matrices[i] * As
		
		return As, Cs
	
	def yield_expand(self):
		for indices in product(*[range(len(E)) for E in self]):
			yield indices, self.expand_indices(indices[::-1])
	
	def yield_feasible_expansions(self):
		for indices, (As, Cs) in self.yield_expand():
			if Cs.nontrivial_polytope()[0]:
				yield indices
	
	def order(self):
		''' Returns the order of this mapping class. If this has infinite order then returns 0. '''
		assert(self.source_triangulation == self.target_triangulation)
		curves, max_order = self.source_triangulation.key_curves(), self.source_triangulation.max_order
		for i in range(1, max_order+1):
			if all(self**i * v == v for v in curves):
				return i
		return 0
	
	def is_identity(self):
		return self.order() == 1
	
	def is_periodic(self):
		return self.order() > 0
	
	def is_reducible(self, certify=False, show_progress=None):
		''' This determines if the induced action of self on V has a fixed point satisfying:
		face_matrix.v >= 0 and marking_matrix.v >= 0 for some marking_matrix in marking_matrices.
		
		If certify is True then this returns (True, example) is there is such fixed point and (False, None) otherwise. '''
		# We now use Ben's branch and bound approach. It's much better.
		assert(self.source_triangulation == self.target_triangulation)
		
		# We first create two little functions to increment the list of indices to the next point that 
		# we are interested in. The first jumps from our current location to the next subtree, the second
		# advances to the next index according to the lex ordering.
		
		sizes = [encoding.size for encoding in self][::-1]
		sizes_mul = [reduce(lambda x,y: x*y, sizes[i:], 1) for i in range(len(sizes))]
		total = sum((scale-1) * scale_prod for scale, scale_prod in zip(sizes, sizes_mul))
		
		def jump(indices):
			indices = list(indices)
			while len(indices) > 0 and indices[-1] == len(self[self.size-len(indices)].condition_matrices)-1:
				indices.pop()
			if len(indices) > 0: indices[-1] += 1
			return indices
		
		def next(indices):
			indices = list(indices)
			if len(indices) < self.size:
				return indices + [0]
			elif len(indices) == self.size:
				return jump(indices)
			else:
				raise IndexError
		
		def progress(indices):
			return float(sum(index * scale for index, scale in zip(indices, sizes_mul))) / total
		
		face_matrix, marking_matrices = self.source_triangulation.face_matrix(), self.source_triangulation.marking_matrices()
		
		M4 = face_matrix
		M6 = Flipper.kernel.matrix.Id_Matrix(self.zeta)
		buckets = {}
		indices = [0]
		while indices != []:
			if len(indices) not in buckets: buckets[len(indices)] = 0
			buckets[len(indices)] += 1
			As, Cs = self.expand_indices(indices)
			if show_progress is not None: show_progress.update_bar(progress(indices))
			if len(indices) < self.size:
				S, certificate = Cs.nontrivial_polytope()
				indices = next(indices) if S else jump(indices)
			else:
				for i in range(len(marking_matrices)):
					M1 = Cs
					M2 = As - M6  # As - Flipper.kernel.matrix.Id_Flipper.kernel.matrix.
					M3 = M6 - As  # Flipper.kernel.matrix.Id_Matrix - As.
					M5 = marking_matrices[i]
					
					# M4 = face_matrix  # These have been precomputed.
					# M6 = Flipper.kernel.matrix.Id_Matrix(self.zeta)
					P = M4.join(M5).join(M2).join(M3).join(M1)  # A better order.
					S, certificate = P.nontrivial_polytope()
					if S:
						certificate = Flipper.Lamination(self.source_triangulation, [2*i for i in certificate])
						assert(self.check_fixedpoint(certificate))
						if show_progress is not None: show_progress.cancel()
						return (True, certificate) if certify else True
				indices = jump(indices)
		
		if show_progress is not None: show_progress.cancel()
		return (False, None) if certify else False
	
	def is_reducible2(self, is_multicurve, certify=False):
		''' This is insane. Never run this. In fact most of the time Python wont let you as you hit the CInt limit. '''
		assert(self.source_triangulation == self.target_triangulation)
		
		K = (self.zeta ** self.zeta) * (3 ** (self.zeta * self.size))
		for vector in product(range(K), repeat=self.zeta):
			if is_multicurve(vector) and self * vector == vector:
				return (True, vector) if certify else True
		return (False, None) if certify else False
	
	def check_fixedpoint(self, certificate):
		assert(self.source_triangulation == self.target_triangulation)
		return certificate.is_multicurve() and self * certificate == certificate
	
	def invariant_lamination(self, exact=True):
		# This uses Flipper.kernel.symboliccomputation.Perron_Frobenius_eigen() to return a lamination
		# (with entries of algebraic_type) which is projectively invariant under this mapping class. 
		
		# This is designed to be called only with pseudo-Anosov mapping classes and so assumes that 
		# the mapping class is not periodic. If not an AssumptionError is thrown.
		
		# The process starts with several curves on the surface and repeatedly applies the map until 
		# they appear to projectively converge. If exact is set to False then the process stops and 
		# returns one of these curves as an approximation of the invariant lamination. Otherwise 
		# Flipper.kernel.symboliccomputation.Perron_Frobenius_eigen() is used to find the nearby 
		# projective fixed point.
		
		# If these curves do not appear to converge, this is detected and a ComputationError thrown. 
		
		# Note: in most pseudo-Anosov cases < 15 iterations are needed, if it fails to
		# converge after 1000 iterations it's actually extremely likely that the map was not pseudo-Anosov.
		
		assert(self.source_triangulation == self.target_triangulation)
		if self.is_periodic():
			raise Flipper.kernel.error.AssumptionError('Mapping class is periodic.')
		curves = self.source_triangulation.key_curves()
		
		def projective_difference(A, B, error_reciprocal):
			# Returns True iff the projective difference between A and B is less than 1 / error_reciprocal.
			A_sum, B_sum = sum(A), sum(B)
			return max(abs((p * B_sum) - q * A_sum) for p, q in zip(A, B)) * error_reciprocal < A_sum * B_sum 
		
		new_curves = [self * curve for curve in curves]
		for i in range(1000):
			new_curves, curves = [self * new_curve for new_curve in new_curves], new_curves
			if i > 3:  # Make sure to do at least n==4 iterations.
				for new_curve, curve in zip(new_curves, curves):
					if projective_difference(new_curve, curve, 1000000000):
						if exact:
							if Flipper.kernel.symboliccomputation._name == 'dummy': raise ImportError('Dummy symbolic library used.')
							if curve == new_curve:
								return Flipper.Lamination(self.source_triangulation, [Flipper.kernel.symboliccomputation.algebraic_type_from_int(v) for v in curve])  # Convert to AlgebraicType!
							else:
								action_matrix, condition_matrix = self.applied_matrix(curve)
								try:
									eigenvector = Flipper.kernel.symboliccomputation.Perron_Frobenius_eigen(action_matrix, curve.vector, condition_matrix)
									return Flipper.Lamination(self.source_triangulation, eigenvector)
								except Flipper.kernel.error.AssumptionError:  # action_matrix was not Perron-Frobenius.
									raise Flipper.kernel.error.ComputationError('Could not estimate invariant lamination.')
						else:
							return Flipper.Lamination(self.source_triangulation, curve)
		else:
			raise Flipper.kernel.error.ComputationError('Could not estimate invariant lamination.')
	
	def dilatation(self, lamination):
		# Returns the dilatation of this mapping class on the given lamination.
		# This only makes sense if the lamination is projectively invariant.
		
		new_lamination = self * lamination
		return new_lamination.weight() / lamination.weight()
