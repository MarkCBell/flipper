
from __future__ import print_function
from random import randint
from time import time
import cProfile
import pstats

import flipper

def main(verbose=False, n=1000, k=100, p=3, q=5):
	if verbose: print('Running matrix profile.')
	
	# This realyl should be a deterministic test.
	start_time = time()
	for _ in range(n):
		M = flipper.kernel.Matrix([[randint(-k, k) for _ in range(p)] for _ in range(q)])
		a = M.nontrivial_polytope()
		b = M.nontrivial_polytope2()
		assert(a == b)
	return time() - start_time

if __name__ == '__main__':
	# pstats.Stats(cProfile.Profile().run('main()')).strip_dirs().sort_stats('time').print_callers(20)
	# pstats.Stats(cProfile.Profile().run('main()')).strip_dirs().sort_stats('time').print_callees(20)
	pstats.Stats(cProfile.Profile().run('main()')).strip_dirs().sort_stats('time').print_stats(20)

