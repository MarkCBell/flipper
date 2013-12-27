
import sys
from cx_Freeze import setup, Executable
from Flipper.Kernel.Version import Flipper_version

setup(
	name = 'Flipper',
	version = Flipper_version,  # Get the version from the Options class.
	description = 'For manipulating curves on surfaces and producing mapping tori.',
	options = {'build_exe':{'icon':'./App/Icon/Icon.ico', 'include_files':['./App/Icon']}},
	executables = [Executable('app.py', base=('Win32GUI' if sys.platform == 'win32' else None))]
	)
