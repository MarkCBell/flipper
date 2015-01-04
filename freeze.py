
import sys
import os
from cx_Freeze import setup, Executable

# Get the correct version.
flipper_directory = os.path.join(os.path.dirname(__file__), 'flipper_triangulation')
from flipper.version import __version__

setup(
	name='flipper',
	version=__version__,  # Get the correct version.
	author='Mark Bell',
	description='For manipulating curves and measured laminations on surfaces and producing mapping tori.',
	package_dir={'flipper': flipper_directory},
	options={'build_exe': {'icon': './flipper_triangulation/app/icon/icon.ico', 'include_files': [('./flipper_triangulation/app/icon/', './icon')]}},
	executables=[Executable('./flipper_triangulation/app/__main__.py', targetName='flipper', base=('Win32GUI' if sys.platform == 'win32' else None))]
	)

