#Aaron Holt
#CSCI 5525
#P0 compiler

#Imports
import sys
import platform
import argparse
import compiler

from compiler.ast import *
from pyast import *

debug=True
# debug=False

if debug:
	print "Debug is on!"


def main():
	inputFile = sys.argv[1]	
	inputFilePath = str(sys.argv[1])	#input path name
	ast = compiler.parseFile(inputFile) #parsed ast

	if debug:
		print str(inputFilePath) #print input path
		print str(ast) #print parsed ast

if __name__ == '__main__':
	main();



