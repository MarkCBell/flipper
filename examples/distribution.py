
from __future__ import print_function

import flipper

def main(n=100):
	times = {}
	S = flipper.examples.abstracttriangulation.Example_S_2_1()
	for length in range(10, 20, 1):
		count = 0
		for i in range(n):
			mapping_class = S.mapping_class(length)
			if mapping_class.NT_type() == flipper.kernel.encoding.NT_TYPE_PSEUDO_ANOSOV:
				count += 1
			print('\rLength: %d, Computed %d/%d - %0.1f%% pA' % (length, (i+1), n, float(count) * 100 / (i+1)), end='')
		print('')

if __name__ == '__main__':
	main()

