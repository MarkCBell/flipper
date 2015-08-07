
from __future__ import print_function

import flipper

def main(verbose=False):
	if verbose: print('Running lamination tests.')
	
	# Add more tests here.
	tests = [
		('S_1_1', 'a'),
		('S_1_2', 'a'),
		('S_1_2', 'b'),
		('S_1_2', 'c'),
		('S_1_2', 'aB'),
		('S_1_2', 'bbaCBAaBabcABB'),
		('S_1_2', 'aCBACBacbaccbAaAAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa'),
		('S_2_1', 'aaabcd'),
		# ('E_12', 'aaaaBBc'),  # Really slow.
		# ('E_12', 'aaBaaBBc)'  # Really slow.
		# ('E_12', 'aaaaBBaBaBc')  # Really slow useful for profiling. Current best time 102s.
		]
	
	try:
		for surface, word in tests:
			if verbose: print(word)
			S = flipper.load(surface)
			mapping_class = S.mapping_class(word)
			mapping_class.invariant_lamination()  # This could fail with a ComputationError.
	except flipper.AssumptionError:
		pass  # mapping_class is not pseudo-Anosov.
	except flipper.ComputationError:
		return False
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))

