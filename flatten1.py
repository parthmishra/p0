
#Imports
import sys
import compiler
import re

from compiler.ast import *

from parser1 import parse_file
from class86 import *
from ExplicitClass import *
# from explicate1 import explicate
# from explicate1 import pure
# from explicate1 import letify
# from closure import *


# debug=True
debug=False

if debug:
	print "Debug is on!"


def flattener(ast, constOrName):
	# global tempVars

	# if debug:
		# print ast
	# print "FLATTTTTEN = ", ast

	if isinstance(ast, Module):
		# print "HERE"
		Stmts = flattener(ast.node, False)
		return Module(ast.doc, Stmt(Stmts))

	elif isinstance(ast,Stmt):
		# n=map(flattener,ast.nodes)
		# n=sum(n,[])
		# return Stmt(n)
		Stmts  = [flattener(s, False) for s in ast.nodes]
		return reduce(lambda a,b: a + b, Stmts, [])

	elif isinstance(ast,Printnl):
		(expr, stmts) = flattener(ast.nodes[0], True)
		return stmts + [Printnl([expr], ast.dest)]

		# #has .nodes and .dest
		# nodes = map(flattener, ast.nodes) #Apply flattener function to all inner nodes
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
		(rExpr, stmts) = flattener(ast.expr, True)
		return stmts + [Assign(ast.nodes, rExpr)]

		#assign has .nodes .expr
		#ass is [AssName('!!!y', 'OP_ASSIGN')]
		#stmts is stuff to left of it
		# n=map(flattener,ast.nodes)
		# ass=[t for (t,l) in n]
		# # print "In flattener,assign:",ass
		# stmts=sum([l for (t,l) in n],[])
		# tn,ts=flattener(ast.expr)
		# return stmts+ts+[Assign(ass,tn)]

	# elif isinstance(ast,AssName):
	# 	tempVars+=1
	# 	ast.name=''+ast.name
	# 	return (ast,[])

	elif isinstance(ast,Discard):
		# tempVars+=1
		# tempName="Discard"+str(tempVars)
		# tempName = name_gen("Discard_")
		# expr,stmts=flattener(ast.expr)
		(expr, stmts) = flattener(ast.expr, True)
		return stmts
		# # stmts.append(expr)
		# stmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], expr))
		# # print expr, stmts
		# return stmts #discard doesn't do anything really... no need to return ast

	elif isinstance(ast,Add):
		(lExpr, lStmts) = flattener(ast.left, True)
		(rExpr, rStmts) = flattener(ast.right, True)
		if constOrName:
			tmp = name_gen('Add_')
			return (Name(tmp), lStmts + rStmts + [Assign([AssName(tmp, 'OP_ASSIGN')], Add((lExpr, rExpr)))])
		else:
			return (Add((lExpr, rExpr)), lStmts + rStmts)
		# #Add has ast.left and ast.right
		# leftExpr,leftStmts = flattener(ast.left)
		# rightExpr,rightStmts = flattener(ast.right)
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
		(expr, stmts) = flattener(ast.expr, True)
		# if not (isinstance(expr, Const) or isinstance(expr, Name)):
		# 	# tempVars+=1
		# 	# tempName="UnarySub"+str(tempVars)
		# 	tempName = name_gen("UnarySub_")
		# 	stmts.append(Assign([AssName(tempName, 'OP_ASSIGN')], expr))
		# 	expr=Name(tempName)
		if constOrName:
			temp = name_gen('tmp')
			return (Name(tmp), ss + [make_assign(tmp, UnarySub(expr))])
		else:
			return (UnarySub(expr), stmts)

	elif isinstance(ast,CallFunc):
		# print ast
		if isinstance(ast.node, Name):
		# if 1:

			args_sss = [flattener(arg, True) for arg in ast.args]
			args = [arg for (arg,ss) in args_sss]
			ss = reduce(lambda a,b: a + b, [ss for (arg,ss) in args_sss], [])
			if constOrName:
				tmp = name_gen('CallFunc_')
				return (Name(tmp), ss + [Assign([AssName(tmp, 'OP_ASSIGN')], CallFunc(ast.node, args))])
			else:
				return (CallFunc(ast.node, args), ss)

		
		# #Const86 has .node, .args, .star_args, .dstar_args
		# #For p0 no args required!
		# (expr,stmts) = flattener(ast.node)
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
		(testExpr, testStmts) = flattener(ast.test, True)
		(thenExpr, thenStmts) = flattener(ast.then, True)
		# print ''
		# print "ELSE:", ast.else_
		# print ''
		(elseExpr, elseStmts) = flattener(ast.else_, True)
		# (elseExpr) = flattener(ast.else_)
		# print "HEREHEREHREHRHERHEHRH"
		# print "flattener else_ flattener = ",elseExpr
		# print "22flattener else_ flattener22 = ",elseStmts

		tmp = name_gen("IfExp_")
		return (Name(tmp), testStmts + [If([(testExpr, Stmt(thenStmts + [Assign([AssName(tmp, 'OP_ASSIGN')], \
						thenExpr)]))], Stmt(elseStmts + [Assign([AssName(tmp, 'OP_ASSIGN')], elseExpr)]))])

	# return (Name(tmp), test_ss + [If([(test, Stmt(then_ss + [make_assign(tmp, then)]))],
	#                                          Stmt(else_ss + [make_assign(tmp, else_)]))])
	
	elif isinstance(ast, Compare):
		(lExpr, lStmts) = flattener(ast.expr, True)
		op = ast.ops[0][0]
		(rExpr, rStmts) = flattener(ast.ops[0][1], True)
		comp = Compare(expr=lExpr, ops=[(op,rExpr)])
		# if not (isinstance(expr, Const) or isinstance(expr, Name)):
		if constOrName:
		# if 1:
			tmp = name_gen("Compare_")
			return (Name(tmp), lStmts+rStmts+[Assign([AssName(tmp, 'OP_ASSIGN')], comp)])
		else:
			return (comp, lStmts+rStmts)

	elif isinstance(ast, Subscript) and constOrName:
		(exprs, stmts) = flattener(ast.expr, True)
		(subExpr, subStmts) = flattener(ast.subs[0], True)
		r = Subscript(expr=exprs, flags=ast.flags, subs=[subExpr])
		if constOrName:
			tmp = name_gen("Subscript_")
			return (Name(tmp), stmts + subStmts + [Assign([AssName(tmp, 'OP_ASSIGN')], r)])
		else:
			return (r, stmts + subStmts)

	elif isinstance(ast, GetTag) and constOrName:
		(exprs, Stmts) = flattener(ast.arg, True)
		tmp = name_gen("GetTag_")
		rExpr = GetTag(exprs)
		return (Name(tmp), Stmts + [Assign([AssName(tmp, 'OP_ASSIGN')], rExpr)])

	elif isinstance(ast, InjectFrom) and constOrName:
		(exprs, Stmts) = flattener(ast.arg, True)
		tmp = name_gen("InjectFrom_")
		rExpr = InjectFrom(ast.typ, exprs)
		return (Name(tmp), Stmts + [Assign([AssName(tmp, 'OP_ASSIGN')], rExpr)])

	elif isinstance(ast, ProjectTo) and constOrName:
		(exprs, Stmts) = flattener(ast.arg, True)
		tmp = name_gen("ProjectTo_")
		rExpr = ProjectTo(ast.typ, exprs)
		return (Name(tmp), Stmts + [Assign([AssName(tmp, 'OP_ASSIGN')], rExpr)])

	elif isinstance(ast, Let) and constOrName:
		#Error here: nonetype not iterable...???
		# print ast.rhs
		(rExpr, rStmts) = flattener(ast.rhs, False)
		(bExpr, bStmts) = flattener(ast.body, True)
		return (bExpr, rStmts + [Assign([AssName(ast.var, 'OP_ASSIGN')], rExpr)] + bStmts)

	elif isinstance(ast, SetSubscript) and constOrName:
		#container key val
		(cExpr, cStmts) = flattener(ast.container, True)
		(kExpr, kStmts) = flattener(ast.key, True)
		(vExpr, vStmts) = flattener(ast.val, True)
		tmp = name_gen("SetSubscript_")
		r = SetSubscript(cExpr, kExpr, vExpr)
		return (Name(tmp), cStmts + kStmts + vStmts + [Assign([AssName(tmp, 'OP_ASSIGN')], r)])


	else:
		print "Error: Instance not in p0, p1"
		# return [ast]
		# print ast


# inputFile = sys.argv[1]
# ast = compiler.parseFile(inputFile)

# flat =  flattener(ast)
# print flat

# ast=explicate(ast)
# typ = typeCheck(explicit)
# print ast
# print ''
# ast=cc(ast)
# print ast
# flat=flattener(ast)
# print flat
# for item in flat[0]:
	# print item