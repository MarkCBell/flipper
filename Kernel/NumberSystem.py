
from math import log10 as log

from Flipper.Kernel.SymbolicComputation import symbolic_degree, symbolic_height
from Flipper.Kernel.AlgebraicApproximation import algebraic_approximation_from_symbolic

# This class represents the number ring ZZ[x_1, ..., x_n] where x_1, ..., x_n are elements of QQ(\lambda)
# and given as the list of generators. We store an algebraic approximation of each generator, correct to
# the current precision. We can increase the precision at any point. We always include the generator 1 as the
# last generator.
class Number_System:
	def __init__(self, generators, initial_precision=200):
		self.generators = generators + [1]
		self.log_height_generators = [log(symbolic_height(generator)) for generator in self.generators]
		self.degree = symbolic_degree(self.generators[0])
		self.current_precision = initial_precision
		self.algebraic_approximations = [algebraic_approximation_from_symbolic(generator, self.current_precision) for generator in self.generators]
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
		self._current_precision = 0
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
		if precision is None: precision = int(sum(log(symbolic_height(a)) for a in self) + sum(self.number_system.log_height_generators) + log(self.number_system.degree)) + 1
		if factor is not None: precision = precision * factor 
		
		# print(precision, self.number_system.current_precision)
		if self._algebraic_approximation is None or self._current_precision < precision:
			# print('Recompute to %d' % precision)
			# if self.number_system.current_precision < precision:
				# print('Recompute number system to %d' % precision)
			self.number_system.increase_precision(precision)  # Increase the precision so the calculation will work.
			self._algebraic_approximation = sum(generator_approximation * a for a, generator_approximation in zip(self, self.number_system.algebraic_approximations) if a != 0)
			self._current_precision = precision
		
		return self._algebraic_approximation
	def __lt__(self, other):
		if isinstance(other, Number_System_Element):
			return (self - other).algebraic_approximation() < 0
		elif isinstance(other, int):
			return self.algebraic_approximation() - other < 0
		else:
			return NotImplemented
	def __eq__(self, other):
		if isinstance(other, Number_System_Element):
			return (self - other).algebraic_approximation() == 0
		elif isinstance(other, int):
			return self.algebraic_approximation() - other == 0
		else:
			return NotImplemented
	def __gt__(self, other):
		if isinstance(other, Number_System_Element):
			return (self - other).algebraic_approximation() > 0
		elif isinstance(other, int):
			return self.algebraic_approximation() - other > 0
		else:
			return NotImplemented

#### Some special Number systems we know how to build.

def number_system_basis(generators):
	N = Number_System(generators)
	return [Number_System_Element(N, [0] * i + [1] + [0] * (len(generators) - i)) for i in range(len(generators))]
