
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
		self.algebraic_approximation = self.degree * self.height
		self.accuracy = 0
		r = max(self.degree, 1) * self.height
		# self.interval = Flipper.kernel.Interval(-r, r, 0)
		self.interval = Flipper.kernel.Interval(0, r, 0)
	
	def copy(self):
		return Polynomial(self.coefficients)
	
	def __str__(self):
		' + '.join('%d x^%d' % (coefficient, index) for index, coefficient in enumerate(self)) 
	def __eq__(self, other):
		return self.coefficients == other.coefficients
	def __ne__(self, other):
		return self.coefficients != other.coefficients
	def __neg__(self):
		return Polynomial([-x for x in self])
	
	def __iter__(self):
		return iter(self.coefficients)
	
	def __getitem__(self, item):
		return self.coefficients[item]
	
	def __add__(self, other):
		if isinstance(other, Polynomial):
			m = max(self.degree, other.degree)
			return Polynomial([a + b for a, b in zip(self.coefficients + [0] * m, other.coefficients + [0] * m)])
	
	def __sub__(self, other):
		if isinstance(other, Polynomial):
			m = max(self.degree, other.degree)
			return Polynomial([a - b for a, b in zip(self.coefficients + [0] * m, other.coefficients + [0] * m)])
	
	def __mul__(self, other):
		if isinstance(other, Flipper.kernel.Integer_Type):
			return Polynomial([a * other for a in self])
	
	def shift(self, power):
		return Polynomial([0] * power + self.coefficients)
	
	def __call__(self, other):
		return sum(a * other**index for index, a in enumerate(self))
	def __mod__(self, other):
		if isinstance(other, Polynomial):
			if other.degree < 0: 
				raise ZeroDivisionError
			
			N = self.copy()
			D = other.copy()
			while N.degree >= D.degree:
				# N = D[-1] * N - N[-1] * D.shift(N.degree - D.degree)
				sign = -1 if D[-1] < 0 else 1  # We can never have the leading coefficient 0.
				N = N * sign * D[-1] - D.shift(N.degree - D.degree) * sign * N[-1]
				# N = Polynomial([coeffN * D[-1] - coeffd * N[-1] for coeffN, coeffd in zip(N, [0]*(N.degree - D.degree) + D.coefficients)])
			return N
		else:
			return NotImplemented
	
	def _call_fraction(self, numerator, denominator):
		return sum(coefficient * numerator**index * denominator**(self.degree - index) for index, coefficient in enumerate(self)), denominator**self.degree
	
	def signs_at_interval_endpoints(self, interval):
		s1 = sum(coefficient * interval.lower**index * 10**(interval.precision*(self.degree - index)) for index, coefficient in enumerate(self))
		s2 = sum(coefficient * interval.upper**index * 10**(interval.precision*(self.degree - index)) for index, coefficient in enumerate(self))
		return (-1 if s1 < 0 else 0 if s1 == 0 else +1), (-1 if s2 < 0 else 0 if s2 == 0 else +1)
	
	def sturm_chain(self):
		f1 = self
		f2 = self.derivative()
		sturm_chain = [f1, f2]
		while sturm_chain[-1] != Polynomial([]):
			sturm_chain.append(-(sturm_chain[-2] % sturm_chain[-1]))
		
		return sturm_chain
	
	def num_roots(self, interval, chain=None):
		if chain is None: chain = self.sturm_chain()
		lower_signs, upper_signs = zip(*[f.signs_at_interval_endpoints(interval) for f in chain])
		lower_non_zero_signs = [x for x in lower_signs if x != 0]
		upper_non_zero_signs = [x for x in upper_signs if x != 0]
		lower_sign_changes = sum(1 if x * y < 0 else 0 for x, y in zip(lower_non_zero_signs, lower_non_zero_signs[1:]))
		upper_sign_changes = sum(1 if x * y < 0 else 0 for x, y in zip(upper_non_zero_signs, upper_non_zero_signs[1:]))
		return lower_sign_changes - upper_sign_changes
	
	def subdivide_iterate(self, interval, chain=None):
		if chain is None: chain = self.sturm_chain()
		return [I for I in interval.subdivide() if self.num_roots(I, chain) > 0][-1]
	
	def is_monic(self):
		return abs(self[-1]) == 1
	
	def derivative(self):
		return Polynomial([a * index for index, a in enumerate(self)][1:])
	
	def NR_iterate(self, interval):
		# For why this works see: http://www.rz.uni-karlsruhe.de/~iam/html/language/cxsc/node12.html
		m = (interval.lower + interval.upper) // 2
		k = 10
		m2 = m * 10**k
		J = Flipper.kernel.Interval(m2 - 1, m2 + 1, interval.precision + k)
		K = J - self(J) / self.derivative()(interval)
		L = K.change_denominator(K.accuracy * 2)
		return L.intersect(interval)
	
	def converge_iterate(self, interval, accuracy):
		chain = self.sturm_chain()
		while interval.accuracy < accuracy:
			try:
				interval = self.NR_iterate(interval)
			except:
				interval = self.subdivide_iterate(interval, chain)
		
		return interval
	
	def increase_accuracy(self, accuracy):
		# Eventually we will find the interval ourselves, however at the minute sage is much faster so
		# we'll just use that.
		if self.accuracy < accuracy:
			#self.algebraic_approximation = Flipper.kernel.symboliccomputation.algebraic_approximation_largest_root(self, accuracy)
			#self.accuracy = accuracy
			self.interval = self.converge_iterate(self.interval, accuracy)
			self.algebraic_approximation = Flipper.kernel.AlgebraicApproximation(self.interval, self.degree, self.log_height)
			self.accuracy = self.interval.accuracy
	
	def algebraic_approximate_leading_root(self, accuracy, power=1):
		# Returns an algebraic approximation of this polynomials leading root raised to the requested power
		# which is correct to at least accuracy decimal places.
		min_accuracy = int(log(self.degree)) + int(self.log_height) + 2 
		accuracy_needed = max(accuracy, min_accuracy)
		accuracy_requested = accuracy_needed + power * int(log(float(self.algebraic_approximation)) + 1)
		
		self.increase_accuracy(accuracy_requested)
		AA = self.algebraic_approximation**power
		assert(AA.interval.accuracy >= accuracy)  # Let's just make sure.
		return AA
	
	def companion_matrix(self):
		# Assumes that this polynomial is irreducible and monic.
		if not self.is_monic():
			raise Flipper.AssumptionError('Cannot construct companion matrix for non monic polynomial.')
		
		scale = -1 if self[-1] == 1 else 1
		return Flipper.kernel.Matrix([[(scale * self[i]) if j == self.degree-1 else 1 if j == i-1 else 0 for j in range(self.degree)] for i in range(self.degree)], self.degree)
