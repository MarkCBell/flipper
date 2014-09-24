
from __future__ import print_function

import flipper

def main(verbose=False):
	if verbose: print('Running number field tests.')
	
	N = flipper.kernel.number_field([-2, 0, 1], '1.41')  # QQ(sqrt(2)).
	x = N.lmbda  # sqrt(2)
	if not (x * x == 2): return False
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))

