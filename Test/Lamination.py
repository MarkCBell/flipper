
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

def determine_type(mapping_class):
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
			preperiodic, periodic, new_dilatation, correct_lamination, isometries = lamination.splitting_sequence()
			print(len(preperiodic), len(periodic))
			print(' -- Pseudo-Anosov.')
		except ComputationError:
			print(' ~~ Probably reducible.')
		except AssumptionError:
			print(' -- Reducible.')
	print('      (Time: %0.4fs)' % (time() - start_time))
	return time() - start_time

def random_test(word=None, num_trials=50):
	print('Start')
	
	times = []
	for k in range(num_trials):
		word, mapping_class = build_example_mapping_class(Example, word)
		print(word)
		times.append(determine_type(mapping_class))
	
	print('Times over %d trials: Average %0.4fs, Max %0.4fs' % (num_trials, sum(times) / len(times), max(times)))

def main():
	# random_test('aBC', num_trials=1)
	# random_test('aBBap' * 3, num_trials=1)
	random_test('aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa', num_trials=1)
	# import cProfile
	# cProfile.run('random_test("aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa", num_trials=1)', sort='time')
	# random_test()
	pass

if __name__ == '__main__':
	main()
