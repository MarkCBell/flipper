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
		''' Runs all of the test suite. '''
		import Flipper.Test.Lamination
		import Flipper.Test.LayeredTriangulation
		import Flipper.Test.Matrix
		
		print('Passed matrix test: %s' % Flipper.Test.Matrix.main())

setup(
	name='Flipper',
	version=Flipper_version,  # Get the version from the Options class.
	description='Flipper',
	author='Mark Bell',
	author_email='M.C.Bell@warwick.ac.uk',
	url='https://bitbucket.org/Mark_Bell/Flipper',
	packages=['Flipper'],
	package_dir={'Flipper':''},
	package_data={'Flipper': ['Examples/*.py', 'Kernel/*.py', 'App/*.py', 'App/Icon/*', 'Test/*.py']},
	cmdclass = {'test': TestCommand}
	)
