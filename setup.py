# Run the build process by running the command 'python setup.py build'
import sys

from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
        name = "PreludeTimer",
        version = "0.1",
        description = "A Timer that can fade and close a media player near end of countdown",
        executables = [Executable("PreludeTimer.py",
                                  icon = "icon.ico",
                                  base = base)])

# You have to include the cpyHook.py file manually from the pyHook library
