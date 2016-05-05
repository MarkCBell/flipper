
import flipper

import cypari

def lcm(numbers):
	''' Return the lcm of a list of numbers. '''
	
	x = cypari.gen.pari(1)
	for number in numbers:
		x = cypari.all.pari_gen.lcm(x, cypari.gen.pari(number))
	
	return int(x)

def directed_eigenvector(action_matrix, condition_matrix):
	''' An implementation of flipper.kernel.symboliccomputation.directed_eigenvector() using CyPari.
	
	See the docstring of the above function for further details. '''
	
	x = cypari.gen.pari('x')
	
	M = cypari.gen.pari.matrix(action_matrix.width, action_matrix.height, action_matrix.flatten())
	f = M.charpoly()
	
	for poly in f.factor()[0]:
		degree = int(poly.poldegree())
		if degree > 1:
			flipper_poly = flipper.kernel.Polynomial([int(poly.polcoeff(i)) for i in range(degree+1)])
			
			a = x.Mod(poly)
			kernel_basis = (M - a).matker()
			
			basis = [[[entry.lift().polcoeff(i) for i in range(degree)] for entry in v] for v in kernel_basis]
			
			scale = lcm([int(coeff.denominator()) for v in basis for entry in v for coeff in entry])
			
			scaled_basis = [[[(int(coeff.numerator()) * scale) / int(coeff.denominator()) for coeff in entry] for entry in v] for v in basis]
			
			for flipper_polynomial_root in sorted(flipper_poly.real_roots(), reverse=True):
				if flipper_polynomial_root >= 1:
					N = flipper.kernel.NumberField(flipper_polynomial_root)
					
					flipper_basis_matrix = flipper.kernel.Matrix([[N.element(entry) for entry in v] for v in scaled_basis])
					
					if len(flipper_basis_matrix) == 1:  # If rank(kernel) == 1.
						flipper_eigenvector = flipper_basis_matrix[0]
						if flipper.kernel.matrix.nonnegative(flipper_eigenvector) and condition_matrix.nonnegative_image(flipper_eigenvector):
							return N.lmbda, flipper_eigenvector
					else:
						T = (flipper.kernel.id_matrix(condition_matrix.width).join(condition_matrix)) * flipper_basis_matrix.transpose()
						try:
							linear_combination = T.find_vector_with_nonnegative_image()
							return N.lmbda, flipper_basis_matrix.transpose()(linear_combination)
						except flipper.AssumptionError:  # Eigenspace is disjoint from the cone.
							pass
		
	
	raise flipper.ComputationError('No interesting eigenvalues in cell.')

