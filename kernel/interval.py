
import flipper

from math import log10 as log

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

class Interval(object):
	''' This represents a closed interval [lower*10**-precision, upper*10**-precision]. '''
	def __init__(self, lower, upper, precision):
		assert(isinstance(lower, flipper.Integer_Type))
		assert(isinstance(upper, flipper.Integer_Type))
		assert(isinstance(precision, flipper.Integer_Type))
		if lower > upper: raise ValueError('Interval is empty.')
		
		self.lower = lower
		self.upper = upper
		self.precision = precision
		# The width of this interval is at most 10^-self.accuracy.
		# That is, this interval defines a number correct to self.accuracy decimal places.
		self.accuracy = float('inf') if self.upper == self.lower else self.precision - int(log(self.upper - self.lower))
		
		self.log_bound = log(max(abs(self.upper), abs(self.lower), 1)) - self.precision
	
	def __repr__(self):
		return self.approximate_string(6)
	
	def __float__(self):
		return float(self.approximate_string(30)[:-1])
	def __hash__(self):
		return hash(self.tuple())
	
	def copy(self):
		return Interval(self.lower, self.upper, self.precision)
	
	def approximate_string(self, accuracy=None):
		if accuracy is None or accuracy > self.accuracy: accuracy = self.accuracy-1
		I = self.change_denominator(accuracy)
		v = (I.lower + I.upper) // 2
		s = str(v).zfill(accuracy + (2 if v < 0 else 1))
		return '%s.%s?' % (s[:-I.precision], s[-I.precision:])
	def tuple(self):
		return (self.lower, self.upper, self.precision)
	def change_denominator(self, new_denominator):
		assert(isinstance(new_denominator, flipper.Integer_Type))
		d = new_denominator - self.precision
		if d > 0:
			return Interval(self.lower * 10**d, self.upper * 10**d, new_denominator)
		elif d == 0:
			return self
		elif d < 0:
			return Interval((self.lower // 10**(-d)) - 1, (self.upper // 10**(-d)) + 1, new_denominator)
	def change_accuracy(self, new_accuracy):
		assert(isinstance(new_accuracy, flipper.Integer_Type))
		if self.accuracy == float('inf'):
			return self
		else:
			assert(new_accuracy <= self.accuracy)
			return self.change_denominator(self.precision - (self.accuracy - new_accuracy))
	def simplify(self):
		d = self.precision - self.accuracy
		if d > 1:
			return self.change_denominator(self.accuracy-1)
		else:
			return self
	def __contains__(self, other):
		if isinstance(other, Interval):
			return self.lower < other.lower and other.upper < self.upper
		elif isinstance(other, flipper.Integer_Type):
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
		elif isinstance(other, flipper.Integer_Type):
			return Interval(self.lower + other * 10**self.precision, self.upper + other * 10**self.precision, self.precision)
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
		elif isinstance(other, flipper.Integer_Type):
			return Interval(self.lower - other * 10**self.precision, self.upper - other * 10**self.precision, self.precision)
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, Interval):
			common_precision = max(self.precision, other.precision)
			P, Q = self.change_denominator(common_precision), other.change_denominator(common_precision)
			values = [P.lower * Q.lower, P.upper * Q.lower, P.lower * Q.upper, P.upper * Q.upper]
			return Interval(min(values), max(values), 2*common_precision)
		elif isinstance(other, flipper.Integer_Type):
			values = [self.lower * other, self.upper * other]
			return Interval(min(values), max(values), self.precision)
		else:
			return NotImplemented
	def __rmul__(self, other):
		return self * other
	def __pow__(self, power):
		if power == 0:
			return 1
		if power > 0:
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
			# !?! RECHECK THIS!
			common_precision = max(self.precision, other.precision)
			P, Q = self.change_denominator(common_precision), other.change_denominator(common_precision)
			values = [P.lower * 10**common_precision // Q.lower, P.upper * 10**common_precision // Q.lower, P.lower * 10**common_precision // Q.upper, P.upper * 10**common_precision // Q.upper]
			return Interval(min(values), max(values), common_precision)
		elif isinstance(other, flipper.Integer_Type):
			values = [self.lower // other, self.upper // other]
			return Interval(min(values), max(values), self.precision)
		else:
			return NotImplemented
	def __truediv__(self, other):
		return self.__div__(other)
	def midpoint(self, magnitude=10):
		m = (10**magnitude) * (self.lower + self.upper) // 2
		return Interval(m-1, m+1, self.precision+magnitude)
	def intersect(self, other):
		common_precision = max(self.precision, other.precision)
		P, Q = self.change_denominator(common_precision), other.change_denominator(common_precision)
		return Interval(max(P.lower, Q.lower), min(P.upper, Q.upper), common_precision)
	def subdivide(self):
		d = self.upper - self.lower
		if d > 1:
			k = 1 + d // 10
			return [Interval(self.lower + i, min(self.lower + i + k, self.upper), self.precision) for i in range(0, d, k)]
		elif d == 1:
			return [Interval(10*self.lower + i, 10*self.lower + i+1, self.precision + 1) for i in range(10)]
		elif d == 0:
			return [Interval(self.lower, self.upper, self.precision)]

#### Some special Intervals we know how to build.

def interval_from_string(string):
	i, r = string.split('.') if '.' in string else (string, '')
	x = int(i + r)
	return Interval(x-10, x+10, len(r))

