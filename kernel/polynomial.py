
from fractions import Fraction
from math import log10 as log

import Flipper

# This class represents an integral polynomial. In various places we will assume that it is 
# irreducible and / or monic. We use this as an efficient way of representing an algebraic number.
# See symboliccomputation.py for more information.
class Polynomial(object):
	def __init__(self, coefficients):
		self.coefficients = coefficients[:min(i for i in range(len(coefficients)+1) if not any(coefficients[i:]))]
		self.height = max(abs(x) for x in self.coefficients) if self.coefficients else 1
		self.log_height = log(self.height)
		self.degree = len(self.coefficients) - 1
		self._interval = Flipper.kernel.interval.Interval(-self.height * max(self.degree, 0) - 1, self.height * max(self.degree, 0) + 1, 0)
		self._sturm_chain = None
	
	def __iter__(self):
		return iter(self.coefficients)

	def copy(self):
		return Polynomial(list(self.coefficients))

	def copy_over_QQ(self):
		return Polynomial([Fraction(x, 1) for x in self])
	
	def __eq__(self, other):
		return self.coefficients == other.coefficients
	
	def __ne__(self, other):
		return self.coefficients != other.coefficients

	def __neg__(self):
		return Polynomial([-x for x in self])

	def __getitem__(self, item):
		return self.coefficients[item]
	
	def __repr__(self):
		return ' + '.join('%s x^%d' % (coefficient, index) for index, coefficient in enumerate(self))
	
	def __call__(self, other):
		return sum(coefficient * other**index for index, coefficient in enumerate(self))
	
	def __mod__(self, other):
		if isinstance(other, Polynomial):
			if other.degree < 0: 
				raise ZeroDivisionError
			
			N = self.copy_over_QQ()
			D = other.copy_over_QQ()
			dD = D.degree
			dN = N.degree
			while dN >= dD:
				mult = N[-1] / D[-1]
				d = [0]*(dN - dD) + [coeff*mult for coeff in D]
				N = Polynomial([coeffN - coeffd for coeffN, coeffd in zip(N, d)])
				dN = N.degree
			return N
		else:
			return NotImplemented
	
	def sign(self, numerator, denominator):
		s = sum(coefficient * numerator**index * denominator**(self.degree - index) for index, coefficient in enumerate(self))
		return 1 if s > 0 else -1 if s < 0 else 0
	
	def sturm_chain(self):
		if self._sturm_chain is None:
			f1 = self
			f2 = self.derivative()
			self._sturm_chain = [f1, f2]
			while self._sturm_chain[-1] != Polynomial([]):
				self._sturm_chain.append(-(self._sturm_chain[-2] % self._sturm_chain[-1]))
		
		return self._sturm_chain
	
	def num_roots(self, lower, upper, precision):
		chain = self.sturm_chain()
		lower_signs = [f.sign(lower, 10**precision) for f in chain]
		upper_signs = [f.sign(upper, 10**precision) for f in chain]
		lower_non_zero_signs = [x for x in lower_signs if x != 0]
		upper_non_zero_signs = [x for x in upper_signs if x != 0]
		lower_sign_changes = sum(1 if x * y < 0 else 0 for x, y in zip(lower_non_zero_signs, lower_non_zero_signs[1:]))
		upper_sign_changes = sum(1 if x * y < 0 else 0 for x, y in zip(upper_non_zero_signs, upper_non_zero_signs[1:]))
		return lower_sign_changes - upper_sign_changes
	
	def num_roots_in_interval(self, interval):
		return self.num_roots(interval.lower, interval.upper, interval.precision)
	
	def is_monic(self):
		return abs(self[-1]) == 1
	
	def derivative(self):
		return Polynomial([index * coefficient for index, coefficient in enumerate(self)][1:]) 
	
	def find_leading_root(self, accuracy):
		while self._interval.accuracy < accuracy:
			self._interval = [interval for interval in self._interval.subdivide() if self.num_roots_in_interval(interval) > 0][-1]
			print(self._interval.accuracy, accuracy)
		
		return self._interval
	
	def algebraic_approximate_leading_root(self, accuracy, power=1):
		# Returns an algebraic approximation of this polynomials leading root raised to the requested power
		# which is correct to at least accuracy decimal places.
		power_error = int(log(float(self.find_leading_root(2)))) + 1
		print(self._interval)
		print(power_error)
		working_accuracy = accuracy + power * power_error
		
		return Flipper.kernel.algebraicapproximation.AlgebraicApproximation(self.find_leading_root(working_accuracy), self.degree, self.log_height)**power
	
	def companion_matrix(self):
		# Assumes that this polynomial is monic.
		if not self.is_monic():
			raise Flipper.AssumptionError('Polynomial is not monic.')
		
		scale = -1 if self[-1] == 1 else 1
		return Flipper.Matrix([[(scale * self[i]) if j == self.degree-1 else 1 if j == i-1 else 0 for j in range(self.degree)] for i in range(self.degree)], self.degree)


if __name__ == '__main__':
	f = Polynomial([-1, -1, 0, 1, 1])
	print(f.sturm_chain())
	print(f.num_roots(-1000, 1000, 1))
	print(f.find_leading_root(10))


