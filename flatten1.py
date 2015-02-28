
#Imports
import sys
import compiler
import re

from compiler.ast import *

from parser1 import parse_file
from class86 import *
from ExplicitClass import *
from explicate1 import explicate
from explicate1 import pure
from explicate1 import letify
from closure import *


# debug=True
debug=False

if debug:
	print "Debug is on!"

def simple(ast):
	return (not (isinstance(ast, Const) or isinstance(ast, Name)))


def flatten(ast):
	global tempVars

	if debug:
		print ast

	if isinstance(ast,Module):
		return Module(ast.doc, flatten(ast.node))

	elif isinstance(ast,Stmt):
		# n=map(flatten,ast.nodes)
		# n=sum(n,[])
		# return Stmt(n)
		sss  = [flatten(s) for s in ast.nodes]
		return reduce(lambda a,b: a + b, sss, [])

	elif isinstance(ast,Printnl):
		(expr, stmts) = flatten(ast.nodes[0])
		return stmts + [Printnl([expr], ast.dest)]

		# #has .nodes and .dest
		# nodes = map(flatten, ast.nodes) #Apply flatten function to all inner nodes
		# p = []
		# for (t,l) in nodes:
		# 	#Check to see if either side has more nodes
		# 	if not (isinstance(t, Const) or isinstance(t, Name)):
		# 		# tempVars+=1
		# 		# tempName="Print"+str(tempVars) 
		# 		tempName = name_gen("Print")
		# 		l.append(Assign([AssName(tempName, 'OP_ASSIGN')], t)) #Assign print name to statement value
		# 		p.append(Name(tempName)) 
		# 	else:
		# 		p.append(t)
		# stmts = sum([l for (t, l) in nodes], [])
		# # print stmts, [Printnl(p, ast.dest)]
		# return stmts + [Printnl(p, ast.dest)]


	elif isinstance(ast,Assign):
		lExpr = ast.nodes[0].name
		(rExpr, stmts) = flatten(ast.expr)
		return stmts + [Assign(ast.nodes, rExpr)]

		#assign has .nodes .expr
		#ass is [AssName('!!!y', 'OP_ASSIGN')]
		#stmts is stuff to left of it
		# n=map(flatten,ast.nodes)
		# ass=[t for (t,l) in n]
		# # print "In flatten,assign:",ass
		# stmts=sum([l for (t,l) in n],[])
		# tn,ts=flatten(ast.expr)
		# return stmts+ts+[Assign(ass,tn)]

	# elif isinstance(ast,AssName):
	# 	tempVars+=1
	# 	ast.name=''+ast.name
	# 	return (ast,[])

	elif isinstance(ast,Discard):
		# tempVars+=1
		# tempName="Discard"+str(tempVars)
		# tempName = name_gen("Discard_")
		# expr,stmts=flatten(ast.expr)
		(expr, stmts) = flatten(ast.expr)
		return stmts
		# # stmts.append(expr)
		# stmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], expr))
		# # print expr, stmts
		# return stmts #discard doesn't do anything really... no need to return ast

	elif isinstance(ast,Add):
		(lExpr, lStmts) = flatten(ast.left)
		(rExpr, rStmts) = flatten(ast.right)
		if simple(lExpr) and simple (rExpr):
			tmp = name_gen('Add_')
			return (Name(tmp), lStmts + rStmts + [Assign([AssName(tmp, 'OP_ASSIGN')], Add((lExpr, rExpr)))])
		else:
			return (Add((lExpr, rExpr)), lStmts + rStmts)
		# #Add has ast.left and ast.right
		# leftExpr,leftStmts = flatten(ast.left)
		# rightExpr,rightStmts = flatten(ast.right)
		# #For left instance
		# if not (isinstance(leftExpr, Const) or isinstance(leftExpr, Name)):
		# 	# tempVars+=1
		# 	# tempName="AddLeft"+str(tempVars)
		# 	tempName = name_gen("AddLeft_")
		# 	leftStmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], leftExpr))
		# 	leftExpr=Name(tempName)
		# #For right instance
		# if not (isinstance(rightExpr, Const) or isinstance(rightExpr, Name)):
		# 	# tempVars+=1
		# 	# tempName="AddRight"+str(tempVars)
		# 	tempName = name_gen("AddRight_")
		# 	rightStmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], rightExpr))
		# 	rightExpr=Name(tempName)
		# return (Add((leftExpr,rightExpr)),leftStmts+rightStmts)

	elif isinstance(ast,UnarySub):
		# tempVars=tempVars+1
		(expr, stmts) = flatten(ast.expr)
		if not (isinstance(expr, Const) or isinstance(expr, Name)):
			# tempVars+=1
			# tempName="UnarySub"+str(tempVars)
			tempName = name_gen("UnarySub_")
			stmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], expr))
			expr=Name(tempName)
		return (UnarySub(expr), stmts)

	elif isinstance(ast,CallFunc):
		# print ast
		if isinstance(ast.node, Name):
		# if 1:

			args_sss = map(flatten,ast.args)
			args = [arg for (arg,ss) in args_sss]
			ss = reduce(lambda a,b: a + b, [ss for (arg,ss) in args_sss], [])
			if simple(args):
				tmp = name_gen('CallFunc_')
				return (Name(tmp), ss + [Assign([AssName(tmp, 'OP_ASSIGN')], CallFunc(ast.node, args))])
			else:
				return (CallFunc(ast.node, args), ss)

		elif isinstance(ast.node, FunName):
			args_sss = map(flatten,ast.args)
			args = [arg for (arg,ss) in args_sss]
			ss = reduce(lambda a,b: a + b, [ss for (arg,ss) in args_sss], [])
			if simple(args):
				tmp = name_gen('CallFunc_')
				return (Name(tmp), ss + [Assign([AssName(tmp, 'OP_ASSIGN')], CallFunc(ast.node, args))])
			else:
				return (CallFunc(ast.node, args), ss)
		else:
			raise Exception('flatten1: only calls to named functions allowed')
		# #Const86 has .node, .args, .star_args, .dstar_args
		# #For p0 no args required!
		# (expr,stmts) = flatten(ast.node)
		# if not (isinstance(expr, Const) or isinstance(expr, Name)):
		# 	# tempVars+=1
		# 	# tempName="CallFunc"+str(tempVars)
		# 	tempName = name_gen("CallFunc_")
		# 	stmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], expr))
		# 	expr=Name(tempName)

		# return (CallFunc(expr,[]),stmts+[])

	elif isinstance(ast,Const):
		return (ast,[]) #terminal, no need for recursive call

	elif isinstance(ast,Name):
		# ast.name=''+ast.name
		return (ast,[]) #terminal, no need for recursive call

	########## Adding in P1 ##############
	elif isinstance(ast, IfExp):
		(testExpr, testStmts) = flatten(ast.test)
		(thenExpr, thenStmts) = flatten(ast.then)
		# print ''
		# print "ELSE:", ast.else_
		# print ''
		(elseExpr, elseStmts) = flatten(ast.else_)
		# (elseExpr) = flatten(ast.else_)
		# print "HEREHEREHREHRHERHEHRH"
		# print "FLATTENED else_ FLATTENED = ",elseExpr
		# print "22FLATTENED else_ FLATTENED22 = ",elseStmts

		tmp = name_gen("IfExp_")
		return (Name(tmp), testStmts + [If([(testExpr, Stmt(thenStmts + [Assign([AssName(tmp, 'OP_ASSIGN')], \
						thenExpr)]))], Stmt(elseStmts + [Assign([AssName(tmp, 'OP_ASSIGN')], elseExpr)]))])

	# return (Name(tmp), test_ss + [If([(test, Stmt(then_ss + [make_assign(tmp, then)]))],
	#                                          Stmt(else_ss + [make_assign(tmp, else_)]))])
	
	elif isinstance(ast, Compare):
		(lExpr, lStmts) = flatten(ast.expr)
		op = ast.ops[0][0]
		(rExpr, rStmts) = flatten(ast.ops[0][1])
		comp = Compare(expr=lExpr, ops=[(op,rExpr)])
		# if not (isinstance(expr, Const) or isinstance(expr, Name)):
		if simple(lExpr) and simple (rExpr):
		# if 1:
			tmp = name_gen("Compare_")
			return (Name(tmp), lStmts+rStmts+[Assign([AssName(tmp, 'OP_ASSIGN')], comp)])
		else:
			return (comp, lStmts+rStmts)

	elif isinstance(ast, Subscript):
		(exprs, stmts) = flatten(ast.expr)
		(subExpr, subStmts) = flatten(ast.subs[0])
		r = Subscript(expr=exprs, flags=ast.flags, subs=[subExpr])
		if not (isinstance(expr, Const) or isinstance(expr, Name)):
			tmp = name_gen("Subscript_")
			return (Name(tmp), stmts + subStmts + [Assign([AssName(tmp, 'OP_ASSIGN')], r)])
		else:
			return (r, stmts + subStmts)

	elif isinstance(ast, GetTag):
		(exprs, Stmts) = flatten(ast.arg)
		tmp = name_gen("GetTag_")
		rExpr = GetTag(exprs)
		return (Name(tmp), Stmts + [Assign([AssName(tmp, 'OP_ASSIGN')], rExpr)])

	elif isinstance(ast, InjectFrom):
		(exprs, Stmts) = flatten(ast.arg)
		tmp = name_gen("InjectFrom_")
		rExpr = InjectFrom(ast.typ, exprs)
		return (Name(tmp), Stmts + [Assign([AssName(tmp, 'OP_ASSIGN')], rExpr)])

	elif isinstance(ast, ProjectTo):
		(exprs, Stmts) = flatten(ast.arg)
		tmp = name_gen("ProjectTo_")
		rExpr = ProjectTo(ast.typ, exprs)
		return (Name(tmp), Stmts + [Assign([AssName(tmp, 'OP_ASSIGN')], rExpr)])

	elif isinstance(ast, Let):
		(rExpr, rStmts) = flatten(ast.rhs)
		(bExpr, bStmts) = flatten(ast.body)
		return (bStmts, rStmts + [Assign([AssName(ast.var, 'OP_ASSIGN')], rExpr)] + bStmts)

	elif isinstance(ast, SetSubscript):
		(cExpr, cStmts) = flatten(ast.container)
		(kExpr, kStmts) = flatten(ast.key)
		(vExpr, cStmts) = flatten(ast.val)
		tmp = name_gen("SetSubscript_")
		r = SetSubscript(cExpr, kExpr, vExpr)
		return (Name(tmp), cStmts + kStmts + vStmts + [Assign([AssName(tmp, 'OP_ASSIGN')], r)])


	else:
		print "Error: Instance not in p0, p1"
		# print ast


# inputFile = sys.argv[1]
# ast = compiler.parseFile(inputFile)

# flat =  flatten(ast)
# print flat

# ast=explicate(ast)
# typ = typeCheck(explicit)
# print ast
# print ''
# ast=cc(ast)
# print ast
# flat=flatten(ast)
# print flat
# for item in flat[0]:
	# print item