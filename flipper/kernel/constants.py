
''' A module for storing constants that should only ever be computed once.

We need to put these in a special place so that flipper can compute these after everything
else has been initialised. '''

import flipper

# Create special permutations.
Permutation = flipper.kernel.Permutation
flipper.kernel.permutation.PERM3 = flipper.kernel.permutation.all_permutations(3)
flipper.kernel.permutation.PERM3_INVERSE = {perm: perm.inverse() for perm in flipper.kernel.permutation.PERM3}
flipper.kernel.permutation.PERM3_LOOKUP = dict((perm, index) for index, perm in enumerate(flipper.kernel.permutation.PERM3))
flipper.kernel.permutation.TRANSITION_PERM3_LOOKUP = {
	(0, 0): Permutation([0, 2, 1]),
	(0, 1): Permutation([1, 0, 2]),
	(0, 2): Permutation([2, 1, 0]),
	(1, 0): Permutation([1, 0, 2]),
	(1, 1): Permutation([2, 1, 0]),
	(1, 2): Permutation([0, 2, 1]),
	(2, 0): Permutation([2, 1, 0]),
	(2, 1): Permutation([0, 2, 1]),
	(2, 2): Permutation([1, 0, 2])
}

