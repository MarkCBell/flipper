
from __future__ import print_function

import flipper

def main(verbose=False):
	try:
		S = flipper.examples.abstracttriangulation.Example_S_1_1()
		T = S.triangulation
		assert(len(T.all_isometries(T)) == 6)
		
		# Check that every triangulation is isometric to itself.
		for example in flipper.examples.abstracttriangulation.SURFACES:
			if verbose: print('Checking: %s' % example)
			S = flipper.examples.abstracttriangulation.SURFACES[example]()
			T = S.triangulation
			assert(T.is_isometric_to(T))
	except AssertionError:
		return False
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))

