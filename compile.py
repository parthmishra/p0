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
from x86classes import *

debug=True
# debug=False

if debug:
	print "Debug is on!"


tempVars=-1 #number of temp variables needed so far
printCount=0 #number of print statements

# print_stmts = 0
# temp_counter = -1

# def temp_gen(basename):
# 	global temp_counter
# 	temp_counter += 1
# 	return basename + str(temp_counter)

# def is_leaf(ast):
#     return isinstance(ast, Const) or isinstance(ast, Name)


def main():
	inputFile = sys.argv[1]	
	inputFilePath = str(sys.argv[1])	#input path name
	ast = compiler.parseFile(inputFile) #parsed ast
	outputFilePath = inputFilePath.split('.')
	outputFilePath = outputFilePath[0]+str('.s')

	if debug:
		print str(inputFilePath) #print input path
		print str(outputFilePath) #print input path
		print "Parsed AST = ",str(ast) #print parsed ast

	flatAST=flatten(ast)

	if debug:
		print "Flat AST = ",str(flatAST)

	x86ast=x86(flatAST)

	if debug:
		print "x86 AST = ",str(x86ast)

def flatten(ast):
	global tempVars
	# if debug:
	# 	print ast

	if isinstance(ast,Module):
		return Module(ast.doc, flatten(ast.node))

	elif isinstance(ast,Stmt):
		##Stmt only has .nodes
		# print "STMT in Stmt = ", str(Stmt), ast
		# return Stmt(flatten(ast.nodes))
		##This left a [] around the inner statement...

		##this gets rid of pesky brackets...
		n=map(flatten,ast.nodes)
		n=sum(n,[])
		return Stmt(n)

	elif isinstance(ast,Printnl):
		# #has .nodes and .dest
		# #again with the pesky brackets...
		# n=map(flatten,ast.nodes)
		# p=[]
		# for (t,l) in n:
		# 	p.append(t)
		# stmts=sum([l for (t, l) in n],[])
		# return stmts, [Printnl(p,ast.dest)]

		############CHECK THIS AGAIN LATER###################
		nodes = map(flatten, ast.nodes) #Apply flatten function to all inner nodes
		p = []
		for (t,l) in nodes:
			#Check to see if either side has more nodes
			if not (isinstance(t, Const) or isinstance(t, Name)):
				tempVars+=1
				tempName="print"+str(tempVars) 
				l.append(Assign([AssName(tempName, 'OP_ASSIGN')], t)) #Assign print name to statement value
				p.append(Name(tempName)) 
			else:
				p.append(t)
		stmts = sum([l for (t, l) in nodes], [])
		return stmts + [Printnl(p, ast.dest)]


	elif isinstance(ast,Assign):
		#assign has .nodes .expr
		n=map(flatten,ast.nodes)
		ass=[t for (t,l) in n]
		stmts=sum([l for (t,l) in n],[])
		tn,ts=flatten(ast.expr)
		return stmts+ts+[Assign(ass,tn)]

	elif isinstance(ast,AssName):
		return (ast,[])

	elif isinstance(ast,Discard):
		tempVars+=1
		tempName="discard"+str(tempVars)
		expr,stmts=flatten(ast.expr)
		stmts.append(expr)
		# print "EXPR, STMTS =", expr,stmts
		# stmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], expr))
		return stmts #discard doesn't do anything really... no need to return ast

	elif isinstance(ast,Add):
		# #Add has ast.left and ast.right
		leftExpr,leftStmts = flatten(ast.left)
		rightExpr,rightStmts = flatten(ast.right)
		#For left instance
		if not (isinstance(leftExpr, Const) or isinstance(leftExpr, Name)):
			tempVars+=1
			tempName="addleft"+str(tempVars)
			leftStmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], leftExpr))
			leftExpr=Name(tempName)
		#For right instance
		if not (isinstance(rightExpr, Const) or isinstance(rightExpr, Name)):
			tempVars+=1
			tempName="addright"+str(tempVars)
			rightStmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], rightExpr))
			rightExpr=Name(tempName)
		return (Add((leftExpr,rightExpr)),leftStmts+rightStmts)

	elif isinstance(ast,UnarySub):
		tempVars=tempVars+1
		expr, stmts = flatten(ast.expr)
		if not (isinstance(expr, Const) or isinstance(expr, Name)):
			tempVars+=1
			tempName="unarysub"+str(tempVars)
			stmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], expr))
			expr=Name(tempName)
		return (UnarySub(expr), stmts)

	elif isinstance(ast,CallFunc):
		#CallFunc has .node, .args, .star_args, .dstar_args
		#For p0 no args required!
		expr,stmts = flatten(ast.node)
		if not (isinstance(expr, Const) or isinstance(expr, Name)):
			tempVars+=1
			tempName="callfunc"+str(tempVars)
			stmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], expr))
			expr=Name(tempName)
		return (CallFunc(expr,[]),stmts+[])

	elif isinstance(ast,Const):
		return (ast,[]) #terminal, no need for recursive call

	elif isinstance(ast,Name):
		return (ast,[]) #terminal, no need for recursive call

	else:
		print "Error: Instance not in p0"

	# flatAST=ast.getChildNodes()
	# if debug:
	# 	print str(flatAST)

def x86(ast):
	if debug:
		print ast

	if isinstance(ast,Module):
		return x86(ast.node)

	if isinstance(ast,Stmt):
		n=map(x86,ast.nodes)
		n=sum(n,[])
		return n
		# return sum(map(x86, ast.nodes),[])

	if isinstance(ast,Const):
		return [ast.value]
		# return ['$'+str(ast.value)]

		# return Const86(ast.value)
		# class Const86(X86Arg):
		#     def __init__(self, value):
		#         self.value = value
		#     def mnemonic(self):
		#         return '$' + str(self.value)
	



if __name__ == '__main__':
	main();



