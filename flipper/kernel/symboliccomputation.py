
import cypari

import flipper

def directed_eigenvector(action_matrix, condition_matrix):
    ''' Return an interesting eigenvector of action_matrix which lives inside of the cone C, defined by condition_matrix.
    
    An eigenvector is interesting if its corresponding eigenvalue is: real, > 1, irrational and bigger than all
    of its Galois conjugates.
    
    Raises a ComputationError if it cannot find an interesting vectors in C.
    Assumes that C contains at most one interesting eigenvector. '''
    
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
