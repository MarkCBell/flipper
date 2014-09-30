
import flipper

import importlib

def main(verbose=False):
	total_time = 0
	for profile_name in dir(flipper.profiles):
		if not profile_name.startswith('_') and profile_name != 'flipper':
			profile = importlib.import_module('flipper.profiles.%s' % profile_name)
			print('Running %s profile...' % profile_name)
			time = profile.main(verbose=verbose)
			total_time += time
			print('\tRan in %0.3fs' % time)
	
	print('Finished profiling.')
	print('\tTotal time: %0.3fs' % total_time)

if __name__ == '__main__':
	main()

