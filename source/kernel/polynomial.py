
''' A module for representing and manipulating polynomials and their roots.

Provides two classes: Polynomial and PolynomialRoot.

There is also a helper function: create_polynomial_root. '''

import flipper

from math import log10 as log

class Polynomial(object):
	''' This represents an integral polynomial in one variable.
	
	It is specified by a list of coefficients. It is capable of determining
	the number of roots it has in a given interval by using a Sturm chain. '''
	def __init__(self, coefficients):
		assert(isinstance(coefficients, (list, tuple)))
		assert(all(isinstance(coefficient, flipper.IntegerType) for coefficient in coefficients))
		
		# It is easier if the zero polynomial has coefficients [0] instead of [].
		# At various points we will want the min of the coefficients etc.
		if not coefficients: coefficients = [0]
		self.coefficients = list(coefficients[:min(i for i in range(1, len(coefficients)+1) if not any(coefficients[i:]))])
		self.height = log(max(max(abs(x) for x in self.coefficients), 1))
		self.degree = len(self.coefficients) - (2 if self.is_zero() else 1)  # The zero polynomial has degree -1.
		self.log_degree = log(max(self.degree, 1))
		self._chain = None  # Stores the Sturm chain associated to this polynomial. See self.sturm_chain().
	
	def copy(self):
		''' Return a copy of this polynomial. '''
		
		return Polynomial(self.coefficients)
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return ' + '.join('%d*x^%d' % (coefficient, index) for index, coefficient in enumerate(self))
	def __bool__(self):
		return not self.is_zero()
	def __nonzero__(self):  # For Python2.
		return self.__bool__()
	def __eq__(self, other):
		return (self - other).is_zero()
	def __ne__(self, other):
		return not (self == other)
	def __neg__(self):
		return Polynomial([-x for x in self])
	
	def __iter__(self):
		return iter(self.coefficients)
	def __len__(self):
		return len(self.coefficients)
	
	def __getitem__(self, item):
		return self.coefficients[item]
	
	def is_zero(self):
		''' Return if this is the zero polynomial. '''
		
		return not any(self)
	
	def __add__(self, other):
		if isinstance(other, Polynomial):
			# Remember to pad the coefficients to ensure none are missed.
			return Polynomial([a + b for a, b in zip(self.coefficients + [0] * len(other), other.coefficients + [0] * len(self))])
		elif isinstance(other, flipper.IntegerType):
			return Polynomial([self[0] + other] + self.coefficients[1:])
		else:
			return NotImplemented
	def __sub__(self, other):
		if isinstance(other, Polynomial):
			# Remember to pad the coefficients to ensure none are missed.
			return Polynomial([a - b for a, b in zip(self.coefficients + [0] * len(other), other.coefficients + [0] * len(self))])
		elif isinstance(other, flipper.IntegerType):
			return Polynomial([self[0] - other] + self.coefficients[1:])
		else:
			return NotImplemented
	def __mul__(self, other):
		if isinstance(other, flipper.IntegerType):
			return Polynomial([a * other for a in self])
		else:
			return NotImplemented
	def __rmul__(self, other):
		return self * other
	
	def shift(self, power):
		''' Return this polynomial multiplied by x^power.
		
		Power must be an integer >= 0. '''
		
		assert(isinstance(power, flipper.IntegerType))
		assert(power >= 0)
		
		return Polynomial([0] * power + self.coefficients)
	
	def __call__(self, other):
		# It is significantly more efficient to compute self(other) as:
		#   a_0 + x*(a_1 + x*( ... + x*(a_n + x * 0) ... ) ).
		
		total = 0
		for coefficient in reversed(list(self)):
			total = (other * total) + coefficient
		return total
	def __divmod__(self, other):
		''' Return the quotient and remainder (and rescaling) of this polynomial by other.
		
		That is, returns polynomials quotient, remainder and an integer scale such that:
			scale * self == quotient * other + remainder, and
			deg(remainder) < deg(other)
		If self and other are integral, by Gauss' lemma if other | self then scale == +/-1. '''
		
		if isinstance(other, Polynomial):
			if other.is_zero():
				raise ZeroDivisionError
			
			quotient = Polynomial([0])
			remainder = self.copy()
			scale = 1
			while remainder.degree >= other.degree:
				# Now if other | self then Gauss' lemma says this condition will always fail.
				if remainder[-1] % other[-1] != 0:
					remainder = remainder * other[-1]
					quotient = quotient * other[-1]
					scale = scale * other[-1]
				rescale = remainder[-1] // other[-1]
				quotient = quotient + (Polynomial([1]).shift(remainder.degree - other.degree) * rescale)
				remainder = remainder - (other.shift(remainder.degree - other.degree) * rescale)
				common_factor = abs(flipper.kernel.gcd(list(quotient) + list(remainder) + [scale]))
				if common_factor != 1:
					scale = scale // common_factor
					quotient = Polynomial([x // common_factor for x in quotient])
					remainder = Polynomial([x // common_factor for x in remainder])
			
			if scale >= 0:
				return quotient, remainder
			else:
				return -quotient, -remainder
		else:
			return NotImplemented
	def __mod__(self, other):
		_, remainder = divmod(self, other)
		return remainder
	def __div__(self, other):
		quotient, remainder = divmod(self, other)
		if not remainder.is_zero():  # Division isn't perfect.
			raise ValueError('Polynomials do not divide.')
		return quotient
	def __truediv__(self, other):
		return self.__div__(other)
	def __floordiv__(self, other):
		return self.__div__(other)
	def divides(self, other):
		''' Return if self divides other. '''
		
		_, remainder = divmod(self, other)
		return remainder.is_zero()
	
	def rescale(self):
		''' Return a possibly simpler polynomial with the same roots. '''
		
		c = max(abs(flipper.kernel.gcd(self)), 1)  # Avoid a possible division by 0.
		return Polynomial([coefficient // c for coefficient in self])
	
	def square_free(self):
		''' Return the polynomial with the same roots but each with multiplicity one. '''
		
		return self // flipper.kernel.gcd([self, self.derivative()])
	
	def signs_at_interval_endpoints(self, interval):
		''' Return the signs of this polynomial at the endpoints of the given polynomial. '''
		
		lower, upper, precision = interval.lower, interval.upper, interval.precision
		lower_sign = sum(coefficient * lower**index * 10**(precision*(self.degree - index)) for index, coefficient in enumerate(self))
		upper_sign = sum(coefficient * upper**index * 10**(precision*(self.degree - index)) for index, coefficient in enumerate(self))
		return (-1 if lower_sign < 0 else 0 if lower_sign == 0 else +1), (-1 if upper_sign < 0 else 0 if upper_sign == 0 else +1)
	
	def sturm_chain(self):
		''' Return the Sturm chain associated to this polynomial.
		
		This is a finite list of polynomials p_0, p_1, ..., p_m of decreasing degree
		with these following properties:
			p_0 = p is square free,
			if p(x) = 0 then sign(p_1(x)) = sign(p'(x)),
			if p_i(x) = 0 then sign(p_{i-1}(x)) = -sign(p_{i+1}(x)), and
			p_m has constant sign.
		We use Sturm's method for constructing such a chain based off of the Euclidean algorithm, see:
			http://en.wikipedia.org/wiki/Sturm's_theorem '''
		
		if self._chain is None:
			square_free = self.square_free()
			self._chain = [square_free, square_free.derivative()]
			while self._chain[-1]:
				self._chain.append(-(self._chain[-2] % self._chain[-1]).rescale())
		
		return self._chain
	
	def num_roots(self, interval):
		''' Return the number of primitive roots of self in (a, b] where [a, b] is the given interval.
		
		For a description of this variant of the algorithm and an explanation why this works see:
			http://en.wikipedia.org/wiki/Sturm's_theorem '''
		
		chain = self.sturm_chain()
		lower_signs, upper_signs = zip(*[f.signs_at_interval_endpoints(interval) for f in chain])
		lower_non_zero_signs = [x for x in lower_signs if x != 0]
		upper_non_zero_signs = [x for x in upper_signs if x != 0]
		lower_sign_changes = sum(1 for x, y in zip(lower_non_zero_signs, lower_non_zero_signs[1:]) if x * y < 0)
		upper_sign_changes = sum(1 for x, y in zip(upper_non_zero_signs, upper_non_zero_signs[1:]) if x * y < 0)
		return lower_sign_changes - upper_sign_changes
	
	def roots(self):
		''' Return a list of (real) PolynomialRoots, one for each root of self.
		
		Repeated roots are not returned multiple times. '''
		
		k = int(self.height + self.log_degree) + 2
		# Roots of self are guaranteed to be separated by at least 10^-k and lie in:
		interval = flipper.kernel.Interval(-10**k, 10**k, 0)
		
		results = []
		to_check = [interval]
		for _ in range(2*k):  # After this many steps all roots must have separated.
			new_to_check = []
			for interval in to_check:
				num_roots = self.num_roots(interval)
				if num_roots > 1:
					new_to_check.extend(interval.subdivide())
				elif num_roots == 1:
					results.append(PolynomialRoot(self, interval))
				else:  # num_roots == 0.
					pass  # So discard this interval.
			to_check = new_to_check
		
		return results
	
	def is_monic(self):
		''' Return if this polynomial is monic or not. '''
		
		return abs(self[-1]) == 1
	
	def derivative(self):
		''' Return the derivative of this polynomial. '''
		
		return Polynomial([a * index for index, a in enumerate(self)][1:])
	
	def companion_matrix(self):
		''' Return the companion matrix of this polynomial.
		
		This is the matrix:
		(  0 |           )
		(----+ -V[:-1]^T )
		( Id |           )
		where V is the vector of coefficients of this polynomial.
		
		Assumes (and checks) that this polynomial is monic. '''
		
		if not self.is_monic():
			raise flipper.AssumptionError('Cannot construct companion matrix for non monic polynomial.')
		
		scale = -1 if self[-1] == 1 else 1
		return flipper.kernel.Matrix([[(scale * self[i]) if j == self.degree-1 else 1 if j == i-1 else 0 for j in range(self.degree)] for i in range(self.degree)])

class PolynomialRoot(object):
	''' This represents a single root of a polynomial.
	
	It is specified by a Polynomial and an Interval.
	
	The interval must contain exactly one root of the polynomial. If
	not an ApproximationError will be raised. '''
	def __init__(self, polynomial, interval):
		assert(isinstance(polynomial, flipper.kernel.Polynomial))
		assert(isinstance(interval, flipper.kernel.Interval))
		
		self.polynomial = polynomial
		self.interval = interval
		self.degree = self.polynomial.degree
		self.log_degree = self.polynomial.log_degree
		self.height = self.polynomial.height + 2 * self.log_degree
		
		# Check that self.polynomial has exactly one root in self.interval.
		if self.polynomial.num_roots(self.interval) != 1:
			raise flipper.ApproximationError('Interval contains %d roots, not one.' % self.polynomial.num_roots(self.interval))
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return 'Root of %s (~%s)' % (self.polynomial, self.interval)
	def __float__(self):
		return float(self.algebraic_approximation())
	
	def __eq__(self, other):
		assert(isinstance(other, PolynomialRoot))
		
		accuracy_needed = int(self.height + self.log_degree + other.height + other.log_degree) + 5
		return self.algebraic_approximation(accuracy_needed) == other.algebraic_approximation(accuracy_needed)
	def __ne__(self, other):
		return not (self == other)
	
	def subdivide_iterate(self):
		''' Return a subinterval of self.interval which contains a root of self.polynomial.
		
		We construct this new interval by looking for the interval from self.interval.subdivide()
		which contains a root of self.polynomial. As self.interval contains a unique root
		of self.polynomial the subinterval is also unique. '''
		
		roots = [I for I in self.interval.subdivide() if self.polynomial.num_roots(I) > 0]
		assert(len(roots) == 1)  # What if a root occurs at the end of an interval? It would have to be rational.
		return roots[0]
	
	def newton_raphson_iterate(self):
		''' Return a subinterval of self.interval which contains a root of self.polynomial.
		
		We construct this new interval by applying one step of the (interval) Newton-Raphson
		algorithm to self.interval. This may throw a ZeroDivisionError or ValueError if
		self.interval was not small enough to begin with.
		
		For a description of this variant of the algorithm and an explanation why this works see:
			http://www.rz.uni-karlsruhe.de/~iam/html/language/cxsc/node12.html '''
		
		I = self.interval.midpoint(10)  # Start by building a really tiny interval containing the midpoint of this one.
		J = I - self.polynomial(I) / self.polynomial.derivative()(self.interval)  # Apply the interval NR step. This can throw a ZeroDivisionError.
		K = J.change_denominator(2 * J.accuracy)  # Stop the precision from blowing up too much.
		return K.intersect(self.interval)  # This can throw a ValueError if the intersection is empty.
	
	def converge_iterate(self, accuracy):
		''' Replace self.interval with a subinterval of at least the requested accuracy.
		
		Repeatedly applies self.newton_raphson_iterate to obtain a more accurate subinterval. This should
		converge quadratically so few iterations are needed, if this fails then use self.subdivide_iterate
		before trying again. '''
		
		while self.interval.accuracy <= accuracy:
			old_accuracy = self.interval.accuracy
			try:
				self.interval = self.newton_raphson_iterate()
			except (ZeroDivisionError, ValueError):
				pass
			
			if self.interval.accuracy == old_accuracy:
				# This is guaranteed to give us at lease 1 more d.p. of accuracy.
				self.interval = self.subdivide_iterate()
		
		self.interval = self.interval.simplify()
	
	def interval_approximation(self, accuracy=0):
		''' Return an interval containing this root, correct to at least the requested accuracy. '''
		
		accuracy_required = max(accuracy, 0)
		if self.interval.accuracy < accuracy_required:
			self.converge_iterate(accuracy_required)
			assert(self.interval.accuracy >= accuracy_required)
			self.interval = self.interval.change_accuracy(accuracy_required)
		
		return self.interval
	
	def algebraic_approximation(self, accuracy=0):
		''' Return an AlgebraicApproximation of this root to at least the requested accuracy. '''
		
		assert(isinstance(accuracy, flipper.IntegerType))
		
		accuracy_needed = int(self.height) + int(self.log_degree) + 2  # This ensures the AlgebraicApproximation is well defined.
		accuracy_required = max(accuracy, accuracy_needed)
		
		return flipper.kernel.AlgebraicApproximation(self.interval_approximation(accuracy_required), self.log_degree, self.height)

def create_polynomial_root(coefficients, strn):
	''' A short way of constructing PolynomialRoots from a list of coefficients and a string. '''
	
	return flipper.kernel.PolynomialRoot(flipper.kernel.Polynomial(coefficients), flipper.kernel.create_interval(strn))

