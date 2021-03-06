#Aaron Holt
#CSCI 5525
#P0 compiler

# import ply.yacc as yacc

#Imports
import sys
import compiler
import re

from compiler.ast import *

from parser1 import parse_file
from class86 import *
from explicate import *


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

	##With builtin parser/lexer
	ast = compiler.parseFile(inputFile) #parsed ast
	# wast = compiler.parseFile(inputFile) #to compare to my new parser

	##With my parser/lexer
	# ast=parse_file(inputFile)

	outputFilePath = inputFilePath.split('.')
	outputFilePath = outputFilePath[0]+str('.s')

	if debug:
		print str(inputFilePath) #print input path
		print str(outputFilePath) #print input path
		print "Parsed AST = ",str(ast) #print parsed ast
		# print "Correct AST = ",str(wast)

	#make flatAST
	flatAST=flatten(ast)

	# if debug:
	# 	print "Flat AST = ",str(flatAST)
	# for item in flatAST:
	# 	print item


	#generate x86ish ast
	x=x86(flatAST)

	# print ''
	# for item in x:
	# 	print item
	# print ''
	
	# x=pickReg(x)

	# finalList2=[]
	# finalList2.append('.globl main')
	# finalList2.append('main:')
	# finalList2.append('pushl %ebp')
	# finalList2.append('movl %esp, %ebp')
	# finalList2.append('subl $4000, %esp')

	# for item in x:
	# 	finalList2.append(item)

	# finalList2.append('movl $0, %eax')
	# finalList2.append('leave')
	# finalList2.append('ret')



	#send flat x86ish ast to liveness
	alive=liveness(x)

	#create interference graph using flat x86ish ast, liveness analysis
	intGraph=interference(x,alive)

	#color the graph
	(color_table, colors_used) = colorer(intGraph)

	#Allocate registers (Finally!)
	assembly_final = assign_homes(x, color_table, colors_used)

	#for ii in assembly_final:
	#	print ii

	# x=pickReg(x)

	# if debug:
	# 	print "x86 AST = ",str(x86ast)

	finalList=[]
	finalList.append('.globl main')
	finalList.append('main:')
	for item in assembly_final:
		finalList.append(item)

	#Found an error, only way I could think of to fix it
	finalList2=[]
	for item in finalList:
		line=str(item)

		line=line.split(' ')
		if line[0]=='movl':
			if line[1][0]=='-' and line[2][0]=='-':
				finalList2.append('movl '+line[1]+' '+'%eax')
				finalList2.append('movl %eax, '+line[2])
			else:
				finalList2.append(item)
		elif line[0]=='addl':
			if line[1][0]=='-':
				finalList2.append('movl '+line[1]+' '+'%eax')
				finalList2.append('addl %eax, '+line[2])
			else:
				finalList2.append(item)
		else:
			finalList2.append(item)
	
	print ''
	for item in finalList2:
		print item

	f=open(outputFilePath,'w')

	for item in finalList2:
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
				tempName="Print"+str(tempVars) 
				l.append(Assign([AssName(tempName, 'OP_ASSIGN')], t)) #Assign print name to statement value
				p.append(Name(tempName)) 
			else:
				p.append(t)
		stmts = sum([l for (t, l) in nodes], [])
		# print stmts, [Printnl(p, ast.dest)]
		return stmts + [Printnl(p, ast.dest)]


	elif isinstance(ast,Assign):
		#assign has .nodes .expr
		#ass is [AssName('!!!y', 'OP_ASSIGN')]
		#stmts is stuff to left of it
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
		ast.name=''+ast.name
		return (ast,[])

	elif isinstance(ast,Discard):
		tempVars+=1
		tempName="Discard"+str(tempVars)
		expr,stmts=flatten(ast.expr)

		# stmts.append(expr)
		stmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], expr))
		# print expr, stmts
		return stmts #discard doesn't do anything really... no need to return ast

	elif isinstance(ast,Add):
		# #Add has ast.left and ast.right
		leftExpr,leftStmts = flatten(ast.left)
		rightExpr,rightStmts = flatten(ast.right)
		#For left instance
		if not (isinstance(leftExpr, Const) or isinstance(leftExpr, Name)):
			tempVars+=1
			tempName="AddLeft"+str(tempVars)
			leftStmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], leftExpr))
			leftExpr=Name(tempName)
		#For right instance
		if not (isinstance(rightExpr, Const) or isinstance(rightExpr, Name)):
			tempVars+=1
			tempName="AddRight"+str(tempVars)
			rightStmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], rightExpr))
			rightExpr=Name(tempName)
		return (Add((leftExpr,rightExpr)),leftStmts+rightStmts)

		#After class discussiong could have done something like:
		# (left, assigns_left) = flatten_expr(e.left)
        # (right, assigns_right) = flatten_expr(e.right)
		#temp=tempnamegen()
		#assign=Assign([AssName(temp,'OP_ASSIGN')],Add((left,right)))
		# return (temp, assigns_left + assigns_right + [assign])

	elif isinstance(ast,UnarySub):
		# tempVars=tempVars+1
		expr, stmts = flatten(ast.expr)
		if not (isinstance(expr, Const) or isinstance(expr, Name)):
			tempVars+=1
			tempName="UnarySub"+str(tempVars)
			stmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], expr))
			expr=Name(tempName)
		return (UnarySub(expr), stmts)

	elif isinstance(ast,CallFunc):
		#Const86 has .node, .args, .star_args, .dstar_args
		#For p0 no args required!
		expr,stmts = flatten(ast.node)
		if not (isinstance(expr, Const) or isinstance(expr, Name)):
			tempVars+=1
			tempName="CallFunc"+str(tempVars)
			stmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], expr))
			expr=Name(tempName)

		return (CallFunc(expr,[]),stmts+[])

	elif isinstance(ast,Const):
		return (ast,[]) #terminal, no need for recursive call

	elif isinstance(ast,Name):

		ast.name=''+ast.name
		return (ast,[]) #terminal, no need for recursive call

	else:
		print "Error: Instance not in p0"
		print ast

def x86(ast):
	if isinstance(ast,Module):
		return x86(ast.node)
	elif isinstance(ast,Stmt):
		return sum(map(x86,ast.nodes),[])
	elif isinstance(ast,CallFunc):
		return [Call86('input')]
	elif isinstance(ast,Const):
		return Const86(ast.value)
	elif isinstance(ast,Name):
		return Var(ast.name, -1)
	elif isinstance(ast,AssName):
		return []
	elif isinstance(ast,Printnl):
		return [Push86(x86(ast.nodes[0])), Call86('print_int_nl'), Add86(Const86(4),ESP)]
	elif isinstance(ast, Assign):
		if isinstance(ast.expr, Add):
			temp = [Move86(x86(ast.expr.left), Var(ast.nodes[0].name,-1))]
			return temp + [Add86(x86(ast.expr.right), Var(ast.nodes[0].name,-1))]
		elif isinstance(ast.expr, UnarySub):
			temp = [Move86(x86(ast.expr.expr), Var(ast.nodes[0].name,-1))]
			return temp + [Neg86(Var(ast.nodes[0].name,-1))]
		elif isinstance(ast.expr, CallFunc):
			temp = x86(ast.expr)
			return temp + [Move86(EAX, Var(ast.nodes[0].name,-1))]
		else:
			return [Move86(x86(ast.expr), Var(ast.nodes[0].name,-1))]
	else:
		print "PANIC"

def add_header_footer_x86(instructions, number_of_stack_vars, value_mode=Move86):
	return [Push86(EBP), Move86(ESP, EBP), Sub86(Const86(number_of_stack_vars * 4), ESP)] + instructions + [Move86(Const86(0), EAX), Leave86(), Ret86()]

current_offset = 0
stack_map = {}
def allocate(var, size):
	global current_offset, stack_map
	if var in stack_map:
		return stack_map[var]
	current_offset = size + current_offset
	stack_map[var] = current_offset
	return current_offset

def get_num_stack_vars(colors_used, num_regs):
	return len(colors_used) - num_regs

def choose_register(c):
	if c == 0:
		return EBX
	elif c == 1:
		return ESI
	elif c == 2:
		return EDI
	elif c == 3:
		return EAX
	elif c == 4:
		return ECX
	elif c == 5:
		return EDX
	elif c > 5:
		return Mem86(allocate(c,4),EBP)
	else:
		raise Exception("Unexpected register: " + str(c))

# def spill_code(ass1, color_tbl, colors_used):

def assign_homes(ass1, color_tbl, colors_used):
	# if not get_num_stack_vars(colors_used, 6):

	for ii in ass1:
		if isinstance(ii, Move86) or isinstance(ii, Add86):
			if isinstance(ii.value, Var):
				ii.value = choose_register(color_tbl.get_color(ii.value.name))
			if isinstance(ii.target, Var):
				# print i.target.name
				ii.target = choose_register(color_tbl.get_color(ii.target.name))
				# print i.target.register
		if isinstance(ii, Neg86):
			if isinstance(ii.target, Var):
				ii.target = choose_register(color_tbl.get_color(ii.target.name))
		if isinstance(ii, Push86):
			if isinstance(ii.value, Var):
				ii.value = choose_register(color_tbl.get_color(ii.value.name))

	assembly = add_header_footer_x86(ass1,get_num_stack_vars(colors_used,6))
	return assembly

EBP = Reg86('ebp')
ESP = Reg86('esp')
EAX = Reg86('eax')
EBX = Reg86('ebx')
ECX = Reg86('ecx')
EDX = Reg86('edx')
ESI = Reg86('esi')
EDI = Reg86('edi')


def get_varW(instr):
	#vars written to by the instruction
	l = []
	if isinstance(instr, Move86) or isinstance(instr,Add86) or isinstance(instr, Neg86):
		if isinstance(instr.target, Var):
			l.append(instr.target.name)	
	return l
		
def get_varR(instr):
	#Vars read from by the instruction
	l = []
	if isinstance(instr, Push86) or isinstance(instr, Move86) or isinstance(instr, Add86):
		if isinstance(instr.value, Var):
			l.append(instr.value.name)
	if isinstance(instr, Add86) or isinstance(instr, Neg86):
		if isinstance(instr.target, Var):
			l.append(instr.target.name)
	return l

def liveness(instr_list):
	#random notes:
	#add before ->  self.before | vars (from class86)
	#add after ->  self.after | vars (from class86)

	#create a live vars class instance
	#first set is before second set is after
	live=[Live_vars(set([]),set([])),]
	#loop over instruction list backwards:
	for ii in range(0,len(instr_list)-1):
		instrListIndex=len(instr_list)-1-ii
		varW=get_varW(instr_list[instrListIndex])
		varR=get_varR(instr_list[instrListIndex])
		# From the text:
		# Lbefore(k) = (Lafter(k) - W(k) Union R(k))
		before=(live[ii].after-set(varW))
		before=before|set(varR)
		live[ii].add_before(before)
		live.append(Live_vars(set([]),live[ii].before))
		# print ii,map(str,live[ii].before),map(str,live[ii].after)

	#You find the live variables going backwards, now want it forwards
	live.reverse()
	# print ''
	# for item in live:
	# 	print map(str,item.before),map(str,item.after)
	return live


def interference(instructions, live):
	#takes an instruction list and the live variable list

	#initialize graph
	variables=[]
	for ii in instructions:
		variables.append(get_varW(ii))
		variables.append(get_varR(ii))
	variables=sum(variables,[])
	#print set(variables)

	interfGraph={}
	for ii in set(variables):
		interfGraph[ii] = set([])


	for ii in range(0, len(instructions)-1):
		instr = instructions[ii]
		live_after = live[ii].after

		# Rule1:
		# If instruction Ik is a move: movl s, t, then add the edge (t, v)
		# for every v that exists in Lafter(k) unless v = t or v = s.
		if (isinstance(instr, Move86) and (isinstance(instr.target, Var))):
			if instr.target.name in live_after:
				for v in live_after:
					if v != instr.target.name:
						if isinstance(instr.value, Var):
							if v != instr.target.name:
								interfGraph[instr.target.name] = set([v]) | interfGraph[instr.target.name]
								interfGraph[v] = set([instr.target.name]) | interfGraph[v]	
						else:	
						#if (isinstance(instr.value, Var) and v != instr.value.name):
							interfGraph[instr.target.name] = set([v]) | interfGraph[instr.target.name]
							interfGraph[v] = set([instr.target.name]) | interfGraph[v]


		# Rule 2:
		# If instruction Ik is not a move but some other arithmetic instruction
		# such as addl s, t, then add the edge (t, v) for every
		# v that exists in Lafter(k) unless v = t.

		if ((isinstance(instr, Add86) or isinstance(instr, Neg86)) and (isinstance(instr.target, Var))):
			for v in live[ii].after:
				if(v != instr.target.name):
					if instr.target.name in interfGraph:
						interfGraph[instr.target.name] = set([v]) | interfGraph[instr.target.name]
					else:
						interfGraph[instr.target.name] = set([v])
					if v in interfGraph:
						interfGraph[v] = set([instr.target.name]) | interfGraph[v]
					else:
						interfGraph[v] = set([instr.target.name])

		# Rule 3
		# If instruction Ik is of the form call label, then add an edge
		# (r, v) for every caller-save register r and every variable v that exists in
		# Lafter(k). (The caller-save registers are eax, ecx, and edx.)

		if isinstance(instr, Call86):
			# print 'CALL'
			interfGraph['eax'] = set([])
			interfGraph['ecx'] = set([])
			interfGraph['edx'] = set([])

			for v in live[ii].after:
					interfGraph['eax'] = set([v]) | interfGraph['eax']
					interfGraph['ecx'] = set([v]) | interfGraph['ecx']
					interfGraph['edx'] = set([v]) | interfGraph['edx']
					interfGraph[v] = set(['eax','ecx','edx']) | interfGraph[v]					

	# print '\n\nInterference Graph'
	# for key in interfGraph:
	# 	print key,":",map(str,interfGraph[key])
	return interfGraph

def new_saturation_table(graph):
	sat_tbl = []
	for key in graph:
		sat_tbl.append([0, key])
	return sat_tbl

def update_saturation_table(sat_tbl, graph, color_tbl):
	for n in sat_tbl:
		sat = 0
		for i in graph[n[1]]:
			if(color_tbl.tbl[i]) >= 0:
				sat += 1
		n[0] = sat
	return sat_tbl

#Create a color adjacency list for the given graph and color table.
#Adjacency list returned will be a dictionary of the variables in the graph
#with the colors of their adjacent nodes
def new_color_adj_list(graph, color_tbl):
	adj = {}
	for key in graph:
		adj[key] = map(color_tbl.get_color, graph[key])
	return adj




def colorer(graph):
	#color that graph yeah!
	colors=[0,1,2,3,4,5]
	
	w = graph.keys()
	color_tbl = ColorTable(graph)
	# print'\n\n'
	# for i in color_tbl.tbl:
	# 	print str(i)+":"+str(color_tbl.tbl[i])
	sat_tbl = new_saturation_table(graph)
	color_adj = new_color_adj_list(graph, color_tbl)
	#print color_tbl
	#print color_adj
	
	n = 0
	while len(w) != 0 :
		#print 'w',w
		current = len(w) - 1
		sat_tbl = update_saturation_table(sat_tbl, graph, color_tbl)
		sat_tbl.sort
		color_adj = new_color_adj_list(graph, color_tbl)
		# print sat_tbl
		# print color_adj
		colors_to_pick_from = set(colors)-set(color_adj[w[current]])
		# print 'colors_to_pick_from1', colors_to_pick_from
		if not colors_to_pick_from:
			# print colors[len(colors)-1] + 1
			colors.append(colors[len(colors)-1] + 1)
		colors_to_pick_from = set(colors)-set(color_adj[w[current]])
		# print 'colors_to_pick_from2', colors_to_pick_from
		color = min(colors_to_pick_from)
		#print 'color',color
		#update color table
		color_tbl.set_color(w[current],color)
		w.remove(w[current])
		#print 'w',w
		n += 1
		# print len(w),n
	# print '\n\nColor Table'
	# for i in color_tbl.tbl:
	# 	print str(i)+":"+str(color_tbl.tbl[i])
	return (color_tbl, colors)

	


def pickReg(ast):
	global tempVars2
	varArray=[]
	finalVars=[]
	finalVarsReg=[]
	for line in ast:
		line=str(line).split(' ')
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
				item=re.sub(',','',item)
				finalVars.append(item)
	finalVars=set(finalVars)
	finalVars=list(finalVars)
	# print "FINAL VARS=",finalVars


	tempVars2=len(finalVars)
	for item in finalVars:

		finalVarsReg.append(str(-finalVars.index(item)*4-4)+"(%ebp)")
		# print str(-finalVars.index(item)*4-4)+"(%ebp)"

	temp2=[]

	for line in ast:
		line=re.sub(',','',str(line))
		line=line.split(' ')
		# print line
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
		line[1]=re.sub(',','',line[1])
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



