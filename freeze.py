
import sys
from cx_Freeze import setup, Executable

# Get the correct version.
from flipper.version import __version__

setup(
	name='flipper',
	version=__version__,  # Get the correct version.
	author='Mark Bell',
	description='For manipulating curves and measured laminations on surfaces and producing mapping tori.',
	options={'build_exe': {'icon': './application/icon/icon.ico', 'include_files': [('./application/icon/', './icon'), ('./application/docs/', './docs')]}},
	executables=[Executable('app.py', base=('Win32GUI' if sys.platform == 'win32' else None))]
	)

