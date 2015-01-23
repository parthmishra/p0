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


tempVars=-1 #number of temp variables needed so far
printCount=0 #number of print statements

def main():
	inputFile = sys.argv[1]	
	inputFilePath = str(sys.argv[1])	#input path name
	ast = compiler.parseFile(inputFile) #parsed ast

	if debug:
		print str(inputFilePath) #print input path
		print "Parsed AST = ",str(ast) #print parsed ast

	flatAST=flatten(ast)

	if debug:
		print "Flat AST = ",str(flatAST)

def flatten(ast):
	if debug:
		print ast

	if isinstance(ast,Module):
		return Module(ast.doc, flatten(ast.node))

	elif isinstance(ast,Stmt):
		# print "STMT in Stmt = ", str(Stmt), ast

		return Stmt(ast.doc,flatten(ast.node))

	elif isinstance(ast,Printnl):
		return ast

	elif isinstance(ast,Assign):
		return ast

	elif isinstance(ast,AssName):
		return ast

	elif isinstance(ast,Discard):
		tempVars+=1
		tempName="discard"+str(tempVars)
		expr,stmts=flatten(ast.expr)
		# print "EXPR, STMTS =", expr,stmts
		stmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], expr))
		return stmts #discard doesn't do anything really... no need to return ast

	elif isinstance(ast,Add):
		return ast

	elif isinstance(ast,UnarySub):
		tempVars+=1
		expr, stmts = flatten(ast.expr)
		return (UnarySub(expr), stmts)

	elif isinstance(ast,CallFunc):
		return ast

	elif isinstance(ast,Const):
		return (ast,[]) #terminal, no need for recursive call

	elif isinstance(ast,Name):
		return (ast,[]) #terminal, no need for recursive call

	else:
		print "Error: Instance not in p0"

	# flatAST=ast.getChildNodes()
	# if debug:
	# 	print str(flatAST)


if __name__ == '__main__':
	main();



