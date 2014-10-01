
from distutils.core import setup, Command
#from setuptools import setup, Command
import os

from versions import version  # Get the correct version number.

setup(
	name='flipper-topology',  # The name 'flipper' is taken on PyPI.
	version=str(version),
	description='For manipulating curves and measured laminations on surfaces and producing mapping tori.',
	author='Mark Bell',
	author_email='M.C.Bell@warwick.ac.uk',
	url='https://bitbucket.org/Mark_Bell/flipper',
	# Remember to update these if the directory structure changes.
	packages=['flipper', 'flipper.application', 'flipper.load', 'flipper.examples', 'flipper.kernel', 'flipper.tests', 'flipper.profiles'],
	package_dir={'flipper': os.path.dirname(__file__)},
	package_data={
		'': ['./README', './LICENSE', 'docs/*'],
		'flipper.application': ['icon/*', 'docs/*'],
		'flipper.load': ['censuses/*.dat']
		}
	)

