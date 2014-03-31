
import Flipper

symbolic_libaray_name = 'dummy'

def PF_eigen(matrix):
	eigenvalue_polynomial = matrix.char_poly().simplify()  # This may not be irreducible.
	eigenvalue_coefficients = eigenvalue_polynomial.coefficients
	
	# We will calculate the eigenvector ourselves.
	N = Flipper.kernel.NumberField(eigenvalue_polynomial)
	M = matrix - N.lmbda
	try:
		[eigenvector] = M.kernel()  # Sage is much better at this than us for large matrices.
	except ValueError:
		raise Flipper.AssumptionError('Largest real eigenvalue is repeated.')
	return eigenvalue_coefficients, [x.linear_combination for x in eigenvector]

