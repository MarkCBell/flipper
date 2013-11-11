from __future__ import print_function
from functools import reduce
from itertools import product
from Matrix import Matrix, Id_Matrix, Empty_Matrix, Permutation_Matrix, nonnegative_image
from Error import AbortError
from Symbolic_Computation import compute_eigen

# These represent the piecewise-linear maps between the coordinates systems 
# of various abstract triangulations.

def Id_Encoding(triangulation):
	return Encoding([Id_Matrix(triangulation.zeta)], [Empty_Matrix(triangulation.zeta)], triangulation, triangulation)

def Permutation_Encoding(perutation, triangulation):
	return Encoding([Permutation_Matrix(perutation)], [Empty_Matrix(triangulation.zeta)], triangulation, triangulation)

class Encoding:
	def __init__(self, actions, conditions, source_triangulation, target_triangulation):
		assert(source_triangulation.zeta == target_triangulation.zeta)
		assert(len(actions) > 0)
		zeta = source_triangulation.zeta
		assert(len(actions) == len(conditions))
		assert(all(len(M) == zeta for M in actions))
		assert(all(len(row) == zeta for M in actions for row in M))
		assert(all(len(row) == zeta for M in conditions for row in M))
		assert(all(abs(M.determinant()) == 1 for M in actions))
		
		self.size = len(actions)
		self.action_matrices = actions
		self.condition_matrices = conditions
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.zeta = zeta
	def __str__(self):
		return '\n'.join(str(self.action_matrices[i]) + '\n' + str(self.condition_matrices[i]) for i in range(self.size))
	def __len__(self):
		return self.size
	def __eq__(self, other):
		if self.size != other.size: return False
		if self.zeta != other.zeta: return False
		for i in range(self.size):
			if all(self.action_matrices[i] != other.action_matrices[j] or not self.condition_matrices[i].equivalent(other.condition_matrices[j]) for j in range(other.size)):
				return False
		return True
	def equivalent(self, other):
		# !?! TO DO: Check if self and other act equivalently.
		if self.zeta != other.zeta: return False
		return False
	def __call__(self, other):
		return self * other
	def __mul__(self, other):
		if isinstance(other, Encoding_Sequence):
			return Encoding_Sequence([self] + other.sequence, other.source_triangulation, self.target_triangulation)
		elif isinstance(other, Encoding):
			X = [self.action_matrices[i] * other.action_matrices[j] for i in range(self.size) for j in range(other.size)]
			Y = [other.condition_matrices[j].join(self.condition_matrices[i]*other.action_matrices[j]) for i in range(self.size) for j in range(other.size)]
			return Encoding(X, Y, other.source_triangulation, self.target_triangulation)
		elif isinstance(other, list):  # other is a vector.
			for i in range(self.size):
				if nonnegative_image(self.condition_matrices[i], other):
					return self.action_matrices[i] * other
			raise IndexError
		else:
			return NotImplemented
	def __pow__(self, n):
		assert(self.source_triangulation == self.target_triangulation)
		if n == 0:
			return Id_Encoding(self)
		if n == 1:
			return self
		if n > 1:
			return reduce(lambda x, y: x * y, [self] * n, Id_Encoding(self))
		if n == -1:
			return self.inverse()
		if n < -1:
			inv = self.inverse()
			return reduce(lambda x, y: x * y, [inv] * n, Id_Encoding(self))
	def copy(self):
		return Encoding([matrix.copy() for matrix in self.action_matrices], [matrix.copy() for matrix in self.condition_matrices], self.source_triangulation, self.target_triangulation)
	def inverse(self):
		X = [self.action_matrices[i].inverse() for i in range(self.size)]  # This is the very slow bit.
		Y = [self.condition_matrices[i] * X[i] for i in range(self.size)]
		return Encoding(X, Y, self.target_triangulation, self.source_triangulation)

def Id_Encoding_Sequence(triangulation):
	return Encoding_Sequence([], triangulation, triangulation)

class Encoding_Sequence:
	def __init__(self, L, source_triangulation, target_triangulation):
		# Should make sure L is a list of encodings all coming from the same source.
		assert(source_triangulation.zeta == target_triangulation.zeta)
		self.sequence = L
		self.zeta = source_triangulation.zeta
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		
		self.size = len(self.sequence)
	def __call__(self, other):
		return self * other
	def __mul__(self, other):
		assert(isinstance(other, (Encoding_Sequence, Encoding, list)))
		if isinstance(other, Encoding_Sequence):
			assert(self.source_triangulation == other.target_triangulation)
			return Encoding_Sequence(self.sequence + other.sequence, other.source_triangulation, self.target_triangulation)
		elif isinstance(other, Encoding):
			assert(self.source_triangulation == other.target_triangulation)
			return Encoding_Sequence(self.sequence + [other], other.source_triangulation, self.target_triangulation)
		elif isinstance(other, list):
			vector = list(other)
			for A in reversed(self.sequence):
				vector = A * vector
			return vector
	def __pow__(self, k):
		assert(self.source_triangulation == self.target_triangulation)
		if k == 0:
			return Id_Encoding_Sequence(self.source_triangulation)
		elif k > 0:
			return Encoding_Sequence(self.sequence * k, self.source_triangulation, self.target_triangulation)
		else:
			return Encoding_Sequence([A.inverse() for A in reversed(self.sequence)] * abs(k), self.source_triangulation, self.target_triangulation)
	def __len__(self):
		return self.size
	def __str__(self):
		return '\n###\n'.join(str(A) for A in self.sequence)
	def __iter__(self):
		return iter(self.sequence)
	def __getitem__(self, key):
		if isinstance(key, slice):
			return Encoding_Sequence(self.sequence[key], self.sequence[key.end].source_triangulation, self.sequence[key.start].target_triangulation)
		elif isinstance(key, int):
			return self.sequence[key]
		else:
			raise TypeError('Invalid argument type.')
	
	def compactify(self):
		''' Returns an Encoding_Sequence which acts equivalently to this one but which only no Encoding of size 1. '''
		X = []
		for encoding in self:
			if len(X) > 0 and len(encoding) == 1:
				X[-1] = X[-1] * encoding
			else:
				X.append(encoding.copy())
		
		if len(X) > 1 and len(X[0]) == 1:
			X[1] = X[0] * X[1]
			X = X[1:]
		
		return Encoding_Sequence(X, self.source_triangulation, self.target_triangulation)
	
	def applied_matrix(self, vector):
		''' Returns the matrix that will be applied to the vector and the condition matrix the vector must satisfy. '''
		vector2 = list(vector)
		indices = []
		for A in reversed(self):
			for i in range(A.size):
				if nonnegative_image(A.condition_matrices[i], vector2):
					indices.append(i)
					vector2 = A.action_matrices[i] * vector2
					break
		
		return self.expand_indices(indices)
	
	def inverse(self):
		return Encoding_Sequence([A.inverse() for A in reversed(self)], self.target_triangulation, self.source_triangulation)
	
	def expand_indices(self, indices):
		''' Given indices = [a_0, ..., a_k] this returns the action and condition matrix of
		choice[a_k] * ... * choice[a_0]. Be careful about the order in which you give the indices. '''
		
		As = Id_Matrix(self.zeta)
		Cs = Empty_Matrix(self.zeta)
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
	
	def is_periodic(self):
		assert(self.source_triangulation == self.target_triangulation)
		key_curves, max_order = self.source_triangulation.key_curves(), self.source_triangulation.max_order
		return any(all(self**i * v == v for v in key_curves) for i in range(1,max_order+1))
	
	def is_reducible(self, certify=False, show_progress=None, options=None):
		''' This determines if the induced action of self on V has a fixed point satisfying:
		face_matrix.v >= 0 and marking_matrix.v >= 0 for some marking_matrix in marking_matrices.
		
		If certify is True then this returns (True, example) is there is such fixed point and (False, None) otherwise. '''
		# We now use Ben's branch and bound approach. It's much better.
		assert(self.source_triangulation == self.target_triangulation)
		
		# We first create two little functions to increment the list of indices to the next point that 
		# we are interested in. The first jumps from our current location to the next subtree, the second
		# advances to the next index according to the lex ordering.
		
		reciprocal_sizes = [float(1) / encoding.size for encoding in self]
		reciprocal_sizes_mul = [reduce(lambda x,y: x*y, reciprocal_sizes[:i], reciprocal_sizes[0]) for i in range(len(reciprocal_sizes))]
		
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
			return sum(index * scale for index, scale in zip(indices, reciprocal_sizes_mul))
		
		face_matrix, marking_matrices = self.source_triangulation.face_matrix(), self.source_triangulation.marking_matrices()
		
		M4 = face_matrix
		M6 = Id_Matrix(self.zeta)
		buckets = {}
		# for i in range(len(marking_matrices)):
		indices = [0]
		# M5 = marking_matrices[i]
		while indices != []:
			if len(indices) not in buckets: buckets[len(indices)] = 0
			buckets[len(indices)] += 1
			As, Cs = self.expand_indices(indices)
			if options is not None and options.debugging: print(indices)
			# if show_progress is not None: show_progress.update_bar((i + progress(indices)) / len(marking_matrices))
			if show_progress is not None: show_progress.update_bar(progress(indices))
			if len(indices) < self.size:
				# S, certificate = M4.join(M5).join(Cs).nontrivial_polytope()
				S, certificate = Cs.nontrivial_polytope()
				indices = next(indices) if S else jump(indices)
			else:
				for i in range(len(marking_matrices)):
					M1 = Cs
					M2 = As - M6  # As - Id_Matrix.
					M3 = M6 - As  # Id_Matrix - As.
					M5 = marking_matrices[i]
					
					# M4 = face_matrix  # These have been precomputed.
					# M5 = marking_matrices[i]
					# M6 = Id_Matrix(self.zeta)
					P = M4.join(M5).join(M2).join(M3).join(M1)  # A better order.
					S, certificate = P.nontrivial_polytope()
					if S:
						assert(self.check_fixedpoint(certificate))
						if show_progress is not None: show_progress.cancel()
						if options is not None and options.statistics: print(buckets)
						return (True, [2*i for i in certificate]) if certify else True
				indices = jump(indices)
		
		if show_progress is not None: show_progress.cancel()
		if options is not None and options.statistics: print(buckets)
		return (False, None) if certify else False
	
	def is_reducible2(self, is_multicurve, certify=False):
		''' This is insane. Never run this. In fact most of the time Python wont let you as you hit the CInt limit. '''
		assert(self.source_triangulation == self.target_triangulation)
		
		K = (self.zeta ** self.zeta) * (3 ** (self.zeta * self.size))
		print(K)
		for vector in product(range(K), repeat=self.zeta):
			if is_multicurve(vector) and self * vector == vector:
				return (True, vector) if certify else True
		return (False, None) if certify else False
	
	def check_fixedpoint(self, certificate):
		assert(self.source_triangulation == self.target_triangulation)
		return self.source_triangulation.is_multicurve(certificate) and self * certificate == certificate
	
	def stable_lamination(self, exact=False):
		# Returns a curve that is quite (very) close to the stable lamination of this mapping class and an 
		# (floating point) estimate of the dilatation. If one cannot be found this an AbortError is thrown. 
		# If exact is set to True then this uses compute_eigen to return the exact stable lamination (as a list of
		# algebraic numbers) along with the exact dilatation (again as an algebraic number).
		
		assert(self.source_triangulation == self.target_triangulation)
		curve = self.source_triangulation.key_curves()[0]
		
		def is_stable(curve, new_curve, error_reciprocal):
			curve_sum, new_curve_sum = sum(curve), sum(new_curve)
			return max(abs((p * new_curve_sum) - q * curve_sum) for p, q in zip(curve, new_curve)) * error_reciprocal < curve_sum * new_curve_sum 
		
		new_curve = self * curve
		for i in range(1000):
			new_curve, curve = self * new_curve, new_curve
			if i > 10 and is_stable(curve, new_curve, 1000000000):  # Make sure to apply at least 10 iterations.
				break
		else:
			raise AbortError
		
		if exact:
			action_matrix, condition_matrix = self.applied_matrix(new_curve)
			eigenvector, eigenvalue = compute_eigen(action_matrix)
			if nonnegative_image(condition_matrix, eigenvector):  # Check that the projective fixed point is actually in this cell. 
				return eigenvector, eigenvalue
			else:
				raise AbortError  # If not then the curve failed to get close enough to the stable lamination.
		else:
			return new_curve, float(new_curve[0]) / curve[0]
