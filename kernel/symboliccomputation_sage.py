
from math import log10 as log

from sage.all import Matrix, lcm, simplify, AlgebraicNumber, NumberField, MatrixSpace

import Flipper
from Flipper.kernel.symboliccomputation_dummy import AlgebraicType

_name = 'sage'

def algebraic_simplify(self, value=None):
	if value is not None:
		value.simplify()
		return value
	else:
		self.value.simplify()
		return self

def algebraic_minimal_polynomial_coefficients(self):
	X = tuple(self.value.minpoly().coeffs())
	scale = abs(lcm([x.denominator() for x in X]))
	return tuple(int(scale * x) for x in X)

# We take the coefficients of the minimal polynomial of each entry and sort them. This has the nice property that there is a
# uniform bound on the number of collisions.
def algebraic_hash(self):
	return self.algebraic_minimal_polynomial_coefficients()

def algebraic_degree(self):
	return len(self.algebraic_minimal_polynomial_coefficients()) - 1

def algebraic_log_height(self):
	return log(max(abs(x) for x in self.algebraic_minimal_polynomial_coefficients()))

def algebraic_approximate(self, accuracy, degree=None, power=1):
	# First we need to correct for the fact that we may lose some digits of accuracy
	# if the integer part of the number is big.
	precision = accuracy + int(log(max((self.value**power).n(digits=1), 1))) + 1
	if degree is None: degree = self.algebraic_degree()  # If not given, assume that the degree of the number field is the degree of this number.
	A = Flipper.kernel.algebraicapproximation.algebraic_approximation_from_string(str((self.value**power).n(digits=precision)), degree, self.algebraic_log_height())
	assert(A.interval.accuracy >= accuracy)
	return A

AlgebraicType.algebraic_simplify = algebraic_simplify
AlgebraicType.algebraic_minimal_polynomial_coefficients = algebraic_minimal_polynomial_coefficients
AlgebraicType.algebraic_hash = algebraic_hash
AlgebraicType.algebraic_degree = algebraic_degree
AlgebraicType.algebraic_log_height = algebraic_log_height
AlgebraicType.algebraic_approximate = algebraic_approximate


def Perron_Frobenius_eigen(matrix, vector=None, condition_matrix=None):
	# Assumes that matrix is Perron-Frobenius and so has a unique real eigenvalue of largest
	# magnitude. If not an AssumptionError is thrown.
	
	APPROACH = 2
	
	if APPROACH == 0:
		M = Matrix(matrix.rows)
		eigenvalue = max(M.eigenvalues())
		N = M - eigenvalue
		try:
			[eigenvector] = N.right_kernel().basis()
		except ValueError:
			raise Flipper.AssumptionError('Matrix is not Perron-Frobenius.')
		
		s = sum(eigenvector)
		if s == 0:
			raise Flipper.AssumptionError('Matrix is not Perron-Frobenius.')
		
		eigenvector = [AlgebraicType(x / s).algebraic_simplify() for x in eigenvector]
	elif APPROACH == 1:
		M = Matrix(matrix.rows)
		eigenvalue = AlgebraicType(max(M.eigenvalues()))
		N = Flipper.kernel.numberfield.NumberField(eigenvalue)
		
		d = eigenvalue.algebraic_degree()
		Id_d = Flipper.kernel.matrix.Id_Matrix(d)
		eigen_companion = Flipper.kernel.matrix.Companion_Matrix(eigenvalue.algebraic_minimal_polynomial_coefficients())
		
		M2 = matrix.substitute_row(0, [1] * len(matrix))
		M3 = Id_d.substitute_row(0, [0] * d)
		
		M4 = M2 ^ Id_d - M3 ^ eigen_companion
		
		solution = M4.solve([1] + [0] * (len(M4)-1))
		
		eigenvector = [N.element(solution[i:i+d]) for i in range(0, len(solution), d)]
	elif APPROACH == 2:
		M = Matrix(matrix.rows)
		eigenvalue = max(M.eigenvalues())
		K = NumberField(eigenvalue.minpoly(), 'L')
		lam = K.gens()[0]
		
		try:
			[eigenvector] = (M - lam).right_kernel().basis()
		except ValueError:
			raise Flipper.AssumptionError('Matrix is not Perron-Frobenius.')
		
		scale = abs(lcm([x.denominator() for v in eigenvector for x in v.polynomial().coeffs()]))
		
		N = Flipper.kernel.numberfield.NumberField(AlgebraicType(eigenvalue))
		eigenvector = [N.element([int(scale * x) for x in v.polynomial().coeffs()]) for v in eigenvector]
	
	if condition_matrix is not None:
		if not condition_matrix.nonnegative_image(eigenvector):
			raise Flipper.AssumptionError('Could not estimate invariant lamination.')  # If not then the curve failed to get close enough to the invariant lamination.
	
	return eigenvector

def algebraic_type_from_int(integer):
	return AlgebraicType(AlgebraicNumber(integer))
