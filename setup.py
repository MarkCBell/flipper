
from __future__ import print_function
from distutils.core import setup, Command
import importlib

# Get the correct version.
from version import Flipper_version

# So we can access all of the test suite just by doing "python setup.py test"
class TestCommand(Command):
	user_options = []
	
	def initialize_options(self):
		pass
	
	def finalize_options(self):
		pass
	
	def run(self):
		''' Runs all of the tests in the Tests directory. '''
		try:
			test_module = importlib.import_module('Flipper.tests')
		except ImportError:
			print('Flipper module unavailable, install by running: \n>>> python setup.py install [--user]')
		else:
			for test_name in dir(test_module):
				if not test_name.startswith('_') and test_name != 'Flipper':
					test = importlib.import_module('Flipper.tests.%s' % test_name)
					print('Running %s test...' % test_name)
					print('\tPassed' if test.main() else '\tFAILED')

setup(
	name='Flipper',
	version=Flipper_version,
	description='Flipper',
	author='Mark Bell',
	author_email='M.C.Bell@warwick.ac.uk',
	url='https://bitbucket.org/Mark_Bell/Flipper',
	packages=['Flipper'],
	package_dir={'Flipper':''},
	# Remember to update these if the directory structure changes.
	package_data={'Flipper':['application/*.py', 'application/icon/*', 'application/docs/*', 'examples/*.py', 'kernel/*.py', 'tests/*.py', 'docs/*', 'version.py']},
	cmdclass={'test':TestCommand}
	)
