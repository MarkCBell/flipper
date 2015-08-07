

from __future__ import print_function
from time import time
import cProfile
import pstats

import flipper

NT_TYPE_PERIODIC = flipper.kernel.encoding.NT_TYPE_PERIODIC
NT_TYPE_REDUCIBLE = flipper.kernel.encoding.NT_TYPE_REDUCIBLE
NT_TYPE_PSEUDO_ANOSOV = flipper.kernel.encoding.NT_TYPE_PSEUDO_ANOSOV

def main(verbose=False):
	if verbose: print('Running encoding profile.')
	
	start_time = time()
	# Add more tests here.
	# These need to be changed if the standard example triangulations ever change.
	num_isometries = [
		('S_0_4', 2),
		('S_1_1', 6),
		('S_1_2', 4),
		('S_2_1', 2),
		('S_3_1', 2),
		('E_12', 12),
		('E_24', 24),
		('E_36', 36)
		]
	
	# Check that every triangulation has the correct number of isometries to itself.
	for surface, num_isoms in num_isometries:
		if verbose: print('Checking: %s' % surface)
		S = flipper.load(surface)
		T = S.triangulation
		T.self_isometries()
		T2 = flipper.triangulation_from_iso_sig(T.iso_sig())
		T.is_isometric_to(T2)
	
	return time() - start_time

if __name__ == '__main__':
	# print(main(verbose=True))
	#pstats.Stats(cProfile.Profile().run('main()')).strip_dirs().sort_stats('time').print_callers(20)
	#pstats.Stats(cProfile.Profile().run('main()')).strip_dirs().sort_stats('cumtime').print_callees(20)
	pstats.Stats(cProfile.Profile().run('main()')).strip_dirs().sort_stats('time').print_stats(30)

