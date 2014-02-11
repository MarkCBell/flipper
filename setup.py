
from __future__ import print_function
import os
from distutils.core import setup, Command

from kernel.version import Flipper_version

# So we can access all of the test suite just by doing "python setup.py test"
class TestCommand(Command):
	user_options = []
	
	def initialize_options(self):
		pass
	
	def finalize_options(self):
		pass
	
	def run(self):
		''' Runs all of the tests in the Tests directory. '''
		import Flipper
		
		print('Running AlgebraicApproximation test...')
		print('\tPassed' if Flipper.tests.algebraicapproximation.main() else '\tFailed')
		print('Running Interval test...')
		print('\tPassed' if Flipper.tests.interval.main() else '\tFailed')
		print('Running Lamination test...')
		print('\tPassed' if Flipper.tests.lamination.main() else '\tFailed')
		print('Running LayeredTriangulation test...')
		print('\tPassed' if Flipper.tests.layeredtriangulation.main() else '\tFailed')
		print('Running Matrix test...')
		print('\tPassed' if Flipper.tests.matrix.main() else '\tFailed')

setup(
	name='Flipper',
	version=Flipper_version,  # Get the correct version.
	description='Flipper',
	author='Mark Bell',
	author_email='M.C.Bell@warwick.ac.uk',
	url='https://bitbucket.org/Mark_Bell/Flipper',
	packages=['Flipper'],
	package_dir={'Flipper':''},
	# Remember to update these if the directory structure changes.
	package_data={'Flipper': ['application/*.py', 'application/icon/*', 'examples/*.py', 'kernel/*.py', 'tests/*.py']},
	cmdclass = {'test': TestCommand}
	)
