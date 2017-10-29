
import os
try:
	from setuptools import setup
except ImportError:
	print('Unable to import setuptools, using distutils instead.')
	from distutils.core import setup

def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name='flipper',
	version='0.12.3',
	description='For manipulating curves and measured laminations on surfaces and producing mapping tori.',
	long_description=read('README'),
	author='Mark Bell',
	author_email='mcbell@illinois.edu',
	url='https://bitbucket.org/Mark_Bell/flipper',
	# Remember to update these if the directory structure changes.
	packages=[
		'flipper',
		'flipper.application',
		'flipper.kernel',
		'flipper.kernel.interface',
		'flipper.test',
		'flipper.profile'
		],
	package_data={
		'flipper': ['censuses/*.csv'],
		'flipper.application': ['icon/*', 'frames/*'],
		},
	install_requires=[
		'pandas',  # censuses.
		],
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Education',
		'Intended Audience :: Science/Research',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Scientific/Engineering :: Mathematics',
		],
	)

