
# We can also produce Encodings using:
#	1) Id_Encoding(triangulation)
# and Encoding Sequences using:
#	1) Id_Encoding_Sequence(triangulation)
#	2) encode_flip(triangulation, edge_index)
#	3) encode_twist(lamination, k=1)
#	4) encode_isometry(isometry)

from __future__ import print_function
from functools import reduce
from itertools import product

from Flipper.Kernel.Lamination import Lamination, key_curves
from Flipper.Kernel.Matrix import Matrix, Id_Matrix, Empty_Matrix, Permutation_Matrix, nonnegative_image, tweak_vector
from Flipper.Kernel.Isometry import all_isometries
from Flipper.Kernel.Error import AbortError, ComputationError, AssumptionError

# These represent the piecewise-linear maps between the coordinates systems of various abstract triangulations.

class Encoding:
	def __init__(self, actions, conditions, source_triangulation, target_triangulation, as_latex=None):
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
		if isinstance(other, Encoding_Sequence):
			return Encoding_Sequence([self] + other.sequence, other.source_triangulation, self.target_triangulation)
		elif isinstance(other, Encoding):
			return Encoding_Sequence([self, other], other.source_triangulation, self.target_triangulation)
		elif isinstance(other, Lamination):
			return Lamination(self.target_triangulation, self * other.vector)
		elif isinstance(other, list):
			for i in range(self.size):
				if nonnegative_image(self.condition_matrices[i], other):
					return self.action_matrices[i] * other
			raise IndexError
		elif other is None:
			return Encoding_Sequence([self], self.source_triangulation, self.target_triangulation)
		else:
			return NotImplemented
	def __rmul__(self, other):
		if other is None:
			return Encoding_Sequence([self], self.source_triangulation, self.target_triangulation)
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

class Encoding_Sequence:
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
		if isinstance(other, Encoding_Sequence):
			assert(self.source_triangulation == other.target_triangulation)
			return Encoding_Sequence(self.sequence + other.sequence, other.source_triangulation, self.target_triangulation)
		elif isinstance(other, Encoding):
			assert(self.source_triangulation == other.target_triangulation)
			return Encoding_Sequence(self.sequence + [other], other.source_triangulation, self.target_triangulation)
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
			return Id_Encoding_Sequence(self.source_triangulation)
		elif k > 0:
			return Encoding_Sequence(self.sequence * k, self.source_triangulation, self.target_triangulation)
		else:
			return Encoding_Sequence([A.inverse() for A in reversed(self.sequence)] * abs(k), self.source_triangulation, self.target_triangulation)
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
			return Encoding_Sequence(self.sequence[key], self.sequence[key.end].source_triangulation, self.sequence[key.start].target_triangulation)
		elif isinstance(key, int):
			return self.sequence[key]
		else:
			raise TypeError('Invalid argument type.')
	
	def compactify(self):
		''' Returns an Encoding_Sequence which acts equivalently to this one but which has no Encoding of size 1. '''
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
	
	def order(self):
		''' Returns the order of this mapping class. If this has infinite order then returns 0. '''
		assert(self.source_triangulation == self.target_triangulation)
		curves, max_order = key_curves(self.source_triangulation), self.source_triangulation.max_order
		for i in range(1, max_order+1):
			if all(self**i * v == v for v in curves):
				return i
		return 0
	
	def is_identity(self):
		return self.order() == 1
	
	def is_periodic(self):
		return self.order() > 0
	
	def is_reducible(self, certify=False, show_progress=None, options=None):
		''' This determines if the induced action of self on V has a fixed point satisfying:
		face_matrix.v >= 0 and marking_matrix.v >= 0 for some marking_matrix in marking_matrices.
		
		If certify is True then this returns (True, example) is there is such fixed point and (False, None) otherwise. '''
		# We now use Ben's branch and bound approach. It's much better.
		assert(self.source_triangulation == self.target_triangulation)
		
		# We first create two little functions to increment the list of indices to the next point that 
		# we are interested in. The first jumps from our current location to the next subtree, the second
		# advances to the next index according to the lex ordering.
		
		sizes = [encoding.size for encoding in self]
		sizes_mul = [reduce(lambda x,y: x*y, sizes[i:], 1) for i in range(len(sizes))]
		total = 2 * sizes[0] * sizes_mul[0]  # !?! BUG FIX?
		
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
		
		def progress(indices):  # !?! BUG HERE.
			return sum(index * scale for index, scale in zip(indices, sizes_mul)) / total
		
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
						certificate = Lamination(self.source_triangulation, [2*i for i in certificate])
						assert(self.check_fixedpoint(certificate))
						if show_progress is not None: show_progress.cancel()
						if options is not None and options.statistics: print(buckets)
						return (True, certificate) if certify else True
				indices = jump(indices)
		
		if show_progress is not None: show_progress.cancel()
		if options is not None and options.statistics: print(buckets)
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

#### Some special Encodings we know how to build.

def Id_Encoding(triangulation):
	return Encoding([Id_Matrix(triangulation.zeta)], [Empty_Matrix(triangulation.zeta)], triangulation, triangulation)

#### Some special Encoding_Sequences we know how to build.

def Id_Encoding_Sequence(triangulation):
	return Encoding_Sequence([], triangulation, triangulation)

def encode_flip(triangulation, edge_index):
	# Returns a forwards and backwards maps to a new triangulation obtained by flipping the edge of index edge_index.
	assert(triangulation.edge_is_flippable(edge_index))
	
	new_triangulation = triangulation.flip_edge(edge_index)
	
	a, b, c, d = triangulation.find_indicies_of_square_about_edge(edge_index)
	A1 = Id_Matrix(triangulation.zeta)
	tweak_vector(A1[edge_index], [a, c], [edge_index, edge_index])  # The double -f here forces A1[f][f] = -1.
	C1 = Matrix(tweak_vector([0] * triangulation.zeta, [a, c], [b, d]), triangulation.zeta)
	
	A2 = Id_Matrix(triangulation.zeta)
	tweak_vector(A2[edge_index], [b, d], [edge_index, edge_index])  # The double -f here forces A2[f][f] = -1.
	C2 = Matrix(tweak_vector([0] * triangulation.zeta, [b, d], [a, c]), triangulation.zeta)
	
	actions = [action_matrix.latex_string()[edge_index] for action_matrix in [A1, A2]]
	conditions = [' \\wedge '.join(condition_matrix.latex_string()) for condition_matrix in [C1, C2]]
	as_latex = '%s(\\underline{x})' + ('[%d]' % edge_index) + ' &= \n\t\\begin{cases} \n' + ' \\\\ \n'.join('\t\t%s &\\mbox{if } %s \\geq 0' % (a, c) for a,c in zip(actions, conditions)) + '\n\t\\end{cases}'
	
	return Encoding([A1, A2], [C1, C2], triangulation, new_triangulation, as_latex), Encoding([A1, A2], [C1, C2], new_triangulation, triangulation, as_latex)

def encode_flips(triangulation, edge_indices):
	forwards_sequence, backwards_sequence = Id_Encoding_Sequence(triangulation), Id_Encoding_Sequence(triangulation)
	for edge_index in edge_indices:
		forwards, backwards = encode_flip(forwards_sequence.target_triangulation, edge_index)
		forwards_sequence = forwards * forwards_sequence
		backwards_sequence = backwards_sequence * backwards
	
	return forwards_sequence, backwards_sequence

def encode_twist(lamination, k=1):
	''' Returns an Encoding of a left Dehn twist about this lamination raised to the power k.
	If k is zero this will return None, which can be used as the identity Encoding. If k is negative this 
	will return an Encoding of a right Dehn twist about this lamination raised to the power -k.
	Assumes that this lamination is a curve, if not an AssumptionError is thrown. '''
	if not lamination.is_good_curve():
		raise AssumptionError('Not a good curve.')
	
	if k == 0: return Id_Encoding_Sequence(lamination.abstract_triangulation)
	
	lamination_copy = lamination.copy()
	
	# We'll keep track of what we have conjugated by as well as it's inverse
	# we could compute this at the end by doing:
	#   conjugation_inverse = conjugation.inverse()
	# but this is much faster as we don't need to invert a load of matrices.
	conjugation = Id_Encoding_Sequence(lamination_copy.abstract_triangulation)
	conjugation_inverse = Id_Encoding_Sequence(lamination_copy.abstract_triangulation)
	
	while lamination.weight() > 2:
		# Find the edge which decreases our weight the most.
		# If none exist then it doesn't matter which edge we flip, so long as it meets the curve.
		# By Lee Mosher's work there is a complexity that we will reduce to by doing this and eventually we will reach weight 2.
		edge_index = min([i for i in range(lamination.zeta) if lamination[i] > 0 and lamination.abstract_triangulation.edge_is_flippable(i)], key=lambda i: lamination.weight_difference_flip_edge(i))
		
		forwards, backwards = encode_flip(lamination.abstract_triangulation, edge_index)
		conjugation = forwards * conjugation
		conjugation_inverse = conjugation_inverse * backwards
		lamination = forwards * lamination
	
	triangulation = lamination.abstract_triangulation
	# Grab the indices of the two edges we meet.
	e1, e2 = [edge_index for edge_index in range(lamination.zeta) if lamination[edge_index] > 0]
	# We might need to swap these edge indices so we have a good frame of reference.
	containing_triangles = triangulation.find_edge(e1)
	if containing_triangles[0][0][containing_triangles[0][1] + 2] != e2: e1, e2 = e2, e1
	# But to do a right twist we'll need to switch framing again.
	if k < 0: e1, e2 = e2, e1
	
	# Finally we can encode the twist.
	forwards, backwards = encode_flip(lamination.abstract_triangulation, e1)
	lamination = forwards * lamination
	new_triangulation = lamination.abstract_triangulation
	
	# Find the correct isometry to take us back.
	map_back = encode_isometry([isom for isom in all_isometries(new_triangulation, triangulation) if isom.edge_map[e1] == e2 and isom.edge_map[e2] == e1 and all(isom.edge_map[x] == x for x in range(triangulation.zeta) if x not in [e1, e2])][0])
	T = map_back * forwards
	
	return conjugation_inverse * T**abs(k) * conjugation

def encode_halftwist(lamination, k=1):
	''' Returns an Encoding of a left Dehn twist about this lamination raised to the power k.
	If k is zero this will return None, which can be used as the identity Encoding. If k is negative this 
	will return an Encoding of a right Dehn twist about this lamination raised to the power -k.
	Assumes that this lamination is a curve, if not an AssumptionError is thrown. '''
	if not lamination.is_pants_boundary():
		raise AssumptionError('Not a boundary of a pair of pants.')
	
	if k == 0: return Id_Encoding_Sequence(lamination.abstract_triangulation)
	
	lamination_copy = lamination.copy()
	
	# We'll keep track of what we have conjugated by as well as it's inverse
	# we could compute this at the end by doing:
	#   conjugation_inverse = conjugation.inverse()
	# but this is much faster as we don't need to invert a load of matrices.
	conjugation = Id_Encoding_Sequence(lamination_copy.abstract_triangulation)
	conjugation_inverse = Id_Encoding_Sequence(lamination_copy.abstract_triangulation)
	
	while lamination.weight() > 2:
		# Find the edge which decreases our weight the most.
		# If none exist then it doesn't matter which edge we flip, so long as it meets the curve.
		# By Lee Mosher's work there is a complexity that we will reduce to by doing this and eventually we will reach weight 2.
		edge_index = min([i for i in range(lamination.zeta) if lamination[i] > 0 and lamination.abstract_triangulation.edge_is_flippable(i)], key=lambda i: lamination.weight_difference_flip_edge(i))
		
		forwards, backwards = encode_flip(lamination.abstract_triangulation, edge_index)
		conjugation = forwards * conjugation
		conjugation_inverse = conjugation_inverse * backwards
		lamination = forwards * lamination
	
	triangulation = lamination.abstract_triangulation
	# Grab the indices of the two edges we meet.
	e1, e2 = [edge_index for edge_index in range(lamination.zeta) if lamination[edge_index] > 0]
	# We might need to swap these edge indices so we have a good frame of reference.
	containing_triangles = triangulation.find_edge(e1)
	if containing_triangles[0][0][containing_triangles[0][1] + 2] != e2: e1, e2 = e2, e1
	# But to do a right twist we'll need to switch framing again.
	if k < 0: e1, e2 = e2, e1
	
	x, y = [edge_indices for edge_indices in triangulation.find_indicies_of_square_about_edge(e1) if edge_indices != e2]
	for triangle in triangulation:
		if (x in triangle or y in triangle) and len(set(triangle)) == 2:
			bottom = x if x in triangle else y
			other = triangle[0] if triangle[0] != bottom else triangle[1]
	
	# Finally we can encode the twist.
	forwards, backwards = encode_flip(lamination.abstract_triangulation, bottom)
	lamination = forwards * lamination
	
	forwards2, backwards2 = encode_flip(lamination.abstract_triangulation, e1)
	lamination = forwards2 * lamination
	
	forwards3, backwards3 = encode_flip(lamination.abstract_triangulation, e2)
	lamination = forwards3 * lamination
	
	new_triangulation = lamination.abstract_triangulation
	
	# Find the correct isometry to take us back.
	map_back = encode_isometry([isom for isom in all_isometries(new_triangulation, triangulation) if isom.edge_map[e1] == e2 and isom.edge_map[e2] == bottom and isom.edge_map[bottom] == e1 and all(isom.edge_map[x] == x for x in range(triangulation.zeta) if x not in [e1, e2, bottom])][0])
	T = map_back * forwards3 * forwards2 * forwards
	
	return conjugation_inverse * T**abs(k) * conjugation

def encode_isometry(isometry):
	return Encoding([Permutation_Matrix(isometry.edge_map)], [Empty_Matrix(isometry.source_triangulation.zeta)], isometry.source_triangulation, isometry.target_triangulation)
