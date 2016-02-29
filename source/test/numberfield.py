
from __future__ import print_function

import flipper

def main(verbose=False):
	if verbose: print('Running number field tests.')
	
	N = flipper.kernel.NumberField.from_tuple([-2, 0, 1], '1.4142135623')  # QQ(sqrt(2)).
	x = N.lmbda  # sqrt(2)
	
	tests = [
		x * x == 2
		]
	
	return all(tests)

if __name__ == '__main__':
	print(main(verbose=True))

