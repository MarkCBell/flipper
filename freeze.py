
import sys
import os
from cx_Freeze import setup, Executable

# Get the correct version.
from flipper.version import __version__

flipper_directory = os.path.join(os.path.dirname(__file__), 'source')
setup(
	name='flipper',
	version=__version__,  # Set the correct version.
	author='Mark Bell',
	description='For manipulating curves and measured laminations on surfaces and producing mapping tori.',
	package_dir={'flipper': flipper_directory},
	options={'build_exe': {
		'icon': os.path.join(flipper_directory, 'application', 'icon', 'icon.ico'),
		'include_files': [(os.path.join(flipper_directory, 'application', 'icon'), './icon')]
		}},
	executables=[Executable(os.path.join(flipper_directory, 'app.py'), targetName='flipper', base=('Win32GUI' if sys.platform == 'win32' else None))]
	)

