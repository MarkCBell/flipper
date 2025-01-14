#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''The setup script.'''

from setuptools import setup, find_packages

requirements = [
    'decorator>=4.3.0',
    'numpy>=1.15.1',
    'networkx>=2.0',
    'pandas>=1.0.0',
    'realalg>=0.3.2',
]

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='flipper',
    version='0.15.6',
    description='For manipulating curves and measured laminations on surfaces and producing mapping tori.',
    long_description=readme(),
    author='Mark Bell',
    author_email='mcbell@illinois.edu',
    url='https://github.com/MarkCBell/flipper',
    packages=find_packages(),
    entry_points='''
    [gui_scripts]
    flipper.app=flipper.app:main
    ''',
    include_package_data=True,
    install_requires=requirements,
    license='MIT License',
    zip_safe=False,
    keywords='flipper',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Mathematics',
        ],
)

