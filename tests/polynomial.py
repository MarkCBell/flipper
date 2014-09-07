
from __future__ import print_function

import flipper

def main(verbose=False):
	if verbose: print('Running polynomial tests.')
	
	f = flipper.kernel.Polynomial([-2, 0, 1])  # f = -2 + x^2.
	g = flipper.kernel.Polynomial([0, 2])  # g = 2x = f'.
	h = flipper.kernel.Polynomial([-2, 2, 1])  # h = -2 + 2x + x^2 = f + g.
	p1 = flipper.kernel.Polynomial([1, -7, 19, -26, 19, -7, 1])
	p2 = flipper.kernel.Polynomial([2, -3, 1])  # 2 - 3x + x^2 = (x - 2) (x - 1).
	
	if not (g == f.derivative()): return False
	if not (h == f + g): return False
	if not (len(f.roots()) == 2): return False
	if not (len(p1.roots()) == 3): return False
	if not (len(p2.roots()) == 2): return False
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))
