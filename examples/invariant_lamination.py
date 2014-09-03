
from __future__ import print_function
from time import time

import flipper

def main(n=100):
	times = {}
	surface = 'S_1_2'
	S = flipper.examples.template(surface)
	for index in range(n):
		word = S.random_word(50)  # , negative=False)
		print('%d/%d: %s %s' % (index+1, n, surface, word), end='')
		mapping_class = S.mapping_class(word)
		t = time()
		try:
			mapping_class.invariant_lamination()
		except flipper.AssumptionError:
			pass  # mapping_class is not pseudo-Anosov.
		# This can also fail with a flipper.ComputationError if self.invariant_lamination()
		# fails to find an invariant lamination.
		times[word] = time() - t
		print(', Time: %0.3f' % times[word])
	print('Average time: %0.3f' % (sum(times.values()) / n))
	print('Slowest: %s, Time: %0.3f' % (max(times, key=lambda w: times[w]), max(times.values())))

if __name__ == '__main__':
	main()

