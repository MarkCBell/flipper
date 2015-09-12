
''' A module for representing and manipulating intervals.

Provides one class: Interval.

There is also a helper function: create_interval. '''

import flipper

from math import log10 as log
from math import ceil

# This class represents the interval (lower / 10^precision, upper / 10^precision).

# For an interval I let acc(I) denote the accuracy of I, that is
#	acc(I) := self.precision - int(log(self.upper - self.lower)).
# For an integer x let log+(x) := log(max(abs(x), 1)) and for an interval I
# let log+(I) := max(log+(I.lower), log+(I.upper), I.precision) - I.precision.

# Suppose that x is an integer and that I and J are intervals and that
# m := min(acc(I), acc(J)).
# Then we obtain the following bounds:
#	acc(I + J) >= m - 1,
#	acc(I * J) >= m - log(I.lower + J.lower + 1)
#	acc(I / J) >= m - log+(J)
#	acc(x * I) >= acc(I) - log+(x)

INFTY = float('inf')

class Interval(object):
	''' This represents a closed interval [lower / 10**precision, upper / 10**precision].
	
	>>> w = create_interval('0.10')
	>>> x = create_interval('10000.0')
	>>> y = create_interval('1.14571')
	>>> z = create_interval('1.00000')
	>>> a = create_interval('-1.200000')
	>>> b = create_interval('1.4142135623')
	>>> a
	-1.2001?
	'''
	def __init__(self, lower, upper, precision):
		assert(isinstance(lower, flipper.IntegerType))
		assert(isinstance(upper, flipper.IntegerType))
		assert(isinstance(precision, flipper.IntegerType))
		if lower > upper: raise ValueError('Interval is empty.')
		
		self.lower = lower
		self.upper = upper
		self.precision = precision
		# The width of this interval is at most 10^-self.accuracy.
		# That is, this interval defines a number correct to self.accuracy decimal places.
		self.accuracy = INFTY if self.upper == self.lower else self.precision - int(ceil(log(self.upper - self.lower)))
		
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return self.approximate_string(6)
	def __float__(self):
		return float(self.approximate_string(30)[:-1])
	def __int__(self):
		# Return an integer approximating this. We really return the floor
		# but we avoid __floor__ and __ceil__ as these expect floats.
		return self.lower // 10**self.precision
	def __hash__(self):
		return hash(self.tuple())
	
	def approximate_string(self, accuracy=None):
		''' Return a string approximating the centre of this interval. '''
		
		if accuracy is None or accuracy > self.accuracy:
			accuracy = self.precision if self.accuracy == INFTY else self.accuracy-1
		I = self.change_denominator(accuracy)
		v = (I.lower + I.upper) // 2
		s = str(v).zfill(accuracy + (2 if v < 0 else 1))
		return '%s.%s?' % (s[:-I.precision], s[-I.precision:])
	def tuple(self):
		''' Return the triple describing this interval. '''
		
		return (self.lower, self.upper, self.precision)
	def log_plus(self):
		''' Return max(log(x), 0) over all x in self. '''
		return max(log(max(abs(self.upper), abs(self.lower), 1)) - self.precision, 0) + 1
	
	def change_denominator(self, new_denominator):
		''' Return a this interval over a new denominator. '''
		
		assert(isinstance(new_denominator, flipper.IntegerType))
		
		d = new_denominator - self.precision
		if d > 0:
			return Interval(self.lower * 10**d, self.upper * 10**d, new_denominator)
		elif d == 0:
			return self
		elif d < 0:
			return Interval((self.lower // 10**(-d)) - 1, (self.upper // 10**(-d)) + 1, new_denominator)
	def change_accuracy(self, new_accuracy):
		''' Return a new interval with the given accuracy.
		
		The new_accuracy must be at most self.accuracy. '''
		
		assert(isinstance(new_accuracy, flipper.IntegerType))
		
		if self.accuracy == INFTY:
			return self
		else:
			assert(new_accuracy <= self.accuracy)
			return self.change_denominator(self.precision - (self.accuracy - new_accuracy))
	def simplify(self):
		''' Return a simpler interval with accuracy at least self.accuracy-1. '''
		
		# As self.change_denominator divides outwards then shifts by +/-1 we need
		# to work with at least two more digits.
		if self.accuracy > 0 and self.precision > self.accuracy + 2:
			I = self.change_denominator(self.accuracy + 2)
		else:
			I = self
		
		assert(I.accuracy >= self.accuracy - 1)
		return I
	
	def __contains__(self, other):
		if isinstance(other, Interval):
			return self.lower < other.lower and other.upper < self.upper
		elif isinstance(other, flipper.IntegerType):
			return self.lower < other * 10**self.precision < self.upper
		else:
			return NotImplemented
	def __neg__(self):
		return Interval(-self.upper, -self.lower, self.precision)
	def __abs__(self):
		if self.lower > 0:  # Interval is entirely positive.
			return self
		elif self.upper < 0:  # Interval is entirely negative.
			return -self
		if self.lower <= 0 <= self.upper:  # Interval straddles 0.
			return Interval(0, max(-self.lower, self.upper), self.precision)
	def __add__(self, other):
		if isinstance(other, Interval):
			common_precision = max(self.precision, other.precision)
			P, Q = self.change_denominator(common_precision), other.change_denominator(common_precision)
			new_lower = P.lower + Q.lower
			new_upper = P.upper + Q.upper
			return Interval(new_lower, new_upper, common_precision)
		elif isinstance(other, flipper.IntegerType):
			return self + Interval(other, other, 0)
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, Interval):
			common_precision = max(self.precision, other.precision)
			P, Q = self.change_denominator(common_precision), other.change_denominator(common_precision)
			new_lower = P.lower - Q.upper
			new_upper = P.upper - Q.lower
			return Interval(new_lower, new_upper, common_precision)
		elif isinstance(other, flipper.IntegerType):
			return self - Interval(other, other, 0)
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, Interval):
			values = [
				self.lower * other.lower,
				self.upper * other.lower,
				self.lower * other.upper,
				self.upper * other.upper
				]
			return Interval(min(values), max(values), self.precision + other.precision)
		elif isinstance(other, flipper.IntegerType):
			values = [self.lower * other, self.upper * other]
			return Interval(min(values), max(values), self.precision)
		else:
			return NotImplemented
	def __rmul__(self, other):
		return self * other
	def __pow__(self, power):
		if power == 0:
			return Interval(1, 1, 0)
		elif power == 1:
			return self
		elif power > 1:
			sqrt = self**(power//2)
			square = sqrt * sqrt
			if power % 2 == 1:
				return self * square
			else:
				return square
	def __div__(self, other):
		if isinstance(other, Interval):
			if 0 in other:
				raise ZeroDivisionError  # Denominator contains 0.
			
			# I suspect that there is a lot of optimisation that could be done here.
			# In particular, if we are willing to make the other interval wider we
			# might be able to avoid an expensive division, hopefully without giving
			# up too much accuracy.
			common_precision = max(self.precision, other.precision)
			P, Q = self.change_denominator(common_precision), other.change_denominator(common_precision)
			values = [
				P.lower * 10**common_precision // Q.lower,
				P.upper * 10**common_precision // Q.lower,
				P.lower * 10**common_precision // Q.upper,
				P.upper * 10**common_precision // Q.upper
				]
			return Interval(min(values), max(values), common_precision)
		elif isinstance(other, flipper.IntegerType):
			values = [self.lower // other, self.upper // other]
			return Interval(min(values), max(values), self.precision)
		else:
			return NotImplemented
	def __truediv__(self, other):
		return self.__div__(other)
	
	def midpoint(self, magnitude=10):
		''' Return a smaller interval containing the midpoint of this interval. '''
		
		assert(isinstance(magnitude, flipper.IntegerType))
		
		m = (10**magnitude) * (self.lower + self.upper) // 2
		return Interval(m-1, m+1, self.precision+magnitude)
	def intersect(self, other):
		''' Return the intersection of this interval with other. '''
		
		assert(isinstance(other, Interval))
		
		common_precision = max(self.precision, other.precision)
		P, Q = self.change_denominator(common_precision), other.change_denominator(common_precision)
		return Interval(max(P.lower, Q.lower), min(P.upper, Q.upper), common_precision)
	
	def subdivide(self):
		''' Return a list of smaller intervals covering this interval. '''
		
		d = self.upper - self.lower
		if d > 1:
			k = 1 + d // 10
			return [Interval(self.lower + i, min(self.lower + i + k, self.upper), self.precision) for i in range(0, d, k)]
		elif d == 1:
			return [Interval(10*self.lower + i, 10*self.lower + i+1, self.precision + 1) for i in range(10)]
		elif d == 0:
			return [Interval(self.lower, self.upper, self.precision)]
	
	def polynomial(self, degree, scale):
		''' Return a polynomial of at most the specified degree and height with a root (hopefully) close to the center of this interval. '''
		
		# This needs rechecking against the literature to ensure that M.LLL() works correctly.
		M = flipper.kernel.id_matrix(degree+1).join(
			flipper.kernel.Matrix([[int(scale * self**i) for i in range(degree+1)]])).transpose()
		
		# Should this also appear in the symbolic library? Sage is much faster than us at LLL.
		
		return flipper.kernel.Polynomial(M.LLL()[0][:-1])

#### Some special Intervals we know how to build.

def create_interval(string):
	''' A short way of constructing Intervals from a string. '''
	
	i, r = string.split('.') if '.' in string else (string, '')
	x = int(i + r)
	return Interval(x-1, x+1, len(r))

def doctest_globs():
	''' Return the globals needed to run doctest on this module. '''
	
	w = create_interval('0.10')
	x = create_interval('10000.0')
	y = create_interval('1.14571')
	z = create_interval('1.00000')
	a = create_interval('-1.200000')
	b = create_interval('1.4142135623')
	
	return {'w': w, 'x': x, 'y': y, 'z': z, 'a': a, 'b': b}

