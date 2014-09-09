
from __future__ import print_function

import flipper

NT_TYPE_PERIODIC = flipper.kernel.encoding.NT_TYPE_PERIODIC
NT_TYPE_REDUCIBLE = flipper.kernel.encoding.NT_TYPE_REDUCIBLE
NT_TYPE_PSEUDO_ANOSOV = flipper.kernel.encoding.NT_TYPE_PSEUDO_ANOSOV

def main(verbose=False):
	if verbose: print('Running encoding tests.')
	
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
		('S_2_1', 'abcdeF', NT_TYPE_PSEUDO_ANOSOV),
		# ('E_12', 'aaaaBBc', NT_TYPE_PSEUDO_ANOSOV),  # Really slow.
		# ('E_12', 'aaBaaBBc', NT_TYPE_PSEUDO_ANOSOV)  # Really slow.
		# ('E_12', 'aaaaBBaBaBc', NT_TYPE_PSEUDO_ANOSOV)  # Really slow useful for profiling. Current best time 102s.
		]
	
	try:
		for surface, word, mapping_class_type in tests:
			if verbose: print(word)
			S = flipper.examples.template(surface)
			mapping_class = S.mapping_class(word)
			if mapping_class.nielsen_thurston_type() != mapping_class_type:
				return False
	except ImportError:
		print('Symbolic computation library required but unavailable, test skipped.')
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))

