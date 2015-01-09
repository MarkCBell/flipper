
from __future__ import print_function

import flipper

import importlib

def main(verbose=False):
	''' Runs all of the tests in the tests directory. '''
	
	failed_tests = []
	for test_name in dir(flipper.test):
		if not test_name.startswith('_'):
			test = importlib.import_module('flipper.test.%s' % test_name)
			print('Running %s test...' % test_name)
			result = test.main(verbose=verbose)
			print('\tPassed' if result else '\tFAILED')
			if not result:
				failed_tests.append(test_name)
	
	print('Finished testing.')
	if len(failed_tests) > 0:
		print('\tFAILED TESTS:')
		for test_name in failed_tests:
			print('\t%s' % test_name)
	else:
		print('\tAll tests passed.')

if __name__ == '__main__':
	main()

