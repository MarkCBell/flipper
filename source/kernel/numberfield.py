
''' A module for representing and manipulating elements of number fields.

Provides two classes: NumberField and NumberFieldElement.

There is also a helper function: create_number_field. '''

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
HASH_DENOMINATOR = 30

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
		assert(polynomial_root.polynomial.is_monic())
		
		if polynomial_root is None: polynomial_root = flipper.kernel.create_polynomial_root([-1, 1], '1.00')
		self.polynomial_root = polynomial_root
		
		self.height = self.polynomial_root.height
		self.degree = self.polynomial_root.degree
		self.log_degree = self.polynomial_root.log_degree
		self.log_plus = self.polynomial_root.log_plus
		
		self.polynomial = self.polynomial_root.polynomial
		self.companion_matrices = self.polynomial.companion_matrix().powers(self.degree)
		
		self._approximations = None  # A list of approximations of lambda^0, ..., lambda^(d-1).
		self.accuracy = -1
		
		self.one = self.element([1])
		self.lmbda = self.element([1]) if self.is_rationals() else self.element([0, 1])  # lambda is a Python keyword.
	
	def lmbda_approximations(self, accuracy):
		''' Return intervals approximating lmbda^0, ..., lmbda^(degree-1) to the given accuracy.
		
		The intervals returned all have the same denominator and so addition / subtraction of these is fast. '''
		
		min_accuracy = 0
		target_accuracy = max(accuracy, min_accuracy)
		
		if self._approximations is None or self.accuracy < target_accuracy:
			# If I is an interval approximating L to k + digits then
			# I^i approximates L^i to at least k digits
			
			# Now note that if I is an interval approximating L to at
			# least k + N.log_plus digits of accuracy then I^i
			# approximates L^i to at least k digits of accuracy.
			request_accuracy = target_accuracy + self.degree * self.log_plus
			
			lmbda = self.polynomial_root.interval_approximation(request_accuracy)
			approximations = [lmbda**i for i in range(self.degree)]
			minimal_accuracy = min(interval.accuracy for interval in approximations)
			self._approximations = [interval.change_denominator(minimal_accuracy) for interval in approximations]
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
		# Now h(\alpha) <= sum(h(a_i \alpha_i)) + d log(2) <= sum(h(a_i)) + sum(h(\alpha_i)) + (d-1) log(2) [AlgebraicApproximation.py L:9].
		self._algebraic_approximation = None
		self.accuracy = -1
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return str(float(self.algebraic_approximation()))
	def __reduce__(self):
		# NumberFieldElements are already pickleable but this results in a smaller pickle.
		return (self.__class__, (self.number_field, self.linear_combination))
	def __iter__(self):
		return iter(self.linear_combination)
	def __len__(self):
		return self.number_field.degree
	def __float__(self):
		return float(self.algebraic_approximation())
	def __bool__(self):
		return self != 0
	def __nonzero__(self):  # For Python2.
		return self.__bool__()
	
	def __neg__(self):
		return NumberFieldElement(self.number_field, [-a for a in self])
	def __add__(self, other):
		if isinstance(other, NumberFieldElement):
			if self.number_field != other.number_field:
				raise TypeError('Cannot add elements of different number fields.')
			return NumberFieldElement(self.number_field, [a+b for a, b in zip(self, other)])
		elif isinstance(other, flipper.IntegerType):
			return NumberFieldElement(self.number_field, [self.linear_combination[0] + other] + self.linear_combination[1:])
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, NumberFieldElement):
			if self.number_field != other.number_field:
				raise TypeError('Cannot subtract elements of different number fields.')
			return NumberFieldElement(self.number_field, [a-b for a, b in zip(self, other)])
		elif isinstance(other, flipper.IntegerType):
			return NumberFieldElement(self.number_field, [self.linear_combination[0] - other] + self.linear_combination[1:])
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, NumberFieldElement):
			if self.number_field != other.number_field:
				raise TypeError('Cannot multiply elements of different number fields.')
			
			return self.number_field.element(flipper.kernel.dot(self, self.number_field.companion_matrices)(other.linear_combination))
		elif isinstance(other, flipper.IntegerType):
			return self.number_field.element([a * other for a in self])
		else:
			return NotImplemented
	def __rmul__(self, other):
		return self * other
	
	def __divmod__(self, other):
		if isinstance(other, flipper.IntegerType):
			return self.number_field.element([coeff // other for coeff in self]), self.number_field.element([coeff % other for coeff in self])
		else:
			return NotImplemented
	def __mod__(self, other):
		_, remainder = divmod(self, other)
		return remainder
	def __div__(self, other):
		quotient, remainder = divmod(self, other)
		if not remainder.is_zero():  # Division isn't perfect.
			raise ValueError('Cannot divide this algebraic number in %s' % str(self.number_field))
		return quotient
	
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
	
	def algebraic_approximation(self, accuracy=0):
		''' Return an AlgebraicApproximation of this element which is correct to at least the requested accuracy.
		
		The accuracy returned is at least the minimum accuracy needed to determine a unique algebraic number. '''
		
		# Let:
		N = self.number_field
		d = N.log_degree
		
		# Suppose that L is generator of N and this algebraic number is:
		#   a_0 + a_1 L + ... + a_D L^D.
		#   = a_0 + (a_1 + ( ... (a_{D-1} + a_D L) ... ) L ) L.
		# Then by induction on D:
		#   h(self) <= sum(h(a_i)) + d (h(L) + lg(2)) and
		#   deg(self) <= D.
		h = sum(flipper.kernel.height_int(coefficient) for coefficient in self) + N.degree * (N.height + LOG_2)
		min_accuracy = h + d
		target_accuracy = max(accuracy, min_accuracy)
		
		if self._algebraic_approximation is None or self.accuracy < target_accuracy:
			# Now note that if I_i is an interval approximating L^i to at
			# least k + max(h(a_i) + D digits of accuracy then sum(a_i I_i)
			# approximates self to at least k digits of accuracy.
			request_accuracy = target_accuracy + max(flipper.kernel.height_int(coefficient) for coefficient in self) + N.degree
			
			intervals = N.lmbda_approximations(request_accuracy)
			self._algebraic_approximation = flipper.kernel.AlgebraicApproximation(flipper.kernel.dot(self, intervals), d, h)
			self.accuracy = self._algebraic_approximation.interval.accuracy
			assert(self.accuracy >= target_accuracy)
		
		return self._algebraic_approximation
	
	def algebraic_hash_ratio(self, other):
		''' Return a hashable object representing this algebraic number / other. '''
		
		# !?! RECHEK THIS AGAINST interval.py.
		
		i1 = self.algebraic_approximation(2*HASH_DENOMINATOR).interval.change_denominator(2*HASH_DENOMINATOR)
		i2 = other.algebraic_approximation(2*HASH_DENOMINATOR).interval.change_denominator(2*HASH_DENOMINATOR)
		return (i1 / i2).change_denominator(HASH_DENOMINATOR).tuple()

def create_number_field(coefficients, strn):
	''' A short way of constructing a NumberField from a list of coefficients and a string. '''
	
	return flipper.kernel.NumberField(flipper.kernel.create_polynomial_root(coefficients, strn))

