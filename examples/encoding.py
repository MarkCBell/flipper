
from __future__ import print_function
from time import time

import flipper

def main(n=100):
	times = {}
	S = flipper.examples.abstracttriangulation.Example_S_2_1()
	for i in range(n):
		word = S.random_word(10)  # , negative=False)
		print('%d: %s' % (i, word), end='')
		mapping_class = S.mapping_class(word)
		t = time()
		print(' - ' + mapping_class.NT_type(), end='')
		times[word] = time() - t
		print(', Time: %0.3f' % times[word])
	print('Average time: %0.3f' % (sum(times.values()) / n))
	print('Slowest: %s, Time: %0.3f' % (max(times, key=lambda w: times[w]), max(times.values())))

if __name__ == '__main__':
	main()

