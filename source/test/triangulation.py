
from __future__ import print_function

import flipper

def main(verbose=False):
	if verbose: print('Running triangulation tests.')
	
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
		if len(T.self_isometries()) != num_isoms > 0:
			return False
		# Check that isomorphism signatures work.
		T2 = flipper.triangulation_from_iso_sig(T.iso_sig())
		if not T.is_isometric_to(T2):
			return False
		if T.iso_sig() != T2.iso_sig():
			return False
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))

