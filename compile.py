#Aaron Holt
#CSCI 5525
#P0 compiler

#Imports
import sys
import platform
import argparse
import compiler

from compiler.ast import *
# from pyast import *
# from x86classes import *

# debug=True
debug=False

if debug:
	print "Debug is on!"


tempVars=0 #number of temp variables needed so far
tempVars2=0 #max number of temp variables 
printCount=0 #number of print statements




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
	tempVars2=tempVars
	x86ast=x86(flatAST)

	if debug:
		print "x86 AST = ",str(x86ast)

	finalList=[]
	finalList.append('.globl main')
	finalList.append('main:')
	finalList.append('pushl %ebp')
	finalList.append('movl %esp, %ebp')
	finalList.append('subl '+ '$'+str(tempVars2*4)+', ' + '%esp')

	for item in x86ast:
		finalList.append(item)

	# finalList.append('movl $2, -4(%ebp)')
	# finalList.append('pushl -4(%ebp)')
	# finalList.append('call input')
	# finalList.append('movl %eax, -4(%ebp)')
	# finalList.append('addl $4, %esp')

	finalList.append('movl $0, %eax')
	finalList.append('leave')
	finalList.append('ret')

	# print "FINAL",finalList
	for item in finalList:
		print item

	f=open(outputFilePath,'w')

	for item in finalList:
		f.write(str(item))
		f.write('\n')
	f.close()

def flatten(ast):
	global tempVars
	if debug:
		print ast

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
				tempName="!!!"+str(tempVars) 
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
		# print "In flatten,assign:",ass
		stmts=sum([l for (t,l) in n],[])
		tn,ts=flatten(ast.expr)
		return stmts+ts+[Assign(ass,tn)]

	elif isinstance(ast,AssName):
		# print ("IN AssName:"),ast,ast.name,ast.name[:3]
		# if str(AssName.)
		temp=str(ast.name)
		if temp[:3]!="!!!":
			tempVars+=1
			temp='!!!'+str(tempVars)
			ast.name=temp
		# if ast.name()[:3]!=['!!!']:
		# 	tempVars+=1
		# 	ast.name='!!!'+str(tempVars)
		return (ast,[])

	elif isinstance(ast,Discard):
		tempVars+=1
		tempName="!!!"+str(tempVars)
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
			tempName="!!!"+str(tempVars)
			leftStmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], leftExpr))
			leftExpr=Name(tempName)
		#For right instance
		if not (isinstance(rightExpr, Const) or isinstance(rightExpr, Name)):
			tempVars+=1
			tempName="!!!"+str(tempVars)
			rightStmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], rightExpr))
			rightExpr=Name(tempName)
		return (Add((leftExpr,rightExpr)),leftStmts+rightStmts)

	elif isinstance(ast,UnarySub):
		tempVars=tempVars+1
		expr, stmts = flatten(ast.expr)
		if not (isinstance(expr, Const) or isinstance(expr, Name)):
			tempVars+=1
			tempName="!!!"+str(tempVars)
			stmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], expr))
			expr=Name(tempName)
		return (UnarySub(expr), stmts)

	elif isinstance(ast,CallFunc):
		#CallFunc has .node, .args, .star_args, .dstar_args
		#For p0 no args required!
		expr,stmts = flatten(ast.node)
		if not (isinstance(expr, Const) or isinstance(expr, Name)):
			tempVars+=1
			tempName="!!!"+str(tempVars)
			stmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], expr))
			expr=Name(tempName)

		# args_exprs = []
		# args_stmts = []
		# for arg in ast.args:
		# 	arg_expr, arg_stmts = flatten(arg)
		# 	if not (isinstance(arg.expr, Const) or isinstance(arg.expr, Name)):
		# 		tempVars+=1
		# 		temp = "!!!"+str(tempVars)
		# 		arg_stmts.append(Assign([AssName(temp, 'OP_ASSIGN')], arg_expr))
		# 		arg_expr = Name(temp)
		# 	args_exprs.append(arg_expr)
		# 	args_stmts = args_stmts + arg_stmts


		# return (CallFunc(expr,[]),stmts+[])
		return (CallFunc(expr, args_exprs), stmts + args_stmts)

	elif isinstance(ast,Const):
		return (ast,[]) #terminal, no need for recursive call

	elif isinstance(ast,Name):
		temp=str(ast.name)
		if temp[:3]!="!!!":
			tempVars+=0
			temp='!!!'+str(tempVars)
			ast.name=temp
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
		tempExprName=str(ast.nodes[0].name)
		tempExprName=int(tempExprName[-1:])
		tempExprName=str(tempExprName*4)
		tempExprName='-'+tempExprName+'(%ebp)'
		temp=[]

		temp.append('pushl '+tempExprName)
		# temp.append(',')
		temp.append('call print_int_nl')
		# temp+=','
		temp.append('addl $4, %esp')
		return temp

	elif isinstance(ast,Assign):
		if isinstance(ast.expr,Add):
			temp=[]
			temp1=[]
			if isinstance(ast.expr.left,Const):
				tempExprLeft=str(x86(ast.expr.left))
				tempExprLeft=int(tempExprLeft[1:])
				tempExprLeft=str(tempExprLeft)
				tempExprLeft='$'+tempExprLeft

				tempExprName=str(ast.nodes[0].name)
				tempExprName=tempExprName.split('!!!',1)
				tempExprName=int(tempExprName[1])*4
				tempExprName=str(tempExprName)
				tempExprName=', -'+tempExprName+'(%ebp)'

				temp.append('movl '+tempExprLeft+tempExprName)

				tempExprRight=x86(ast.expr.right)
				temp1='addl '+tempExprRight+tempExprName
				temp1=[temp1]
			elif isinstance(ast.expr.left,Name):
				tempExprLeft=str(x86(ast.expr.left))
				tempExprLeft=tempExprLeft.split('!!!',1)
				tempExprLeft=int(tempExprLeft[1])*4
				tempExprLeft=str(tempExprLeft)
				tempExprLeft='-'+tempExprLeft+'(%ebp)'
				temp.append('movl '+tempExprLeft+', %eax')

				tempExprName=str(ast.nodes[0].name)
				tempExprName=tempExprName.split('!!!',1)
				tempExprName=int(tempExprName[1])*4
				tempExprName=str(tempExprName)
				tempExprName=', -'+tempExprName+'(%ebp)'
				
				temp.append('movl '+'%eax'+tempExprName)
				print 'in Assign, Add:',tempExprLeft,tempExprName
				tempExprRight=x86(ast.expr.right)

				temp1='addl '+tempExprRight+tempExprName
				temp1=[temp1]

			return temp+temp1


		elif isinstance(ast.expr,UnarySub):

			temp=[]
			temp1=[]

			if isinstance(ast.expr.expr,Name):
				tempExpr=str(x86(ast.expr.expr))
				tempExpr=tempExpr.split('!!!',1)
				tempExpr=int(tempExpr[1])*4
				tempExpr=str(tempExpr)
				tempExpr='-'+tempExpr+'(%ebp)'
				temp.append('movl '+tempExpr+', %eax')
				temp.append('negl '+'%eax')

				tempExprName=str(ast.nodes[0].name)
				tempExprName=tempExprName.split('!!!',1)
				tempExprName=int(tempExprName[1])*4
				tempExprName=str(tempExprName)
				tempExprName=', -'+tempExprName+'(%ebp)'
				
				temp.append('movl '+'%eax'+tempExprName)
				# print 'in Assign, UnarySub:',tempExpr,tempExprName

			elif isinstance(ast.expr.expr,Const):
				tempExpr=str(x86(ast.expr.expr))
				tempExpr=int(tempExpr[1:])
				tempExpr=str(tempExpr)
				tempExpr='$'+tempExpr
				
				temp.append('movl '+tempExpr+', %eax')
				temp.append('negl '+'%eax')

				tempExprName=str(ast.nodes[0].name)
				tempExprName=tempExprName.split('!!!',1)
				tempExprName=int(tempExprName[1])*4
				tempExprName=str(tempExprName)
				tempExprName=', -'+tempExprName+'(%ebp)'

				temp.append('movl '+'%eax'+tempExprName)
				# print 'in Assign, UnarySub, CONST:',tempExpr,tempExprName


			return temp

		elif isinstance(ast.expr,CallFunc):
			tempExpr=x86(ast.expr)
			temp=[]
			tempExprName=str(ast.nodes[0].name)

			tempExprName=tempExprName.split('!!!',1)
			tempExprName=int(tempExprName[1])*4
			# tempExprName=int(tempExprName[-1:])

			tempExprName=str(tempExprName)
			tempExprName=', -'+tempExprName+'(%ebp)'
				
			temp.append('movl '+'%eax'+tempExprName)
			# print 'tempExpr =', tempExpr
			# tempExprName=str(ast.nodes[0].name)
			# temp1='movl '+'%eax, '+'%'+str(ast.nodes[0].name)
			# temp1=[temp1]
			# print 'temp1 =',temp1
			return tempExpr+temp
			# return tempExpr

		else:
			tempExprName=str(ast.nodes[0].name)

			tempExprName=tempExprName.split('!!!',1)
			tempExprName=int(tempExprName[1])*4
			# tempExprName=int(tempExprName[-1:])

			tempExprName=str(tempExprName)
			tempExprName=', -'+tempExprName+'(%ebp)'
			return ['movl '+x86(ast.expr)+tempExprName]
			# print "HEREHEREHERE", x86(ast.expr)
			# return ['movl '+x86(ast.expr)+' '+str(ast.nodes[0].name)]

	if isinstance(ast,Add):
		if isinstance(ast.left,Const):
			tempExprLeft=x86(ast.left)
			tempExprName='%eax'
		elif isinstance(ast.left,Name):
			# tempExprLeft='%'+x86(ast.left)
			tempExprLeft=str(x86(ast.left))

			tempExprLeft=tempExprLeft.split('!!!',1)
			tempExprLeft=int(tempExprLeft[1])*4
			# tempExprLeft=int(tempExprLeft[-1:])

			tempExprLeft=str(tempExprLeft)
			tempExprLeft='-'+tempExprLeft+'(%ebp)'
			# print 'HEREHEREHERE', tempExprLeft

		if isinstance(ast.right,Const):
			tempExprRight=x86(ast.right)
			tempExprName='%eax'
		elif isinstance(ast.right,Name):
			# tempExprRight='%'+x86(ast.right)
			# tempExprName=str(x86(ast.right))
			tempExprRight=str(x86(ast.left))

			tempExprRight=tempExprRight.split('!!!',1)
			tempExprRight=int(tempExprRight[1])*4
			# tempExprRight=int(tempExprRight[-1:])

			tempExprRight=str(tempExprRight)
			tempExprRight='-'+tempExprRight+'(%ebp)'


		# print "TER=", tempExprRight
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
		# l=[]
		# l.append('$'+str(ast.value))
		# # l.append(ast.value)
		# return l
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



