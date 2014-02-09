
# A library for manipulating real algebraic numbers via interval approximations.

# Suppose that f(x) = a_n x^n + ... + a_0 \in ZZ[x] is a (not necessarily irreducible) polynomial with a_n != 0. We define
# H(f) := max(|a_n|) to be its height and deg(f) := n to be its degree. For convenience we also define h(f) := log(H(f))
# to be its log height.
#
# Let K := QQ(\lambda) be a number field and x_0 \in K be an algebraic number. We define
# H(x_0) := H(minpoly(x_0)) to be its the height and deg(x_0) := deg(minpoly(x_0)) to be its degree.
# Be careful to note that if x_0 \in ZZ then H(x_0) = max(abs(x_0), 1). Again we define h(x_0) := log(H(x_0)).

# We use the following facts:
#	1a) For x_0, x_1 \in K, H(x_0 +/- x_1) <= 2 * H(x_0) * H(x_1),
#	 b) H(x_0 * x_1) <= H(x_0) * H(x_1) and
#	 c) H(1 / x_0) == H(x_0) [Waldschmidt "Diophantine approximation on linear algebraic groups", Property 3.3].
#	2) If 0 != x_0 \in K is a root of f(x) = a_n x^n + ... + a_0 then |x_0| >= 1 / sum(|a_i / a_0|) [Basu et al. "Algorithms in Real Algebraic Geometry", Lemma 10.3]. 

# An immediate consequence of 1) is that if x_0 \in K is a root of f \in ZZ[x] then H(x_0) <= H(f).

# From 2) it follows that so long as the accuracy of the interval of an Algebraic_Approximation is at least
#	-log(1 / sum(|a_i / a_0|)) = log(sum(|a_i / a_0|)) <= log(sum(|a_i|)) <= log(deg(x_0) * H(f)) <= log(deg(x_0)) + h(x_0)
# it uniquely determines an algebraic number.

# Thus by knowing a sufficiently accurate approximation of x_0 we can determine if x_0 > 0. Combining this with 1) we can 
# therefore determine if x_0 > x_1 by determining if (x_0 - x_1) > 0.

from math import log10 as log

import Flipper

def log_height_int(number):
	return log(max(abs(number), 1))

# This class uses a sufficiently small interval to represent an algebraic number exactly. It is specified
# by an interval with contains the number, an upper bound on the degree of the field extension in which this number lives and an
# upper bound on the log height of this number.
class Algebraic_Approximation:
	__slots__ = ['interval', 'degree', 'log_height', 'accuracy_needed']  # Force minimal RAM usage.
	
	def __init__(self, interval, degree, log_height):
		self.interval = interval
		self.degree = degree
		# We need to make sure that 10^self.log_height >= height(algebraic number) in order to maintain an upper bound.
		# This is a bit of a hack and eventually I might find a better way to do this 
		# but at least for now it works.
		self.log_height = round(log_height, 5) + 0.00001
		self.accuracy_needed = int(log(self.degree)) + int(self.log_height) + 2
		# An algebraic approximation is good if it is known to more interval places
		# than its accuracy needed. That is if self.interval.accuracy >= self.accuracy_needed.
		if self.interval.accuracy < self.accuracy_needed:
			raise Flipper.Kernel.Error.ApproximationError('An algebraic number with degree at most %d and height at most %d requires an interval with accuracy at least %d not %d.' % (self.degree, self.log_height, self.accuracy_needed, self.interval.accuracy))
	
	def __repr__(self):
		return repr((self.interval, self.degree, self.log_height))
	
	def __neg__(self):
		return Algebraic_Approximation(-self.interval, self.degree, self.log_height)
	
	# These all assume that other lies in the same field extension of QQ.
	def __add__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.interval + other.interval, self.degree, self.log_height + other.log_height + log(2))
		elif isinstance(other, Flipper.Kernel.Types.Integer_Type):
			return Algebraic_Approximation(self.interval + other, self.degree, self.log_height + log_height_int(other) + log(2))
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.interval - other.interval, self.degree, self.log_height + other.log_height + log(2))
		elif isinstance(other, Flipper.Kernel.Types.Integer_Type):
			return Algebraic_Approximation(self.interval - other, self.degree, self.log_height + log_height_int(other) + log(2))
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.interval * other.interval, self.degree, self.log_height + other.log_height)
		elif isinstance(other, Flipper.Kernel.Types.Integer_Type):
			# Multiplication by 0 would cause problems here as we work with open intervals.
			if other == 0: return 0
			return Algebraic_Approximation(self.interval * other, self.degree, self.log_height + log_height_int(other))
		else:
			return NotImplemented
	def __rmult__(self, other):
		return self * other
	def __div__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.interval / other.interval, self.degree, self.log_height + other.log_height)
		elif isinstance(other, Flipper.Kernel.Types.Integer_Type):
			return Algebraic_Approximation(self.interval / other, self.degree, self.log_height + log_height_int(other))
		else:
			return NotImplemented
	def __truediv__(self, other):
		return self.__div__(other)
	def __rdiv__(self, other):
		if isinstance(other, Flipper.Kernel.Types.Integer_Type):
			return Algebraic_Approximation(other / self.interval, self.degree, self.log_height + log_height_int(other))
		else:
			return NotImplemented  # !?!
	def __rtruediv__(self, other):
		return self.__rdiv__(other)
	
	def is_positive(self):
		return self.interval.lower > 0
	def is_negative(self):
		return self.interval.upper < 0
	def is_zero(self):
		return not self.is_positive() and not self.is_negative()
	
	def __lt__(self, other):
		return (self - other).is_negative()
	def __eq__(self, other):
		return (self - other).is_zero()
	def __gt__(self, other):
		return (self - other).is_positive()
	
	def __le__(self, other):
		return self < other or self == other
	def __ge__(self, other):
		return self > other or self == other
	
	def algebraic_simplify(self):
		return self
	def algebraic_hash(self):
		# The common denominator to switch Algebraic_Approximations to before hashing.
		HASH_DENOMINATOR = 5
		
		return self.interval.change_denominator(HASH_DENOMINATOR).tuple()
	
	# Perhaps we don't need these.
	def algebraic_degree(self):
		return self.degree
	def algebraic_log_height(self):
		return self.log_height
	def algebraic_approximate(self, accuracy, degree=None):
		pass

#### Some special Algebraic approximations we know how to build.

def algebraic_approximation_from_string(string, degree, log_height):
	return Algebraic_Approximation(Flipper.Kernel.Interval.interval_from_string(string), degree, log_height)

def algebraic_approximation_from_int(integer, accuracy, degree, log_height):
	return Algebraic_Approximation(Flipper.Kernel.Interval.interval_from_int(integer, accuracy), degree, log_height)

def algebraic_approximation_from_fraction(numerator, denominator, accuracy, degree, log_height):
	return Algebraic_Approximation(Flipper.Kernel.Interval.interval_from_fraction(numerator, denominator, accuracy), degree, log_height)
