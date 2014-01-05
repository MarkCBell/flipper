
from __future__ import print_function
from itertools import combinations, groupby, product
from fractions import gcd
from functools import reduce

def tweak_vector(v, add, subtract):
	for i in add: v[i] += 1
	for i in subtract: v[i] -= 1
	return v

def antipodal(v, w):
	# Returns if v & w are antipodal vectors.
	return all([v[i] == -w[i] for i in range(len(v))])

def find_antipodal(R, width):
	X = sorted(R, key=lambda x:[abs(i) for i in x])
	for k, g in groupby(X, key=lambda x:[abs(i) for i in x]):
		for R1, R2 in combinations(g, 2):
			if antipodal(R1, R2):
				yield (R1, R2)
	
	return

def find_one(v):
	# Returns the index of a +/-1 entry of v or -1 if there isn't one.
	for i in range(len(v)):
		if abs(v[i]) == 1:
			return i
	return -1

def rescale(v):
	c = abs(reduce(gcd, v))
	return [x // c for x in v]

def nonnegative(v):
	return all(x >= 0 for x in v)

def nonnegative_image(M, v):
	return all(dot(row, v) >= 0 for row in M)

def nontrivial(v):
	return any(v)

def dot(a, b):
	return sum([a[i] * b[i] for i in range(len(a))])
	# return sum(x * y for x, y in zip(a,b))

class Matrix:
	def __init__(self, data, width):
		if not data or isinstance(data[0], (list, tuple)):
			assert(all(isinstance(row, (list, tuple)) for row in data))
			self.rows = [list(row) for row in data]
		else:
			self.rows = list(list(data[i:i+width]) for i in range(0,len(data),width))
		self.width = width
		self.height = len(self.rows)
		assert(all(len(row) == self.width for row in self))
	def copy(self):
		return Matrix([list(row) for row in self], self.width)
	def __iter__(self):
		return iter(self.rows)
	def __getitem__(self, index):
		return self.rows[index]
	def __str__(self):
		return '[\n' + ',\n'.join(str(row) for row in self) + '\n]'
	def __mul__(self, other):
		if isinstance(other, Matrix):
			assert(self.width == len(other))
			otherT = other.transpose()
			return Matrix([[dot(a, b) for b in otherT] for a in self], other.width)
		elif isinstance(other, list):  # other is a vector.
			assert(self.width == len(other))
			return [dot(row, other) for row in self]
		elif isinstance(other, int):
			return Matrix([[entry * other for entry in row] for row in self], self.width)
		else:
			return NotImplemented
	def __add__(self, other):
		assert(self.width == other.width and self.height == other.height)
		return Matrix([[self[i][j] + other[i][j] for j in range(self.width)] for i in range(self.height)], self.width)
	def __sub__(self, other):
		assert(self.width == other.width and self.height == other.height)
		return Matrix([[self[i][j] - other[i][j] for j in range(self.width)] for i in range(self.height)], self.width)
	def __len__(self):
		return self.height
	def __iter__(self):
		return iter(self.rows)
	def __eq__(self, other):
		if self.width != other.width or self.height != other.height: return False
		return all(row1 == row2 for row1, row2 in zip(self.rows, other.rows))
	def equivalent(self, other):
		return sorted(self.rows) == sorted(other.rows)
	def inverse(self):
		assert(self.width == self.height)
		I = self.determinant()
		assert(abs(I) == 1)
		A = [[0] * self.width for i in range(self.height)]
		for i in range(self.height):
			for j in range(self.width):
				M = Matrix([[self.rows[k][l] for l in range(self.width) if l != j] for k in range(self.height) if k != i], self.width-1)
				A[j][i] = I * (-1 if (i+j) % 2 else 1) * M.determinant()  # Remember to transpose.
		assert(Matrix(A, self.width) * self == Id_Matrix(self.width))
		return Matrix(A, self.width)
	def transpose(self):
		return Matrix(list(zip(*self.rows)), self.height)
	def trace(self):
		return sum(self[i][i] for i in range(self.width))
	def tensor(self, other):
		return Matrix([[self[i][j] * other[a][b] for j, b in product(range(self.width), range(other.width))] for i, a in product(range(self.height), range(other.height))], self.width * other.width)
	def __xor__(self, other):
		return self.tensor(other)
	def char_poly(self):
		A = self.copy()
		p = [1]
		for i in range(1, self.width+1):
			ci = -A.trace() // i
			p.append(ci)
			A = self * (A + Id_Matrix(self.width) * ci)
		return p[::-1]
	def substitute_row(self, index, new_row):
		return Matrix([(row if i != index else new_row) for i, row in enumerate(self.rows)], self.width)
	def discard_column(self, column):
		self.rows = [[row[i] for i in range(self.width) if i != column] for row in self]
		self.width -= 1
	def join(self, other):
		assert(self.width == other.width)
		return Matrix(self.rows + other.rows, self.width)
	def bound(self):
		if self.height == 0: return 0
		return max(abs(self[i][j]) for i in range(self.height) for j in range(self.width))
	def basic_simplify(self):
		return Matrix(list(set(tuple(rescale(row)) for row in self if nontrivial(row))), self.width)
	def simplify(self):
		R = set(tuple(rescale(row)) for row in self if nontrivial(row))
		R_width = self.width
		A = Id_Matrix(self.width)
		while R_width > 1:
			for R1, R2 in find_antipodal(R, R_width):
				index = find_one(R1)
				sign = R1[index] > 0
				if index != -1:
					if R1[index] == -1: R1 = R2  # Swap to R2 to ensure R1[index] > 0
					R = set([tuple([row[j] - R1[j] * row[index] for j in range(len(row)) if j != index]) for row in R if row != R1])
					R = set([tuple(rescale(row)) for row in R if nontrivial(row)])
					# Update the reconstruction matrix.
					for i in range(A.height):
						for j in range(A.width):
							if j != index: A[i][j] =  A[i][j] - (R1[j] * A[i][index])
					A.discard_column(index)
					R.add(tuple([-R1[i] for i in range(R_width) if i != index]))
					
					R_width -= 1
					break
			else:
				break
		while True:
			for R1, R2 in combinations(R, 2):
				if all(r1 < r2 for r1, r2 in zip(R1, R2)):
					R.remove(R2)
					break
			else:
				break
		R = [row for row in R if not all(r >= 0 for r in row)]
		return Matrix(list(R), R_width), A
	def determinant(self):
		# Uses Bareiss' algorithm to compute the determinant in ~O(n^3).
		assert(self.width == self.height)
		scale = 1
		A = [list(row) for row in self]
		for i in range(self.width-1):
			if A[i][i] == 0:
				for j in range(i+1, self.height):
					if A[j][i] != 0:
						A[i], A[j] = A[j], A[i]
						scale = -scale
						break
				else:
					return 0  # We have a column of all 0's.
			for j in range(i+1, self.width):
				for k in range(i+1, self.width):
					A[j][k] = A[j][k]*A[i][i] - A[j][i]*A[i][k]
					if i: A[j][k] //= A[i-1][i-1]  # Division is exact.
		
		return scale * A[self.width-1][self.width-1]
	
	def find_edge_vector(self):
		''' Returns a non-trivial vector in the polytope or None if none exists. '''
		# !?! This breaks when there is a linear determinancy in the equations.
		
		R, B = self.simplify()  # Reduce to a simpler problem.
		# R, B = self.copy(), Id_Matrix(self.width)
		
		if R.width == 1:
			if nonnegative_image(R, [1]):
				return B * [1]
			else:
				return None
		
		R = Matrix([[1] * R.width], R.width).join(Id_Matrix(R.width)).join(R)
		
		def row_choice_inverse(rc):
			A = Matrix([R.rows[i] for i in rc[1:]], R.width).transpose()
			v = [Matrix([A.rows[j] for j in range(A.height) if j != i], A.width).determinant() for i in range(A.height)]
			A_det = sum(v)
			if A_det > 0 : sign = 1 
			elif A_det < 0: sign = -1
			else: return None  # This is where the problem is!
			return [sign * (-1 if i % 2 else 1) * v[i] for i in range(len(v))]
			
			# A = Matrix([R.rows[i] for i in rc], R.width).transpose()
			# v = [A.substitute_row(i, new_row).determinant() for i in range(A.height)]
			# return [sign * A.substitute_row(i, new_row).determinant() for i in range(A.height)]
		
		def score_image(b):
			return sum(1 if i < 0 else 0 for i in b)
		
		rc = list(range(R.width))
		v = row_choice_inverse(rc)
		b = R*v
		b_score = score_image(b)
		while True:
			if b_score == 0 and b[0] >= 1:
				return B*v
			else:
				r = min([index for index in range(R.height)], key=lambda i: b[i])  # Gets the index of the most negative row.
				row = R.rows[r]
				
				best_row = -1
				best_row_score = b_score + 1
				for i in range(1, R.width):
					rc2 = [rc[j] if j != i else r for j in range(R.width)]
					v2 = row_choice_inverse(rc2)
					if v2 is not None:
						b2 = R * v2
						b2_score = score_image(b2)
						if b2_score < best_row_score or (b2_score == best_row_score and r < i):
							best_row = i
							best_row_score = b2_score
				if best_row != -1:
					rc = [rc[j] if j != best_row else r for j in range(R.width)]
				else:
					return None  # Infeasible.
	
	def find_edge_vector_old(self):
		R, B = self.simplify()  # Reduce to a simpler problem.
		
		if any(all(x < 0 for x in row) for row in R): return
		if R.width == 1: 
			if nonnegative_image(R, [1]):
				return B * [1]
		
		R = R.join(Id_Matrix(R.width))
		
		for rc in combinations(range(R.height), R.width-1):
			A = Matrix([R.rows[i] for i in rc], R.width).transpose()
			v = [(-1 if i % 2 else 1) * Matrix([A.rows[j] for j in range(A.height) if i != j], A.width).determinant() for i in range(A.height)]
			if nontrivial(v):
				if not nonnegative(v): v = [-x for x in v]  # Might need to flip v.
				if nonnegative(v) and nonnegative_image(R, v):
					return B*v
		return
	
	def nontrivial_polytope(self):
		''' Determines if the polytope Ax >= 0, x >= 0 is non-trivial, i.e. not just {0}.'''
		# certificate = self.find_edge_vector()
		certificate = self.find_edge_vector_old()
		if certificate is not None: assert(self.check_nontrivial_polytope(certificate))
		return (certificate is not None), certificate
	def check_nontrivial_polytope(self, certificate):
		return nonnegative(certificate) and nontrivial(certificate) and nonnegative_image(self, certificate)
	def is_aperiodic(self):
		assert(self.width == self.height)
		A = Id_matrix(self.width)
		for i in range(self.width):
			A = A * self
			if all(x > 0 for row in A for x in row):
				return True
		return False
	def contracting(self, action):
		M = self * action
		return all(nonnegative_image(M, v) for v in self.edge_vectors())

#### Some special Matrices we know how to build.

def Id_Matrix(dim):
	return Matrix([[1 if i == j else 0 for j in range(dim)] for i in range(dim)], dim)

def Empty_Matrix(dim):
	return Matrix([], dim)

def Permutation_Matrix(perm):
	dim = len(perm)
	return Matrix([[1 if i == perm[j] else 0 for j in range(dim)] for i in range(dim)], dim)
