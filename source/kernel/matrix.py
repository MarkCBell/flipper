
''' A module for representing and manipulating matrices.

Provides one class: Matrix.

There are also helper functions: id_matrix and zero_matrix. '''

import flipper

import itertools

def nonnegative(v):
	''' Return if the given vector is non-negative. '''
	
	return all(x >= 0 for x in v)

def dot(a, b):
	''' Return the dot product of the two given iterables. '''
	
	# Is it significantly faster to do:
	#c = 0
	#for x, y in zip(a, b):
	#	c += x * y
	#return c
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
		return str(self)
	def __str__(self):
		return '[\n' + ',\n'.join(str(row) for row in self) + '\n]'
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
			return Matrix([[a+b for a, b in zip(r1, r2)] for r1, r2 in zip(self, other)])
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
	
	def __call__(self, other):
		assert(isinstance(other, (list, tuple)))
		assert(self.width == 0 or self.width == len(other))
		return [dot(row, other) for row in self]
	
	def __mul__(self, other):
		if isinstance(other, Matrix):
			assert(self.width == 0 or self.width == len(other))
			other_transpose = other.transpose()
			return Matrix([[dot(a, b) for b in other_transpose] for a in self])
		else:  # Multiply entry wise.
			return Matrix([[entry * other for entry in row] for row in self])
	def __rmul__(self, other):
		return self * other
	def __pow__(self, power):
		assert(self.is_square())
		
		if power == 0:
			return id_matrix(self.width)
		elif power == 1:
			return self
		elif power > 1:
			sqrt = self**(power//2)
			square = sqrt * sqrt
			if power % 2 == 1:
				return self * square
			else:
				return square
		else:  # power < 0.
			raise TypeError('Can only raise matrices to positive powers.')
	
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
		
		This matrix must be square and have determinant +/-1. '''
		
		assert(self.is_square())
		
		P = self.characteristic_polynomial()
		assert(abs(P[0]) == 1)  # Check that the determinant is +/-1.
		# In the next line we should do x // -P[0], but as we know that P[0] == +/-1
		# 1/-P[0] == -P[0] and so we can use a cheaper multiplication.
		return flipper.kernel.Polynomial([x * -P[0] for x in P[1:]])(self)
	
	def transpose(self):
		''' Return the transpose of this matrix. '''
		
		return Matrix(list(zip(*self.rows)))
	def join(self, other):
		''' Return the matrix:
			(self )
			(-----)
			(other)
		This is the same as Sages Matrix.stack() function. '''
		
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
	def characteristic_polynomial(self):
		''' Return the characteristic polynomial of this matrix.
		
		Based off of the Faddeev-Leverrier method. See:
			http://mathfaculty.fullerton.edu/mathews/n2003/FaddeevLeverrierMod.html
		This avoids have to compute an expesive determinant.
		
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
	
	def elementary(self, i, j, k=1):
		''' Return the matrix obtained by performing the elementary move:
			replace row i by row i + k * row j. '''
		
		return Matrix([self[n] if n != i else [x+k*y for x, y in zip(self[i], self[j])] for n in range(self.height)])
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
			for b, a in itertools.product(range(j, zeroing_width), range(i, self.height)):
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
	
	def nonnegative_image(self, v):
		''' Return if self * v >= 0. '''
		
		return all(dot(row, v) >= 0 for row in self)
	
	def simplify(self):
		''' Return a simpler matrix defining the same cone. '''
		
		# Remove nonnegative rows.
		rows = [row for row in self if any(entry < 0 for entry in row)]
		# Remove dupliates.
		rows = list(set(tuple(row) for row in rows))
		# Remove dominated rows.
		rows = [row for row in rows if all(row == row2 or any(x < y for x, y in zip(row, row2)) for row2 in rows)]
		return Matrix(rows)

#################################################
#### Some helper functions for building matrices.

def id_matrix(dim):
	''' Return the identity matrix of given dimension. '''
	
	return Matrix([[1 if i == j else 0 for j in range(dim)] for i in range(dim)])

def zero_matrix(width, height=None):
	''' Return the zero matrix of given dimensions. '''
	
	if height is None: height = width
	return Matrix([[0] * width for _ in range(height)])

