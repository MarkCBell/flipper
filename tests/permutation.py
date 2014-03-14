
from __future__ import print_function
from itertools import permutations

import Flipper

def main():
	
	# !?! TO DO.
	
	all_perms = [Flipper.kernel.Permutation(perm) for perm in permutations(range(4), 4)]
	
	try:
		assert(len([perm for perm in all_perms if perm.is_even()]) == len([perm for perm in all_perms if not perm.is_even()]))
	except AssertionError:
		return False
	
	return True

if __name__ == '__main__':
	print(main())