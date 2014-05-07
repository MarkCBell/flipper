
from __future__ import print_function
from time import time

import flipper

NT_TYPE_PERIODIC = flipper.kernel.encoding.NT_TYPE_PERIODIC
NT_TYPE_REDUCIBLE = flipper.kernel.encoding.NT_TYPE_REDUCIBLE
NT_TYPE_PSEUDO_ANOSOV = flipper.kernel.encoding.NT_TYPE_PSEUDO_ANOSOV

def main(verbose=False):
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
	
	try:
		for surface, word, mapping_class_type in tests:
			if verbose: print(word)
			S = flipper.examples.abstracttriangulation.SURFACES[surface]()
			mapping_class = S.mapping_class(word)
			assert(mapping_class.NT_type() == mapping_class_type)
	except ImportError:
		print('Symbolic computation library required but unavailable, test skipped.')
	except AssertionError:
		return False
	
	if verbose: print('Time taken: %0.3fs' % (time() - start_time))
	return True

if __name__ == '__main__':
	print(main(verbose=True, timings=True))

