
from __future__ import print_function
from time import time

import Flipper

def determine_type(mapping_class, verbose=False):
	start_time = time()
	if mapping_class.is_periodic():
		print(' -- Periodic.')
	else:
		try:
			# We know the map cannot be periodic.
			# If this computation fails it will throw a ComputationError - the map was probably reducible.
			# In theory it could also fail by throwing an AssumptionError but we have already checked that the map is not periodic.
			lamination = mapping_class.invariant_lamination()
			dilatation = mapping_class.dilatation(lamination)
			print('      (Midpoint time: %0.4fs)' % (time() - start_time))
			# If this computation fails it will throw an AssumptionError - the map _is_ reducible.
			splitting = lamination.splitting_sequence()
			new_dilatation = splitting.dilatation()
			if verbose: print('Periodic length: %d' % len(splitting.flips))
			if verbose: print('Dilatation: %s, %s' % (dilatation, new_dilatation))
			print(' -- Pseudo-Anosov.')
		except ImportError:
			print(' Cannot determine without a symbolic library.')
		except Flipper.ComputationError:
			print(' ~~ Probably reducible.')
		except Flipper.AssumptionError:
			print(' -- Reducible.')
	print('      (Time: %0.4fs)' % (time() - start_time))
	return time() - start_time

def random_test(example, words=None, num_trials=None, verbose=False):
	print('Start')
	
	times = []
	if num_trials is not None:
		for _ in range(num_trials):
			mapping_class = example()
			print(mapping_class.name)
			times.append(determine_type(mapping_class, verbose))
	elif words is not None:
		num_trials = len(words)
		for word in words:
			mapping_class = example(word)
			print(mapping_class.name)
			times.append(determine_type(mapping_class, verbose))
	else:
		raise TypeError('A list of words or number of trials must be provided.')
	
	print('Times over %d trials: Average %0.4fs, Max %0.4fs' % (num_trials, sum(times) / len(times), max(times)))

def main():
	random_test(Flipper.examples.abstracttriangulation.Example_S_1_2, ['aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa'], verbose=True)

if __name__ == '__main__':
	main()
