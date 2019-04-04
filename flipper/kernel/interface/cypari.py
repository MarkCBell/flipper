
''' A module for interfacing with CyPari. '''

from __future__ import absolute_import

import cypari

import flipper

def directed_eigenvector(action_matrix, condition_matrix):
    ''' An implementation of flipper.kernel.symboliccomputation.directed_eigenvector() using CyPari.
    
    See the docstring of the above function for further details. '''
    
    x = cypari.pari('x')
    
    M = cypari.pari.matrix(action_matrix.width, action_matrix.height, action_matrix.flatten())
    
    for polynomial in M.charpoly().factor()[0]:
        degree = int(polynomial.poldegree())
        if degree > 1:
            try:
                K = flipper.kernel.RealNumberField([int(polynomial.polcoeff(i)) for i in range(degree+1)])
            except IndexError:
                continue
            
            if K.lmbda >= 1:
                # Compute the kernel:
                a = x.Mod(polynomial)
                kernel_basis = (M - a).matker()
                
                basis = [[[entry.lift().polcoeff(i) for i in range(degree)] for entry in v] for v in kernel_basis]
                flipper_basis_matrix = flipper.kernel.Matrix([[K(entry) for entry in v] for v in basis])
                
                if len(flipper_basis_matrix) == 1:  # If rank(kernel) == 1.
                    [flipper_eigenvector] = flipper_basis_matrix
                    if flipper.kernel.matrix.nonnegative(flipper_eigenvector) and condition_matrix.nonnegative_image(flipper_eigenvector):
                        return K.lmbda, flipper_eigenvector
                else:
                    pass
    
    raise flipper.ComputationError('No interesting eigenvalues in cell.')

