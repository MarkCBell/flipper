
from __future__ import print_function
from math import log10 as log

import Flipper

# This class represents the number ring ZZ[x_1, ..., x_n] where x_1, ..., x_n are elements of K := QQ(\lambda)
# and are given as the list of generators and an upper bound on the degree of K. We store an algebraic
# approximation of each generator, correct to the current accuracy. We can increase the accuracy at any point.
class NumberSystem:
	def __init__(self, generators, degree):
		self.generators = generators
		self.sum_log_height_generators = sum(generator.algebraic_log_height() for generator in generators)
		self.degree = degree  # We assume that this is degree(\lambda)).
		self.log_degree = log(self.degree)
		
		self.verbose = False
		self.current_accuracy = -1
		self.algebraic_approximations = [None] * len(self.generators)
		self.increase_accuracy(100)
	
	def __len__(self):
		return len(self.generators)
	
	def increase_accuracy(self, accuracy):
		if self.current_accuracy < accuracy:
			# Increasing the accuracy is expensive, so when we have to do it we'll get a fair amount more just to amortise the cost
			self.current_accuracy = 2 * accuracy  # We'll actually work to double what is requested.
			if self.verbose: print('Recomputing number system to %d places.' % self.current_accuracy)
			self.algebraic_approximations = [generator.algebraic_approximate(self.current_accuracy, degree=self.degree) for generator in self.generators]

# This class represents an element of a NumberSystem. At any point we can convert it to an Flipper.kernel.algebraicapproximation. In fact we have
# to do this if you want to do multiply or divide two of these.
class NumberSystemElement:
	def __init__(self, NumberSystem, linear_combination):
		self.NumberSystem = NumberSystem
		self.linear_combination = linear_combination
		self._algebraic_approximation = None
		self.current_accuracy = -1
	def __repr__(self):
		return str(self.algebraic_approximation())
		# return str(self.linear_combination)
	def __iter__(self):
		return iter(self.linear_combination)
	def __neg__(self):
		return NumberSystemElement(self.NumberSystem, [-a for a in self])
	def __add__(self, other):
		if isinstance(other, NumberSystemElement):
			if self.NumberSystem != other.NumberSystem:
				raise TypeError('Cannot add elements of different number systems.')
			return NumberSystemElement(self.NumberSystem, [a+b for a, b in zip(self, other)])
		elif isinstance(other, Flipper.kernel.algebraicapproximation.AlgebraicApproximation):
			return self.algebraic_approximation() + other
		elif isinstance(other, Flipper.kernel.types.Integer_Type):
			if other == 0: return self
			return self.algebraic_approximation() + other
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, NumberSystemElement):
			if self.NumberSystem != other.NumberSystem:
				raise TypeError('Cannot subtract elements of different number systems.')
			return NumberSystemElement(self.NumberSystem, [a-b for a, b in zip(self, other)])
		elif isinstance(other, Flipper.kernel.algebraicapproximation.AlgebraicApproximation):
			return self.algebraic_approximation() - other
		elif isinstance(other, Flipper.kernel.types.Integer_Type):
			if other == 0: return self
			return self.algebraic_approximation() - other
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, NumberSystemElement):
			return self.algebraic_approximation(multiplicative_error=3, additive_error=3) * other.algebraic_approximation(multiplicative_error=3, additive_error=3)
		elif isinstance(other, Flipper.kernel.algebraicapproximation.AlgebraicApproximation):
			return self.algebraic_approximation(multiplicative_error=3, additive_error=3) * other
		elif isinstance(other, Flipper.kernel.types.Integer_Type):
			return NumberSystemElement(self.NumberSystem, [a * other for a in self])
		else:
			return NotImplemented
	def __rmul__(self, other):
		return self * other
	def __div__(self, other):
		if isinstance(other, NumberSystemElement):
			return self.algebraic_approximation(multiplicative_error=3, additive_error=3) / other.algebraic_approximation(multiplicative_error=3, additive_error=3)
		elif isinstance(other, Flipper.kernel.algebraicapproximation.AlgebraicApproximation):
			return self.algebraic_approximation(multiplicative_error=3, additive_error=3) / other
		elif isinstance(other, Flipper.kernel.types.Integer_Type):
			return self.algebraic_approximation(multiplicative_error=3, additive_error=3) / other
		else:
			return NotImplemented
	def __truediv__(self, other):
		return self.__div__(other)
	def __rdiv__(self, other):
		return other / self.algebraic_approximation(multiplicative_error=3, additive_error=3)
	def __rtruediv__(self, other):
		return self.__rdiv__(other)
	def algebraic_approximation(self, accuracy=None, multiplicative_error=1, additive_error=0):
		# If no accuracy is given, calculate how much accuracy is needed to ensure that
		# the AlgebraicApproximation produced is well defined.
		N = self.NumberSystem
		
		# Let n := len(N).
		# Let [a_i] := self.linear_combination, [\alpha_i] := N.algebraic_approximations and [I_i] := [\alpha_i.interval].
		# Let \alpha := sum(a_i * \alpha_i) and I := \alpha.interval = sum(a_i * I_i)
		# As \alpha also lies in K = QQ(\lambda) it also has degree at most deg(N).
		
		# Now if acc(I_i) == k then acc(I) >= k - (n-1) [Interval.py L:13].
		# Additionally, 
		#	log(height(\alpha)) <= sum(log(height(a_i \alpha_i))) + log(n) <= sum(log(a_i)) + sum(log(\alpha_i)) + n log(2) [AlgebraicApproximation.py L:9].
		# Hence for \alpha to determine a unique algebraic number we need that:
		#	acc(I) >= log(deg(\alpha)) + log(height(\alpha)).
		# That is:
		#	k - (n-1) >= log(deg(\alpha)) + sum(log(a_i)) + sum(log(\alpha_i)) + n log(2).
		# Hence:
		#	k >= sum(log(a_i)) + N.sum_log_height_generators + N.log_degree + (n-1) + n log(2).
		
		# Therefore we start by setting the accuracy of each I_i to at least:
		#	int(sum(log(a_i)) + N.sum_log_height_generators + N.log_degree + 2*n).
		if accuracy is None: accuracy = int(sum(Flipper.kernel.algebraicapproximation.log_height_int(a) for a in self) + N.sum_log_height_generators + 2*len(N) + N.log_degree)
		accuracy = accuracy * multiplicative_error + additive_error
		
		if self._algebraic_approximation is None or self.current_accuracy < accuracy:
			self.NumberSystem.increase_accuracy(accuracy)  # Increase the accuracy so the calculation will work.
			# Actually this will probably be too precise.
			
			# Watch out there is an all zeros case to worry about. We'll be careful but this should never be used though.
			if all(a == 0 for a in self):
				self._algebraic_approximation = Flipper.kernel.algebraicapproximation.algebraic_approximation_from_int(0, 2*accuracy, self.NumberSystem.degree, 1)
			else:
				self._algebraic_approximation = sum(generator_approximation * a for a, generator_approximation in zip(self, self.NumberSystem.algebraic_approximations))
			
			self.current_accuracy = self._algebraic_approximation.interval.accuracy
			# Now if accuracy was not None then self.current_accuracy >= accuracy.
		
		return self._algebraic_approximation
	def algebraic_hash_ratio(self, other):
		# !?! RECHEK THIS AGAINST Interval.py.
		HASH_DENOMINATOR = 30
		
		i1 = self.algebraic_approximation(2*HASH_DENOMINATOR).interval.change_denominator(2*HASH_DENOMINATOR)
		i2 = other.algebraic_approximation(2*HASH_DENOMINATOR).interval.change_denominator(2*HASH_DENOMINATOR)
		return (i1 / i2).change_denominator(HASH_DENOMINATOR).tuple()
	def __lt__(self, other):
		return (self - other).algebraic_approximation() < 0
	def __eq__(self, other):
		return (self - other).algebraic_approximation() == 0
	def __gt__(self, other):
		return (self - other).algebraic_approximation() > 0

#### Some special Number systems we know how to build.

def NumberSystem_basis(generators, degree):
	N = NumberSystem(generators, degree)
	return [NumberSystemElement(N, [0] * i + [1] + [0] * (len(generators) - i)) for i in range(len(generators))]
