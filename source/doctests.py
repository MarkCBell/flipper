
import flipper

import os
import doctest
from importlib import import_module

def run_tests(verbose=False):
	failed_tests = []
	num_failed, num_attempted = 0, 0
	for filename in dir(flipper.kernel):
		if os.path.exists(os.path.join(os.path.dirname(flipper.kernel.__file__), filename + '.py')):
			if verbose: print('Running %s test...' % filename)
			mod = import_module('flipper.kernel.' + filename)
			results = doctest.testmod(mod, extraglobs=mod.doctest_globs() if hasattr(mod, 'doctest_globs') else {})
			if results.failed == 0:
				if verbose: print('\t%s' % str(results))
			else:
				failed_tests.append(filename)
			num_failed += results.failed
			num_attempted += results.attempted
	
	if verbose:
		print('Attempted: %d' % num_attempted)
		print('Failed: %d' % num_failed)
	if failed_tests:
		print('FAILED TESTS:')
		for test in failed_tests:
			print('\t%s' % test)
		return False
	else:
		print('All tests passed.')
		return True

if __name__ == '__main__':
	run_tests(verbose=True)

