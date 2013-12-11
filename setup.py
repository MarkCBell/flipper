
import sys
from cx_Freeze import setup, Executable
from Source.Version import Flipper_version

setup(
	name = 'Flipper',
	version = Flipper_version,  # Get the version from the Options class.
	description = 'For manipulating curves on surfaces and producing mapping tori.',
	options = {'build_exe':{'icon':'./Source/Icon/Icon.ico', 'include_files':['./Source/Icon']}},
	executables = [Executable('Flipper.py', base=('Win32GUI' if sys.platform == 'win32' else None))]
	)
