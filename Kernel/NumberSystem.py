
from math import log10 as log

from Flipper.Kernel.SymbolicComputation import symbolic_degree, symbolic_height
from Flipper.Kernel.AlgebraicApproximation import algebraic_approximation_from_symbolic, log_height

# This class represents the number ring ZZ[x_1, ..., x_n] where x_1, ..., x_n are elements of QQ(\lambda)
# and given as the list of generators. We always include the generator 1 as the last generator. We store
# an algebraic approximation of each generator, correct to the current precision. We can increase the 
# precision at any point.  
class Number_System:
	def __init__(self, generators, degree, initial_precision=100):
		self.generators = generators + [1]
		self.sum_log_height_generators = sum(log_height(generator) for generator in self.generators)
		self.log_degree = log(degree)  # We assume that this is log(degree(\lambda))
		self.current_precision = initial_precision
		self.algebraic_approximations = [algebraic_approximation_from_symbolic(generator, self.current_precision) for generator in self.generators]
	def __len__(self):
		return len(self.generators)
	def increase_precision(self, precision):
		if self.current_precision < precision:
			# Increasing the precision is expensive, so when we have to do it we'll get a fair amount more just to amortise the cost
			self.current_precision = 2 * precision  # We'll actually work to double what is requested.
			print('Recomputing number system to %d places.' % self.current_precision)
			self.algebraic_approximations = [algebraic_approximation_from_symbolic(generator, self.current_precision) for generator in self.generators]

# This class represents an element of a Number_System.
class Number_System_Element:
	def __init__(self, number_system, linear_combination):
		self.number_system = number_system
		self.linear_combination = linear_combination
		self._algebraic_approximation = None
		self.current_precision = -1
	def __repr__(self):
		return str(self.algebraic_approximation())
	def __iter__(self):
		return iter(self.linear_combination)
	def __neg__(self):
		return Number_System_Element(self.number_system, [-a for a in self])
	def __add__(self, other):
		if isinstance(other, Number_System_Element):
			if self.number_system != other.number_system:
				raise TypeError('Cannot add elements of different number systems.')
			return Number_System_Element(self.number_system, [a+b for a, b in zip(self, other)])
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
		elif isinstance(other, int):
			return Number_System_Element(self.number_system, self.linear_combination[:-1] + [self.linear_combination[-1] - other])
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def algebraic_approximation(self, precision=None, factor=None):
		# If no precision is given, calculate how much precision is needed to ensure that
		# the Algebraic_Approximation produced is well defined.
		N = self.number_system
		if precision is None: precision = int(sum(log_height(a) for a in self) + N.sum_log_height_generators + 2*len(N) + N.log_degree) + 2
		if factor is None: factor = 1
		precision = precision * factor
		
		if self._algebraic_approximation is None or self.current_precision < precision:
			self.number_system.increase_precision(precision)  # Increase the precision so the calculation will work.
			# Actually this will probably be too precise.
			self._algebraic_approximation = sum(generator_approximation * a for a, generator_approximation in zip(self, self.number_system.algebraic_approximations))
			self.current_precision = self._algebraic_approximation.interval.accuracy
			assert(self.current_precision > precision)
		
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
