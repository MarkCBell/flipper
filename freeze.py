
import sys
from cx_Freeze import setup, Executable

# Get the correct version.
from versions import version

setup(
	name='flipper',
	version=str(version),  # Get the correct version.
	author='Mark Bell',
	description='For manipulating curves and measured laminatins on surfaces and producing mapping tori.',
	options={'build_exe': {'icon': './application/icon/icon.ico', 'include_files': [('./application/icon/', './icon'), ('./application/docs/', './docs')]}},
	executables=[Executable('app.py', base=('Win32GUI' if sys.platform == 'win32' else None))]
	)

