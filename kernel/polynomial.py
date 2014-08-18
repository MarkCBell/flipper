
from math import log10 as log

import flipper

# This class represents an integral polynomial. In various places we will assume that it is 
# irreducible and / or monic. We use this as an efficient way of representing an algebraic number.
class Polynomial(object):
	''' This represents a polynomial in one variable. The most important method of this is 
	self.algebraic_approximate_leading_root() which returns an AlgebraicApproximation of the largest real
	root or raises an AssumptionError if there are none. '''
	def __init__(self, coefficients):
		assert(all(isinstance(coefficient, flipper.Integer_Type) for coefficient in coefficients))  # Should this be Number_Type?
		
		if coefficients == []: coefficients = [0]
		self.coefficients = list(coefficients[:min(i for i in range(1, len(coefficients)+1) if not any(coefficients[i:]))])
		height = max(max(abs(x) for x in self.coefficients), 1)
		self.height = log(height)
		self.degree = len(self.coefficients) - (2 if self.is_zero() else 1)
		self.log_degree = log(max(self.degree, 1))
		self.accuracy = 0
		self._chain = None  # Stores the Sturm chain associated to this polynomial.
		
		root_range = max(self.degree, 1) * height  # All roots of self must be in +/- this amount.
		self.interval = flipper.kernel.Interval(-root_range, root_range, 0)
	
	def copy(self):
		return Polynomial(self.coefficients)
	
	def __repr__(self):
		return ' + '.join('%d*x^%d' % (coefficient, index) for index, coefficient in enumerate(self)) 
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
		return not any(self)
	
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
		if isinstance(other, flipper.Integer_Type):
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
		_, R, k = self.divmod(other)
		return R if k >= 0 else -R
	def __div__(self, other):
		# Assumes that the division is perfect.
		Q, R, k = self.divmod(other)
		if not R.is_zero():
			raise ValueError('Polynomials do not divide.')
		return Q if k >= 0 else -Q
	def __truediv__(self, other):
		return self.__div__(other)
	def __floordiv__(self, other):
		return self.__div__(other)
	def rescale(self):
		return Polynomial(flipper.kernel.matrix.rescale(self))
	
	def signs_at_interval_endpoints(self, interval):
		s1 = sum(coefficient * interval.lower**index * 10**(interval.precision*(self.degree - index)) for index, coefficient in enumerate(self))
		s2 = sum(coefficient * interval.upper**index * 10**(interval.precision*(self.degree - index)) for index, coefficient in enumerate(self))
		return (-1 if s1 < 0 else 0 if s1 == 0 else +1), (-1 if s2 < 0 else 0 if s2 == 0 else +1)
	
	def sturm_chain(self):
		if self._chain is None:
			f1 = self
			f2 = self.derivative()
			self._chain = [f1, f2]
			while self._chain[-1]:
				self._chain.append(-(self._chain[-2] % self._chain[-1]).rescale())
		
		return self._chain
	
	def num_roots(self, interval):
		''' Returns the number of roots of self in the interior of the given interval. '''
		chain = self.sturm_chain()
		
		lower_signs, upper_signs = zip(*[f.signs_at_interval_endpoints(interval) for f in chain])
		lower_non_zero_signs = [x for x in lower_signs if x != 0]
		upper_non_zero_signs = [x for x in upper_signs if x != 0]
		lower_sign_changes = sum(1 for x, y in zip(lower_non_zero_signs, lower_non_zero_signs[1:]) if x * y < 0)
		upper_sign_changes = sum(1 for x, y in zip(upper_non_zero_signs, upper_non_zero_signs[1:]) if x * y < 0)
		return lower_sign_changes - upper_sign_changes
	
	def subdivide_iterate(self, interval):
		try:
			return [I for I in interval.subdivide() if self.num_roots(I) > 0][-1]
		except IndexError:
			raise flipper.AssumptionError('Polynomial has no real roots.')
	
	def is_monic(self):
		return abs(self[-1]) == 1
	
	def derivative(self):
		return Polynomial([a * index for index, a in enumerate(self)][1:])
	
	def NR_iterate(self, interval):
		# For why this works see: http://www.rz.uni-karlsruhe.de/~iam/html/language/cxsc/node12.html
		# Start by building a really tiny interval containing the midpoint of this one.
		J = interval.midpoint(10)
		K = J - self(J) / self.derivative()(interval)  # Apply the interval NR step. Could throw a ZeroDivisionError.
		L = K.change_denominator(2 * K.accuracy)  # Stop the precision from blowing up too much.
		return L.intersect(interval)  # This can throw a ValueError if the intersection is empty.
	
	def converge_iterate(self, interval, accuracy):
		while interval.accuracy <= accuracy:
			old_accuracy = interval.accuracy
			try:
				interval = self.NR_iterate(interval)
			except (ZeroDivisionError, ValueError):
				pass
			
			# This is guranteed to give us at lease 1 more d.p. of accuracy.
			if interval.accuracy == old_accuracy:
				interval = self.subdivide_iterate(interval)
		
		return interval.simplify()
	
	def increase_accuracy(self, accuracy):
		# You cannot set the accuracy to less than this:
		accuracy = max(int(accuracy), int(log(max(self.degree, 1))) + 2 * int(self.height) + 20, 1)  # !?! Check this.
		if self.accuracy < accuracy:
			self.interval = self.converge_iterate(self.interval, accuracy)
			self.accuracy = self.interval.accuracy
			assert(self.accuracy >= accuracy)  # Let's just make sure.
	
	def algebraic_approximate_leading_root(self, accuracy):  # !! Eventually remove.
		# Returns an algebraic approximation of this polynomials leading root which has at least
		# the requested accuracy.
		self.increase_accuracy(accuracy)
		return flipper.kernel.AlgebraicApproximation(self.interval, self.log_degree, self.height)
	
	def companion_matrix(self):  # !! Eventually remove.
		# Assumes that this polynomial is irreducible and monic.
		if not self.is_monic():
			raise flipper.AssumptionError('Cannot construct companion matrix for non monic polynomial.')
		
		scale = -1 if self[-1] == 1 else 1
		return flipper.kernel.Matrix([[(scale * self[i]) if j == self.degree-1 else 1 if j == i-1 else 0 for j in range(self.degree)] for i in range(self.degree)])

class PolynomialRoot(object):
	def __init__(self, polynomial, interval):
		# Assumes that polynomial has exactly one root in interval.
		assert(isinstance(polynomial, flipper.kernel.Polynomial))
		assert(isinstance(interval, flipper.kernel.Interval))
		
		self.polynomial = polynomial
		self.interval = interval
		self.degree = self.polynomial.degree
		self.log_degree = self.polynomial.log_degree
		self.height = self.polynomial.height + 2 * self.log_degree
		
		if self.polynomial.num_roots(self.interval) != 1:
			raise flipper.AssumptionError('Interval does not determine unique root of polynomial.')
	
	def __repr__(self):
		return 'Root of %s (~%s)' % (self.polynomial, self.interval)
	
	def interval_approximation(self, accuracy=0):
		''' Returns an interval containing this number correct to the requested accuracy. '''
		accuracy_required = max(accuracy, 0)
		if self.interval.accuracy < accuracy_required:
			self.interval = self.polynomial.converge_iterate(self.interval, accuracy_required)
			assert(self.interval.accuracy >= accuracy_required)
			self.interval = self.interval.change_accuracy(accuracy_required)
		
		return self.interval
	
	def algebraic_approximation(self, accuracy=0):
		accuracy_needed = int(self.height) + int(self.log_degree) + 2  # This ensures the AlgebraicApproximation is well defined.
		accuracy_required = max(accuracy, accuracy_needed)
		
		return flipper.kernel.AlgebraicApproximation(self.interval_approximation(accuracy_required), self.log_degree, self.height)
	
	def as_algebraic_monomial(self):
		return flipper.kernel.AlgebraicMonomial([self])
	
	def as_algebraic_number(self):
		return flipper.kernel.AlgebraicNumber({self.as_algebraic_monomial(): 1}, height=self.height)

def polynomial_root_from_info(coefficients, strn):
	interval_from_string = flipper.kernel.interval.interval_from_string
	return flipper.kernel.PolynomialRoot(flipper.kernel.Polynomial(coefficients), interval_from_string(strn))

