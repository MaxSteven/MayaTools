
# Standard modules
import os

# Our modules
import arkInit
arkInit.init()

import moduleTools

def main():
	moduleTools.compileAllModules(quiet=False)

if __name__ == '__main__':
	main()
