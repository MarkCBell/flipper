
from __future__ import print_function
from time import time
import cProfile
import pstats

import flipper

NT_TYPE_PERIODIC = flipper.kernel.encoding.NT_TYPE_PERIODIC
NT_TYPE_REDUCIBLE = flipper.kernel.encoding.NT_TYPE_REDUCIBLE
NT_TYPE_PSEUDO_ANOSOV = flipper.kernel.encoding.NT_TYPE_PSEUDO_ANOSOV

def main(verbose=False):
	if verbose: print('Running equippedtriangulation profile.')
	
	start_time = time()
	# Add more tests here.
	
	tests = [
		('S_1_1', 10, None),
		('S_1_2', 6, None),
		('S_0_4', 4, ['a', 'b']),
		]
	
	for surface, depth, letters in tests:
		sum(1 for _ in flipper.load.equipped_triangulation(surface).all_words(depth, letters=letters))
	
	return time() - start_time

if __name__ == '__main__':
	# main()
	# print(main(verbose=True))
	#pstats.Stats(cProfile.Profile().run('main()')).strip_dirs().sort_stats('time').print_callers(20)
	#pstats.Stats(cProfile.Profile().run('main()')).strip_dirs().sort_stats('cumtime').print_callees(20)
	pstats.Stats(cProfile.Profile().run('main()')).strip_dirs().sort_stats('time').print_stats(30)

