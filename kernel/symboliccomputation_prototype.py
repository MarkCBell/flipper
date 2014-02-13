
# WARNING: This library is designed ONLY to work with Lamination.splitting_sequence(exact=False)
# It does NOT meet the requirement of implementing addition, subtraction, division, comparison and 
# equality with integers and other algebraic_types required by Lamination.splitting_sequence(exact=True).

from math import log10 as log

import Flipper
from Flipper.kernel.symboliccomputation_dummy import AlgebraicType

_name = 'custom'

def projective_difference(A, B, error_reciprocal):
	# Returns True iff the projective difference between A and B is less than 1 / error_reciprocal.
	A_sum, B_sum = sum(A), sum(B)
	return max(abs((p * B_sum) - q * A_sum) for p, q in zip(A, B)) * error_reciprocal < A_sum * B_sum 

# This class represents the leading eigenvector of a matrix.
class Eigenvector:
	def __init__(self, matrix, vector=None):
		self.matrix = matrix  # This is the matrix we were given
		self.power_matrix = self.matrix  # and this is some power of that matrix.
		self.current_accuracy = -1
		
		# We will use notions and notation from Flipper.kernel.algebraicapproximation.py, you should probably read that first.
		# If M = (a_ij) is a matrix of algebraic numbers we define height(M) := max(height(a_ij)).
		#
		# Now suppose that M is an n x n non-zero integer matrix with eigenvalue, eigenvector pair \lambda, v = (v_i).
		# Suppose additionally that \lambda has multiplicity one and that sum(v_i) == 1. We would
		# like to obtain good bounds on height(\lambda) and height(v_i).
		#
		# Let f(x) be the minimal polynomial of \lambda, we note that as the characteristic polynomial of M is monic 
		# f is too by Gauss's lemma. Let d := deg(\lambda) = deg(f) <= n and let
		#	M(f) := \prod_{x a root of f} max(1, |x|)
		# be the Mahler measure of f. Note that this is equivalent to the standard definition 
		# of the Mahler measure of a polynomial which involves some complicated looking
		# integral [Borwein and Erdelyi 1995, p. 271].
		#
		# Now if x is an a root of f then it is also eigenvalue of M and so by the Gershgorin circle 
		# theorem as M has integer entries:
		#	 |x| <= n height(M).
		# Hence, as n height(M) > 1:
		#	M(f) <= (n height(M))^n.
		# Finally we note that:
		#	height(f) <= (n choose n/2) M(f) [http://en.wikipedia.org/wiki/Height_of_a_polynomial].
		#
		# Thus we are able to determine that:
		#	height(f) <= (n choose n/2) (n height(M))^n <= (2 (n+1) height(M))^n.
		# and so that:
		#	log(height(\lambda)) <= n (log(height(M)) + log(n) + log(2)).
		#
		# Now to deal with height(v_i). Let K := QQ(\lambda). We identify K == {sum(a_i \lambda^i) : a_i \in QQ} 
		# with QQ^d and think of M as acting on QQ^{nd}.
		#
		# Let M' be the rational matrix corresponding to the action of M - \lambda I on QQ^{nd}. Then 
		#	height(M') <= height(M) + height(\lambda) and
		#	rank(M') == d(n-1).
		#
		# As v is an eigenvector of M, we may write v_i = sum(b_ij \lambda^i) with b_ij rational. Then,
		# as v lies in the kernel of M - \lambda I, b := (b_11 ... b_1d b_21 ... b_2d ... b_n1 ... b_nd) lies 
		# in the kernel of M'. Furthermore, as sum(v_i) == 1, we have that:
		#	sum_j(b_ij) == { 1 if i == 1
		#	               { 0 otherwise.
		#
		# Taken together with (n-1)d of the equations of M' these form a set of nd linearly independent equations
		# which the entries of b must satisfy. We can then solve these equations for b_ij by using Kramer's method
		# to find that:
		#	b_ij == det(M_ij) / det(M'')
		# where M_ij and M'' are matrices with entries from M' and so:
		#	height(M_ij), height(M'') <= height(M')
		#
		# Finally, by Hadamard's inequality, |det(M_ij)|, |det(M'')| <= (sqrt(nd) height(M'))^{nd} <= (n height(M')^{nd}. Hence:
		#	height(b_ij) <= (sqrt(nd) height(M'))^{nd} <= (n height(M')^{nd}
		# and so:
		#	height(v_i) = height(sum(b_ij \lambda^j)) <= d * \prod_j height(b_ij) height(\lambda)^j <= d * (n height(M'))^{nd^2} height(\lambda)^{d^2}
		#
		# Therefore:
		#	log(height(v_i)) <= log(d) + n d^2 [log(n) + log(height(M'))] + d^2 log(height(\lambda))
		#	                 <= log(n) + n^3 [log(n) + log(height(M) + height(\lambda)))] + n^2 log(height(\lambda))
		
		
		# Something like this:
		# (  ?  ) ( )   (1)
		# (__?__) (b)   (0)
		# (     ) ( ) = (0)
		# (  M' )       (0)
		# (     )       (0)
		
		self.degree = self.matrix.width
		self.height_matrix = self.matrix.bound()
		self.log_height_eigenvalue = self.degree * (log(self.height_matrix) + log(self.degree) + log(2))
		self.log_height = 2 * self.degree**3 * (log(self.degree) + log(self.matrix.bound()) + self.log_height_eigenvalue)
		self.log_height = 100  # !?! Deal with this!
		self.accuracy_needed = int(log(self.degree)) + int(self.log_height) + 2
		
		if vector is None: vector = [1] * self.matrix.width
		self.old_vector = vector
		self.vector = self.matrix * self.old_vector
		
		self.algebraic_approximation = [None] * self.matrix.width
		self.increase_accuracy()
	
	
	def increase_accuracy(self, accuracy=None):
		if accuracy is None: accuracy = self.accuracy_needed
		
		if self.current_accuracy < accuracy:
			while not projective_difference(self.old_vector, self.vector, 10**accuracy):
				self.old_vector, self.vector = self.vector, self.power_matrix * self.vector
				self.power_matrix = self.power_matrix * self.power_matrix  # Now square the power matrix so we converge faster.
			
			self.current_accuracy = accuracy
			self.algebraic_approximations = [Flipper.kernel.algebraicapproximation.algebraic_approximation_from_fraction(entry, sum(self.vector), self.current_accuracy, self.degree, self.log_height) for entry in self.vector]


def algebraic_simplify(self, value=None):
	if value is not None:
		return value
	else:
		return self

def algebraic_hash(self):
	return None

def algebraic_hash_ratio(self, other):
	return None

def algebraic_degree(self):
	return self.value[0].degree

def algebraic_log_height(self):
	return self.value[0].log_height

def algebraic_approximate(self, accuracy, degree=None):
	self.value[0].increase_accuracy(accuracy)
	return self.value[0].algebraic_approximations[self.value[1]]

AlgebraicType.algebraic_simplify = algebraic_simplify
AlgebraicType.algebraic_hash = algebraic_hash
AlgebraicType.algebraic_hash_ratio = algebraic_hash_ratio
AlgebraicType.algebraic_degree = algebraic_degree
AlgebraicType.algebraic_log_height = algebraic_log_height
AlgebraicType.algebraic_approximate = algebraic_approximate

# Eventually we could implement these so Lamination.splitting_sequence(exact=True) would work.
AlgebraicType.__neg__ = NotImplemented
AlgebraicType.__add__ = NotImplemented
AlgebraicType.__radd__ = NotImplemented
AlgebraicType.__sub__ = NotImplemented
AlgebraicType.__rsub__ = NotImplemented
AlgebraicType.__mul__ = NotImplemented
AlgebraicType.__rmul__ = NotImplemented
AlgebraicType.__div__ = NotImplemented
AlgebraicType.__truediv__ = NotImplemented
AlgebraicType.__rdiv__ = NotImplemented
AlgebraicType.__rtruediv__ = NotImplemented
AlgebraicType.__lt__ = NotImplemented
AlgebraicType.__eq__ = NotImplemented
AlgebraicType.__gt__ = NotImplemented


def Perron_Frobenius_eigen(matrix, vector=None, condition_matrix=None):
	# Assumes that matrix is Perron-Frobenius and so has a unique real eigenvalue of largest
	# magnitude. If not an AssumptionError is thrown.
	
	EV = Eigenvector(matrix, vector=vector)
	
	eigenvector = [AlgebraicType((EV, i)) for i in range(matrix.width)]
	
	if condition_matrix is not None:
		# Make sure that we have enough accuracy ...
		new_accuracy_needed = sum(entry.accuracy_needed for entry in eigenvector) + matrix.width * (int(Flipper.kernel.algebraicapproximation.log_height_int(matrix.bound())) + 2)
		for entry in eigenvector:
			entry.increase_accuracy(new_accuracy_needed)
		
		# ... so that this computation cannot fail.
		if not condition_matrix.nonnegative_image(eigenvector):
			raise Flipper.kernel.error.ComputationError('Could not estimate invariant lamination.')
	
	return eigenvector


def algebraic_type_from_int(integer):
	return AlgebraicType((Eigenvector(Flipper.Matrix([[1]], 1), vector=[1]), 0))
