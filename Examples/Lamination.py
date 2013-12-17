
###########################################################################
# Some Tests #
###########################################################################

def determine_type(mapping_class):
	from Error import ComputationError, AssumptionError
	from time import time
	
	start_time = time()
	if mapping_class.is_periodic():
		print(' -- Periodic.')
	else:
		try:
			# We know the map cannot be periodic.
			# If this computation fails it will throw a ComputationError - the map was probably reducible.
			# In theory it could also fail by throwing an AssumptionError but we have already checked that the map is not periodic.
			lamination, dilatation = invariant_lamination(mapping_class, exact=True)
			# If this computation fails it will throw an AssumptionError - the map _is_ reducible.
			preperiodic, periodic, new_dilatation, lamination, isometries = lamination.splitting_sequence()
			print(' -- Pseudo-Anosov.')
		except ComputationError:
			print(' ~~ Probably reducible.')
		except AssumptionError:
			print(' -- Reducible.')
	print('      (Time: %0.4fs)' % (time() - start_time))
	return time() - start_time

def random_test(Example, word=None, num_trials=50):
	from time import time
	from Examples import build_example_mapping_class
	
	print('Start')
	
	times = []
	for k in range(num_trials):
		word, mapping_class = build_example_mapping_class(Example, word)
		print(word)
		times.append(determine_type(mapping_class))
	
	print('Times over %d trials: Average %0.4fs, Max %0.4fs' % (num_trials, sum(times) / len(times), max(times)))

if __name__ == '__main__':
	from Examples import Example_24 as Example
	# from Examples import Example_S_1_1 as Example
	# from Examples import Example_S_1_2 as Example
	random_test(Example, 'aBC', num_trials=1)
	# random_test(Example, 'aBBap' * 3, num_trials=1)
	# random_test(Example, 'aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa', num_trials=1)
	# import cProfile
	# cProfile.run('random_test(Example, "aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa", num_trials=1)', sort='cumtime')
	# random_test(Example)
