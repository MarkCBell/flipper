
from __future__ import print_function
from time import time

import flipper

def main(verbose=False):
	start_time = time()
	# Add more tests here.
	
	x = flipper.kernel.AlgebraicNumber(flipper.kernel.Polynomial([-2, 0, 1]), flipper.kernel.interval.interval_from_string('1.41'))
	y = flipper.kernel.AlgebraicNumber(flipper.kernel.Polynomial([-3, 0, 1]), flipper.kernel.interval.interval_from_string('1.732'))
	z = flipper.kernel.AlgebraicNumber(flipper.kernel.Polynomial([-1001, 0, 1]), flipper.kernel.interval.interval_from_string('31.639'))
	[a, b, c] = flipper.kernel.NumberRing([x, y, z]).basis()
	if a * a != 2:
		return False
	if b * b != 3:
		return False
	if a * b != b * a:
		return False
	if (a + 1) * (b + 1) != 1 + a + b + a * b:
		return False
	if (1 + a + b) * (b + 1) != 1 + a + b + b + a * b + b * b:
		return False
	if (1 + a + b) * (1 + a) * (1 + b) != 6 + 5 * a + 4 * b + 3 * a * b:
		return False
	if 10000 * c * c != 10000 * 1001:
		return False
	
	if verbose: print('Time taken: %0.3fs' % (time() - start_time))
	return True

if __name__ == '__main__':
	print(main(verbose=True))

