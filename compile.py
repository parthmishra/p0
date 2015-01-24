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

print_stmts = 0
temp_counter = -1

def temp_gen(basename):
	global temp_counter
	temp_counter += 1
	return basename + str(temp_counter)

def is_leaf(ast):
    return isinstance(ast, Const) or isinstance(ast, Name)


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

	# x86ast=instr_select_vars(flatAST)

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



def x86(ast):
	global tempVars

	if debug:
		print ast

	if isinstance(ast,Module):
		return x86(ast.node)

	elif isinstance(ast,Stmt):
		n=map(x86,ast.nodes)
		n=sum(n,[])
		return n

	elif isinstance(ast,Printnl):
		# print "#####Printnl x86 ast.nodes[0]####",x86(ast.nodes[0])

		temp=''
		temp+='pushl '+str(x86(ast.nodes[0]))
		temp+=','
		temp+='call print_int_nl'
		temp+=','
		temp+='addl $4, %esp'
		return [temp]

	elif isinstance(ast,Assign):
		if isinstance(ast.expr,Add):

			tempExprLeft=x86(ast.expr.left)
			tempExprName=str(ast.nodes[0].name)
			# if tempExprName=='None':
			# 	tempExprName='ebp'
			temp='movl '+tempExprLeft+', %'+tempExprName
			temp=[temp]
			

			tempExprRight=x86(ast.expr.right)
			tempExprName=str(ast.nodes[0].name)
			temp1='addl '+tempExprRight+', %'+tempExprName
			temp1=[temp1]

			# print 'temp = ',temp
			# print 'temp1 = ',temp1
			# print temp+temp1

			return temp + temp1

		elif isinstance(ast.expr,UnarySub):
			tempExpr=x86(ast.expr.expr)
			tempExprName=str(ast.nodes[0].name)
			temp='movl '+'%'+tempExpr+', %'+tempExprName
			temp=[temp]

			temp1='negl '+'%'+str(ast.nodes[0].name)
			temp1=[temp1]

			# print 'temp = ',temp
			# print 'temp1 = ',temp1
			# print temp+temp1

			return temp+temp1

		elif isinstance(ast.expr,CallFunc):
			tempExpr=x86(ast.expr)

			# print 'tempExpr =', tempExpr
			# tempExprName=str(ast.nodes[0].name)
			temp1='movl '+'%eax, '+'%'+str(ast.nodes[0].name)
			temp1=[temp1]
			# print 'temp1 =',temp1
			return tempExpr+temp1

		else:
			return ['movl '+x86(ast.expr)+' '+str(ast.nodes[0].name)]

	if isinstance(ast,Add):
		if isinstance(ast.left,Const):
			tempExprLeft=x86(ast.left)
			tempExprName='%eax'
		elif isinstance(ast.left,Name):
			tempExprLeft='%'+x86(ast.left)
			tempExprName=str(x86(ast.left))

		if isinstance(ast.right,Const):
			tempExprRight=x86(ast.right)
			tempExprName='%eax'
		elif isinstance(ast.right,Name):
			tempExprRight='%'+x86(ast.right)
			tempExprName=str(x86(ast.right))

		temp='movl '+tempExprLeft+', '+tempExprName
		temp=[temp]
		temp1='addl '+tempExprRight+', '+tempExprName
		# print 'In Add:temp = ',temp
		# print 'In Add:temp1 = ',temp1
		return temp+[temp1]


	elif isinstance(ast,AssName):
		return []

	elif isinstance(ast,CallFunc):
		return ['call input']

	elif isinstance(ast,Const):
		return '$'+str(ast.value)

	elif isinstance(ast,Name):
		temp=tempVars
		tempVars-=1
		return ''+ast.name
		# return ''+str(ast.name)

	else:
		print "!!!!!!!!!!Error: Instance not in p0 (You Shoudn't get here...)!!!!!!!!!!"	


if __name__ == '__main__':
	main();



