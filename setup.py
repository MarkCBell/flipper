
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
		import flipper
		
		flipper.test.main()

# So we can access all of the profiling suite just by doing 'python setup.py profile'
class ProfileCommand(Command):
	description = 'Runs all tests in the tests directory.'
	user_options = []
	
	def initialize_options(self):
		pass
	
	def finalize_options(self):
		pass
	
	def run(self):
		import flipper
		
		flipper.profile.main()

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
		'flipper': ['./README', './LICENSE', 'docs/*'],
		'flipper.application': ['icon/*', 'docs/*'],
		'flipper.load': ['censuses/*.dat']
		},
	cmdclass={'test': TestCommand, 'profile': ProfileCommand}
	)
