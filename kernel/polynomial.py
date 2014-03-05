
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
		self.algebraic_approximations = [None] * self.degree
		self.accuracy = 0
		self.increase_accuracy(5)
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
	
	def _call_fraction(self, numerator, denominator):
		return sum(coefficient * numerator**index * denominator**(self.degree - index) for index, coefficient in enumerate(self)), denominator**self.degree
	
	def _call_interval(self, interval):
		if self.derivative().num_roots_in_interval(interval) > 0:
			raise ValueError('Derivative is zero inside of interval.')
		
		lower, precision = self._call_fraction(interval.lower, interval.precison)
		upper, precision = self._call_fraction(interval.upper, interval.precison)
		return Flipper.kernel.interval.Interval(lower, upper, precision)
	
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
		# Returns the sign of self(numerator / denominator).
		s = self._call_fraction(numerator, denominator)
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
	
	def definitely_contains_root(self, interval):
		return self.sign(interval.lower, 10**interval.precision) != self.sign(interval.upper, 10**interval.precision)
	
	def descartes_signs(self):
		non_zero_signs = [x for x in self if x != 0]
		return sum(1 if x * y < 0 else 0 for x, y in zip(non_zero_signs, non_zero_signs[1:]))
	
	def is_monic(self):
		return abs(self[-1]) == 1
	
	def derivative(self):
		return Polynomial([index * coefficient for index, coefficient in enumerate(self)][1:]) 
	
	def increase_accuracy(self, accuracy):
		# Eventually we will find the interval ourselves, however at the minute sage is much faster so
		# we'll just use that.
		if self.accuracy < accuracy:
			self.algebraic_approximations = [Flipper.kernel.symboliccomputation.algebraic_approximation_largest_root(self, accuracy, power) for power in range(self.degree)]
			self.accuracy = accuracy
		
		return
		
		# Alternatively ...
		# Subdivide using repeated subdivision until we have a unique root.
		while self.num_roots_in_interval(self._interval) > 1:
			self._interval = [interval for interval in self._interval.subdivide() if self.num_roots_in_interval(interval) > 0][-1]
		
		# Subdivide using repeated subdivision.
		# Eventually we should use NR-iteration here to get quadratic convergence.
		while self._interval.accuracy < accuracy:
			self._interval = [interval for interval in self._interval.subdivide() if self.definitely_contains_root(interval)][-1]
		
		return self._interval
	
	def algebraic_approximate_leading_root(self, accuracy, power=1):
		# Returns an algebraic approximation of this polynomials leading root raised to the requested power
		# which is correct to at least accuracy decimal places.
		self.increase_accuracy(accuracy)
		return self.algebraic_approximations[power]
	
	def companion_matrix(self):
		# Assumes that this polynomial is monic.
		if not self.is_monic():
			raise Flipper.AssumptionError('Polynomial is not monic.')
		
		scale = -1 if self[-1] == 1 else 1
		return Flipper.Matrix([[(scale * self[i]) if j == self.degree-1 else 1 if j == i-1 else 0 for j in range(self.degree)] for i in range(self.degree)], self.degree)
