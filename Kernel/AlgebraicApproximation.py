
# A library for manipulating real algebraic numbers via decimal approximations.

from math import log10 as log

from Flipper.Kernel.Decimal import Decimal, decimal_from_string, decimal_epsilon
from Flipper.Kernel.Error import AssumptionError, ApproximationError
from Flipper.Kernel.SymbolicComputation import symbolic_approximate, symbolic_degree, symbolic_height, algebraic_type

class Algebraic_Approximation:
	def __init__(self, decimal, degree, height):
		self.decimal = decimal
		self.degree = degree
		self.height = height
		self.precision_needed = int(log(self.degree) + log(self.height)) + 1
		# An algebraic approximation is good if it is known to more decimal places
		# than its precision needed. That is if self.decimal.q >= self.precision_needed.
		if self.decimal.q < self.precision_needed:
			raise ApproximationError('%s does not define a unique algebraic number with degree at most %d and height at most %d.' % (self.decimal, self.degree, self.height))
	def __repr__(self):
		# return repr((self.decimal, self.degree, self.height))
		return repr((self.decimal.p, self.decimal.q, self.degree, self.height))
	def log(self):
		return self.decimal.log()
	def __neg__(self):
		return Algebraic_Approximation(-self.decimal, self.degree, self.height)
	# These all assume that other lies in the same field extension of QQ.
	def __add__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.decimal + other.decimal, self.degree, self.height + other.height + 1)
		elif isinstance(other, int):
			return Algebraic_Approximation(self.decimal + other, self.degree, self.height + abs(other) + 1)
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.decimal - other.decimal, self.degree, self.height + other.height + 1)
		elif isinstance(other, int):
			return Algebraic_Approximation(self.decimal - other, self.degree, self.height + abs(other) + 1)
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.decimal * other.decimal, self.degree, self.height + other.height)
		elif isinstance(other, int):
			return Algebraic_Approximation(self.decimal * other, self.degree, self.height + abs(other))
		else:
			return NotImplemented
	def __rmult__(self, other):
		return self * other
	def __div__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return NotImplemented
		elif isinstance(other, int):
			return Algebraic_Approximation(self.decimal // other, self.degree, self.height + abs(other))
		else:
			return NotImplemented
	# These may raise ApproximationError if not enough accuracy is present.
	def __lt__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return self.decimal - other.decimal < decimal_epsilon(self.precision_needed, self.decimal.q)
		elif isinstance(other, int):
			return self.decimal - other < decimal_epsilon(self.precision_needed, self.decimal.q)
		else:
			return NotImplemented
	def __eq__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return -decimal_epsilon(self.precision_needed, self.decimal.q) < self.decimal - other.decimal < decimal_epsilon(self.precision_needed, self.decimal.q)
		elif isinstance(other, int):
			return -decimal_epsilon(self.precision_needed, self.decimal.q) < self.decimal - other < decimal_epsilon(self.precision_needed, self.decimal.q)
		else:
			return NotImplemented
	def __gt__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return decimal_epsilon(self.precision_needed, self.decimal.q) < self.decimal - other.decimal
		elif isinstance(other, int):
			return decimal_epsilon(self.precision_needed, self.decimal.q) < self.decimal - other
		else:
			return NotImplemented

#### Some special Algebraic approximations we know how to build.

def algebraic_approximation_from_string(string, degree, height):
	return Algebraic_Approximation(decimal_from_string(string), degree, height)

def algebraic_approximation_from_algebraic(number, precision):
	if isinstance(number, algebraic_type):
		return algebraic_approximation_from_string(symbolic_approximate(number, precision), symbolic_degree(number), symbolic_height(number))
	elif isinstance(number, int):
		return algebraic_approximation_from_string(str(number) + '.' + '0' * precision, 1, abs(number))
	else:
		raise TypeError

if __name__ == '__main__':
	x = algebraic_approximation_from_string('1.4142135623730951', 2, 2)
	y = algebraic_approximation_from_string('1.41421356237', 2, 2)
	z = algebraic_approximation_from_string('1.000', 2, 2)
	
	print(z != y)
	print(x == y)
	print(x + y == x + x)
	print(y * y == 2)
	print(y * y + x == 2 + x)
	print(x * x == y * y)
	print((x + x) > 0)
	print(x.log())
