
import sys
import os
from cx_Freeze import setup, Executable

# Get the correct version.
from flipper.version import __version__

DIRECTORY = os.path.join(os.path.dirname(__file__), 'source')
if sys.platform == 'win32':
	BASE = 'Win32GUI'
	TARGET_NAME = 'flipper.exe'
else:
	BASE = None
	TARGET_NAME = 'flipper'

setup(
	name='flipper',
	version=__version__,  # Set the correct version.
	author='Mark Bell',
	description='For manipulating curves and measured laminations on surfaces and producing mapping tori.',
	package_dir={'flipper': DIRECTORY},
	options={'build_exe': {
		'icon': os.path.join(DIRECTORY, 'application', 'icon', 'icon.ico'),
		'include_files': [(os.path.join(DIRECTORY, 'application', 'icon'), './icon')]
		}},
	executables=[Executable(os.path.join(DIRECTORY, 'app.py'), targetName=TARGET_NAME, base=BASE)]
	)

