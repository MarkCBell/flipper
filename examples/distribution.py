
from __future__ import print_function

import flipper

def main(n=10):
	times = {}
	S = flipper.examples.abstracttriangulation.Example_S_2_1()
	for length in range(10, 100, 2):
		count = 0
		for i in range(n):
			print('\r%d: %d' % (i, count), end='')
			word = S.random_word(length)
			mapping_class = S.mapping_class(word)
			if mapping_class.NT_type() == flipper.kernel.encoding.NT_TYPE_PSEUDO_ANOSOV:
				count += 1
		print('')
		print('Length: %d - %d%%' % (length, float(count) * 100 / n))

if __name__ == '__main__':
	main()

