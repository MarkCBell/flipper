
from math import log10 as log

_name = 'dummy'

# This symbolic calculation library provides a dummy Algebraic_Type class which
# holds a single value and can add, subtract ...
# Other librarys can modify this class to save them from implementing 
# all of these features from scratch. Features which don't work should be removed
# by setting the functions to NotImplemented.

class Algebraic_Type:
	def __init__(self, value):
		# We make sure to always start by using Algebraic_Type.algebraic_simplify(), just to be safe.
		self.value = self.algebraic_simplify(value)
	
	def __str__(self):
		return str(self.value)
	
	def __repr__(self):
		return repr(self.value)
	
	def __neg__(self):
		return Algebraic_Type(-self)
	
	def __add__(self, other):
		if isinstance(other, Algebraic_Type):
			return Algebraic_Type(self.value + other.value)
		else:
			return Algebraic_Type(self.value + other)
	
	def __radd__(self, other):
		return self + other
	
	def __sub__(self, other):
		if isinstance(other, Algebraic_Type):
			return Algebraic_Type(self.value - other.value)
		else:
			return Algebraic_Type(self.value - other)
	
	def __rsub__(self, other):
		return -(self - other)
	
	def __mul__(self, other):
		if isinstance(other, Algebraic_Type):
			return Algebraic_Type(self.value * other.value)
		else:
			return Algebraic_Type(self.value * other)
	
	def __rmul__(self, other):
		return self * other
	
	def __div__(self, other):
		if isinstance(other, Algebraic_Type):
			return Algebraic_Type(self.value / other.value)
		else:
			return Algebraic_Type(self.value / other)
	
	def __truediv__(self, other):
		return self.__div__(other)
	
	def __rdiv__(self, other):
		if isinstance(other, Algebraic_Type):
			return Algebraic_Type(other.value / self.value)
		else:
			return Algebraic_Type(other / self.value)
	
	def __rtruediv__(self, other):
		return self.__rdiv__(other)
	
	def __lt__(self, other):
		if isinstance(other, Algebraic_Type):
			return self.value < other.value
		else:
			return self.value < other
	
	def __eq__(self, other):
		if isinstance(other, Algebraic_Type):
			return self.value == other.value
		else:
			return self.value == other
	
	def __gt__(self, other):
		if isinstance(other, Algebraic_Type):
			return self.value > other.value
		else:
			return self.value > other
	
	def algebraic_simplify(self, value=None):
		if value is not None: 
			return value
		else:
			return self
	
	def algebraic_hash(self):
		return None
	
	def algebraic_hash_ratio(self, other):
		return (self / other).algebraic_hash()
	
	def algebraic_degree(self):
		return -1
	
	def algebraic_log_height(self):
		return -1
	
	def algebraic_approximate(self, accuracy, degree=None):
		return None

def Perron_Frobenius_eigen(matrix):
	return None

def algebraic_type_from_int(integer):
	return None
