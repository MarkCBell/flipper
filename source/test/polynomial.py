
from __future__ import print_function

import flipper

def main(verbose=False):
	if verbose: print('Running polynomial tests.')
	
	f = flipper.kernel.Polynomial([-2, 0, 1])  # f = -2 + x^2.
	g = flipper.kernel.Polynomial([0, 2])  # g = 2x = f'.
	h = flipper.kernel.Polynomial([-2, 2, 1])  # h = -2 + 2x + x^2 = f + g.
	p1 = flipper.kernel.Polynomial([1, -7, 19, -26, 19, -7, 1])
	p2 = flipper.kernel.Polynomial([2, -3, 1])  # 2 - 3x + x^2 = (x - 2) (x - 1).
	
	tests = [
		g == f.derivative(),
		h == f + g,
		len(f.real_roots()) == 2,
		len(p1.real_roots()) == 3,
		len(p2.real_roots()) == 2
		]
	
	return all(tests)

if __name__ == '__main__':
	print(main(verbose=True))
