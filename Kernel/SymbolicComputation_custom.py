
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

# This class represents the leading eigenvector of a matrix.
class Eigenvector:
	def __init__(self, matrix, vector=None):
		self.matrix = matrix  # 
		self.power_matrix = self.matrix
		self.current_accuracy = -1
		
		self.degree = self.matrix.width
		self.log_height = 100  # !?! Deal with this!
		self.accuracy_needed = int(log(self.degree)) + int(self.log_height) + 2
		
		if vector is None: vector = [1] * self.matrix.width
		self.old_vector = vector
		self.vector = self.matrix * self.old_vector
		
		self.algebraic_approximation = [None] * self.matrix.width
		self.eigenvalue = None
		self.increase_accuracy()
	
	# @profile
	def increase_accuracy(self, accuracy=None):
		if accuracy is None: accuracy = self.accuracy_needed
		
		if self.current_accuracy < accuracy:
			while not projective_difference(self.old_vector, self.vector, 10**accuracy):
				self.old_vector, self.vector = self.vector, self.power_matrix * self.vector
				self.power_matrix = self.power_matrix * self.power_matrix  # Now square the power matrix so we converge faster.
			
			self.current_accuracy = accuracy
			self.algebraic_approximations = [algebraic_approximation_from_fraction(entry, sum(self.vector), self.current_accuracy, self.degree, self.log_height) for entry in self.vector]
			self.eigenvalue = algebraic_approximation_from_fraction(sum(self.matrix * self.vector), sum(self.vector), self.current_accuracy, self.degree, self.log_height)

class EigenvectorEntry:
	def __init__(self, eigenvector, entry, vector=None):
		self.eigenvector = eigenvector
		self.entry = entry
	
	# @profile
	def increase_accuracy(self, accuracy=None):
		self.eigenvector.increase_accuracy(accuracy)
	
	def __add__(self, other):
		if isinstance(other, EigenvectorEntry):
			return self.eigenvector.algebraic_approximations[self.entry] + other.eigenvector.algebraic_approximations[other.entry]
		else:
			return self.eigenvector.algebraic_approximations[self.entry] + other
	def __radd__(self, other):
		return self + other
	
	def __sub__(self, other):
		if isinstance(other, EigenvectorEntry):
			return self.eigenvector.algebraic_approximations[self.entry] - other.eigenvector.algebraic_approximations[other.entry]
		else:
			return self.eigenvector.algebraic_approximations[self.entry] - other
	
	def __rsub__(self, other):
		return -(self - other)
	
	def __mul__(self, other):
		if isinstance(other, EigenvectorEntry):
			return self.eigenvector.algebraic_approximations[self.entry] * other.eigenvector.algebraic_approximations[other.entry]
		else:
			return self.eigenvector.algebraic_approximations[self.entry] * other
	def __rmul__(self, other):
		return self * other
	
	def __lt__(self, other):
		if isinstance(other, EigenvectorEntry):
			return self.eigenvector.algebraic_approximations[self.entry] < other.eigenvector.algebraic_approximations[other.entry]
		else:
			return self.eigenvector.algebraic_approximations[self.entry] < other
	def __eq__(self, other):
		if isinstance(other, EigenvectorEntry):
			return self.eigenvector.algebraic_approximations[self.entry] == other.eigenvector.algebraic_approximations[other.entry]
		else:
			return self.eigenvector.algebraic_approximations[self.entry] == other
	def __gt__(self, other):
		if isinstance(other, EigenvectorEntry):
			return self.eigenvector.algebraic_approximations[self.entry] > other.eigenvector.algebraic_approximations[other.entry]
		else:
			return self.eigenvector.algebraic_approximations[self.entry] > other

algebraic_type = EigenvectorEntry

def simplify_algebraic_type(number):
	return number

def string_algebraic_type(number):
	return number.eigenvector.algebraic_approximations[number.entry].interval.approximate_string(accuracy=4)

def hash_algebraic_type(number):
	return number.eigenvector.algebraic_approximations[number.entry].interval.change_denominator(HASH_DENOMINATOR).tuple()

def degree_algebraic_type(number):
	return number.eigenvector.degree

def log_height_algebraic_type(number):
	return number.eigenvector.log_height

def approximate_algebraic_type(number, accuracy, degree=None):
	number.increase_accuracy(accuracy)
	return number.eigenvector.algebraic_approximations[number.entry]


def Perron_Frobenius_eigen(matrix, vector=None, condition_matrix=None):
	# Assumes that matrix is Perron-Frobenius and so has a unique real eigenvalue of largest
	# magnitude. If not an AssumptionError is thrown.
	
	EV = Eigenvector(matrix, vector=vector)
	
	eigenvector, eigenvalue = [EigenvectorEntry(EV, i) for i in range(matrix.width)], EV.eigenvalue
	
	if condition_matrix is not None:
		# Make sure that we have enough accuracy ...
		new_accuracy_needed = sum(entry.accuracy_needed for entry in eigenvector) + matrix.width * (int(log_height_int(matrix.bound())) + 2)
		for entry in eigenvector:
			entry.increase_accuracy(new_accuracy_needed)
		
		# ... so that this computation cannot fail.
		if not nonnegative_image(condition_matrix, eigenvector):
			raise ComputationError('Could not estimate invariant lamination.')
	
	return eigenvector, eigenvalue
