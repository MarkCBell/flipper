
from itertools import combinations, groupby, product
from fractions import gcd
from functools import reduce
from time import time

import Flipper

# !?! This is not pure.
def tweak_vector(v, add, subtract):
	for i in add:
		v[i] += 1
	for i in subtract:
		v[i] -= 1
	return v

def tweak_matrix(M, one, minus_one):
	return Matrix([[1 if (i, j) in one else -1 if (i, j) in minus_one else M[i][j] for j in range(M.width)] for i in range(M.height)])

def antipodal(v, w):
	# Returns if v & w are antipodal vectors.
	return all([v[i] == -w[i] for i in range(len(v))])

def find_antipodal(R):
	abs_row = lambda x: [abs(i) for i in x]
	for _, g in groupby(sorted(R, key=abs_row), key=abs_row):
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
	c = max(abs(reduce(gcd, v)), 1)  # Avoid a possible division by 0.
	return [x // c for x in v]

def nonnegative(v):
	return all(x >= 0 for x in v)

def nontrivial(v):
	return any(v)

def dot(a, b):
	return sum(a[i] * b[i] for i in range(len(a)))

class Matrix(object):
	def __init__(self, data):
		self.rows = [list(row) for row in data]
		self.height = len(self.rows)
		self.width = len(self.rows[0]) if self.height > 0 else 0
		assert(all(len(row) == self.width for row in self))
	def copy(self):
		return Matrix(self.rows)
	def __getitem__(self, index):
		return self.rows[index]
	def __repr__(self):
		return '[\n' + ',\n'.join(str(row) for row in self) + '\n]'
	def __float__(self):
		return Matrix([[float(x) for x in row] for row in self])
	def is_empty(self):
		return self.width == 0
	
	def __add__(self, other):
		if isinstance(other, Matrix):
			assert(self.width == other.width and self.height == other.height)
			return Matrix([[self[i][j] + other[i][j] for j in range(self.width)] for i in range(self.height)])
		else:
			return self + (Id_Matrix(self.width) * other)
	def __radd__(self, other):
		return self + other
	def __neg__(self):
		return Matrix([[-x for x in row] for row in self])
	def __sub__(self, other):
		if isinstance(other, Matrix):
			assert(self.width == other.width and self.height == other.height)
			return Matrix([[self[i][j] - other[i][j] for j in range(self.width)] for i in range(self.height)])
		else:
			return self - (Id_Matrix(self.width) * other)
	def __rsub__(self, other):
		return -(self - other)
	
	def __mul__(self, other):
		if isinstance(other, Matrix):
			assert(self.width == 0 or self.width == len(other))
			otherT = other.transpose()
			return Matrix([[dot(a, b) for b in otherT] for a in self])
		elif isinstance(other, list):  # other is a vector.
			assert(self.width == 0 or self.width == len(other))
			return [dot(row, other) for row in self]
		else:  # Multiply entry wise.
			return Matrix([[entry * other for entry in row] for row in self])
	def __rmul__(self, other):
		return self * other
	def __pow__(self, power):
		assert(self.width == self.height)
		if power == 0:
			return Id_Matrix(self.width)
		if power > 0:
			sqrt = self**(power//2)
			square = sqrt * sqrt
			if power % 2 == 1:
				return self * square
			else:
				return square
	def powers(self, max_power):
		assert(self.width == self.height)
		Ms = [Id_Matrix(self.width)]
		for _ in range(max_power):
			Ms.append(self * Ms[-1])
		return Ms
	def __len__(self):
		return self.height
	def __iter__(self):
		return iter(self.rows)
	def __eq__(self, other):
		return self.width == other.width and self.height == other.height and all(row1 == row2 for row1, row2 in zip(self.rows, other.rows))
	def inverse(self):
		# See self.char_poly().
		assert(self.width == self.height)
		A = self.copy()
		for i in range(1, self.width-1):
			A = self * (A - (A.trace() // i))
		return A - (A.trace() // (self.width-1)) 
	def transpose(self):
		return Matrix(list(zip(*self.rows)))
	def join(self, other):
		return Matrix(self.rows + other.rows)
	
	def trace(self):
		return sum(self[i][i] for i in range(self.width))
	def determinant(self):
		# Uses Bareiss' algorithm to compute the determinant in ~O(n^3).
		# See: http://cs.nyu.edu/exact/core/download/core_v1.4/core_v1.4/progs/bareiss/bareiss.cpp
		# We could also just get the constant term of the characteristic polynomial,
		# that is do:
		#	return self.char_poly()[0]
		# but this is ~10x faster.
		assert(self.width == self.height)
		scale = 1
		A = [list(row) for row in self]
		for i in range(self.width-1):
			if not A[i][i]:  # == 0.
				for j in range(i+1, self.height):
					if A[j][i]:  # != 0.
						A[i], A[j] = A[j], A[i]
						scale = -scale
						break
				else:
					return 0  # We have a column of all 0's.
			for j in range(i+1, self.width):
				for k in range(i+1, self.width):
					A[j][k] = A[j][k]*A[i][i] - A[j][i]*A[i][k]
					if i: A[j][k] = A[j][k] // A[i-1][i-1]  # Division is exact.
		
		return scale * A[self.width-1][self.width-1]
	def char_poly(self):
		# Based off of the Faddeev-Leverrier method. See: http://mathfaculty.fullerton.edu/mathews/n2003/FaddeevLeverrierMod.html
		assert(self.width == self.height)
		# We will actually compute det(\lambdaI - self). Then at the
		# end we correct this by multiplying by the required +/-1.
		A = self.copy()
		p = [1] * (self.width+1)
		for i in range(1, self.width+1):
			p[i] = -A.trace() // i
			# If we were smarter we would skip this on the final iteration.
			A = self * (A + Id_Matrix(self.width) * p[i])
		# Actually now A / pi == A^{-1}. 
		sign = +1 if self.width % 2 == 0 else -1
		return Flipper.kernel.Polynomial(p[::-1]) * sign
	
	def row_reduce(self, zeroing_width=None):
		# Returns this matrix after applying elementary row operations
		# so that in each row each non-zero entry either:
		#	1) has a non-zero entry to the left of it,
		#	2) has no non-zero entries below it, or
		#	3) is in a column > zeroing_width.
		if zeroing_width is None: zeroing_width = self.width
		i, j = 0, 0
		A = [list(row) for row in self]
		while j <= zeroing_width:
			for b, a in product(range(i, zeroing_width), range(j, self.height)):
				if A[a][b] != 0:
					A[i], A[a] = A[a], A[i]
					j = b
					break
			else:
				break
			
			rlead = A[i][j]
			for k in range(i+1, self.height):
				r2lead = A[k][j]
				if r2lead != 0:
					A[k] = [A[k][x] * rlead - A[i][x] * r2lead for x in range(self.width)]
			
			i += 1
			j += 1
		return Matrix(A)
	def kernel(self):
		A = self.join(Id_Matrix(self.width))
		B = A.transpose()
		C = B.row_reduce(zeroing_width=self.height)
		return Matrix([row[self.height:] for row in C if any(row) and not any(row[:self.height])])
	
	def solve(self, target):
		# Returns an x such that self*x == target*k for some k \in ZZ. 
		assert(self.width == self.height)
		A = self.transpose()
		d = A.determinant()
		sign = +1 if d > 0 else -1
		sol = [sign * A.substitute_row(i, target).determinant() for i in range(A.height)]
		return rescale(sol)
	def nonnegative_image(self, v):
		return all(dot(row, v) >= 0 for row in self)
	def substitute_row(self, index, new_row):
		return Matrix([(row if i != index else new_row) for i, row in enumerate(self.rows)])
	def discard_column(self, column):
		self.rows = [[row[i] for i in range(self.width) if i != column] for row in self]
		self.width -= 1
	def basic_simplify(self):
		return Matrix(list(set(tuple(rescale(row)) for row in self if nontrivial(row))))
	def simplify(self):
		R = set(tuple(rescale(row)) for row in self if nontrivial(row))
		R_width = self.width
		A = Id_Matrix(self.width)
		while R_width > 1:
			for R1, R2 in find_antipodal(R):
				index = find_one(R1)
				if index != -1:
					if R1[index] == -1: R1 = R2  # Swap to R2 to ensure R1[index] > 0
					R = set([tuple([row[j] - R1[j] * row[index] for j in range(len(row)) if j != index]) for row in R if row != R1])
					R = set([tuple(rescale(row)) for row in R if nontrivial(row)])
					# Update the reconstruction matrix.
					for i in range(A.height):
						for j in range(A.width):
							if j != index: A[i][j] = A[i][j] - (R1[j] * A[i][index])
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
		return Matrix(R), A
	
	def find_edge_vector(self):
		''' Returns a non-trivial vector in the polytope given by self*x >= 0 or None if none exists. 
		Note: if self is empty then considers self as a map from RR^0 --> RR^0 and so returns None. '''
		
		if self.is_empty():
			return None
		
		R, B = self.simplify()  # Reduce to a simpler problem.
		
		if R.width == 0:
			return B * ([1]*B.width)
		elif R.width == 1: 
			if R.nonnegative_image([1]):
				return B * [1]
		elif R.width > 1:
			if any(all(x < 0 for x in row) for row in R): return
			R = R.join(Id_Matrix(R.width))
			
			for rc in combinations(range(R.height), R.width-1):
				# Should use A.solve() here.
				A = Matrix([R.rows[i] for i in rc]).transpose()
				v = [(-1 if i % 2 else 1) * Matrix([A.rows[j] for j in range(A.height) if i != j]).determinant() for i in range(A.height)]
				if nontrivial(v):
					if not nonnegative(v): v = [-x for x in v]  # Might need to flip v.
					if nonnegative(v) and R.nonnegative_image(v):
						return B*v
		
		# Polytope is trivial.
		return None
	def check_nontrivial_polytope(self, certificate):
		return nonnegative(certificate) and nontrivial(certificate) and self.nonnegative_image(certificate)
	
	def nontrivial_polytope(self):
		''' Determines if the polytope given by self*x >= 0, x >= 0 is non-trivial, i.e. not just {0}. '''
		# We need to handle the empty case separately.
		if self.is_empty():
			return True
		
		certificate = self.find_edge_vector()
		if certificate is not None: assert(self.check_nontrivial_polytope(certificate))
		return (certificate is not None)

#### Some special Matrices we know how to build.

def Id_Matrix(dim):
	return Matrix([[1 if i == j else 0 for j in range(dim)] for i in range(dim)])

def Zero_Matrix(width, height=None):
	if height is None: height = width
	return Matrix([[0] * width for _ in range(height)])

def Empty_Matrix():
	return Matrix([])

