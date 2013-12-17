from distutils.core import setup
import os
from Source.Version import Flipper_version

main_src = ['./lib/py_wrapper.cpp']
kernel_path = './lib/kernel/'
kernal_src = ['twister.cpp', 'manifold.cpp', 'parsing.cpp', 'global.cpp']


setup(
	name='Flipper',
	version=Flipper_version,  # Get the version from the Options class.
	description='Flipper',
	author='Mark Bell',
	author_email='M.C.Bell@warwick.ac.uk',
	url='https://bitbucket.org/Mark_Bell/flipper',
	packages=['Flipper'],
	package_dir={'Flipper':'Source'}
	package_data={'Flipper': ['surfaces/*']},
	)
