
from math import log10 as log

from Flipper.Kernel.Error import AssumptionError, ComputationError
from Flipper.Kernel.Matrix import nonnegative_image
from Flipper.Kernel.AlgebraicApproximation import algebraic_approximation_from_fraction, log_height_int

_name = 'custom'

HASH_DENOMINATOR = 5

def projective_difference(A, B, error_reciprocal):
	# Returns True iff the projective difference between A and B is less than 1 / error_reciprocal.
	A_sum, B_sum = sum(A), sum(B)
	return max(abs((p * B_sum) - q * A_sum) for p, q in zip(A, B)) * error_reciprocal < A_sum * B_sum 

class EigenvectorEntry:
	def __init__(self, matrix, entry, vector=None):
		self.matrix = matrix
		self.entry = entry
		self.current_accuracy = -1
		
		self.degree = self.matrix.width
		self.log_height = 20  # !?! Deal with this!
		self.accuracy_needed = int(log(self.degree)) + int(self.log_height) + 2
		
		# Let M' := M - \lambda I. Then there is an invertible matrix P such that T := P^{-1} M' P is upper triangular
		# and its last column is all zeros.
		# Then e_n \in \ker(T) and P e_n \in \ker(M').
		# 
		
		
		if vector is None: vector = [1] * self.matrix.width
		self.old_vector = vector
		self.vector = self.matrix * self.old_vector
		
		self.algebraic_approximation = None
		self.increase_accuracy()
	
	def increase_accuracy(self, accuracy=None):
		if accuracy is None: accuracy = self.accuracy_needed
		if self.current_accuracy < accuracy:
			while not projective_difference(self.old_vector, self.vector, 10**accuracy):
				self.old_vector, self.vector = self.vector, self.matrix * self.vector
			
			self.current_accuracy = accuracy
			self.algebraic_approximation = algebraic_approximation_from_fraction(self.vector[self.entry], sum(self.vector), self.current_accuracy, self.degree, self.log_height)
	
	def __add__(self, other):
		if isinstance(other, EigenvectorEntry):
			return self.algebraic_approximation + other.algebraic_approximation
		else:
			return self.algebraic_approximation + other
	def __radd__(self, other):
		return self + other
	
	def __sub__(self, other):
		if isinstance(other, EigenvectorEntry):
			return self.algebraic_approximation - other.algebraic_approximation
		else:
			return self.algebraic_approximation - other
	
	def __rsub__(self, other):
		return -(self - other)
	
	def __mul__(self, other):
		if isinstance(other, EigenvectorEntry):
			return self.algebraic_approximation * other.algebraic_approximation
		else:
			return self.algebraic_approximation * other
	def __rmul__(self, other):
		return self * other
	
	def __lt__(self, other):
		if isinstance(other, EigenvectorEntry):
			return self.algebraic_approximation < other.algebraic_approximation
		else:
			return self.algebraic_approximation < other
	def __eq__(self, other):
		if isinstance(other, EigenvectorEntry):
			return self.algebraic_approximation == other.algebraic_approximation
		else:
			return self.algebraic_approximation == other
	def __gt__(self, other):
		if isinstance(other, EigenvectorEntry):
			return self.algebraic_approximation > other.algebraic_approximation
		else:
			return self.algebraic_approximation > other

algebraic_type = EigenvectorEntry

def simplify_algebraic_type(number):
	return number

def string_algebraic_type(number):
	return number.algebraic_approximation.interval.approximate_string(4)

def hash_algebraic_type(number):
	return number.interval.change_denominator(HASH_DENOMINATOR).tuple()

def degree_algebraic_type(number):
	return number.degree

def log_height_algebraic_type(number):
	return number.log_height

def approximate_algebraic_type(number, accuracy, degree=None):
	number.increase_accuracy(accuracy)
	return number.algebraic_approximation


def Perron_Frobenius_eigen(matrix, vector=None, condition_matrix=None):
	# Assumes that matrix is Perron-Frobenius and so has a unique real eigenvalue of largest
	# magnitude. If not an AssumptionError is thrown.
	
	eigenvector, eigenvalue = [EigenvectorEntry(matrix, i, vector=vector) for i in range(matrix.width)], 1  # !?! Shouldn't be 1
	
	if condition_matrix is not None:
		# Make sure that we have enough accuracy ...
		new_accuracy_needed = sum(entry.accuracy_needed for entry in eigenvector) + matrix.width * (int(log_height_int(matrix.bound())) + 2)
		for entry in eigenvector:
			entry.increase_accuracy(new_accuracy_needed)
		
		# ... so that this computation cannot fail.
		if not nonnegative_image(condition_matrix, eigenvector):
			raise ComputationError('Could not estimate invariant lamination.')
	
	return eigenvector, eigenvalue
