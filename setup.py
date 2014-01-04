
import os
from distutils.core import setup, Command
from Kernel.Version import Flipper_version

# So we can access all of the test suite just by doing "python setup.py test"
class TestCommand(Command):
	user_options = []
	
	def initialize_options(self):
		pass
	
	def finalize_options(self):
		pass
	
	def run(self):
		''' Runs all of the tests in the Tests directory. '''
		import Flipper.Tests.AlgebraicApproximation
		import Flipper.Tests.Interval
		import Flipper.Tests.Lamination
		import Flipper.Tests.LayeredTriangulation
		import Flipper.Tests.Matrix
		
		print('Running AlgebraicApproximation test...')
		print('\tPassed' if Flipper.Tests.AlgebraicApproximation.main() else '\tFailed')
		print('Running Interval test...')
		print('\tPassed' if Flipper.Tests.Interval.main() else '\tFailed')
		print('Running Lamination test...')
		print('\tPassed' if Flipper.Tests.Lamination.main() else '\tFailed')
		print('Running LayeredTriangulation test...')
		print('\tPassed' if Flipper.Tests.LayeredTriangulation.main() else '\tFailed')
		print('Running Matrix test...')
		print('\tPassed' if Flipper.Tests.Matrix.main() else '\tFailed')

setup(
	name='Flipper',
	version=Flipper_version,  # Get the version from the Options class.
	description='Flipper',
	author='Mark Bell',
	author_email='M.C.Bell@warwick.ac.uk',
	url='https://bitbucket.org/Mark_Bell/Flipper',
	packages=['Flipper'],
	package_dir={'Flipper':''},
	# Remember to update these if the directory structure changes.
	package_data={'Flipper': ['Examples/*.py', 'Kernel/*.py', 'App/*.py', 'App/Icon/*', 'Tests/*.py']},
	cmdclass = {'test': TestCommand}
	)
