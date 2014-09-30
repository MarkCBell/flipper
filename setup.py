
from __future__ import print_function

from distutils.core import setup, Command
import importlib

# Get the correct version.
from versions import version

# So we can access all of the test suite just by doing 'python setup.py test'
class TestCommand(Command):
	description = 'Runs all tests in the tests directory.'
	user_options = []
	
	def initialize_options(self):
		pass
	
	def finalize_options(self):
		pass
	
	def run(self):
		''' Runs all of the tests in the tests directory. '''
		try:
			test_module = importlib.import_module('flipper.tests')
		except ImportError:
			print('flipper module unavailable, install by running: \n>>> python setup.py install [--user]')
		else:
			failed_tests = []
			for test_name in dir(test_module):
				if not test_name.startswith('_') and test_name != 'flipper':
					test = importlib.import_module('flipper.tests.%s' % test_name)
					print('Running %s test...' % test_name)
					result = test.main(verbose=False)
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

# So we can access all of the profiling suite just by doing 'python setup.py profile'
class ProfileCommand(Command):
	description = 'Runs all tests in the tests directory.'
	user_options = []
	
	def initialize_options(self):
		pass
	
	def finalize_options(self):
		pass
	
	def run(self):
		''' Runs all of the tests in the tests directory. '''
		profile_module = importlib.import_module('flipper.profiles')
		try:
			profile_module = importlib.import_module('flipper.profiles')
		except ImportError:
			print('flipper module unavailable, install by running: \n>>> python setup.py install [--user]')
		else:
			total_time = 0
			for profile_name in dir(profile_module):
				if not profile_name.startswith('_') and profile_name != 'flipper':
					profile = importlib.import_module('flipper.profiles.%s' % profile_name)
					print('Running %s profile...' % profile_name)
					time = profile.main()
					total_time += time
					print('\tRan in %0.3fs' % time)
			
			print('Finished profiling.')
			print('\tTotal time: %0.3fs' % total_time)

setup(
	name='flipper',
	version=str(version),
	description='flipper',
	author='Mark Bell',
	author_email='M.C.Bell@warwick.ac.uk',
	url='https://bitbucket.org/Mark_Bell/flipper',
	# Remember to update these if the directory structure changes.
	packages=['flipper', 'flipper.application', 'flipper.load', 'flipper.examples', 'flipper.kernel', 'flipper.tests', 'flipper.profiles'],
	package_dir={'flipper': ''},
	package_data={
		'flipper': ['docs/*'],
		'flipper.application': ['icon/*', 'docs/*'],
		'flipper.load': ['censuses/*.dat']
		},
	cmdclass={'test': TestCommand, 'profile': ProfileCommand}
	)
