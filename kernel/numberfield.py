
from __future__ import print_function
from math import log10 as log

import Flipper

# Eventually this will replace numbersystem as a way of storing / manipulating
# elements of QQ(\lambda). The advantage that this has is that it can do multiplication
# of these elements without having to drop to an AlgebraicApproximation. However
# this requires the symbolic computation library to return the entries of the 
# eigenvector of a PF matrix as linear combinations of 1, \lambda, ..., \lambda^{d-1}.

log_height_int = Flipper.kernel.algebraicapproximation.log_height_int

class NumberField(object):
	def __init__(self, generator):
		self.generator = generator
		self.minpoly_coefficients = self.generator.algebraic_minimal_polynomial_coefficients()
		self.generator_d = [-a for a in self.minpoly_coefficients[:-1]]  # The expression of self.generator^d.
		self.degree = len(self.minpoly_coefficients) - 1
		self.log_height = max(log_height_int(coefficient) for coefficient in self.minpoly_coefficients)
		self.sum_log_height_powers = self.degree * self.degree * self.log_height
		
		self.verbose = False
		self.current_accuracy = -1
		self.algebraic_approximations = [None] * self.degree  # A list of approximations of \lambda^0, ..., \lambda^(d-1).
		self.increase_accuracy(100)
	
	def increase_accuracy(self, accuracy):
		if self.current_accuracy < accuracy:
			# Increasing the accuracy is expensive, so when we have to do it we'll get a fair amount more just to amortise the cost
			self.current_accuracy = 2 * accuracy  # We'll actually work to double what is requested.
			if self.verbose: print('Recomputing number system to %d places.' % self.current_accuracy)
			self.algebraic_approximations = [self.generator.algebraic_approximate(self.current_accuracy, degree=self.degree, power=index) for index in range(self.degree)]
	
	def element(self, linear_combination):
		return NumberFieldElement(self, linear_combination)

class NumberFieldElement(object):
	def __init__(self, number_field, linear_combination):
		self.number_field = number_field
		if len(linear_combination) < self.number_field.degree:
			linear_combination = linear_combination + [0] * (self.number_field.degree - len(linear_combination))
		self.linear_combination = linear_combination
		self._algebraic_approximation = None
		self.current_accuracy = -1
	
	def __repr__(self):
		return ' + '.join('%d L^%d' % (coefficient, index) for index, coefficient in enumerate(self)) + ' ~= ' + str(self.algebraic_approximation())
	def __iter__(self):
		return iter(self.linear_combination)
	
	def __neg__(self):
		return NumberFieldElement(self.number_field, [-a for a in self])
	def __add__(self, other):
		if isinstance(other, NumberFieldElement):
			if self.number_field != other.number_field:
				raise TypeError('Cannot add elements of different number systems.')
			return NumberFieldElement(self.number_field, [a+b for a, b in zip(self, other)])
		elif isinstance(other, Flipper.Integer_Type):
			return NumberFieldElement(self.number_field, [self.linear_combination[0] + other] + self.linear_combination[1:])
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, NumberFieldElement):
			if self.number_field != other.number_field:
				raise TypeError('Cannot subtract elements of different number systems.')
			return NumberFieldElement(self.number_field, [a-b for a, b in zip(self, other)])
		elif isinstance(other, Flipper.Integer_Type):
			return NumberFieldElement(self.number_field, [self.linear_combination[0] - other] + self.linear_combination[1:])
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, NumberFieldElement):
			if self.number_field != other.number_field:
				raise TypeError('Cannot add elements of different number systems.')
			
			w = [a * other.linear_combination[0] for a in self]
			x = [0] + self.linear_combination[:-1]
			y = [a * self.linear_combination[-1] for a in self.number_field.generator_d]
			z = other.linear_combination[1:] + [0]
			
			W = NumberFieldElement(self.number_field, w)
			X = NumberFieldElement(self.number_field, x)
			Y = NumberFieldElement(self.number_field, y)
			Z = NumberFieldElement(self.number_field, z)
			
			if z == [0] * self.number_field.degree:
				return W
			else:
				return W + (X + Y) * Z
		elif isinstance(other, Flipper.Integer_Type):
			w = [a * other for a in self]
			assert(len(w) == len(self.linear_combination))
			return NumberFieldElement(self.number_field, w)
		else:
			return NotImplemented
	def __rmul__(self, other):
		return self * other
	def __div__(self, other):
		if isinstance(other, NumberFieldElement):
			if self.number_field != other.number_field:
				raise TypeError('Cannot add elements of different number systems.')
			
			return self.algebraic_approximation(multiplicative_error=3) / other.algebraic_approximation(multiplicative_error=3) 
		else:
			return NotImplemented
	def __truediv__(self, other):
		return self.__div__(other)
	
	def __lt__(self, other):
		return (self - other).is_negative()
	def __eq__(self, other):
		return (self - other).is_zero()
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
	
	def algebraic_approximation(self, accuracy=None, multiplicative_error=1, additive_error=0):
		# If no accuracy is given, calculate how much accuracy is needed to ensure that
		# the AlgebraicApproximation produced is well defined.
		N = self.number_field
		
		# Let N = QQ(\lambda) and d := N.degree.
		# Let [a_i] := self.linear_combination, [\alpha_i] := \lambda^i.algebraic_approximations and [I_i] := [\alpha_i.interval].
		# Let \alpha := sum(a_i * \alpha_i) and I := \alpha.interval = sum(a_i * I_i)
		# As \alpha also lies in K = QQ(\lambda) it also has degree at most d.
		
		# Now if acc(I_i) >= k then acc(I) >= k - (d-1) [Interval.py L:13].
		# Additionally, 
		#	log(height(\alpha)) <= sum(log(height(a_i \alpha_i))) + log(d) <= sum(log(a_i)) + sum(log(height(\alpha_i))) + d log(2) [AlgebraicApproximation.py L:9].
		# Hence for \alpha to determine a unique algebraic number we need that:
		#	acc(I) >= log(d)) + log(height(\alpha)).
		# That is:
		#	k - (d-1) >= log(n) + sum(log(a_i)) + sum(log(height(\alpha_i))) + d log(2).
		# Hence:
		#	k >= sum(log(a_i)) + N.sum_log_height_powers + log(N.degree) + (d-1) + d log(2).
		
		# Therefore we start by setting the accuracy of each I_i to at least:
		#	int(sum(log(a_i)) + N.sum_log_height_powers + log(N.degree) + 2*d).
		if accuracy is None: accuracy = int(sum(log_height_int(coefficient) for coefficient in self) + N.sum_log_height_powers + log(N.degree) + 2*N.degree)
		accuracy = accuracy * multiplicative_error + additive_error
		
		if self._algebraic_approximation is None or self.current_accuracy < accuracy:
			N.increase_accuracy(accuracy)  # Increase the accuracy so the calculation will work.
			# Actually this will probably be too precise.
			
			# Watch out there is an all zeros case to worry about. We'll be careful but this should never be used though.
			if all(a == 0 for a in self):
				self._algebraic_approximation = Flipper.kernel.algebraicapproximation.algebraic_approximation_from_int(0, 2*accuracy, self.number_field.degree, 1)
			else:
				self._algebraic_approximation = sum(a * generator_approximation for a, generator_approximation in zip(self, N.algebraic_approximations))
			
			self.current_accuracy = self._algebraic_approximation.interval.accuracy
			# Now if accuracy was not None then self.current_accuracy >= accuracy.
		
		return self._algebraic_approximation
	
	def algebraic_hash_ratio(self, other):
		# !?! RECHEK THIS AGAINST Interval.py.
		HASH_DENOMINATOR = 30
		
		i1 = self.algebraic_approximation(2*HASH_DENOMINATOR).interval.change_denominator(2*HASH_DENOMINATOR)
		i2 = other.algebraic_approximation(2*HASH_DENOMINATOR).interval.change_denominator(2*HASH_DENOMINATOR)
		return (i1 / i2).change_denominator(HASH_DENOMINATOR).tuple()
	