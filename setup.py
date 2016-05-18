
from __future__ import print_function

import os
try:
	from setuptools import setup
except ImportError:
	print('Unable to import setuptools, using distutils instead.')
	from distutils.core import setup

this_directory = os.path.dirname(__file__)
source_directory = os.path.join(this_directory, 'source')
exec(open(os.path.join(source_directory, 'version.py')).read())  # Load in the variable __version__.

setup(
	name='flipper',
	version=__version__,
	description='For manipulating curves and measured laminations on surfaces and producing mapping tori.',
	author='Mark Bell',
	author_email='M.C.Bell@warwick.ac.uk',
	url='https://bitbucket.org/Mark_Bell/flipper',
	# Remember to update these if the directory structure changes.
	packages=[
		'flipper',
		'flipper.application',
		'flipper.doc',
		'flipper.example',
		'flipper.kernel',
		'flipper.kernel.interface',
		'flipper.test',
		'flipper.profile'
		],
	package_dir={'flipper': source_directory},
	package_data={
		'flipper': ['censuses/*.dat'],
		'flipper.doc': ['flipper.pdf'],
		'flipper.application': ['icon/*', 'frames/*'],
		},
	install_requires=['cypari']
	)

