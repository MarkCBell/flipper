
import flipper

import cypari

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
			
			scale = flipper.kernel.product([int(coeff.denominator()) for v in basis for entry in v for coeff in entry])
			
			scaled_basis = [[[(int(coeff.numerator()) * scale) / int(coeff.denominator()) for coeff in entry] for entry in v] for v in basis]
			
			for flipper_polynomial_root in flipper_poly.real_roots():
				N = flipper.kernel.NumberField(flipper_polynomial_root)
				
				flipper_basis_matrix = flipper.kernel.Matrix([[N.element(entry) for entry in v] for v in scaled_basis])
				
				T = (flipper.kernel.id_matrix(condition_matrix.width).join(condition_matrix)) * flipper_basis_matrix.transpose()
				try:
					linear_combination = T.find_vector_with_nonnegative_image()
					return N.lmbda, flipper_basis_matrix.transpose()(linear_combination)
				except flipper.AssumptionError:  # Eigenspace is disjoint from the cone.
					pass
		
	
	raise flipper.ComputationError('No interesting eigenvalues in cell.')

