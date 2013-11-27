
import sys
from cx_Freeze import setup, Executable

setup(
	name = 'Flipper',
	version = '0.1.0',
	description = 'For manipulating curves on surfaces and producing mapping tori.',
	# options = {'build_exe':{'create_shared_zip':False, 'packages': ['sympy']}},
	executables = [Executable('Flipper.py', base=('Win32GUI' if sys.platform == 'win32' else None))]  # , appendScriptToExe=True, appendScriptToLibrary=False)]
	)
