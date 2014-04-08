
from __future__ import print_function
from time import time

import Flipper

def determine_type(mapping_class, verbose=False):
	start_time = time()
	try:
		# If this computation fails it will throw a ComputationError - the map was probably reducible.
		print(' -- %s.' % mapping_class.NT_type_alternate())
	except ImportError:
		print(' Cannot determine without a symbolic library.')
	except Flipper.ComputationError:
		print(' ~~ Probably reducible.')
	print('      (Time: %0.4fs)' % (time() - start_time))
	return time() - start_time

def random_test(S, words=None, num_trials=None, verbose=False):
	print('Start')
	
	times = []
	if words is None and num_trials is None:
		raise TypeError('A list of words or number of trials must be provided.')
	
	if words is None:
		words = [S.random_word(20) for _ in range(num_trials)]
	
	num_trials = len(words)
	for word in words:
		mapping_class = S.mapping_class(word)
		print(mapping_class.name)
		times.append(determine_type(mapping_class, verbose))
	
	print('Times over %d trials: Average %0.4fs, Max %0.4fs' % (num_trials, sum(times) / len(times), max(times)))

def main():
	S = Flipper.examples.abstracttriangulation.Example_S_1_2()
	random_test(S, ['aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa'], verbose=True)

if __name__ == '__main__':
	main()

