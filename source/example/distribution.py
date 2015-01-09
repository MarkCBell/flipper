
from __future__ import print_function

import flipper

def main(surface, lower, upper, step=1, sample=100):
	S = flipper.load.equipped_triangulation(surface)
	for length in range(lower, upper, step):
		count = 0
		for i in range(sample):
			mapping_class = S.mapping_class(length)
			if mapping_class.nielsen_thurston_type() == flipper.kernel.encoding.NT_TYPE_PSEUDO_ANOSOV:
				count += 1
			print('\rLength: %d, Computed %d/%d - %0.1f%% pA' % (length, (i+1), sample, float(count) * 100 / (i+1)), end='')
		print('')

if __name__ == '__main__':
	#main('S_1_2', 27, 30, sample=500)
	main('S_2_1', 10, 20)

