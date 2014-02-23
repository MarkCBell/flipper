
from math import log10 as log

_name = 'dummy'

# This symbolic calculation library provides a dummy AlgebraicType class which
# holds a single value and can add, subtract ...
# Other librarys can modify this class to save them from implementing 
# all of these features from scratch. Features which don't work should be removed
# by setting the functions to NotImplemented.

class AlgebraicType(object):
	def __init__(self, value):
		# We make sure to always start by using AlgebraicType.algebraic_simplify(), just to be safe.
		self.value = self.algebraic_simplify(value)
	
	def __str__(self):
		return str(self.value)
	
	def __repr__(self):
		return repr(self.value)
	
	def __neg__(self):
		return AlgebraicType(-self)
	
	def __add__(self, other):
		if isinstance(other, AlgebraicType):
			return AlgebraicType(self.value + other.value)
		else:
			return AlgebraicType(self.value + other)
	
	def __radd__(self, other):
		return self + other
	
	def __sub__(self, other):
		if isinstance(other, AlgebraicType):
			return AlgebraicType(self.value - other.value)
		else:
			return AlgebraicType(self.value - other)
	
	def __rsub__(self, other):
		return -(self - other)
	
	def __mul__(self, other):
		if isinstance(other, AlgebraicType):
			return AlgebraicType(self.value * other.value)
		else:
			return AlgebraicType(self.value * other)
	
	def __rmul__(self, other):
		return self * other
	
	def __div__(self, other):
		if isinstance(other, AlgebraicType):
			return AlgebraicType(self.value / other.value)
		else:
			return AlgebraicType(self.value / other)
	
	def __truediv__(self, other):
		return self.__div__(other)
	
	def __rdiv__(self, other):
		if isinstance(other, AlgebraicType):
			return AlgebraicType(other.value / self.value)
		else:
			return AlgebraicType(other / self.value)
	
	def __rtruediv__(self, other):
		return self.__rdiv__(other)
	
	def __lt__(self, other):
		if isinstance(other, AlgebraicType):
			return self.value < other.value
		else:
			return self.value < other
	
	def __eq__(self, other):
		if isinstance(other, AlgebraicType):
			return self.value == other.value
		else:
			return self.value == other
	
	def __gt__(self, other):
		if isinstance(other, AlgebraicType):
			return self.value > other.value
		else:
			return self.value > other
	
	def __ge__(self, other):
		return self > other or self == other
	
	def __le__(self, other):
		return self < other or self == other
	
	def algebraic_simplify(self, value=None):
		if value is not None: 
			return value
		else:
			return self
	
	def algebraic_hash(self):
		return None
	
	def algebraic_minimal_polynomial_coefficients(self):
		return None
	
	def algebraic_hash_ratio(self, other):
		return (self / other).algebraic_hash()
	
	def algebraic_degree(self):
		return -1
	
	def algebraic_log_height(self):
		return -1
	
	def algebraic_approximate(self, accuracy, degree=None, power=1):
		return None

def Perron_Frobenius_eigen(matrix):
	raise ImportError('Dummy symbolic computation library cannot do this calculation.')
	return None

def algebraic_type_from_int(integer):
	raise ImportError('Dummy symbolic computation library cannot do this calculation.')
	return None
