
import sys
import os
from cx_Freeze import setup, Executable

# Get the correct version.
flipper_directory = os.path.join(os.path.dirname(__file__), 'flipper_package')
from flipper.version import __version__

setup(
	name='flipper',
	version=__version__,  # Get the correct version.
	author='Mark Bell',
	description='For manipulating curves and measured laminations on surfaces and producing mapping tori.',
	package_dir={'flipper': flipper_directory},
	options={'build_exe': {'icon': './flipper_package/application/icon/icon.ico', 'include_files': [('./flipper_package/application/icon/', './icon'), ('./flipper_package/application/docs/', './flipper_package/docs')]}},
	executables=[Executable('./flipper_package/app.py', base=('Win32GUI' if sys.platform == 'win32' else None))]
	)

