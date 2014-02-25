
from math import log10 as log

import Flipper

_name = 'dummy'

# This symbolic calculation library provides a dummy AlgebraicType class which
# holds a single value and can add, subtract ...
# Other librarys can modify this class to save them from implementing 
# all of these features from scratch. Features which don't work should be removed
# by setting the functions to NotImplemented.

class AlgebraicType(object):
	def __init__(self, value):
		# We make sure to always start by using AlgebraicType.algebraic_simplify(), just to be safe.
		self.value = value
		self.algebraic_simplify()
	
	def __str__(self):
		return str(self.value)
	
	def __repr__(self):
		return repr(self.value)
	
	def algebraic_simplify(self):
		pass
	
	def algebraic_minimal_polynomial_coefficients(self):
		return None
	
	def algebraic_degree(self):
		return len(self.algebraic_minimal_polynomial_coefficients()) - 1
	
	def algebraic_log_height(self):
		return log(max(abs(x) for x in self.algebraic_minimal_polynomial_coefficients()))
	
	def algebraic_approximate(self, accuracy, degree=None, power=1):
		return None

def Perron_Frobenius_eigen(matrix):
	raise ImportError('Dummy symbolic computation library cannot do this calculation.')
	return None

def eigenvector_from_eigenvalue(matrix, eigenvalue):
	N = Flipper.kernel.numberfield.NumberField(eigenvalue)
	d = eigenvalue.algebraic_degree()
	w = matrix.width
	
	Id_d = Flipper.kernel.matrix.Id_Matrix(d)
	eigen_companion = Flipper.kernel.matrix.Companion_Matrix(eigenvalue.algebraic_minimal_polynomial_coefficients())
	
	M2 = matrix.substitute_row(0, [1] * len(matrix))
	M3 = Flipper.kernel.matrix.Id_Matrix(w).substitute_row(0, [0] * w)
	
	M4 = (M2 ^ Id_d) - (M3 ^ eigen_companion)
	
	solution = M4.solve([1] + [0] * (len(M4)-1))
	return [N.element(solution[i:i+d]) for i in range(0, len(solution), d)]

