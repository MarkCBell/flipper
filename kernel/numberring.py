
from math import log10 as log

import flipper

class NumberRingMonomial(object):
	''' This represents a product of algebraic numbers. '''
	def __init__(self, terms):
		''' Takes a list of AlgebraicNumbers and produces the '''
		assert(isinstance(terms, (list, tuple)))
		assert(all(isinstance(term, flipper.kernel.AlgebraicNumber) for term in terms))
		self.terms = tuple(sorted(terms))
		self.degree = flipper.kernel.product(term.degree for term in self)  # Switch to log degree?
		self.height = sum(term.height for term in self)
		self._algebraic_approximation = None
		self._accuracy = -1
	
	def __repr__(self):
		return str(float(self))
	def __float__(self):
		return float(self.algebraic_approximation())
	def __iter__(self):
		return iter(self.terms)
	def __eq__(self, other):
		return self.terms == other.terms
	def __ne__(self, other):
		return self.terms != other.terms
	def __mul__(self, other):
		if isinstance(other, NumberRingMonomial):
			return NumberRingMonomial(list(self) + list(other))
		else:
			return NotImplemented
	def __hash__(self):
		return hash(self.terms)
	def is_one(self):
		return not self.terms  # self.terms == ()
	
	def algebraic_approximation(self, accuracy=0):
		''' Returns an AlgebraicApproximation of this monomial which is correct to at least the
		requested accuracy. If no accuracy is given then accuracy will be chosen such that
		the approximation will determine a unique algebraic number. '''
		# Let:
		accuracy_needed = int(self.height) + int(log(self.degree)) + 2  # This ensures the AlgebraicApproximation is well defined.
		accuracy = max(accuracy, accuracy_needed)
		
		if self._algebraic_approximation is None or self._accuracy < accuracy:
			if self.is_one():
				self._algebraic_approximation = flipper.kernel.algebraicnumber.algebraic_approximation_from_integer(1)
			else:
				inter = flipper.kernel.product([term.interval for term in self])
				term_accuracy = accuracy + max(accuracy - inter.accuracy, 0)  # Recheck this!
				self._algebraic_approximation = flipper.kernel.product([term.algebraic_approximation(term_accuracy) for term in self])
			
			self._accuracy = self._algebraic_approximation.accuracy
			assert(self._accuracy >= accuracy)
		
		return self._algebraic_approximation

class NumberRingElement(object):
	''' This represents an element of a number ring, an integer linear combination of NumberRingMonomials. '''
	def __init__(self, terms):
		assert(isinstance(terms, dict))
		assert(all(isinstance(term, NumberRingMonomial) for term in terms))
		assert(all(isinstance(terms[term], flipper.kernel.Integer_Type) for term in terms))
		assert(len(set(terms)) == len(terms))  # Check for repeated terms.
		self.terms = terms
		self.degree = flipper.kernel.product([term.degree for term in self])
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
		return NumberRingElement(dict((term, -self.co(term)) for term in self))
	def __add__(self, other):
		if isinstance(other, NumberRingElement):
			return NumberRingElement(dict((term, self.co(term) + other.co(term)) for term in self.common_terms(other)))
		elif isinstance(other, flipper.kernel.Integer_Type):
			return self + other * NumberRingElement({NumberRingMonomial([]): 1})
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, NumberRingElement):
			return NumberRingElement(dict((term, self.co(term) - other.co(term)) for term in self.common_terms(other)))
		elif isinstance(other, flipper.kernel.Integer_Type):
			return self - other * NumberRingElement({NumberRingMonomial([]): 1})
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, NumberRingElement):
			return sum(NumberRingElement(dict((term1 * term2, self.co(term1) * other.co(term2)) for term2 in other)) for term1 in self)
		elif isinstance(other, flipper.kernel.Integer_Type):
			return NumberRingElement(dict((term, other * self.co(term)) for term in self))
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
		if isinstance(other, NumberRingElement):
			return set(self).union(set(other))
		else:
			return NotImplemented
	
	def algebraic_approximation(self, accuracy=0):
		''' Returns an AlgebraicApproximation of this element which is correct to at least the
		requested accuracy. If no accuracy is given then accuracy will be chosen such that
		the approximation will determine a unique algebraic number. '''
		
		# Let:
		accuracy_needed = int(self.height) + int(log(self.degree)) + 2  # This ensures the AlgebraicApproximation is well defined.
		accuracy = max(accuracy, accuracy_needed)
		
		if self._algebraic_approximation is None or self._accuracy < accuracy:
			monomial_accuracy = accuracy + sum(flipper.kernel.height_int(self.co(term)) for term in self) + 2 * int(log(self.degree)) + 1  # Recheck this!
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

