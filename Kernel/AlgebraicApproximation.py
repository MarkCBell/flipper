
from math import log10 as log

from Flipper.Kernel.Decimal import decimal_from_string
from Flipper.Kernel.Error import AssumptionError, ApproximationError

class Algebraic_Approximation:
	def __init__(self, decimal, degree, height):
		self.decimal = decimal
		self.degree = degree
		self.height = height
		self.precision_needed = int(log(self.degree) + log(self.height)) + 1
	def good(self):
		return self.decimal.q >= self.precision_needed
	def __repr__(self):
		return repr(self.decimal)
	# These all assume that other lies in the same field extension of QQ.
	def __add__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.decimal + other.decimal, self.degree, self.height + other.height + 1)
		elif isinstance(other, int):
			return Algebraic_Approximation(self.decimal + other, self.degree, self.height + abs(other) + 1)
		else:
			return NotImplemented
	def __sub__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.decimal - other.decimal, self.degree, self.height + other.height + 1)
		elif isinstance(other, int):
			return Algebraic_Approximation(self.decimal - other, self.degree, self.height + abs(other) + 1)
		else:
			return NotImplemented
	def __mul__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return Algebraic_Approximation(self.decimal * other.decimal, self.degree, self.height + other.height)
		elif isinstance(other, int):
			return Algebraic_Approximation(self.decimal * other, self.degree, self.height + abs(other))
		else:
			return NotImplemented
	# These may raise ApproximationError if not enough accuracy is present.
	def sign(self):
		return self.decimal.demote(self.precision_needed).sign()
	def __lt__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return self.decimal.demote(self.precision_needed) < other.decimal.demote(self.precision_needed)
		elif isinstance(other, int):
			return self.decimal.demote(self.precision_needed) < other
		else:
			return NotImplemented
	def __eq__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return self.decimal.demote(self.precision_needed) == other.decimal.demote(self.precision_needed)
		elif isinstance(other, int):
			return self.decimal.demote(self.precision_needed) == other
		else:
			return NotImplemented
	def __gt__(self, other):
		if isinstance(other, Algebraic_Approximation):
			return self.decimal.demote(self.precision_needed) > other.decimal.demote(self.precision_needed)
		elif isinstance(other, int):
			return self.decimal.demote(self.precision_needed) > other
		else:
			return NotImplemented

def algebraic_approximation_from_string(string, degree, height):
	return Algebraic_Approximation(decimal_from_string(string), degree, height)

if __name__ == '__main__':
	x = algebraic_approximation_from_string('1.4142135623730951', 2, 2)
	y = algebraic_approximation_from_string('1.41421356237', 2, 2)
	print(x == y)
	print(x + x)
	print(x + y == x + x)
	print(x * x == 2)
	print((x + x) > 0)
	