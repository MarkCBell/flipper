
from __future__ import print_function

import flipper

NT_TYPE_PERIODIC = flipper.kernel.encoding.NT_TYPE_PERIODIC
NT_TYPE_REDUCIBLE = flipper.kernel.encoding.NT_TYPE_REDUCIBLE
NT_TYPE_PSEUDO_ANOSOV = flipper.kernel.encoding.NT_TYPE_PSEUDO_ANOSOV

def main(verbose=False):
	if verbose: print('Running encoding tests.')
	
	S = flipper.load('S_1_1')
	f, g = S.mapping_class('aB'), S.mapping_class('bA')  # Some pseudo-Anosov ones.
	h, i = S.mapping_class('ab'), S.mapping_class('')  # Some finite order ones.
	
	tests = [
		h != i,
		h**6 == i,
		h**-3 == h**3,
		h**0 == i,
		h.order() == 6,
		f != g,
		f.is_conjugate_to(g),
		not f.is_conjugate_to(h),
		not h.is_conjugate_to(i),
		]
	
	if not all(tests):
		if verbose: print(tests)
		return False
	
	# Add more examples here.
	examples = [
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
	
	for surface, word, mapping_class_type in examples:
		if verbose: print(word)
		S = flipper.load(surface)
		if S.mapping_class(word).nielsen_thurston_type() != mapping_class_type:
			return False
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))

