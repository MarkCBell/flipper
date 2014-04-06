
from math import log10 as log

import Flipper

# This class represents an integral polynomial. In various places we will assume that it is 
# irreducible and / or monic. We use this as an efficient way of representing an algebraic number.
class Polynomial(object):
	''' This represents a polynomial in one variable. The most important method of this is 
	self.algebraic_approximate_leading_root() which returns an AlgebraicApproximation of the largest real
	root or raises an AssumptionError if there are none. '''
	def __init__(self, coefficients):
		if coefficients == []: coefficients = [0]
		self.coefficients = list(coefficients[:min(i for i in range(1, len(coefficients)+1) if not any(coefficients[i:]))])
		self.height = max(max(abs(x) for x in self.coefficients), 1)
		self.log_height = log(self.height)
		self.degree = len(self.coefficients) - (2 if self.is_zero() else 1)
		self.accuracy = 0
		self.root_range = max(self.degree, 1) * self.height  # All roots of self must be in +/- this amount.
		self.interval = Flipper.kernel.Interval(-self.root_range, self.root_range, 0)
		# self.interval = Flipper.kernel.Interval(0, r, 0)
	
	def copy(self):
		return Polynomial(self.coefficients)
	
	def __repr__(self):
		return ' + '.join('%d x^%d' % (coefficient, index) for index, coefficient in enumerate(self)) 
	def __bool__(self):
		return not self.is_zero()
	def __nonzero__(self):
		return self.__bool__()
	def __eq__(self, other):
		return (self - other).is_zero()
	def __ne__(self, other):
		return not (self - other).is_zero()
	def __neg__(self):
		return Polynomial([-x for x in self])
	
	def __iter__(self):
		return iter(self.coefficients)
	
	def __getitem__(self, item):
		return self.coefficients[item]
	
	def is_zero(self):
		return all(coefficient == 0 for coefficient in self)
	
	def __add__(self, other):
		if isinstance(other, Polynomial):
			m = max(self.degree, other.degree) + 1
			return Polynomial([a + b for a, b in zip(self.coefficients + [0] * m, other.coefficients + [0] * m)])
		else:
			return Polynomial([self[0] + other] + self.coefficients[1:])
	
	def __sub__(self, other):
		if isinstance(other, Polynomial):
			m = max(self.degree, other.degree) + 1
			return Polynomial([a - b for a, b in zip(self.coefficients + [0] * m, other.coefficients + [0] * m)])
		else:
			return Polynomial([self[0] - other] + self.coefficients[1:])
	
	def __mul__(self, other):
		if isinstance(other, Flipper.kernel.Integer_Type):
			return Polynomial([a * other for a in self])
	def __rmull__(self, other):
		return self * other
	
	def shift(self, power):
		if power > 0:
			return Polynomial([0] * power + self.coefficients)
		elif power == 0:
			return self
		elif power < 0:
			return Polynomial(self.coefficients[power:])
	
	def __call__(self, other):
		return sum(a * other**index for index, a in enumerate(self))
	
	def divmod(self, other):
		# Returns polynomials Q, R and an integer k such that k*self == Q * other + R.
		# If self and other are integral, by Gauss' lemma if other | self then k == 1.
		if isinstance(other, Polynomial):
			if other.is_zero(): 
				raise ZeroDivisionError
			
			Q = Polynomial([0])
			R = self.copy()
			k = 1
			while R.degree >= other.degree:
				# Now if other | self then Gauss' lemma says this condition will always fail.
				if R[-1] % other[-1] != 0: 
					R = R * other[-1]
					Q = Q * other[-1]
					k = k * other[-1]
				scale = R[-1] // other[-1]  
				Q = Q + (Polynomial([1]).shift(R.degree - other.degree) * scale)
				R = R - (other.shift(R.degree - other.degree) * scale)
			return Q, R, k
		else:
			return NotImplemented
	def __mod__(self, other):
		Q, R, k = self.divmod(other)
		return R
	def __div__(self, other):
		# Assumes that the division is perfect.
		Q, R, k = self.divmod(other)
		if not R.is_zero():
			raise ValueError('Polynomials do not divide.')
		return Q
	def __truediv__(self, other):
		return self.__div__(other)
	def __floordiv__(self, other):
		return self.__div__(other)
	
	def remove_factors(self, possible_factors):
		# Returns self with all factors in possible_factors removed.
		p = self.copy()
		if not self.is_zero():
			for q in possible_factors:
				Q, R = p, Polynomial([0]), 
				while R.is_zero():
					p = Q
					Q, R, k = p.divmod(q)
		return p
	def simplify(self):
		return self.remove_factors(cyclotomic_polynomials(self.degree))
	
	def signs_at_interval_endpoints(self, interval):
		s1 = sum(coefficient * interval.lower**index * 10**(interval.precision*(self.degree - index)) for index, coefficient in enumerate(self))
		s2 = sum(coefficient * interval.upper**index * 10**(interval.precision*(self.degree - index)) for index, coefficient in enumerate(self))
		return (-1 if s1 < 0 else 0 if s1 == 0 else +1), (-1 if s2 < 0 else 0 if s2 == 0 else +1)
	
	def sturm_chain(self):
		f1 = self
		f2 = self.derivative()
		sturm_chain = [f1, f2]
		while not sturm_chain[-1].is_zero():
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
		try:
			return [I for I in interval.subdivide() if self.num_roots(I, chain) > 0][-1]
		except IndexError:
			raise Flipper.AssumptionError('Polynomial has no real roots.')
	
	def is_monic(self):
		return abs(self[-1]) == 1
	
	def derivative(self):
		return Polynomial([a * index for index, a in enumerate(self)][1:])
	
	def NR_iterate(self, interval):
		# For why this works see: http://www.rz.uni-karlsruhe.de/~iam/html/language/cxsc/node12.html
		# Start by building a really tiny interval containing the midpoint of this one.
		J = interval.midpoint(10)
		K = J - self(J) / self.derivative()(interval)  # Apply the interval NR step. Could throw division by zero.
		L = K.change_denominator(K.accuracy * 2)  # Stop the precision from blowing up too much.
		return L.intersect(interval)
	
	def converge_iterate(self, interval, accuracy):
		chain = self.sturm_chain()
		while interval.accuracy <= accuracy:
			old_accuracy = interval.accuracy
			try:
				interval = self.NR_iterate(interval)
			except ZeroDivisionError:
				pass
			
			if interval.accuracy == old_accuracy:
				interval = self.subdivide_iterate(interval, chain)
		
		return interval
	
	def increase_accuracy(self, accuracy):
		# Eventually we will find the interval ourselves, however at the minute sage is much faster so
		# we'll just use that.
		if self.accuracy < accuracy:
			self.interval = self.converge_iterate(self.interval, accuracy)
			self.accuracy = self.interval.accuracy
	
	def algebraic_approximate_leading_root(self, accuracy):
		# Returns an algebraic approximation of this polynomials leading root raised to the requested power
		# which is correct to at least accuracy decimal places.
		accuracy = max(int(accuracy), int(log(self.degree)) + 2 * int(self.log_height) + 20, 1)  # !?! Check this.
		self.increase_accuracy(accuracy)
		AA = Flipper.kernel.AlgebraicApproximation(self.interval, self.degree, self.log_height).change_denominator(accuracy)
		assert(AA.interval.accuracy >= accuracy)  # Let's just make sure.
		return AA
	
	def companion_matrix(self):
		# Assumes that this polynomial is irreducible and monic.
		if not self.is_monic():
			raise Flipper.AssumptionError('Cannot construct companion matrix for non monic polynomial.')
		
		scale = -1 if self[-1] == 1 else 1
		return Flipper.kernel.Matrix([[(scale * self[i]) if j == self.degree-1 else 1 if j == i-1 else 0 for j in range(self.degree)] for i in range(self.degree)])


def cyclotomic_polynomials(n):
	# Returns a list containing the first n cyclotomic polynomials.
	
	small_cyclotomic_polynomials = [Polynomial([0]),
		Polynomial([-1, 1]), Polynomial([1, 1]), Polynomial([1, 1, 1]), Polynomial([1, 0, 1]),
		Polynomial([1, 1, 1, 1, 1]), Polynomial([1, -1, 1]), Polynomial([1, 1, 1, 1, 1, 1, 1]),
		Polynomial([1, 0, 0, 0, 1]), Polynomial([1, 0, 0, 1, 0, 0, 1]), Polynomial([1, -1, 1, -1, 1])
		]
	
	for i in range(11, n+1):
		p = Polynomial([-1] + [0]*(i-1) + [1])
		for j in range(1, i):
			if i % j == 0:
				p = p // small_cyclotomic_polynomials[j]
		small_cyclotomic_polynomials.append(p)
	
	return small_cyclotomic_polynomials[1:n+1]

