
''' A module for representing and manipulating polynomials and their roots.

Provides two classes: Polynomial and PolynomialRoot. '''

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
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		# So it turns out that displaying polynomials correctly is really hard.
		s = ''
		for index, coefficient in enumerate(self):
			if coefficient != 0:
				pos = coefficient > 0
				power = '^%d' % index if index > 1 else ''
				coeff = '' if abs(coefficient) == 1 else '%d*' % abs(coefficient)
				if index == 0:
					s += str(coefficient)
				elif s == '':
					s += '%s%sx%s' % ('' if pos else '-', coeff, power)
				elif s != '':
					s += ' %s %sx%s' % ('+' if pos else '-', coeff, power)
		
		return '0' if s == '' else s
	def __bool__(self):
		return not self.is_zero()
	def __nonzero__(self):  # For Python2.
		return self.__bool__()
	def __eq__(self, other):
		if isinstance(other, Polynomial):
			return self.degree == other.degree and all(a == b for a, b in zip(self, other))
		elif isinstance(other, flipper.IntegerType):
			return self.degree == 0 and self[0] == other
		else:
			return NotImplemented
	def __ne__(self, other):
		return not (self == other)
	def __hash__(self):
		return hash(tuple(self.coefficients))
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
		
		Power must be an integer '''
		
		assert(isinstance(power, flipper.IntegerType))
		
		if power >= 0:
			return Polynomial([0] * power + self.coefficients)
		else:
			return Polynomial(self.coefficients[abs(power):])
	
	def __call__(self, other):
		# It is significantly more efficient to compute self(other) as:
		#   a_0 + x*(a_1 + x*( ... + x*(a_n + x * 0) ... ) )
		# using Horner's rule.
		
		total = 0
		for coefficient in reversed(self):
			total = (other * total) + coefficient
		return total
	def __divmod__(self, other):
		''' Return the quotient and remainder (and rescaling) of this polynomial by other.
		
		That is, returns polynomials quotient and remainder such that:
			scale * self == quotient * other + remainder, and
			deg(remainder) < deg(other)
		If self and other are integral, by Gauss' lemma if other | self then scale == 1. '''
		
		if isinstance(other, Polynomial):
			if other.is_zero():
				raise ZeroDivisionError
			
			# We really should do this calculation modulo some large prime
			# to avoid exponential blowup.
			quotient = Polynomial([0])
			remainder = self
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
		elif isinstance(other, flipper.IntegerType):
			# Just so self % d will work.
			return None, Polynomial([coefficient % other for coefficient in self])
		else:
			return NotImplemented
	def __mod__(self, other):
		_, remainder = divmod(self, other)
		return remainder
	def __floordiv__(self, other):
		quotient, remainder = divmod(self, other)
		if not remainder.is_zero():  # Division isn't perfect.
			raise ValueError('Polynomials do not divide.')
		return quotient
	def divides(self, other):
		''' Return if self divides other. '''
		
		_, remainder = divmod(other, self)
		return remainder.is_zero()
	
	def gcd(self, other):
		''' Return the GCD(self, other). '''
		
		# Note that doing flipper.kernel.gcd([self, other])
		# may not give the correct answer, it may have the
		# wrong scaling due to how divmod works.
		
		f = flipper.kernel.gcd([self, other]).rescale()
		return f * abs(flipper.kernel.gcd(list(self // f) + list(other // f)))
	
	def rescale(self):
		''' Return a possibly simpler polynomial with the same roots. '''
		
		c = max(abs(flipper.kernel.gcd(self)), 1)  # Avoid a possible division by 0.
		return Polynomial([coefficient // c for coefficient in self])
	
	def square_free(self):
		''' Return the polynomial with the same roots but each with multiplicity one. '''
		
		return self // self.gcd(self.derivative())
	
	def signs_at_interval_endpoints(self, interval):
		''' Return the signs of this polynomial at the endpoints of the given interval. '''
		
		assert(isinstance(interval, flipper.kernel.Interval))
		
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
	
	def real_roots(self):
		''' Return a list of (real) PolynomialRoots, one for each root of self.
		
		Repeated roots are not returned multiple times. If you are planning on using
		these roots you should really use self.square_free().real_roots() to ensure
		the Newton-Raphson convergence of these is effective. '''
		
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
	not an ApproximationError will be raised. These methods are significantly
	faster when the polynomial is square free. '''
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
	
	@classmethod
	def from_tuple(cls, coefficients, string):
		''' A short way of constructing PolynomialRoots from a list of coefficients and a string. '''
		
		return cls(Polynomial(coefficients), flipper.kernel.Interval.from_string(string))
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return 'Root of %s (~%s)' % (self.polynomial, self.approximate_string(6))
	def approximate_string(self, accuracy=None):
		''' Return a string approximating this NumberFieldElement. '''
		
		return self.algebraic_approximation(accuracy).approximate_string(accuracy)
	def __float__(self):
		return float(self.algebraic_approximation())
	def __hash__(self):
		# Just hashing self.polynomial works well as the map:
		#   algebraic number |--> min polynomial
		# is finite-to-one.
		return hash(self.polynomial)
	
	def compare(self, other, operator):
		''' Return the result of operator on sufficiently good algebraic approximations of self and other. '''
		
		if isinstance(other, flipper.IntegerType):
			accuracy_needed = int(self.height + self.log_degree + flipper.kernel.height_int(other) + 0) + 5
			return operator(self.algebraic_approximation(accuracy_needed), other)
		else:
			try:
				accuracy_needed = int(self.height + self.log_degree + other.height + other.log_degree) + 5
				return operator(self.algebraic_approximation(accuracy_needed), other.algebraic_approximation(accuracy_needed))
			except AttributeError:
				return NotImplemented
	
	def __lt__(self, other):
		return self.compare(other, lambda x, y: x < y)
	def __eq__(self, other):
		return self.compare(other, lambda x, y: x == y)
	def __gt__(self, other):
		return self.compare(other, lambda x, y: x > y)
	def __le__(self, other):
		return not (self > other)
	def __ne__(self, other):
		return not (self == other)
	def __ge__(self, other):
		return not (self < other)
	
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
		
		# At the end we will call self.interval.simplify() which may cost us
		# a point of accuracy, so we will have to iteration until we hit at
		# least accuracy + 1.
		while self.interval.accuracy <= accuracy+1:
			old_accuracy = self.interval.accuracy
			try:
				self.interval = self.newton_raphson_iterate()
			except (ZeroDivisionError, ValueError):
				pass
			
			if self.interval.accuracy == old_accuracy:
				# This is guaranteed to give us at lease 1 more d.p. of accuracy.
				self.interval = self.subdivide_iterate()
		
		# We may lose one point of accuracy here.
		self.interval = self.interval.simplify()
	
	def interval_approximation(self, accuracy=0):
		''' Return an interval containing this root, correct to at least the requested accuracy. '''
		
		min_accuracy = 0
		target_accuracy = max(accuracy, min_accuracy)
		
		if self.interval.accuracy < target_accuracy:
			request_accuracy = target_accuracy
			
			self.converge_iterate(request_accuracy)
			assert(self.interval.accuracy >= target_accuracy)
		
		return self.interval
	
	def algebraic_approximation(self, accuracy=None):
		''' Return an AlgebraicApproximation of this root to at least the requested accuracy. '''
		
		if accuracy is None: accuracy = 0
		min_accuracy = self.height + self.log_degree  # This ensures the AlgebraicApproximation is well defined.
		target_accuracy = max(accuracy, min_accuracy)
		
		request_accuracy = target_accuracy
		
		return flipper.kernel.AlgebraicApproximation(self.interval_approximation(request_accuracy), self.log_degree, self.height)
	
	def square_free_representation(self):
		''' Return this PolynomialRoot but with a square free polynomial.
		
		This can be useful as Newton-Raphson works much better (and so
		convergence happens much faster) for square-free polynomials. '''
		
		return PolynomialRoot(self.polynomial.square_free(), self.interval)
	
	def irreducible_representation(self):
		''' Return this PolynomialRoot but with an irreducible polynomial.
		
		You can make this faster by ensuring that the polynomial is square
		free first.'''
		
		Id = flipper.kernel.id_matrix(self.degree)
		precision = int(self.height + 2*self.degree) + 1
		while True:
			k = 10**precision
			I = self.interval_approximation(precision)
			M = Id.join(flipper.kernel.Matrix([[int(k * I**i) for i in range(self.degree)]])).transpose()
			N = M.LLL()  # This is really slow :(.
			f = flipper.kernel.Polynomial(N[0][:-1])
			if self in f.real_roots():
				return PolynomialRoot(f, I)
			else:
				# This should never happen if we chose precision correctly.
				# However Cohen described this choice as `subtle' so let's be
				# careful and repeat the calculation if we got the wrong answer.
				precision = 2 * precision

