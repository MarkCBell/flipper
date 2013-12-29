
# A library for manipulating real algebraic numbers via interval approximations.

# This relies on the following facts:
# ???

from math import log10 as log

from Flipper.Kernel.Interval import Interval, interval_from_string, interval_epsilon
from Flipper.Kernel.Error import AssumptionError, ApproximationError
from Flipper.Kernel.SymbolicComputation import symbolic_approximate, symbolic_degree, symbolic_height, algebraic_type

def log_height(number):
	return log(symbolic_height(number))

class Algebraic_Approximation:
	def __init__(self, interval, degree, log_height):
		self.interval = interval
		self.degree = degree
		self.log_height = log_height
		self.precision_needed = int(log(self.degree)) + int(self.log_height) + 2
		# An algebraic approximation is good if it is known to more interval places
		# than its precision needed. That is if self.interval.q >= self.precision_needed.
		if self.interval.q < self.precision_needed:
			raise ApproximationError('%s may not define a unique algebraic number with degree at most %d and height at most %d.' % (self.interval, self.degree, self.log_height))
	def change_denominator(self, new_q):
		return Algebraic_Approximation(self.interval.change_denominator(new_q), self.degree, self.log_height)
	def __repr__(self):
		return repr((self.interval, self.degree, self.log_height))
	def __neg__(self):
		return Algebraic_Approximation(-self.interval, self.degree, self.log_height)
	# These all assume that other lies in the same field extension of QQ.
	def __add__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.interval + other.interval, self.degree, self.log_height + other.log_height + 1)
		elif isinstance(other, int):
			# return self + algebraic_approximation_from_integer(other, self.degree)
			return Algebraic_Approximation(self.interval + other, self.degree, self.log_height + log_height(other) + 1)
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.interval - other.interval, self.degree, self.log_height + other.log_height + 1)
		elif isinstance(other, int):
			# return self - algebraic_approximation_from_integer(other, self.degree)
			return Algebraic_Approximation(self.interval - other, self.degree, self.log_height + log_height(other) + 1)
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.interval * other.interval, self.degree, self.log_height + other.log_height)
		elif isinstance(other, int):
			# return self * algebraic_approximation_from_integer(other, self.degree)
			return Algebraic_Approximation(self.interval * other, self.degree, self.log_height + log_height(other))
		else:
			return NotImplemented
	def __rmult__(self, other):
		return self * other
	def __div__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.interval / other.interval, self.degree, self.log_height + other.log_height)
		elif isinstance(other, int):
			# return self / algebraic_approximation_from_integer(other, self.degree)
			return Algebraic_Approximation(self.interval / other, self.degree, self.log_height + log_height(other))
		else:
			return NotImplemented
	def __truediv__(self, other):
		return self.__div__(other)
	def __rdiv__(self, other):
		return NotImplemented  # !?!
	# These may raise ApproximationError if not enough accuracy is present.
	def __lt__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return self.interval - other.interval < interval_epsilon(self.precision_needed, self.interval.q)
		elif isinstance(other, int):
			return self.interval - other < interval_epsilon(self.precision_needed, self.interval.q)
		else:
			return NotImplemented
	def __eq__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return -interval_epsilon(self.precision_needed, self.interval.q) < self.interval - other.interval < interval_epsilon(self.precision_needed, self.interval.q)
		elif isinstance(other, int):
			return -interval_epsilon(self.precision_needed, self.interval.q) < self.interval - other < interval_epsilon(self.precision_needed, self.interval.q)
		else:
			return NotImplemented
	def __gt__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return interval_epsilon(self.precision_needed, self.interval.q) < self.interval - other.interval
		elif isinstance(other, int):
			return interval_epsilon(self.precision_needed, self.interval.q) < self.interval - other
		else:
			return NotImplemented
	def __hash__(self):
		return hash((self.interval, self.degree, self.log_height))

#### Some special Algebraic approximations we know how to build.

def algebraic_approximation_from_integer(integer, degree):
	return Algebraic_Approximation(interval_from_string('%d.0' % integer), degree, log_height(integer))

def algebraic_approximation_from_string(string, degree, height):
	return Algebraic_Approximation(interval_from_string(string), degree, height)

def algebraic_approximation_from_symbolic(number, precision):
	if isinstance(number, algebraic_type):
		return algebraic_approximation_from_string(symbolic_approximate(number, precision), symbolic_degree(number), log(symbolic_height(number)))
	elif isinstance(number, int):
		return algebraic_approximation_from_string(str(number) + '.' + '0' * precision, 1, log_height(number))
	else:
		raise TypeError

if __name__ == '__main__':
	x = algebraic_approximation_from_string('1.4142135623730951', 2, 2)
	y = algebraic_approximation_from_string('1.41421356237', 2, 2)
	z = algebraic_approximation_from_string('1.000', 2, 2)
	
	print(z != y)
	print(x == y)
	print(x + y == x + x)
	print(x * x == 2)
	print(y * y == 2)
	print(y * y + x == 2 + x)
	print(x * x == y * y)
	print((x + x) > 0)
	print(hash(x))
