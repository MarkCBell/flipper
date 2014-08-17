
# This module is replicates the ring of real algebraic numbers.

import flipper

from math import log10 as log
log_2 = log(2)

def height_int(number):
	return log(max(abs(number), 1))

class AlgebraicMonomial(object):
	''' This represents a product of algebraic numbers. '''
	def __init__(self, terms, height=None):
		''' Takes a list of PolynomialRoots and produces the '''
		assert(isinstance(terms, (list, tuple)))
		assert(all(isinstance(term, flipper.kernel.PolynomialRoot) for term in terms))
		self.terms = tuple(sorted(terms))
		self.log_degree = sum(term.log_degree for term in self)
		if height is None: height = float('inf')
		self.height = min(height, sum(term.height for term in self))
		self._algebraic_approximation = None
		self._accuracy = -1
		self._interval = None
		self._interval_accuracy = -1
		self._hash = hash(self.terms)
	
	def __repr__(self):
		return 'product of roots of: \n' + '\n'.join(str(term.polynomial) for term in self)
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
		if isinstance(other, AlgebraicMonomial):
			return AlgebraicMonomial(list(self) + list(other), height=self.height+other.height)
		else:
			return NotImplemented
	def __hash__(self):
		return self._hash
	
	def interval_approximation(self, accuracy=0):
		''' Returns an interval containing this number correct to the requested accuracy. '''
		
		accuracy_required = max(accuracy, 0)
		if self._interval is None or self._interval_accuracy < accuracy_required:
			if any(self):
				# inter = flipper.kernel.product([term.interval_approximation() for term in self])
				# term_accuracy = accuracy_required + max(accuracy_required - inter.accuracy, 0)
				term_accuracy = accuracy_required + max(int(sum(term.interval.log_bound + 1 for term in self)), 0) + 1
				self._interval = flipper.kernel.product([term.interval_approximation(term_accuracy) for term in self])
			else:
				self._interval = flipper.kernel.interval.interval_from_integer(1)
			
			self._interval = self._interval.change_accuracy(accuracy_required)
			self._interval_accuracy = self._interval.accuracy
			assert(self._interval_accuracy >= accuracy_required)
		
		return self._interval
	
	def algebraic_approximation(self, accuracy=0):
		''' Returns an AlgebraicApproximation of this monomial which is correct to at least the
		requested accuracy. If no accuracy is given then accuracy will be chosen such that
		the approximation will determine a unique algebraic number. '''
		
		# Let:
		accuracy_needed = int(self.height) + int(self.log_degree) + 2  # This ensures the AlgebraicApproximation is well defined.
		accuracy_required = max(accuracy, accuracy_needed)
		
		if self._algebraic_approximation is None or self._accuracy < accuracy_required:
			self._algebraic_approximation = flipper.kernel.AlgebraicApproximation(self.interval_approximation(accuracy_required), self.log_degree, self.height)
			
			self._accuracy = self._algebraic_approximation.accuracy
			assert(self._accuracy >= accuracy_required)
		
		return self._algebraic_approximation

class AlgebraicNumber(object):
	''' This represents an element of a number ring, an integer linear combination of AlgebraicMonomials. '''
	def __init__(self, terms, height=None):
		assert(isinstance(terms, dict))
		assert(all(isinstance(term, AlgebraicMonomial) for term in terms))
		assert(all(isinstance(terms[term], flipper.Integer_Type) for term in terms))
		assert(len(set(terms)) == len(terms))  # Check for repeated terms.
		self.terms = dict((term, terms[term]) for term in terms if terms[term] != 0)
		self.log_degree = sum(term.log_degree for term in self)
		if height is None: height = float('inf')
		self.height = min(height, sum(flipper.kernel.height_int(self.co(term)) + term.height + 1 for term in self))
		self._algebraic_approximation = None
		self._accuracy = -1
		self._interval = None
		self._interval_accuracy = -1
	
	def __repr__(self):
		return ' + '.join('%d*x_%d' % (self.co(term), i) for i, term in enumerate(self)) + '\nwhere:\n' + \
			'\n'.join('x_%d := %s' % (i, term) for i, term in enumerate(self))
		return str(float(self))
	def __iter__(self):
		return iter(self.terms)
	def __len__(self):
		return len(self.terms)
	def __float__(self):
		return float(self.algebraic_approximation())
	def __bool__(self):
		return not self.is_zero()
	def __nonzero__(self):  # For Python2.
		return self.__bool__()
	
	def __neg__(self):
		return AlgebraicNumber(dict((term, -self.co(term)) for term in self), height=self.height)
	def __add__(self, other):
		if isinstance(other, AlgebraicNumber):
			return AlgebraicNumber(dict((term, self.co(term) + other.co(term)) for term in self.common_terms(other)), height=self.height+other.height+log_2)
		elif isinstance(other, flipper.Integer_Type):
			return self + other * AlgebraicNumber({AlgebraicMonomial([]): 1}, height=self.height+flipper.kernel.height_int(other)+log_2)
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, AlgebraicNumber):
			return AlgebraicNumber(dict((term, self.co(term) - other.co(term)) for term in self.common_terms(other)), height=self.height+other.height+log_2)
		elif isinstance(other, flipper.Integer_Type):
			return self - other * AlgebraicNumber({AlgebraicMonomial([]): 1}, height=self.height+flipper.kernel.height_int(other)+log_2)
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, AlgebraicNumber):
			terms = dict()
			for term1 in self:
				for term2 in other:
					term = term1 * term2
					terms[term] = self.co(term1) * other.co(term2) + (terms[term] if term in terms else 0)
			return AlgebraicNumber(terms, height=self.height+other.height)
		elif isinstance(other, flipper.Integer_Type):
			return AlgebraicNumber(dict((term, other * self.co(term)) for term in self), height=self.height+flipper.kernel.height_int(other))
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
		if isinstance(other, AlgebraicNumber):
			return set(self).union(set(other))
		else:
			return NotImplemented
	
	def interval_approximation(self, accuracy=0):
		''' Returns an interval containing this number correct to the requested accuracy. '''
		
		accuracy_required = max(accuracy, 0)
		if self._interval is None or self._interval_accuracy < accuracy_required:
			if any(self):
				monomial_accuracy = accuracy_required + int(max(flipper.kernel.height_int(self.co(term)) for term in self)) + len(self) + 1
				
				self._interval = sum(self.co(term) * term.interval_approximation(monomial_accuracy) for term in self)
			else:
				self._interval = flipper.kernel.interval.interval_from_integer(0)
			
			self._interval = self._interval.change_accuracy(accuracy_required)
			self._interval_accuracy = self._interval.accuracy
			assert(self._interval_accuracy >= accuracy_required)
		
		return self._interval
	
	def algebraic_approximation(self, accuracy=0):
		''' Returns an AlgebraicApproximation of this element which is correct to at least the
		requested accuracy. If no accuracy is given then accuracy will be chosen such that
		the approximation will determine a unique algebraic number. '''
		
		# Let:
		accuracy_needed = int(self.log_degree) + int(self.height) + 2  # This ensures the AlgebraicApproximation is well defined.
		accuracy_required = max(accuracy, accuracy_needed)
		
		if self._algebraic_approximation is None or self._accuracy < accuracy_required:
			self._algebraic_approximation = flipper.kernel.AlgebraicApproximation(self.interval_approximation(accuracy_required), self.log_degree, self.height)
			
			self._accuracy = self._algebraic_approximation.accuracy
			assert(self._accuracy >= accuracy_required)
		
		return self._algebraic_approximation
	
	def algebraic_hash_ratio(self, other):
		# !?! RECHEK THIS AGAINST Interval.py.
		HASH_DENOMINATOR = 30
		
		i1 = self.algebraic_approximation(2*HASH_DENOMINATOR).interval.change_denominator(2*HASH_DENOMINATOR)
		i2 = other.algebraic_approximation(2*HASH_DENOMINATOR).interval.change_denominator(2*HASH_DENOMINATOR)
		return (i1 / i2).change_denominator(HASH_DENOMINATOR).tuple()

def algebraic_number_from_info(coefficients, strn):
	return flipper.kernel.polynomial.polynomial_root_from_info(coefficients, strn).as_algebraic_number()

