
''' A module for interfacing with Sage. '''

from __future__ import absolute_import

import flipper

from sage.all import Matrix, NumberField, lcm  # pylint: disable=import-error, no-name-in-module

def directed_eigenvector(action_matrix, condition_matrix):
    ''' An implementation of flipper.kernel.symboliccomputation.directed_eigenvector() using Sage.
    
    See the docstring of the above function for further details. '''
    
    M = Matrix(action_matrix.rows)
    
    for polynomial, _ in M.characteristic_polynomial().factor():
        degree = int(polynomial.degree())
        
        if degree > 1:
            K = flipper.kernel.RealNumberField([int(x) for x in polynomial.coefficients(sparse=False)])
            
            if K.lmbda >= 1:
                # Compute the kernel:
                K = NumberField(polynomial, 'L')
                a = K.gen()
                
                kernel_basis = (M - a).right_kernel().basis()
                
                basis = [[entry.polynomial().coefficients(sparse=False) for entry in v] for v in kernel_basis]
                scale = lcm([int(coeff.denominator()) for v in basis for entry in v for coeff in entry])
                scaled_basis = [[[int(int(coeff.numerator()) * scale) / int(coeff.denominator()) for coeff in entry] for entry in v] for v in basis]
                
                flipper_basis_matrix = flipper.kernel.Matrix([[K(entry) for entry in v] for v in scaled_basis])
                
                if len(flipper_basis_matrix) == 1:  # If rank(kernel) == 1.
                    [flipper_eigenvector] = flipper_basis_matrix
                    if flipper.kernel.matrix.nonnegative(flipper_eigenvector) and condition_matrix.nonnegative_image(flipper_eigenvector):
                        return K.lmbda, flipper_eigenvector
                else:
                    # We could use sage.Polyhedron here.
                    pass
    
    raise flipper.ComputationError('No interesting eigenvalues in cell.')

