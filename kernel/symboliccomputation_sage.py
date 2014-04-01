
from sage.all import Matrix, lcm, NumberField, QQ
from sage.rings.number_field.number_field import NumberField_generic

import Flipper

symbolic_libaray_name = 'sage'

def PF_eigen(matrix):
	# Assumes that matrix is Perron-Frobenius and so has a unique real eigenvalue of largest
	# magnitude. If not an AssumptionError is thrown.
	
	M = Matrix(matrix.rows)
	eigenvalue = max(M.eigenvalues(), key=abs)
	
	# We could just return None as the eigenvector but this is much faster.
	# We need to be a little careful, for some reason sage needs a variable name if eigenvalue is a rational.
	polynomial = eigenvalue.minpoly() if eigenvalue not in QQ else eigenvalue.minpoly('x')
	scale = abs(lcm([x.denominator() for x in polynomial.coeffs()]))
	eigenvalue_coefficients = [int(scale * x) for x in polynomial.coeffs()]
	
	K = NumberField(polynomial, 'L')
	[lam] = K.gens()
	
	try:
		D = M - lam
		[eigenvector] = (M - lam).right_kernel().basis()
	except ValueError:
		raise Flipper.AssumptionError('Matrix is not Perron-Frobenius.')
	
	scale2 = abs(lcm([x.denominator() for v in eigenvector for x in v.polynomial().coeffs()]))
	eigenvector_coefficients = [[int(scale2 * x) for x in v.polynomial().coeffs()] for v in eigenvector]
	
	return eigenvalue_coefficients, eigenvector_coefficients 

