
''' A module for representing and manipulating matrices.

Provides one class: Matrix.

There are also helper functions: id_matrix, zero_matrix and empty_matrix. '''

import flipper

from itertools import combinations, groupby, product
from fractions import gcd
from functools import reduce as freduce

def antipodal(v, w):
	''' Return if v and w are antipodal vectors, that is, if v == -w. '''
	
	return all([v[i] == -w[i] for i in range(len(v))])

def find_antipodal(R):
	''' Yields the pairs of antipodal vectors in R. '''
	
	abs_row = lambda x: [abs(i) for i in x]
	for _, g in groupby(sorted(R, key=abs_row), key=abs_row):
		for R1, R2 in combinations(g, 2):
			if antipodal(R1, R2):
				yield (R1, R2)
	
	return

def find_one(v):
	''' Return the index of a +/-1 entry of v or -1 if there isn't one. '''
	
	for i in range(len(v)):
		if abs(v[i]) == 1:
			return i
	return -1

def rescale(v):
	''' Return the given vector rescaled by 1 / gcd(vector). '''
	
	c = max(abs(freduce(gcd, v)), 1)  # Avoid a possible division by 0.
	return [x // c for x in v]

def nonnegative(v):
	''' Return if the given vector is non-negative. '''
	
	return all(x >= 0 for x in v)

def nontrivial(v):
	''' Return if the given vector is non-trivial. '''
	
	return any(v)

def dot(a, b):
	''' Return the dot product of the two given vectors. '''
	
	return sum(x * y for x, y in zip(a, b))

class Matrix(object):
	''' This represents a matrix. '''
	def __init__(self, data):
		assert(isinstance(data, (list, tuple)))
		assert(all(isinstance(row, (list, tuple)) for row in data))
		
		self.rows = [list(row) for row in data]
		self.height = len(self.rows)
		self.width = len(self.rows[0]) if self.height > 0 else 0
		assert(all(len(row) == self.width for row in self))
	def copy(self):
		''' Return a copy of this matrix. '''
		
		return Matrix(self.rows)
	def __getitem__(self, index):
		return self.rows[index]
	def __repr__(self):
		return '[\n' + ',\n'.join(str(row) for row in self) + '\n]'
	def __float__(self):
		return Matrix([[float(x) for x in row] for row in self])
	def is_empty(self):
		''' Return if this matrix is empty. '''
		
		return self.width == 0
	def __len__(self):
		return self.height
	def __iter__(self):
		return iter(self.rows)
	def __eq__(self, other):
		return self.width == other.width and self.height == other.height and all(row1 == row2 for row1, row2 in zip(self.rows, other.rows))
	def __ne__(self, other):
		return not (self == other)
	
	def __neg__(self):
		return Matrix([[-x for x in row] for row in self])
	def __add__(self, other):
		if isinstance(other, Matrix):
			assert(self.width == other.width and self.height == other.height)
			return Matrix([[self[i][j] + other[i][j] for j in range(self.width)] for i in range(self.height)])
		else:
			return self + (id_matrix(self.width) * other)
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, Matrix):
			assert(self.width == other.width and self.height == other.height)
			return Matrix([[self[i][j] - other[i][j] for j in range(self.width)] for i in range(self.height)])
		else:
			return self - (id_matrix(self.width) * other)
	def __rsub__(self, other):
		return -(self - other)
	
	def __mul__(self, other):
		if isinstance(other, Matrix):
			assert(self.width == 0 or self.width == len(other))
			other_transpose = other.transpose()
			return Matrix([[dot(a, b) for b in other_transpose] for a in self])
		elif isinstance(other, list):  # other is a vector.
			assert(self.width == 0 or self.width == len(other))
			return [dot(row, other) for row in self]
		else:  # Multiply entry wise.
			return Matrix([[entry * other for entry in row] for row in self])
	def __rmul__(self, other):
		return self * other
	def __pow__(self, power):
		assert(self.is_square())
		
		if power == 0:
			return id_matrix(self.width)
		if power > 0:
			sqrt = self**(power//2)
			square = sqrt * sqrt
			if power % 2 == 1:
				return self * square
			else:
				return square
	
	def is_square(self):
		''' Return if this matrix is square. '''
		
		return self.width == self.height
	
	def powers(self, max_power):
		''' Return the list [self**0, ..., self**max_power].
		
		This matrix must be square. '''
		
		assert(self.is_square())
		
		Ms = [id_matrix(self.width)]
		for _ in range(max_power):
			Ms.append(self * Ms[-1])
		return Ms
	def inverse(self):
		''' Return the inverse of this matrix.
		
		This matrix must be square. '''
		
		# For why this works see self.char_poly().
		
		assert(self.is_square())
		
		A = self.copy()
		for i in range(1, self.width-1):
			A = self * (A - (A.trace() // i))
		return A - (A.trace() // (self.width-1))
	def transpose(self):
		''' Return the transpose of this matrix. '''
		
		return Matrix(list(zip(*self.rows)))
	def join(self, other):
		''' Return the matrix:
			(self )
			(-----)
			(other)
		This is the same as sages Matrix.stack() function. '''
		
		return Matrix(self.rows + other.rows)
	def tweak(self, increment, decrement):
		''' Return a copy of this matrix where each increment entry has been increased by 1 and each decrement entry has been decreased by 1. '''
		
		A = self.copy()
		for (i, j) in increment:
			A[i][j] += 1
		for (i, j) in decrement:
			A[i][j] -= 1
		return A
	
	def trace(self):
		''' Return the trace of this matrix. '''
		
		return sum(self[i][i] for i in range(self.width))
	def determinant(self):
		''' Return the determinant of this matrix.
		
		Uses Bareiss' algorithm to compute the determinant in ~O(n^3). See:
			http://cs.nyu.edu/exact/core/download/core_v1.4/core_v1.4/progs/bareiss/bareiss.cpp
		
		This matrix must be square. '''
		
		# We could also just get the constant term of the characteristic polynomial, but this is ~10x faster.
		
		assert(self.is_square())
		
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
		''' Return the characteristic polynomial of this matrix.
		
		Based off of the Faddeev-Leverrier method. See:
			http://mathfaculty.fullerton.edu/mathews/n2003/FaddeevLeverrierMod.html
		
		This matrix must be square. '''
		
		assert(self.is_square())
		
		# We will actually compute det(\lambdaI - self). Then at the
		# end we correct this by multiplying by the required +/-1.
		A = self.copy()
		p = [1] * (self.width+1)
		for i in range(1, self.width+1):
			p[i] = -A.trace() // i
			# If we were smarter we would skip this on the final iteration.
			A = self * (A + p[i])
		# Actually now A / p[i] == A^{-1}.
		sign = +1 if self.width % 2 == 0 else -1
		return flipper.kernel.Polynomial(p[::-1]) * sign
	
	def row_reduce(self, zeroing_width=None):
		''' Return this matrix after applying elementary row operations
		so that in each row each non-zero entry either:
			1) has a non-zero entry to the left of it,
			2) has no non-zero entries below it, or
			3) is in a column > zeroing_width.
		if zeroing_width is None: zeroing_width = self.width. '''
		
		i, j = 0, 0
		A = [list(row) for row in self]
		while j < zeroing_width:
			for b, a in product(range(j, zeroing_width), range(i, self.height)):
				if A[a][b] != 0:
					A[i], A[a] = A[a], A[i]
					j = b
					break
			else:
				break
			
			rlead = A[i][j]
			for k in range(self.height):
				if k != i:
					r2lead = A[k][j]
					if r2lead != 0:
						for x in range(j, self.width):
							A[k][x] = (A[k][x] * rlead) - (A[i][x] * r2lead)
			
			i += 1
			j += 1
		return Matrix(A)
	def kernel(self):
		''' Return a matrix whose rows are a basis for the kernel of this matrix. '''
		
		A = self.join(id_matrix(self.width))
		B = A.transpose()
		C = B.row_reduce(zeroing_width=self.height)
		return Matrix([row[self.height:] for row in C if any(row) and not any(row[:self.height])])
	
	def substitute_row(self, index, new_row):
		''' Return a matrix in which the row with given index has been replaced by the given vector. '''
		
		return Matrix([(row if i != index else new_row) for i, row in enumerate(self.rows)])
	def solve(self, target):
		''' Return an x such that self * x == target * k for some k in ZZ.
		
		This matrix must be square. '''
		
		assert(self.is_square())
		
		A = self.transpose()
		d = A.determinant()
		sign = +1 if d > 0 else -1
		# return [Fraction(A.substitute_row(i, target).determinant(), d) for i in range(A.height)]
		sol = [sign * A.substitute_row(i, target).determinant() for i in range(A.height)]
		return rescale(sol)
	
	def nonnegative_image(self, v):
		''' Return if self * v >= 0. '''
		
		return all(dot(row, v) >= 0 for row in self)
	
	# Methods for making Ax >= 0 into a simpler problem.
	def discard_column(self, column):
		''' Return the matrix obtained by discarding the given column. '''
		
		return Matrix([[row[i] for i in range(self.width) if i != column] for row in self])
	def basic_simplify(self):
		''' Return a copy of this matrix with duplicated and dominated rows removed. '''
		
		# Rescale rows and remove duplicates and rows that are all non-negative (these are always satisfied).
		rows = list(set(tuple(rescale(row)) for row in self if not all(r >= 0 for r in row)))
		# Remove any dominated rows.
		undominated_indices = [i for i in range(len(rows)) if not any(all(y <= x for x, y in zip(rows[i], rows[j])) for j in range(len(rows)) if i != j)]
		rows = [rows[i] for i in undominated_indices]
		return Matrix(rows)
	def simplify(self):
		''' Return a matrix where determined variables in self * v >= 0 have been eliminated. '''
		
		# Remove all trivial rows.
		R = set(tuple(rescale(row)) for row in self if nontrivial(row))
		R_width = self.width
		A = id_matrix(self.width)
		# We repeatedly search for a pair of antipodal rows in self and use them to eliminate
		# one variable. This frequently occurs in the reducibility problem.
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
					A = A.discard_column(index)
					R.add(tuple([-R1[i] for i in range(R_width) if i != index]))
					
					R_width -= 1
					break
			else:
				break
		
		# Remove any dominated rows.
		return Matrix(list(R)).basic_simplify(), A
	def fourier_motzkin_eliminate(self, index=0):
		''' Return the matrix obtained by using Fourier--Motzkin elimination on this matrix.
		
		Repeated use can result in doubly exponential complexity. See:
			http://en.wikipedia.org/wiki/Fourier%E2%80%93Motzkin_elimination
		for more information. '''
		
		pos_rows = [row for row in self if row[index] > 0]
		neg_rows = [row for row in self if row[index] < 0]
		non_rows = [row for row in self if row[index] == 0]
		if len(neg_rows) == 0:  # Problem is trivially solvable by (0 ... 0 1 0 ... 0)
			return Matrix([[1]])
		elif len(pos_rows) == 0:
			return self.discard_column(index)  # Problem is independent of x_index.
		else:
			new_rows = [[r1[index] * y - r2[index] * x for x, y in zip(r1, r2)] for r1, r2 in product(pos_rows, neg_rows)]
			return Matrix(new_rows + non_rows + neg_rows).discard_column(index)
	
	def nontrivial_polytope2(self):
		''' Return if the polytope given by self*x >= 0, x >= 0 is non-trivial.
		
		Uses self.fourier_motzkin_eliminate() repeatedly and so may take doubly exponential time.
		
		Note: As with self.find_edge_vector() we consider the empty matrix
		as a map RR^0 --> RR^0 and so return False. '''
		
		A = self.copy()
		A = A.basic_simplify()
		while A.height > 1:
			A = A.fourier_motzkin_eliminate()
			A = A.basic_simplify()
		return any(x >= 0 for x in A[0])
	
	def find_edge_vector(self):
		''' Return a non-trivial vector in the polytope given by self * x >= 0 or None if none exists.
		
		Note: if self is empty then considers self as a map from RR^0 --> RR^0 and so returns None. '''
		
		# !?! To do: Redo this using the simplex method / ellipsoid method and pre-solving.
		
		if self.is_empty():
			return None
		
		R, B = self.simplify()  # Reduce to a simpler problem.
		
		if R.width == 0:
			return B * ([1] * B.width)
		elif R.width == 1:
			if R.nonnegative_image([1]):
				return B * [1]
		elif R.width > 1:
			if not any(all(x < 0 for x in row) for row in R):
				R = R.join(id_matrix(R.width))
				
				for rc in combinations(range(R.height), R.width-1):
					A = Matrix([[1] * R.width] + [R[i] for i in rc])
					v = A.solve([1] + [0]*(R.width-1))
					if nontrivial(v):
						if not nonnegative(v): v = [-x for x in v]  # Might need to flip v.
						if nonnegative(v) and R.nonnegative_image(v):
							return B * v
		
		# Polytope is trivial.
		return None
	
	def nontrivial_polytope(self):
		''' Return if the polytope given by self*x >= 0, x >= 0 is non-trivial.
		
		Uses self.find_edge_vector().
		
		Note: As with self.find_edge_vector() we consider the empty matrix
		as a map RR^0 --> RR^0 and so return False. '''
		
		return self.find_edge_vector() is not None

#### Some special Matrices we know how to build.

def id_matrix(dim):
	''' Return the identity matrix of given dimension. '''
	
	return Matrix([[1 if i == j else 0 for j in range(dim)] for i in range(dim)])

def zero_matrix(width, height=None):
	''' Return the zero matrix of given dimensions. '''
	
	if height is None: height = width
	return Matrix([[0] * width for _ in range(height)])

def empty_matrix():
	''' Return the empty matrix. '''
	
	return Matrix([])

