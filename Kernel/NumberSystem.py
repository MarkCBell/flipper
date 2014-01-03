
from math import log10 as log

from Flipper.Kernel.AlgebraicApproximation import Algebraic_Approximation, algebraic_approximation_from_symbolic, log_height
from Flipper.Kernel.SymbolicComputation import symbolic_degree, symbolic_height

# This class represents the number ring ZZ[x_1, ..., x_n] where x_1, ..., x_n are elements of K := QQ(\lambda)
# and are given as the list of generators. We always include the generator 1 as the last generator. We store
# an algebraic approximation of each generator, correct to the current accuracy. We can increase the 
# accuracy at any point.
class Number_System:
	def __init__(self, generators, degree, initial_accuracy=100):
		self.generators = generators + [1]
		self.sum_log_height_generators = sum(log_height(generator) for generator in self.generators)
		self.degree = degree  # We assume that this is degree(\lambda)).
		self.log_degree = log(self.degree)
		self.current_accuracy = initial_accuracy
		self.algebraic_approximations = [algebraic_approximation_from_symbolic(generator, self.current_accuracy, degree=self.degree) for generator in self.generators]
		self.verbose = False
	def __len__(self):
		return len(self.generators)
	def increase_accuracy(self, accuracy):
		if self.current_accuracy < accuracy:
			# Increasing the accuracy is expensive, so when we have to do it we'll get a fair amount more just to amortise the cost
			self.current_accuracy = 2 * accuracy  # We'll actually work to double what is requested.
			if self.verbose: print('Recomputing number system to %d places.' % self.current_accuracy)
			self.algebraic_approximations = [algebraic_approximation_from_symbolic(generator, self.current_accuracy, degree=self.degree) for generator in self.generators]

# This class represents an element of a Number_System. At any point we can convert it to an Algebraic_Approximation. In fact we have
# to do this if you want to do multiply or divide two of these.
class Number_System_Element:
	def __init__(self, number_system, linear_combination):
		self.number_system = number_system
		self.linear_combination = linear_combination
		self._algebraic_approximation = None
		self.current_accuracy = -1
	def __repr__(self):
		return str(self.algebraic_approximation())
		# return str(self.linear_combination)
	def __iter__(self):
		return iter(self.linear_combination)
	def __neg__(self):
		return Number_System_Element(self.number_system, [-a for a in self])
	def __add__(self, other):
		if isinstance(other, Number_System_Element):
			if self.number_system != other.number_system:
				raise TypeError('Cannot add elements of different number systems.')
			return Number_System_Element(self.number_system, [a+b for a, b in zip(self, other)])
		elif isinstance(other, Algebraic_Approximation):
			return self.algebraic_approximation() + other
		elif isinstance(other, int):
			return Number_System_Element(self.number_system, self.linear_combination[:-1] + [self.linear_combination[-1] + other])
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, Number_System_Element):
			if self.number_system != other.number_system:
				raise TypeError('Cannot subtract elements of different number systems.')
			return Number_System_Element(self.number_system, [a-b for a, b in zip(self, other)])
		elif isinstance(other, Algebraic_Approximation):
			return self.algebraic_approximation() - other
		elif isinstance(other, int):
			return Number_System_Element(self.number_system, self.linear_combination[:-1] + [self.linear_combination[-1] - other])
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, Number_System_Element):
			return self.algebraic_approximation(factor=2) * other.algebraic_approximation(factor=2)
		elif isinstance(other, Algebraic_Approximation):
			return self.algebraic_approximation(factor=2) * other
		elif isinstance(other, int):
			return Number_System_Element(self.number_system, [a * other for a in self])
		else:
			return NotImplemented
	def __rmul__(self, other):
		return self * other
	def __div__(self, other):
		if isinstance(other, Number_System_Element):
			return self.algebraic_approximation(factor=2) / other.algebraic_approximation(factor=2)
		elif isinstance(other, Algebraic_Approximation):
			return self.algebraic_approximation(factor=2) / other
		elif isinstance(other, int):
			return self.algebraic_approximation(factor=2) / other
		else:
			return NotImplemented
	def __truediv__(self, other):
		return self.__div__(other)
	def __rdiv__(self, other):
		return NotImplemented  # !?!
	def algebraic_approximation(self, accuracy=None, factor=None):
		# If no accuracy is given, calculate how much accuracy is needed to ensure that
		# the Algebraic_Approximation produced is well defined.
		N = self.number_system
		
		# Let n := len(N).
		# Let [a_i] := self.linear_combination, [\alpha_i] := N.algebraic_approximations and [I_i] := [\alpha_i.interval].
		# Let \alpha := sum(a_i * \alpha_i) and I := \alpha.interval = sum(a_i * I_i)
		# As \alpha also lies in K = QQ(\lambda) it also has degree at most deg(N).
		
		# Now if acc(I_i) == k then acc(I) >= k - (n-1) [Interval.py L:13].
		# Additionally, 
		#	log(height(\alpha)) <= sum(log(height(a_i \alpha_i))) + (n-1) * log(2) <= sum(log(a_i)) + sum(log(\alpha_i)) + (n-1) * log(2) [AlgebraicApproximation.py L:9].
		# Hence for \alpha to determine a unique algebraic number we need that:
		#	acc(I) >= log(deg(\alpha)) + log(height(\alpha)).
		# That is:
		#	k - (n-1) >= log(deg(\alpha)) + sum(log(a_i)) + sum(log(\alpha_i)) + (n-1) * log(2).
		# Hence:
		#	k >= sum(log(a_i)) + N.sum_log_height_generators + N.log_degree + (n-1) * (1 + log(2)).
		
		# Therefore we start by setting the accuracy of each I_i to at least:
		#	int(sum(log(a_i)) + N.sum_log_height_generators + N.log_degree + 2*n).
		
		if accuracy is None: accuracy = int(sum(log_height(a) for a in self) + N.sum_log_height_generators + 2*len(N) + N.log_degree)
		if factor is None: factor = 1
		accuracy = accuracy * factor
		
		if self._algebraic_approximation is None or self.current_accuracy < accuracy:
			self.number_system.increase_accuracy(accuracy)  # Increase the accuracy so the calculation will work.
			# Actually this will probably be too precise.
			self._algebraic_approximation = sum(generator_approximation * a for a, generator_approximation in zip(self, self.number_system.algebraic_approximations))
			self.current_accuracy = self._algebraic_approximation.interval.accuracy
			assert(self.current_accuracy > accuracy)
		
		return self._algebraic_approximation
	def __lt__(self, other):
		return (self - other).algebraic_approximation() < 0
	def __eq__(self, other):
		return (self - other).algebraic_approximation() == 0
	def __gt__(self, other):
		return (self - other).algebraic_approximation() > 0

#### Some special Number systems we know how to build.

def number_system_basis(generators):
	degree = max(symbolic_degree(generator) for generator in generators)
	N = Number_System(generators, degree)
	# Remember that the number system has one extra generator (1) that we didn't install at the end of its list of generators.
	return [Number_System_Element(N, [0] * i + [1] + [0] * (len(generators) - i)) for i in range(len(generators))]
