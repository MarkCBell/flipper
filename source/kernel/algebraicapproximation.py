
''' A module for representing approximations of real algebraic numbers.

Provides two classes: AlgebraicApproximation.

There is also a helper function: create_algebraic_approximation. '''

# Suppose that f(x) = a_n x^n + ... + a_0 \in ZZ[x] is a (not necessarily irreducible) polynomial with a_n != 0. We define
# h(f) := log(max(|a_n|)) to be its height and deg(f) := n to be its degree.
#
# Let K be a number field and x_0 \in K be an algebraic number. We define h(x_0) := h(minpoly(x_0)) to be its the height
# and deg(x_0) := deg(minpoly(x_0)) to be its degree.
#
# We use the following facts:
#	1a) For x_0, x_1 \in K, h(x_0 +/- x_1) <= h(x_0) + h(x_1) + 1,
#	 b) h(x_0 * x_1) <= h(x_0) + h(x_1) and
#	 c) h(1 / x_0) == h(x_0) [Waldschmidt "Diophantine approximation on linear algebraic groups", Property 3.3].
#	2) If 0 != x_0 \in K is a root of f(x) = a_n x^n + ... + a_0 then
#		|x_0| >= 1 / sum(|a_i / a_0|) [Basu et al. "Algorithms in Real Algebraic Geometry", Lemma 10.3].
#
# An immediate consequence of 1) is that if x_0 \in K is a root of f \in ZZ[x] then h(x_0) <= h(f) + 2 \deg(f).
#
# From 2) it follows that so long as the accuracy of the interval of an AlgebraicApproximation is at least
#	-log(1 / sum(|a_i / a_0|)) = log(sum(|a_i / a_0|)) <= log(sum(|a_i|)) <= log(deg(x_0) * H(f)) <= log(deg(x_0)) + h(x_0)
# then it uniquely determines an algebraic number.
#
# Thus by knowing a sufficiently accurate approximation of x_0 we can determine if x_0 > 0. Combining this with 1) we can
# therefore determine if x_0 > x_1 by determining if (x_0 - x_1) > 0.

import flipper

from math import log10 as log
LOG_2 = log(2)

class AlgebraicApproximation(object):
	''' This represents an algebraic number.
	
	It is specified by an interval which contains the number, an upper
	bound on the log of its degree and its height.
	
	If the interval is not sufficiently small, in terms of the log_degree
	and height bounds, to uniquely determine the algebraic number then
	an ApproximationError will be raised.
	
	>>> import flipper
	>>> I = flipper.kernel.AlgebraicApproximation(flipper.kernel.Interval(141421356, 141421357, 8), 2, 2)
	>>> I
	1.414213?
	>>> J = flipper.kernel.create_algebraic_approximation('1.41421356', 2, 2)
	>>> J
	1.414213?
	>>> flipper.kernel.create_algebraic_approximation('1.41', 2, 2)  # doctest: +ELLIPSIS
	Traceback (most recent call last):
	    ...
	ApproximationError: ...
	'''
	def __init__(self, interval, log_degree, height):
		assert(isinstance(interval, flipper.kernel.Interval))
		assert(isinstance(log_degree, flipper.kernel.NumberType))
		assert(isinstance(height, flipper.kernel.NumberType))
		
		self.interval = interval
		self.log_degree = log_degree
		self.accuracy = self.interval.accuracy
		self.height = height
		self.accuracy_needed = self.log_degree + self.height
		# An algebraic approximation is good if it is known to more places
		# than its accuracy needed. That is if self.interval.accuracy >= self.accuracy_needed.
		if self.accuracy < self.accuracy_needed:
			raise flipper.kernel.ApproximationError('An algebraic number with log(degree) at most %0.3f and height at most %0.3f requires an interval with accuracy at least %0.3f, not %d.' % (self.log_degree, self.height, self.accuracy_needed, self.accuracy))
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return str(self.interval)
	
	def __float__(self):
		return float(self.interval)
	
	def change_denominator(self, new_denominator):
		''' Return a new approximation of this algebraic number with the given denominator. '''
		
		assert(isinstance(new_denominator, flipper.IntegerType))
		
		return AlgebraicApproximation(self.interval.change_denominator(new_denominator), self.log_degree, self.height)
	
	def change_accuracy(self, new_accuracy):
		''' Return a new approximation of this algebraic number with the given accuracy.
		
		The new_accuracy must be at most self.accuracy.
		
		>>> I.change_accuracy(5)
		1.4142?
		'''
		
		assert(isinstance(new_accuracy, flipper.IntegerType))
		
		return AlgebraicApproximation(self.interval.change_accuracy(new_accuracy), self.log_degree, self.height)
	
	def simplify(self):
		''' Return a new approximation of this algebraic number with the given accuracy.
		
		>>> I.simplify()
		1.414213?
		'''
		
		return AlgebraicApproximation(self.interval.simplify(), self.log_degree, self.height)
	
	def __neg__(self):
		return AlgebraicApproximation(-self.interval, self.log_degree, self.height)
	def __add__(self, other):
		if isinstance(other, AlgebraicApproximation):
			return AlgebraicApproximation(self.interval + other.interval, self.log_degree + other.log_degree, self.height + other.height + LOG_2)
		elif isinstance(other, flipper.IntegerType):
			return AlgebraicApproximation(self.interval + other, self.log_degree, self.height + flipper.kernel.height_int(other) + LOG_2)
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, AlgebraicApproximation):
			return AlgebraicApproximation(self.interval - other.interval, self.log_degree + other.log_degree, self.height + other.height + LOG_2)
		elif isinstance(other, flipper.IntegerType):
			return AlgebraicApproximation(self.interval - other, self.log_degree, self.height + flipper.kernel.height_int(other) + LOG_2)
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, AlgebraicApproximation):
			return AlgebraicApproximation(self.interval * other.interval, self.log_degree + other.log_degree, self.height + other.height)
		elif isinstance(other, flipper.IntegerType):
			return AlgebraicApproximation(self.interval * other, self.log_degree, self.height + flipper.kernel.height_int(other))
		else:
			return NotImplemented
	def __rmul__(self, other):
		return self * other
	def __pow__(self, power):
		if power == 0:
			return AlgebraicApproximation(flipper.kernel.Interval(1, 1, 0), 0, 1)
		if power > 0:
			sqrt = self**(power//2)
			square = sqrt * sqrt
			if power % 2 == 1:
				return self * square
			else:
				return square
	def __div__(self, other):
		if isinstance(other, AlgebraicApproximation):
			return AlgebraicApproximation(self.interval / other.interval, self.log_degree + other.log_degree, self.height + other.height)
		elif isinstance(other, flipper.IntegerType):
			return AlgebraicApproximation(self.interval / other, self.log_degree, self.height + flipper.kernel.height_int(other))
		else:
			return NotImplemented
	def __truediv__(self, other):
		return self.__div__(other)
	def __rdiv__(self, other):
		if isinstance(other, flipper.IntegerType):
			return AlgebraicApproximation(other / self.interval, self.log_degree, self.height + flipper.kernel.height_int(other))
		else:
			return NotImplemented
	def __rtruediv__(self, other):
		return self.__rdiv__(other)
	
	def sign(self):
		''' Return the sign of the underlying algebraic number.
		
		>>> I.sign()
		1
		'''
		
		if self.interval.lower > 0:
			return +1
		elif self.interval.upper < 0:
			return -1
		else:
			return 0
	
	def __lt__(self, other):
		return (self - other).sign() == -1
	def __eq__(self, other):
		return (self - other).sign() == 0
	def __ne__(self, other):
		return not (self == other)
	def __gt__(self, other):
		return (self - other).sign() == +1
	
	def __le__(self, other):
		return self < other or self == other
	def __ge__(self, other):
		return self > other or self == other

#### Some special Algebraic approximations we know how to build.
# These are useful for creating tests.

def create_algebraic_approximation(string, degree, height):
	''' A short way of constructing AlgebraicApproximations from a string and degree and height bounds. '''
	
	return AlgebraicApproximation(flipper.kernel.create_interval(string), log(max(degree, 1)), height)

def doctest_globs():
	''' Return the globals needed to run doctest on this module. '''
	
	I = flipper.kernel.AlgebraicApproximation(flipper.kernel.Interval(141421356, 141421357, 8), 2, 2)
	J = flipper.kernel.create_algebraic_approximation('1.41421356', 2, 2)
	
	return {'I': I, 'J': J}

