
from __future__ import print_function
from itertools import product, permutations

import flipper

def main(n=4):
	# Get some example permutations.
	all_perms = flipper.kernel.permutation.all_permutations(n)
	
	try:
		# Check that there are the same number of odd and even permutations.
		assert(len([perm for perm in all_perms if perm.is_even()]) == len([perm for perm in all_perms if not perm.is_even()]))
		# Check that composition respects parity.
		assert(all((p1 * p2).is_even() == p1.is_even() ^ p2.is_even() ^ True for p1, p2 in product(all_perms, all_perms)))
		# Check that every permutation acts transitively.
		assert(all(set(perm * p1 for p1 in all_perms) == set(all_perms) for perm in all_perms))
	except AssertionError:
		return False
	
	return True

if __name__ == '__main__':
	print(main())
