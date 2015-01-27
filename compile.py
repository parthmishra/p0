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

varList=[] #keep track of named variables
alias=[] #named variables x86 alias

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
		# print "Parsed AST = ",str(ast) #print parsed ast

	flatAST=flatten(ast)

	# if debug:
	# 	print "Flat AST = ",str(flatAST)
	# for item in flatAST:
	# 	print item

	# x86ast=instr_select_vars(flatAST)
	x=x86(flatAST)

	# print tempVars
	# print ''

	# for item in x:
	# 	print item
	# print ''

	x=pickReg(x)

	# if debug:
	# 	print "x86 AST = ",str(x86ast)

	finalList=[]
	finalList.append('.globl main')
	finalList.append('main:')
	finalList.append('pushl %ebp')
	finalList.append('movl %esp, %ebp')
	finalList.append('subl '+ '$'+str(tempVars2*4)+', ' + '%esp')

	for item in x:
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
	global varList

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
				tempName="Print!!!"+str(tempVars) 
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

		# print "IN ASSIGN", stmts,ts,[Assign(ass,tn)]
		# print "IN ASSIGN", stmts,ts,ass
		# print "IN ASSIGN", stmts,ts,tn

		return stmts+ts+[Assign(ass,tn)]

	elif isinstance(ast,AssName):
		tempVars+=1
		ast.name='!!!'+ast.name
		return (ast,[])

	elif isinstance(ast,Discard):
		tempVars+=1
		tempName="Discard!!!"+str(tempVars)
		expr,stmts=flatten(ast.expr)
		# stmts.append(expr)
		stmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], expr))

		return stmts #discard doesn't do anything really... no need to return ast

	elif isinstance(ast,Add):
		# #Add has ast.left and ast.right
		leftExpr,leftStmts = flatten(ast.left)
		rightExpr,rightStmts = flatten(ast.right)
		#For left instance
		if not (isinstance(leftExpr, Const) or isinstance(leftExpr, Name)):
			tempVars+=1
			tempName="AddLeft!!!"+str(tempVars)
			leftStmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], leftExpr))
			leftExpr=Name(tempName)
		#For right instance
		if not (isinstance(rightExpr, Const) or isinstance(rightExpr, Name)):
			tempVars+=1
			tempName="AddRight!!!"+str(tempVars)
			rightStmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], rightExpr))
			rightExpr=Name(tempName)
		return (Add((leftExpr,rightExpr)),leftStmts+rightStmts)

	elif isinstance(ast,UnarySub):
		# tempVars=tempVars+1
		expr, stmts = flatten(ast.expr)
		if not (isinstance(expr, Const) or isinstance(expr, Name)):
			tempVars+=1
			tempName="UnarySub!!!"+str(tempVars)
			stmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], expr))
			expr=Name(tempName)
		return (UnarySub(expr), stmts)

	elif isinstance(ast,CallFunc):
		#CallFunc has .node, .args, .star_args, .dstar_args
		#For p0 no args required!
		expr,stmts = flatten(ast.node)
		if not (isinstance(expr, Const) or isinstance(expr, Name)):
			tempVars+=1
			tempName="CallFunc!!!"+str(tempVars)
			stmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], expr))
			expr=Name(tempName)

		return (CallFunc(expr,[]),stmts+[])

	elif isinstance(ast,Const):
		return (ast,[]) #terminal, no need for recursive call

	elif isinstance(ast,Name):
		# temp=str(ast.name)
		# if temp[:3]!="!!!":
		# 	tempVars+=0
		# 	temp='!!!'+str(tempVars)
		ast.name='!!!'+ast.name
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
		##First case for printint variables, Second for constants
		try:
			tempExprName=str(ast.nodes[0].name)
		except AttributeError:
			tempExprName=str(x86(ast.nodes[0]))
			# print ast
		# tempExprName=int(tempExprName[-1:])
		# tempExprName=str(tempExprName*4)
		# tempExprName='-'+tempExprName+'(%ebp)'
		temp=[]

		temp.append('pushl,'+tempExprName)
		# temp.append(',')
		temp.append('call,print_int_nl')
		# temp+=','
		temp.append('addl,$4,%esp')
		return temp

	elif isinstance(ast,Assign):
		if isinstance(ast.expr,Add):
			temp=[]
			temp1=[]

			tempExprLeft=str(x86(ast.expr.left))
			tempExprNameLeft=str(ast.nodes[0].name)
			temp.append('movl,'+tempExprLeft+','+tempExprNameLeft)

			tempExprRight=x86(ast.expr.right)
			tempExprNameRight=str(ast.nodes[0].name)
			temp1.append('addl,'+tempExprRight+','+tempExprNameRight)

			return temp+temp1


		elif isinstance(ast.expr,UnarySub):

			temp=[]

			tempExpr=str(x86(ast.expr.expr))
			tempExprName=str(ast.nodes[0].name)
				
			temp.append('movl,'+tempExpr+','+tempExprName)
			temp.append('negl,'+tempExprName)
				# print 'in Assign, UnarySub:',tempExpr,tempExprName

			return temp

		elif isinstance(ast.expr,CallFunc):
			temp=[]

			tempExpr=x86(ast.expr)
			tempExprName=str(ast.nodes[0].name)

			temp.append('movl,%eax,'+tempExprName)
			# print "In Assign, CallFunc", tempExprName

			return tempExpr+temp

		else:
			temp=[]

			tempExpr=str(x86(ast.expr))
			tempExprName=str(ast.nodes[0].name)

			temp.append('movl,'+tempExpr+','+tempExprName)

			# print "TempExprName=",tempExprName

			return temp

	

	elif isinstance(ast,AssName):
		return []

	elif isinstance(ast,CallFunc):
		return ['call,input']

	elif isinstance(ast,Const):
		# l=[]
		# l.append('$'+str(ast.value))
		# # l.append(ast.value)
		# return l
		return '$'+str(ast.value)

	elif isinstance(ast,Name):
		# temp=tempVars
		# tempVars-=1
		return ''+ast.name
		# return ''+str(ast.name)

	else:
		print "!!!!!!!!!!Error: Instance not in p0 (You Shoudn't get here...)!!!!!!!!!!"

def pickReg(ast):
	global tempVars2
	varArray=[]
	finalVars=[]
	finalVarsReg=[]
	for line in ast:
		line=line.split(',')
		# print line[1][:1]
		if line[0]=='movl' or line[0]=='addl':
			if line[1] not in varArray:
				varArray.append(line[1])
			if line[2] not in varArray:
				varArray.append(line[2])
		if line[0]=='negl' or line[0]=='pushl':
			if line[1] not in varArray:
				varArray.append(line[1])
		# print line

	# print varArray

	for item in varArray:
		# print item
		if item[:1]!='$':
			if item[:1]!='%':
				finalVars.append(item)

	# print finalVars


	tempVars2=len(finalVars)
	for item in finalVars:
		finalVarsReg.append(str(-finalVars.index(item)*4-4)+"(%ebp)")
		# print str(-finalVars.index(item)*4-4)+"(%ebp)"

	temp2=[]

	for line in ast:
		line=line.split(',')
		if line[1] in finalVars:
			line[1]=finalVarsReg[finalVars.index(line[1])]
		try:
			if line[2] in finalVars:
				line[2]=finalVarsReg[finalVars.index(line[2])]
		except IndexError:
			pass	
		# print line	
		temp2.append(line)
	# print temp2	

	temp3=[]

	for line in temp2:
		if line[0]=='movl':
			if line[1][:1]=='$' or line[2][:1]=='$':
				temp3.append(line[0]+' '+line[1]+', '+line[2])
			else:
				temp3.append('movl '+line[1]+', '+'%eax')
				temp3.append('movl %eax, '+line[2])
		elif line[0]=='addl':
			if line[1][:1]=='$' or line[2][:1]=='$':
				temp3.append(line[0]+' '+line[1]+', '+line[2])
			else:
				temp3.append('movl '+line[1]+', '+'%eax')
				temp3.append('addl %eax, '+line[2])
		elif line[0]=='negl':
			temp3.append('movl '+line[1]+', '+'%eax')
			temp3.append(line[0]+' '+'%eax')
			temp3.append('movl %eax, '+line[1])

		else:
			temp3.append(line[0]+' '+line[1])


	# for line in temp3:
	# 	print line

	return temp3






if __name__ == '__main__':
	main();



