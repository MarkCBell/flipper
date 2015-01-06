
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
	tests = [
		('S_1_1', 'a', NT_TYPE_REDUCIBLE),
		('S_1_2', 'a', NT_TYPE_REDUCIBLE),
		('S_1_2', 'b', NT_TYPE_REDUCIBLE),
		('S_1_2', 'c', NT_TYPE_REDUCIBLE),
		('S_1_2', 'aB', NT_TYPE_REDUCIBLE),
		('S_1_2', 'bbaCBAaBabcABB', NT_TYPE_REDUCIBLE),
		('S_1_2', 'aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa', NT_TYPE_PSEUDO_ANOSOV),
		('S_2_1', 'aaabcd', NT_TYPE_PSEUDO_ANOSOV),
		# ('E_12', 'aaaaBBc', NT_TYPE_PSEUDO_ANOSOV),  # Really slow.
		# ('E_12', 'aaBaaBBc', NT_TYPE_PSEUDO_ANOSOV)  # Really slow.
		# ('E_12', 'aaaaBBaBaBc', NT_TYPE_PSEUDO_ANOSOV)  # Really slow useful for profiling. Current best time 102s.
		]
	
	for surface, word, _ in tests:
		if verbose: print(word)
		mapping_class = flipper.load.equipped_triangulation(surface).mapping_class(word)
		try:
			mapping_class.invariant_lamination()
		except flipper.AssumptionError:
			# The mapping class was not pseudo-Anosov.
			pass
	
	return time() - start_time

if __name__ == '__main__':
	# main()
	# print(main(verbose=True))
	#pstats.Stats(cProfile.Profile().run('main()')).strip_dirs().sort_stats('time').print_callers(20)
	#pstats.Stats(cProfile.Profile().run('main()')).strip_dirs().sort_stats('cumtime').print_callees(20)
	pstats.Stats(cProfile.Profile().run('main()')).strip_dirs().sort_stats('time').print_stats(30)

