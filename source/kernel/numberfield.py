
''' A module for representing and manipulating elements of number fields.

Provides two classes: NumberField and NumberFieldElement. '''

# This provides us with a way of storing and manipulating elements of QQ(lambda),
# where lambda is an algebraic integer (however technically this can currently only actually
# manipulate elements of ZZ[lambda]). This can even do multiplication of these
# elements without having to drop to an AlgebraicApproximation and so is significantly
# faster that the previous way of doing this sort of calculation.
#
# This requires the numbers to be given as a linear combinations of
# 1, lambda, ..., lambda^{d-1}. Currently Sage is much better at doing this than we are.

import flipper

from math import log10 as log

LOG_2 = log(2)
INFTY = float('inf')

def height_int(number):
	''' Return the height of the given integer. '''
	
	assert(isinstance(number, flipper.IntegerType))
	
	return log(max(abs(number), 1))

class NumberField(object):
	''' This represents a number field QQ(lambda).
	
	Additionally NumberField() returns QQ.
	
	The given PolynomialRoot must be a monic polynomial. '''
	def __init__(self, polynomial_root=None):
		assert(polynomial_root is None or isinstance(polynomial_root, flipper.kernel.PolynomialRoot))
		if polynomial_root is None: polynomial_root = flipper.kernel.PolynomialRoot.from_tuple([-1, 1], '1.00')
		assert(polynomial_root.polynomial.is_monic())
		
		self.polynomial_root = polynomial_root
		
		self.height = self.polynomial_root.height
		self.degree = self.polynomial_root.degree
		self.log_degree = self.polynomial_root.log_degree
		self.accuracy_error = self.degree * self.polynomial_root.interval.log_plus()
		self.height_error = self.degree * (self.height + LOG_2)
		
		self.polynomial = self.polynomial_root.polynomial
		self.companion_matrices = self.polynomial.companion_matrix().powers(self.degree)
		
		self._approximations = None  # A list of approximations of lambda^0, ..., lambda^(d-1).
		self.accuracy = -1
		
		self.one = self.element([1])
		self.lmbda = self.element([1]) if self.is_rationals() else self.element([0, 1])  # lambda is a Python keyword.
	
	@classmethod
	def from_tuple(cls, coefficients, string):
		''' A short way of constructing a NumberField from a list of coefficients and a string. '''
		
		return cls(flipper.kernel.PolynomialRoot.from_tuple(coefficients, string))
	
	def lmbda_approximations(self, accuracy):
		''' Return intervals approximating lmbda^0, ..., lmbda^(degree-1) to the given accuracy.
		
		The intervals returned all have the same denominator and so addition / subtraction of these is fast. '''
		
		min_accuracy = 0
		target_accuracy = max(accuracy, min_accuracy)
		
		if self._approximations is None or self.accuracy < target_accuracy:
			# Note that if I is an interval approximating L to at
			# least k + i * N.log_plus digits of accuracy then I^i
			# approximates L^i to at least k digits of accuracy.
			request_accuracy = target_accuracy + self.accuracy_error
			
			lmbda = self.polynomial_root.interval_approximation(request_accuracy)
			self._approximations = [lmbda**i for i in range(self.degree)]
			minimal_accuracy = min(interval.accuracy for interval in self._approximations)
			if minimal_accuracy < INFTY:
				self._approximations = [interval.change_denominator(minimal_accuracy) for interval in self._approximations]
			self.accuracy = min(interval.accuracy for interval in self._approximations)
			assert(self.accuracy >= target_accuracy)
		
		return self._approximations
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return 'QQ[%s]' % str(self.polynomial)
	def __reduce__(self):
		# NumberFields are already pickleable but this results in a smaller pickle.
		return (self.__class__, (self.polynomial_root,))
	def __hash__(self):
		return hash(self.polynomial_root)
	def __eq__(self, other):
		return self.polynomial == other.polynomial and self.polynomial_root == other.polynomial_root
	def __ne__(self, other):
		return not (self == other)
	
	def element(self, linear_combination):
		''' Return a new element of this number field. '''
		
		return NumberFieldElement(self, linear_combination)
	
	def is_rationals(self):
		''' Return if this number field is QQ. '''
		
		return self.degree == 1

class NumberFieldElement(object):
	''' This represents an element of a number field. You shouldn't create NumberFieldElements directly but instead
	should use NumberField.element() which creates an element in that number field. '''
	def __init__(self, number_field, linear_combination):
		self.number_field = number_field
		if len(linear_combination) < self.number_field.degree:
			linear_combination = linear_combination + [0] * (self.number_field.degree - len(linear_combination))
		elif len(linear_combination) > self.number_field.degree:
			raise TypeError('Linear combination: %s has more terms than the degree of the field in which it lives' % linear_combination)
		self.linear_combination = linear_combination
		# Let N = QQ(lambda) and d := N.degree.
		# Let [a_i] := self.linear_combination, [\alpha_i] := N._algebraic_approximations[i].
		# Let \alpha := sum(a_i * \alpha_i).
		# Now h(\alpha) <= sum(h(a_i \alpha_i)) + d log(2)
		#               <= sum(h(a_i)) + sum(h(\alpha_i)) + (d-1) log(2) [AlgebraicApproximation.py L:9]
		#               <= sum(h(a_i)) + N.height_error
		self.degree = self.number_field.degree
		self.log_degree = self.number_field.log_degree
		self.height = sum(flipper.kernel.height_int(coefficient) for coefficient in self) + self.number_field.height_error
		self._interval = None
		self.accuracy = -1
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return self.approximate_string(6)
	def approximate_string(self, accuracy=None):
		''' Return a string approximating this NumberFieldElement. '''
		
		return self.algebraic_approximation(accuracy).approximate_string(accuracy)
	def __reduce__(self):
		# NumberFieldElements are already pickleable but this results in a smaller pickle.
		return (self.__class__, (self.number_field, self.linear_combination))
	def __iter__(self):
		return iter(self.linear_combination)
	def __len__(self):
		return self.number_field.degree
	def __float__(self):
		return float(self.algebraic_approximation())
	def __int__(self):
		return int(self.algebraic_approximation())
	def __bool__(self):
		return self != 0
	def __nonzero__(self):  # For Python2.
		return self.__bool__()
	def __hash__(self):
		# Warning: This is only really a hash when self.number_field.polynomial is irreducible.
		return hash((self.number_field, tuple(self.linear_combination)))
	
	def __neg__(self):
		return NumberFieldElement(self.number_field, [-a for a in self])
	def __abs__(self):
		return self if self >= 0 else -self
	def __add__(self, other):
		if isinstance(other, NumberFieldElement):
			if self.number_field != other.number_field:
				raise TypeError('Cannot add elements of different number fields.')
			return self.number_field.element([a+b for a, b in zip(self, other)])
		elif isinstance(other, flipper.IntegerType):
			return self.number_field.element([self.linear_combination[0] + other] + self.linear_combination[1:])
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, NumberFieldElement):
			if self.number_field != other.number_field:
				raise TypeError('Cannot subtract elements of different number fields.')
			return self.number_field.element([a-b for a, b in zip(self, other)])
		elif isinstance(other, flipper.IntegerType):
			return self.number_field.element([self.linear_combination[0] - other] + self.linear_combination[1:])
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def companion_matrix(self):
		''' Return the companion matrix of this Element.
		
		This describes how multiplication by this Element acts on the underlying vector space. '''
		
		return flipper.kernel.dot(self, self.number_field.companion_matrices)
	def __mul__(self, other):
		if isinstance(other, NumberFieldElement):
			if self.number_field != other.number_field:
				raise TypeError('Cannot multiply elements of different number fields.')
			
			return self.number_field.element(self.companion_matrix()(other.linear_combination))
		elif isinstance(other, flipper.IntegerType):
			return self.number_field.element([a * other for a in self])
		else:
			return NotImplemented
	def __rmul__(self, other):
		return self * other
	def __pow__(self, power):
		if power == 0:
			return self.number_field.one
		elif power == 1:
			return self
		elif power > 1:
			sqrt = self**(power//2)
			square = sqrt * sqrt
			if power % 2 == 1:
				return self * square
			else:
				return square
	
	def __div__(self, other):
		return self.__truediv__(other)
	def __truediv__(self, other):
		if other == 0:
			raise ZeroDivisionError
		
		if isinstance(other, NumberFieldElement):
			if self.number_field != other.number_field:
				raise TypeError('Cannot multiply elements of different number fields.')
			
			I = flipper.kernel.id_matrix(self.degree+1)
			precision = int(self.height + other.height + self.degree) + 1
			while True:
				k = 10**precision
				
				lmbdas = self.number_field.lmbda_approximations(2*precision)
				
				a = self.interval_approximation(precision)
				b = other.interval_approximation(precision)
				
				M = I.join(flipper.kernel.Matrix([[int(k * lmbda) for lmbda in lmbdas] + [int(k * a / b)]])).transpose()
				N = M.LLL()  # This is really slow :(.
				div, scalar = self.number_field.element(N[0][:self.degree]), -N[0][-2]
				if div * other == scalar * self:
					return div, scalar
				else:
					# This should never happen if we chose precision correctly.
					# However Cohen described this choice as `subtle' so let's be
					# careful and repeat the calculation if we got the wrong answer.
					precision = 2 * precision
		elif isinstance(other, flipper.IntegerType):
			return self.number_field.element([coeff // other for coeff in self])
		else:
			return NotImplemented
	def __floordiv__(self, other):
		if other == 0:
			raise ZeroDivisionError
		
		if isinstance(other, flipper.IntegerType):
			return int(self) // other
		else:
			try:
				accuracy_needed = int(self.height + self.log_degree + other.height + other.log_degree) + 5
				return int(self.algebraic_approximation(accuracy_needed) / other.algebraic_approximation(accuracy_needed))
			except AttributeError:
				return NotImplemented
	def __mod__(self, other):
		if isinstance(other, flipper.IntegerType):
			return self.number_field.element([coeff % other for coeff in self])
		else:
			return NotImplemented
	
	def polynomial(self):
		''' Return a polynomial that this algebraic number is a root of.
		
		Note that this is NOT guaranteed to return the minimal polynomial
		of self. However it will whenever:
			deg(self) == def(self.number_field). '''
		
		# We get such a polynomial from the characteristic polynomial of the matrix
		# describing the action of self on the basis 1, \lmbda, \lambda^2, ...
		
		return flipper.kernel.dot(self, self.number_field.companion_matrices).characteristic_polynomial()
	
	def minimal_polynomial(self):
		''' Return the minimal polynomial of this algebraic number. '''
		
		# Get a really good approximation. Exactly how good we need is "...subtle, and
		# depends in part on what one knows about the problem" see Cohen Page 100.
		t = int(self.degree + self.height) + 1
		while True:
			I = self.interval_approximation(t)
			f = I.polynomial(self.degree, scale=10**t)
			
			if f(self) == 0:
				break
			else:
				t = 2 * t
		return f
	
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
	
	def interval_approximation(self, accuracy=0):
		''' Return an interval containing this algebraic number, correct to at least the requested accuracy. '''
		
		min_accuracy = 0
		target_accuracy = max(accuracy, min_accuracy)
		
		if self._interval is None or self._interval.accuracy < target_accuracy:
			# We need to request a little more accuracy for the intervals of \lmbda**i because of the sum.
			# We need at least: max(flipper.kernel.height_int(coefficient) for coefficient in self) + self.degree
			# more, but that involves a lot of logs so we'll use:
			request_accuracy = target_accuracy + self.height
			intervals = self.number_field.lmbda_approximations(request_accuracy)
			self._interval = flipper.kernel.dot(self, intervals)
			assert(self._interval.accuracy >= target_accuracy)
		
		return self._interval
	
	def algebraic_approximation(self, accuracy=None):
		''' Return an AlgebraicApproximation of this element which is correct to at least the requested accuracy.
		
		The accuracy returned is at least the minimum accuracy needed to determine a unique algebraic number. '''
		
		# Let:
		# Suppose that L is generator of N and this algebraic number is:
		#   a_0 + a_1 L + ... + a_D L^D.
		#   = a_0 + (a_1 + ( ... (a_{D-1} + a_D L) ... ) L ) L.
		# Then by induction on D:
		#   h(self) <= sum(h(a_i)) + d (h(L) + lg(2)) and
		#   deg(self) <= D.
		if accuracy is None: accuracy = 0
		min_accuracy = self.height + self.log_degree
		target_accuracy = max(accuracy, min_accuracy)
		
		request_accuracy = target_accuracy
		
		return flipper.kernel.AlgebraicApproximation(self.interval_approximation(request_accuracy), self.log_degree, self.height)

