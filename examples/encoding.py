
from __future__ import print_function
from time import time

import flipper

def main():
	S = flipper.examples.abstracttriangulation.Example_S_1_2()
	words = ['aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa']
	
	times = []
	num_trials = len(words)
	for word in words:
		print(word)
		mapping_class = S.mapping_class(word)
		start_time = time()
		try:
			# If this computation fails it will throw a ComputationError - the map was probably reducible.
			print(' -- %s.' % mapping_class.nielsen_thurston_type())
		except ImportError:
			print(' Cannot determine without a symbolic library.')
		except flipper.ComputationError:
			print(' ~~ Probably reducible.')
		print('      (Time: %0.4fs)' % (time() - start_time))
		times.append(time() - start_time)
	
	print('Times over %d trials: Average %0.4fs, Max %0.4fs' % (num_trials, sum(times) / len(times), max(times)))


if __name__ == '__main__':
	main()

