import cx_Freeze
import sys
import os
import tkinter
import numpy
os.environ['TCL_LIBRARY']='C:\\Users\\Administrator\\Anaconda3\\tcl\\tcl8\\8.6'
os.environ['TK_LIBRARY']='C:\\Users\\Administrator\\Anaconda3\\tcl\\tk8.6'

base = None

if sys.platform == 'win32':
    base = "Win32GUI"


executables = [cx_Freeze.Executable("main.py", base=base)]

cx_Freeze.setup(
    name = "Bitcoin Lookup",
    options = {"build_exe": {"packages":["tkinter","matplotlib.backends.backend_tkagg","matplotlib.pyplot","matplotlib","numpy","numpy.core._methods","tkinter.filedialog"], "include_files": ['tcl86t.dll','tk86t.dll']}},
    version = "0.01",
    description = "Bitcoin trading application",
    executables = executables
    )
