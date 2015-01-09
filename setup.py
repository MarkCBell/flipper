
from __future__ import print_function

import os
try:
	from setuptools import setup, Command
except ImportError:
	print('Unable to import setuptools, using distutils instead.')
	from distutils.core import setup, Command

flipper_directory = os.path.join(os.path.dirname(__file__), 'source')
exec(open(os.path.join(flipper_directory, 'version.py')).read())  # Load in the variable __version__.

setup(
	name='flipper',
	version=__version__,
	description='For manipulating curves and measured laminations on surfaces and producing mapping tori.',
	author='Mark Bell',
	author_email='M.C.Bell@warwick.ac.uk',
	url='https://bitbucket.org/Mark_Bell/flipper',
	# Remember to update these if the directory structure changes.
	packages=['flipper', 'flipper.app', 'flipper.doc', 'flipper.load', 'flipper.example', 'flipper.kernel', 'flipper.test', 'flipper.profile'],
	package_dir={'flipper': flipper_directory},
	package_data={
		'': ['README', 'LICENSE'],
		'flipper.doc': ['flipper.pdf'],
		'flipper.app': ['icon/*', 'frames/*'],
		'flipper.load': ['censuses/*.dat']
		}
	)

