#!/usr/bin/env python
import os
import tkMessageBox
import webbrowser
cwd = os.getcwd() + '\support_Files'
if os.path.exists('C:\Program Files\doxygen') == True:
    
    os.system("q: && cd " + cwd + " && doxygen doxyFile.txt")
else:
    tkMessageBox.showerror("Error, get Doxygen to run", "Doxygen must be on the machine that is running this command.\n Please download and install Doxygen at the following link:\n http://www.stack.nl/~dimitri/doxygen/download.html#latestsrc")
    webbrowser.open("http://www.stack.nl/~dimitri/doxygen/download.html#latestsrc")

