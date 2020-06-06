
''' A module for representing and manipulating matrices.

Provides one class: Matrix.

There are also helper functions: id_matrix and zero_matrix. '''

import numpy as np
import realalg

import flipper

def nonnegative(v):
    ''' Return if the given vector is non-negative. '''
    
    return all(x >= 0 for x in v)

def dot(a, b):
    ''' Return the dot product of the two given iterables. '''
    
    # Is it significantly faster to do:
    # c = 0
    # for x, y in zip(a, b):
    #     c += x * y
    # return c
    return sum(x * y for x, y in zip(a, b))

class Matrix(object):
    ''' This represents a matrix. '''
    def __init__(self, data):
        assert isinstance(data, (list, tuple))
        assert all(isinstance(row, (list, tuple)) for row in data)
        
        self.rows = [list(row) for row in data]
        self.height = len(self.rows)
        self.width = len(self.rows[0]) if self.height > 0 else 0
        assert all(len(row) == self.width for row in self)
    def copy(self):
        ''' Return a copy of this Matrix. '''
        return Matrix([list(row) for row in self])
    def __getitem__(self, index):
        return self.rows[index]
    def __repr__(self):
        return str(self)
    def __str__(self):
        return '[\n' + ',\n'.join('[' + ', '.join(str(entry) for entry in row) + ']' for row in self) + '\n]'
        # Suggestion: Make Matrices easier to read by omitting zeros.
        # return '[\n' + ',\n'.join('[' + ', '.join(str(entry) if entry != 0 else ' ' for entry in row) + ']' for row in self) + '\n]'
    def __hash__(self):
        return hash(tuple([self.width, self.height] + [tuple(row) for row in self]))
    def __len__(self):
        return self.height
    def __iter__(self):
        return iter(self.rows)
    def __eq__(self, other):
        return self.width == other.width and self.height == other.height and all(row1 == row2 for row1, row2 in zip(self.rows, other.rows))
    def __ne__(self, other):
        return not self == other
    
    def __neg__(self):
        return Matrix([[-x for x in row] for row in self])
    def __add__(self, other):
        if isinstance(other, Matrix):
            assert self.width == other.width and self.height == other.height
            return Matrix([[a+b for a, b in zip(r1, r2)] for r1, r2 in zip(self, other)])
        else:
            return self + (id_matrix(self.width) * other)
    def __radd__(self, other):
        return self + other
    def __sub__(self, other):
        if isinstance(other, Matrix):
            assert self.width == other.width and self.height == other.height
            return Matrix([[self[i][j] - other[i][j] for j in range(self.width)] for i in range(self.height)])
        else:
            return self - (id_matrix(self.width) * other)
    def __rsub__(self, other):
        return -(self - other)
    
    def __call__(self, other):
        assert isinstance(other, (list, tuple))
        assert self.width == 0 or self.width == len(other)
        return [dot(row, other) for row in self]
    
    def __mul__(self, other):
        if isinstance(other, Matrix):
            assert self.width == 0 or self.width == len(other)
            other_transpose = other.transpose()
            return Matrix([[dot(a, b) for b in other_transpose] for a in self])
        else:  # Multiply entry wise.
            return Matrix([[entry * other for entry in row] for row in self])
    def __rmul__(self, other):
        return self * other
    def __pow__(self, power):
        assert self.is_square()
        
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
            raise ValueError('Can only raise matrices to non-negative powers.')
    
    def is_square(self):
        ''' Return if this matrix is square. '''
        
        return self.width == self.height
    
    def flatten(self):
        ''' Return the entries of this matrix as a single flattened list. '''
        return [entry for row in self for entry in row]
    def transpose(self):
        ''' Return the transpose of this matrix. '''
        
        return Matrix(list(zip(*self.rows)))
    def join(self, other):
        ''' Return the matrix::
        
            (self )
            (-----)
            (other)
        
        This is the same as Sages Matrix.stack() function. '''
        
        return Matrix(self.rows + other.rows)
    def tweak(self, increment, decrement):
        ''' Return a copy of this matrix where each increment entry has been increased by 1 and each decrement entry has been decreased by 1. '''
        
        rows = [list(row) for row in self]
        for (i, j) in increment:
            rows[i][j] += 1
        for (i, j) in decrement:
            rows[i][j] -= 1
        return Matrix(rows)
    
    def elementary(self, i, j, k=1):
        ''' Return the matrix obtained by performing the elementary move:
            replace row i by row i + k * row j. '''
        
        return Matrix([self[n] if n != i else [x+k*y for x, y in zip(self[i], self[j])] for n in range(self.height)])
    
    def nonnegative_image(self, v):
        ''' Return if self * v >= 0. '''
        
        return all(dot(row, v) >= 0 for row in self)
    
    def directed_eigenvector(self, condition_matrix):
        ''' Return an `interesting` (eigenvalue, eigenvector) pair  which lives inside of the cone C, defined by condition_matrix.
        
        See realalg for the definition of `interesting`.
        
        Raises a ComputationError if it cannot find an interesting vectors in C.
        Assumes that C contains at most one interesting eigenvector. '''
        
        M = np.array(self.rows, dtype=object)
        for eigenvalue, eigenvector in realalg.eigenvectors(M):
            if condition_matrix.nonnegative_image(eigenvector):
                return eigenvalue, eigenvector
        
        raise flipper.ComputationError('No interesting eigenvalues in cell.')


##############################################
# Some helper functions for building matrices.

def id_matrix(dim):
    ''' Return the identity matrix of given dimension. '''
    
    return Matrix([[1 if i == j else 0 for j in range(dim)] for i in range(dim)])

def zero_matrix(width, height=None):
    ''' Return the zero matrix of given dimensions. '''
    
    if height is None: height = width
    return Matrix([[0] * width for _ in range(height)])

