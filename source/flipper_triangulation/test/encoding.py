
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
		('S_1_1', 'ab', NT_TYPE_PERIODIC),
		('S_1_1', 'aB', NT_TYPE_PSEUDO_ANOSOV),
		('S_1_2', 'a', NT_TYPE_REDUCIBLE),
		('S_1_2', 'b', NT_TYPE_REDUCIBLE),
		('S_1_2', 'c', NT_TYPE_REDUCIBLE),
		('S_1_2', 'aB', NT_TYPE_REDUCIBLE),
		('S_1_2', 'bbaCBAaBabcABB', NT_TYPE_REDUCIBLE),
		('S_1_2', 'aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa', NT_TYPE_PSEUDO_ANOSOV),
		('S_2_1', 'aaabcd', NT_TYPE_PSEUDO_ANOSOV),
		('S_2_1', 'abcdeF', NT_TYPE_PSEUDO_ANOSOV),
		#('E_12', 'aaaaBBp', NT_TYPE_PSEUDO_ANOSOV),
		#('E_12', 'aaBaaBBp', NT_TYPE_REDUCIBLE),
		#('E_12', 'aaaaBBaBaBp', NT_TYPE_PSEUDO_ANOSOV),
		]
	
	for surface, word, mapping_class_type in tests:
		if verbose: print(word)
		S = flipper.load.equipped_triangulation(surface)
		if S.mapping_class(word).nielsen_thurston_type() != mapping_class_type:
			return False
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))

