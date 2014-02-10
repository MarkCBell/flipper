
from __future__ import print_function
from math import log10 as log

import Flipper
interval_from_string = Flipper.Kernel.Interval.interval_from_string

def main():
	w = interval_from_string('0.1')
	x = interval_from_string('10000.0')
	y = interval_from_string('1.14571')
	z = interval_from_string('1.00000')
	a = interval_from_string('-1.200000')
	b = interval_from_string('1.4142135623')
	
	if not (2 in (b * b)):
		return False
	
	# Check:
	#	acc(I + J) >= min(acc(I), acc(J)) - 1,
	#	acc(I * J) >= min(acc(I), acc(J)) - log(I.lower + J.lower + 1)
	#	acc(I / J) >= min(acc(I), acc(J)) - log+(J)
	#	acc(x * I) >= acc(I) - log+(x)
	
	pairs = [(w, x), (b, y)]
	
	for I, J in pairs:
		m = min(I.accuracy, J.accuracy)
		if not ((I + J).accuracy >= m - 1):
			return False
		if not ((I * J).accuracy >= m - log(I.lower + J.lower + 1)):
			return False
		if not ((I / J).accuracy >= m - J.log_plus):
			return False
	
	return True

if __name__ == '__main__':
	print(main())