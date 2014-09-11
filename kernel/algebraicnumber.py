
''' A module for representing and manipulating elements of the ring of real algebraic numbers.

Provides two classes: AlgebraicMonomial and AlgebraicNumber.
	An AlgebraicMonomial is a product of PolynomialRoots.
	An AlgebraicNumber is an integer linear combination of AlgebraicMonomials.

There is also a helper function: algebraic_number. '''

import flipper

from math import log10 as log

LOG_2 = log(2)
HASH_DENOMINATOR = 30

def height_int(number):
	''' Return the height of the given integer. '''
	
	assert(isinstance(number, flipper.IntegerType))
	
	return log(max(abs(number), 1))

class AlgebraicMonomial(object):
	''' This represents a product of algebraic numbers. '''
	def __init__(self, terms, height=None):
		assert(all(isinstance(term, flipper.kernel.PolynomialRoot) for term in terms))
		
		# We could record self.terms as tuple(sorted(terms)) but to make this work in Python 3
		# we would have to add comparison operators to PolynomialRoot.
		self.terms = tuple(terms)
		self.log_degree = sum(term.log_degree for term in self)
		if height is None: height = float('inf')
		self.height = min(height, sum(term.height for term in self))
		self._interval = None
		self._accuracy = -1
		self._hash = hash(self.terms)
	
	def __repr__(self):
		return 'product of roots of: \n' + '\n'.join(str(term.polynomial) for term in self)
	def __float__(self):
		return float(self.algebraic_approximation())
	def __iter__(self):
		return iter(self.terms)
	def __eq__(self, other):
		return self.terms == other.terms
	def __ne__(self, other):
		return not (self == other)
	def __mul__(self, other):
		if isinstance(other, AlgebraicMonomial):
			return AlgebraicMonomial(list(self) + list(other), height=self.height+other.height)
		else:
			return NotImplemented
	def __hash__(self):
		return self._hash
	
	def interval_approximation(self, accuracy=0):
		''' Return an interval containing this number correct to the requested accuracy. '''
		
		accuracy_required = max(accuracy, 0)
		if self._interval is None or self._accuracy < accuracy_required:
			term_accuracy = accuracy_required + max(int(sum(term.interval.log_bound + 1 for term in self)), 0) + 1
			self._interval = flipper.kernel.product([term.interval_approximation(term_accuracy) for term in self], start=flipper.kernel.Interval(1, 1, 0))
			
			self._interval = self._interval.change_accuracy(accuracy_required)
			self._accuracy = self._interval.accuracy
			assert(self._accuracy >= accuracy_required)
		
		return self._interval
	
	def algebraic_approximation(self, accuracy=0):
		''' Return an AlgebraicApproximation of this monomial which is correct to at least the
		requested accuracy. If no accuracy is given then accuracy will be chosen such that
		the approximation will determine a unique algebraic number. '''
		
		# Let:
		accuracy_needed = int(self.height) + int(self.log_degree) + 2  # This ensures the AlgebraicApproximation is well defined.
		accuracy_required = max(accuracy, accuracy_needed)
		
		return flipper.kernel.AlgebraicApproximation(self.interval_approximation(accuracy_required), self.log_degree, self.height)

class AlgebraicNumber(object):
	''' This represents an element of a number ring, an integer linear combination of AlgebraicMonomials. '''
	def __init__(self, terms, height=None):
		assert(isinstance(terms, dict))
		assert(all(isinstance(term, AlgebraicMonomial) for term in terms))
		assert(all(isinstance(terms[term], flipper.IntegerType) for term in terms))
		assert(height is None or isinstance(height, flipper.NumberType))
		assert(len(set(terms)) == len(terms))  # Check for repeated terms.
		
		self.terms = dict((term, terms[term]) for term in terms if terms[term] != 0)
		self.log_degree = sum(term.log_degree for term in self)
		if height is None: height = float('inf')
		self.height = min(height, sum(flipper.kernel.height_int(self.co(term)) + term.height + 1 for term in self))
		self._interval = None
		self._accuracy = -1
	
	def __repr__(self):
		return str(float(self))
		# return ' + '.join('%d*x_%d' % (self.co(term), i) for i, term in enumerate(self)) + '\nwhere:\n' + \
		#	'\n'.join('x_%d := %s' % (i, term) for i, term in enumerate(self))
	def __iter__(self):
		return iter(self.terms)
	def __len__(self):
		return len(self.terms)
	def __float__(self):
		return float(self.algebraic_approximation())
	def __bool__(self):
		return self != 0
	def __nonzero__(self):  # For Python2.
		return self.__bool__()
	
	def __neg__(self):
		return AlgebraicNumber(dict((term, -self.co(term)) for term in self), height=self.height)
	def __add__(self, other):
		if isinstance(other, AlgebraicNumber):
			return AlgebraicNumber(dict((term, self.co(term) + other.co(term)) for term in self.all_terms(other)), height=self.height + other.height + LOG_2)
		elif isinstance(other, flipper.IntegerType):
			return self + other * AlgebraicNumber({AlgebraicMonomial([]): 1}, height=self.height+flipper.kernel.height_int(other) + LOG_2)
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, AlgebraicNumber):
			return AlgebraicNumber(dict((term, self.co(term) - other.co(term)) for term in self.all_terms(other)), height=self.height + other.height + LOG_2)
		elif isinstance(other, flipper.IntegerType):
			return self - other * AlgebraicNumber({AlgebraicMonomial([]): 1}, height=self.height+flipper.kernel.height_int(other) + LOG_2)
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
		elif isinstance(other, flipper.IntegerType):
			return AlgebraicNumber(dict((term, other * self.co(term)) for term in self), height=self.height+flipper.kernel.height_int(other))
		else:
			return NotImplemented
	def __rmul__(self, other):
		return self * other
	
	def __lt__(self, other):
		return (self - other).sign() == -1
	def __eq__(self, other):
		return (self - other).sign() == 0
	def __ne__(self, other):
		return not (self == other)
	def __gt__(self, other):
		return (self - other).sign() == +1
	def __le__(self, other):
		return self < other or self == other
	def __ge__(self, other):
		return self > other or self == other
	
	def sign(self):
		''' Return the sign of this algebraic number. '''
		
		return self.algebraic_approximation().sign()
	
	def coefficient(self, term):
		''' Return the coefficient of the given term. '''
		
		return self.terms[term] if term in self.terms else 0
	def co(self, term):
		''' A shorter alias for self.coefficient(). '''
		
		return self.coefficient(term)
	def all_terms(self, other):
		''' Return the set of terms in this algebraic number or other. '''
		
		assert(isinstance(other, AlgebraicNumber))
		
		return set(self).union(set(other))
	
	def interval_approximation(self, accuracy=0):
		''' Return an interval containing this number correct to the requested accuracy. '''
		
		accuracy_required = max(accuracy, 0)
		if self._interval is None or self._accuracy < accuracy_required:
			monomial_accuracy = accuracy_required + int(sum(flipper.kernel.height_int(self.co(term)) for term in self)) + len(self) + 1
			
			self._interval = sum([self.co(term) * term.interval_approximation(monomial_accuracy) for term in self], flipper.kernel.Interval(0, 0, 0))
			
			self._interval = self._interval.change_accuracy(accuracy_required)
			self._accuracy = self._interval.accuracy
			assert(self._accuracy >= accuracy_required)
		
		return self._interval
	
	def algebraic_approximation(self, accuracy=0):
		''' Return an AlgebraicApproximation of this element which is correct to at least the
		requested accuracy. If no accuracy is given then accuracy will be chosen such that
		the approximation will determine a unique algebraic number. '''
		
		# Let:
		accuracy_needed = int(self.log_degree) + int(self.height) + 2  # This ensures the AlgebraicApproximation is well defined.
		accuracy_required = max(accuracy, accuracy_needed)
		
		return flipper.kernel.AlgebraicApproximation(self.interval_approximation(accuracy_required), self.log_degree, self.height)
	
	def algebraic_hash_ratio(self, other):
		''' Return a hashable object representing this algebraic number / other. '''
		
		# !?! RECHEK THIS AGAINST Interval.py.
		
		i1 = self.algebraic_approximation(2*HASH_DENOMINATOR).interval.change_denominator(2*HASH_DENOMINATOR)
		i2 = other.algebraic_approximation(2*HASH_DENOMINATOR).interval.change_denominator(2*HASH_DENOMINATOR)
		return (i1 / i2).change_denominator(HASH_DENOMINATOR).tuple()

def algebraic_number(coefficients, strn):
	''' A short way of constructing an AlgebraicNumber from a list of coefficients and a string. '''
	
	return AlgebraicNumber({AlgebraicMonomial([flipper.kernel.polynomial_root(coefficients, strn)]): 1})

