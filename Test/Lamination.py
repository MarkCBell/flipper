
###########################################################################
# Some Tests #
###########################################################################

from time import time

from Flipper.Kernel.Lamination import invariant_lamination
from Flipper.Kernel.Error import ComputationError, AssumptionError
from Flipper.Examples.Examples import build_example_mapping_class

# from Flipper.Examples.Examples import Example_24 as Example
# from Flipper.Examples.Examples import Example_S_1_1 as Example
from Flipper.Examples.Examples import Example_S_1_2 as Example

def determine_type(mapping_class, verbose=False):
	start_time = time()
	if mapping_class.is_periodic():
		print(' -- Periodic.')
	else:
		try:
			# We know the map cannot be periodic.
			# If this computation fails it will throw a ComputationError - the map was probably reducible.
			# In theory it could also fail by throwing an AssumptionError but we have already checked that the map is not periodic.
			lamination, dilatation = invariant_lamination(mapping_class, exact=True)
			print('      (Midpoint time: %0.4fs)' % (time() - start_time))
			# If this computation fails it will throw an AssumptionError - the map _is_ reducible.
			preperiodic, periodic, new_dilatation, correct_lamination, isometries = lamination.splitting_sequence4()
			if verbose: print('Perperiodic, periodic length: %d, %d' %(len(preperiodic), len(periodic)))
			if verbose: print('Dilatation: %s, %s' % (dilatation, new_dilatation))
			print(' -- Pseudo-Anosov.')
		except ComputationError:
			print(' ~~ Probably reducible.')
		except AssumptionError:
			print(' -- Reducible.')
	print('      (Time: %0.4fs)' % (time() - start_time))
	return time() - start_time

def random_test(words=None, num_trials=None, verbose=False):
	print('Start')
	
	times = []
	if num_trials is not None:
		for k in range(num_trials):
			word, mapping_class = build_example_mapping_class(Example)
			print(word)
			times.append(determine_type(mapping_class, verbose))
	elif words is not None:
		num_trials = len(words)
		for word in words:
			word, mapping_class = build_example_mapping_class(Example, word)
			print(word)
			times.append(determine_type(mapping_class, verbose))
	else:
		raise TypeError('words or num_trials must be set')
	
	print('Times over %d trials: Average %0.4fs, Max %0.4fs' % (num_trials, sum(times) / len(times), max(times)))

def main():
	# random_test(['aBC'])
	# random_test(['aBBap' * 3])
	random_test(['aB', 'bbaCBAaBabcABB', 'aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa'], verbose=True)
	# import cProfile
	# cProfile.run('random_test(["aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa"])', sort='time')
	# random_test()
	pass

if __name__ == '__main__':
	main()
