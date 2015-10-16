
from __future__ import print_function
from time import time

import flipper

# The purpose of this example is to demonstrate that:
#   generically Encoding.invariant_lamination() does not raise flipper.ComputationErrors.

def main(n=100):
	times = {}
	surface = 'S_3_1'
	S = flipper.load(surface)
	for index in range(n):
		word = S.random_word(20)  # , negative=False)
		print('%3d/%d: %s %s' % (index+1, n, surface, word.replace('.', '')), end='')
		mapping_class = S.mapping_class(word)
		t = time()
		try:
			mapping_class.invariant_lamination()
		except flipper.AssumptionError:
			print(', Claim: not pA', end='')
		# This can also fail with a flipper.ComputationError if self.invariant_lamination()
		# fails to find an invariant lamination.
		times[word] = time() - t
		print(', Time: %0.3f' % times[word])
	print('Average time: %0.3f' % (sum(times.values()) / n))
	print('Slowest: %s, Time: %0.3f' % (max(times, key=lambda w: times[w]).replace('.', ''), max(times.values())))
	print('Total time: %0.3f' % sum(times.values()))

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Demonstrate the effectiveness of flippers heuristics for finding invariant laminations.')
	parser.add_argument('--show', action='store_true', default=False, help='show the source code of this example and exit')
	args = parser.parse_args()
	
	if args.show:
		print(open(__file__, 'r').read())
	else:
		main()

