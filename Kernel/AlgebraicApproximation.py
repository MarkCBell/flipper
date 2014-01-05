
# A library for manipulating real algebraic numbers via interval approximations.

# Let K := QQ(\lambda) be a number field and x \in K.
# If x has minimal polynomial a_n x^n + ... + a_0 then 
# let deg(x) := n be the degree of x and height(x) := max(|a_n|) be the height of x.
# Be careful to note that if x \in ZZ then height(x) = max(abs(x), 1).

# We use the following facts:
#	1a) For x, y \in K, height(x +/- y) <= 2 * height(x) * height(y) and
#	 b) height(x *// y) <= height(x) * height(y) [Waldschmidt "Diophantine approximation on linear algebraic groups", Property 3.3].
#	2) If 0 != x \in K then |x| >= 1 / sum(|a_i / a_0|) [Basu et al. "Algorithms in Real Algebraic Geometry", Lemma 10.3]. 

# From 1) we can obtain an upper bound on the height of an equation of algebraic numbers. In fact the more general formula is that:
#	height(sum(x_i)) <= n prod(height(x_i))
# See: http://mathoverflow.net/questions/64643/height-of-algebraic-numbers

# From 2) it follows that so long as the accuracy of the interval of an Algebraic_Approximation is at least
#	-log(1 / sum(|a_i / a_0|)) = log(sum(|a_i / a_0|)) <= log(sum(|a_i|)) <= log(deg(x) * height(x)) = log(deg(x)) + log(height(x))
# it uniquely determines an algebraic number.

# Thus by knowing a sufficiently accurate approximation of x we can determine if x > 0. Combining this with 1) we can 
# therefore determine if x > y by determining if (x - y) > 0.

from math import log10 as log

from Flipper.Kernel.Interval import Interval, interval_from_string, interval_from_int, interval_from_fraction, interval_epsilon
from Flipper.Kernel.Error import ApproximationError

def log_height_int(number):
	return log(max(abs(number), 1))

# This class uses a sufficiently small interval to represent an algebraic number exactly. It is specified
# by an interval, an upper bound on the degree of the field extension in which this number lives and an
# upper bounds on the log of the height of this number.
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
			raise ApproximationError('%s may not define a unique algebraic number with degree at most %d and height at most %d.' % (self.interval, self.degree, self.log_height))
	
	def __repr__(self):
		return repr((self.interval, self.degree, self.log_height))
	
	def __neg__(self):
		return Algebraic_Approximation(-self.interval, self.degree, self.log_height)
	
	# These all assume that other lies in the same field extension of QQ.
	def __add__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.interval + other.interval, self.degree, self.log_height + other.log_height + 2)
		elif isinstance(other, int):
			return Algebraic_Approximation(self.interval + other, self.degree, self.log_height + log_height_int(other) + 2)
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.interval - other.interval, self.degree, self.log_height + other.log_height + 2)
		elif isinstance(other, int):
			return Algebraic_Approximation(self.interval - other, self.degree, self.log_height + log_height_int(other) + 2)
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.interval * other.interval, self.degree, self.log_height + other.log_height)
		elif isinstance(other, int):
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
		elif isinstance(other, int):
			return Algebraic_Approximation(self.interval / other, self.degree, self.log_height + log_height_int(other))
		else:
			return NotImplemented
	def __truediv__(self, other):
		return self.__div__(other)
	def __rdiv__(self, other):
		if isinstance(other, int):
			return Algebraic_Approximation(other / self.interval, self.degree, self.log_height + log_height_int(other))
		else:
			return NotImplemented  # !?!
	def __rtruediv__(self, other):
		return self.__rdiv__(other)
	
	def hashable(self):
		# The common denominator to switch Algebraic_Approximations to before hashing.
		HASH_DENOMINATOR = 5
		
		return self.interval.change_denominator(HASH_DENOMINATOR).tuple()
	
	# These may raise ApproximationError if not enough accuracy is present.
	def __lt__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return self.interval - other.interval < interval_epsilon(self.accuracy_needed, self.interval.accuracy)
		elif isinstance(other, int):
			return self.interval - other < interval_epsilon(self.accuracy_needed, self.interval.accuracy)
		else:
			return NotImplemented
	def __eq__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return -interval_epsilon(self.accuracy_needed, self.interval.accuracy) < self.interval - other.interval < interval_epsilon(self.accuracy_needed, self.interval.accuracy)
		elif isinstance(other, int):
			return -interval_epsilon(self.accuracy_needed, self.interval.accuracy) < self.interval - other < interval_epsilon(self.accuracy_needed, self.interval.accuracy)
		else:
			return NotImplemented
	def __gt__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return interval_epsilon(self.accuracy_needed, self.interval.accuracy) < self.interval - other.interval
		elif isinstance(other, int):
			return interval_epsilon(self.accuracy_needed, self.interval.accuracy) < self.interval - other
		else:
			return NotImplemented
	def __le__(self, other):
		return self < other or self == other
	def __ge__(self, other):
		return self > other or self == other

#### Some special Algebraic approximations we know how to build.

def algebraic_approximation_from_string(string, degree, log_height):
	return Algebraic_Approximation(interval_from_string(string), degree, log_height)

def algebraic_approximation_from_int(integer, accuracy, degree, log_height):
	return Algebraic_Approximation(interval_from_int(integer, accuracy), degree, log_height)

def algebraic_approximation_from_fraction(numerator, denominator, accuracy, degree, log_height):
	return Algebraic_Approximation(interval_from_fraction(numerator, denominator, accuracy), degree, log_height)
