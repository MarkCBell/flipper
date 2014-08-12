
from math import log10 as log

import flipper

class NumberRing(object):
	''' This represents the number ring ZZ[gen_1, ..., gen_k]. '''
	def __init__(self, generators, degree=None):
		''' Each generator must be an AlgebraicNumber and, if given, each element of the ring 
		must have degree at most degree. '''
		assert(all(isinstance(gen, flipper.kernel.AlgebraicNumber) for gen in generators))
		self.generators = generators
		self.num_generators = len(self.generators)
		self.degree = degree if degree is not None else flipper.kernel.product([gen.degree for gen in self.generators])
		self.one = self.element({self.monomial((0,) * self.num_generators): 1})
		self.sum_height = sum(gen.height for gen in self.generators)
		self._generator_approxs = [gen.algebraic_approximation() for gen in self.generators]
		self._accuracy = min(gen_approx.accuracy for gen_approx in self._generator_approxs)
	
	def __repr__(self):
		return 'ZZ%s' % list(self.generators)
	
	def __iter__(self):
		return iter(self.generators)
	
	def __contains__(self, other):
		return isinstance(other, (NumberRingMonomial, NumberRingElement)) and other.number_ring == self
	
	def monomial(self, powers):
		return NumberRingMonomial(self, powers)
	
	def element(self, terms):
		return NumberRingElement(self, terms)
	
	def monomial_basis(self):
		''' Returns the basis: gen_1, ..., gen_k as monomials. '''
		return [self.monomial((0,) * i + (1,) + (0,) * (self.num_generators - 1 - i)) for i in range(self.num_generators)]
	
	def basis(self):
		''' Returns the basis: gen_1, ..., gen_k as elements. '''
		return [self.element({monomial: 1}) for monomial in self.monomial_basis()]
	
	def algebraic_approximations(self, accuracy):
		if self._accuracy < accuracy:
			self._generator_approxs = [gen.algebraic_approximation(accuracy) for gen in self.generators]
			self._accuracy = min(gen_approx.accuracy for gen_approx in self._generator_approxs)
			assert(self._accuracy >= accuracy)
		
		return self._generator_approxs

class NumberRingMonomial(object):
	''' This represents a monomial in a number ring.
	You shouldn't create NumberRingElements directly but instead should use NumberRing.monomial(). '''
	def __init__(self, number_ring, powers):
		assert(isinstance(number_ring, NumberRing))
		assert(isinstance(powers, tuple))
		assert(all(isinstance(power, flipper.kernel.Integer_Type) for power in powers))
		self.number_ring = number_ring
		self.powers = powers
		if len(self) != self.number_ring.num_generators:
			raise TypeError('Monomial must be specified by %d--tuples.' % self.number_ring.num_generators)
		self.degree = self.number_ring.degree
		self.height = sum(y * gen.height for gen, y in zip(self.number_ring, self))
		self._algebraic_approximation = None
		self._accuracy = -1
	
	def __repr__(self):
		return str(float(self))
	def __float__(self):
		return float(self.algebraic_approximation())
	def __len__(self):
		return len(self.powers)
	def __iter__(self):
		return iter(self.powers)
	def __eq__(self, other):
		return self.powers == other.powers
	def __ne__(self, other):
		return self.powers != other.powers
	def __mul__(self, other):
		if isinstance(other, NumberRingMonomial):
			if other.number_ring == self.number_ring:
				return NumberRingMonomial(self.number_ring, tuple(a+b for a, b in zip(self, other)))
			else:
				raise TypeError('Cannot multiply monomials of different number rings.')
		else:
			return NotImplemented
	def __hash__(self):
		return hash(self.powers)
	def is_one(self):
		return not any(self)
	
	def algebraic_approximation(self, accuracy=0):
		''' Returns an AlgebraicApproximation of this monomial which is correct to at least the
		requested accuracy. If no accuracy is given then accuracy will be chosen such that
		the approximation will determine a unique algebraic number. '''
		# Let:
		N = self.number_ring
		accuracy_needed = int(self.height + self.degree) + 1  # This ensures the AlgebraicApproximation is well defined.
		accuracy = max(accuracy, accuracy_needed)
		
		if self._algebraic_approximation is None or self._accuracy < accuracy:
			if self.is_one():
				self._algebraic_approximation = flipper.kernel.algebraicnumber.algebraic_approximation_from_int(1, degree=self.degree)
			else:
				inter = flipper.kernel.product([gen.interval for gen, y in zip(N._generator_approxs, self) for i in range(y)])
				generator_accuracy = accuracy + max(accuracy - inter.accuracy, 0)  # Recheck this!
				self._algebraic_approximation = flipper.kernel.product([gen**y for gen, y in zip(N.algebraic_approximations(generator_accuracy), self)])
			
			self._accuracy = self._algebraic_approximation.accuracy
			assert(self._accuracy >= accuracy)
		
		return self._algebraic_approximation

class NumberRingElement(object):
	''' This represents an element of a number ring, an integer linear combination of NumberRingMonomials.
	You shouldn't create NumberRingElements directly but instead should use NumberRing.element(). '''
	def __init__(self, number_ring, terms):
		assert(isinstance(number_ring, NumberRing))
		assert(isinstance(terms, dict))
		assert(all(isinstance(term, NumberRingMonomial) for term in terms))
		assert(all(term in number_ring for term in terms))
		assert(len(set(terms)) == len(terms))  # Check for repeated terms.
		self.number_ring = number_ring
		self.terms = terms
		self.degree = self.number_ring.degree
		self.height = sum(flipper.kernel.height_int(self.co(term)) + term.height + 1 for term in self)
		self._algebraic_approximation = None
		self._accuracy = -1
	
	def __repr__(self):
		return str(float(self))
	def __iter__(self):
		return iter(self.terms)
	def __float__(self):
		return float(self.algebraic_approximation())
	def __bool__(self):
		return not self.is_zero()
	def __nonzero__(self):  # For Python2.
		return self.__bool__()
	
	def __neg__(self):
		return self.number_ring.element(dict((term, -self.co(term)) for term in self))
	def __add__(self, other):
		if isinstance(other, NumberRingElement):
			if self.number_ring != other.number_ring:
				raise TypeError('Cannot add elements of different number rings.')
			return self.number_ring.element(dict((term, self.co(term) + other.co(term)) for term in self.common_terms(other)))
		elif isinstance(other, flipper.kernel.Integer_Type):
			return self + other * self.number_ring.one
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, NumberRingElement):
			if self.number_ring != other.number_ring:
				raise TypeError('Cannot subtract elements of different number fields.')
			return self.number_ring.element(dict((term, self.co(term) - other.co(term)) for term in self.common_terms(other)))
		elif isinstance(other, flipper.kernel.Integer_Type):
			return self - other * self.number_ring.one
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, NumberRingElement):
			if self.number_ring != other.number_ring:
				raise TypeError('Cannot multiply elements of different number fields.')
			
			return sum(self.number_ring.element(dict((term1 * term2, self.co(term1) * other.co(term2)) for term2 in other)) for term1 in self)
		elif isinstance(other, flipper.kernel.Integer_Type):
			return self.number_ring.element(dict((term, other * self.co(term)) for term in self))
		else:
			return NotImplemented
	def __rmul__(self, other):
		return self * other
	
	def __lt__(self, other):
		return (self - other).is_negative()
	def __eq__(self, other):
		return (self - other).is_zero()
	def __ne__(self, other):
		return not (self - other).is_zero()
	def __gt__(self, other):
		return (self - other).is_positive()
	def __le__(self, other):
		return self < other or self == other
	def __ge__(self, other):
		return self > other or self == other
	
	def is_positive(self):
		return self.algebraic_approximation().is_positive()
	def is_negative(self):
		return self.algebraic_approximation().is_negative()
	def is_zero(self):
		return not self.is_positive() and not self.is_negative()
	
	def coefficient(self, term):
		return self.terms[term] if term in self.terms else 0
	def co(self, term):  # Shorter alias.
		return self.coefficient(term)
	def common_terms(self, other):
		if isinstance(other, NumberRingElement) and self.number_ring == other.number_ring:
			return set(self).union(set(other))
		else:
			return NotImplemented
	
	def algebraic_approximation(self, accuracy=0):
		''' Returns an AlgebraicApproximation of this element which is correct to at least the
		requested accuracy. If no accuracy is given then accuracy will be chosen such that
		the approximation will determine a unique algebraic number. '''
		
		# Let:
		N = self.number_ring
		accuracy_needed = int(self.height + self.degree) + 1  # This ensures the AlgebraicApproximation is well defined.
		accuracy = max(accuracy, accuracy_needed)
		
		if self._algebraic_approximation is None or self._accuracy < accuracy:
			monomial_accuracy = accuracy + sum(flipper.kernel.height_int(self.co(term)) for term in self) + 2 * self.degree  # Recheck this!
			self._algebraic_approximation = sum(self.co(term) * term.algebraic_approximation(monomial_accuracy) for term in self)
			
			self._accuracy = self._algebraic_approximation.accuracy
			assert(self._accuracy >= accuracy)
		
		return self._algebraic_approximation
	
	def algebraic_hash_ratio(self, other):
		# !?! RECHEK THIS AGAINST Interval.py.
		HASH_DENOMINATOR = 30
		
		i1 = self.algebraic_approximation(2*HASH_DENOMINATOR).interval.change_denominator(2*HASH_DENOMINATOR)
		i2 = other.algebraic_approximation(2*HASH_DENOMINATOR).interval.change_denominator(2*HASH_DENOMINATOR)
		return (i1 / i2).change_denominator(HASH_DENOMINATOR).tuple()

