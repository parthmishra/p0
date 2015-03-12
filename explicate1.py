#explicate

import compiler
from class86 import *
from compiler.ast import *
from ExplicitClass import *
import sys
import compiler
import re

##Helper functions prof Chang showed us in class that I found useful:
def is_true(e):
    if True:
        return IfExp(Compare(GetTag(e), [('==', Const(tag['int']))]),
                     Compare(Const(0), [('!=', ProjectTo('int', e))]),
                     IfExp(Compare(GetTag(e), [('==', Const(tag['bool']))]),
                           Compare(Const(0),
                                   [('!=', ProjectTo('int', e))]),
                           CallFunc(Name('is_true'), [e])))
    else:
        return CallFunc(Name('is_true'), [e])


def constOrName(expr):
    return isinstance(expr, Name) or isinstance(expr, Const)

def letify(expr, k):
    if constOrName(expr):
        return k(expr)
    else:
        n = name_gen('letify_')
        return Let(n, expr, k(Name(n)))

def explicate(ast):
	if isinstance(ast,Module):
		return Module(ast.doc, explicate(ast.node))

	elif isinstance(ast, Stmt):
		fnodes = map(explicate, ast.nodes)
		return Stmt(fnodes)

	elif isinstance(ast, Printnl):
		e=explicate(ast.nodes[0])
		return Printnl([e],ast.dest)

	elif isinstance(ast, Const):
		if isinstance(ast.value, str):
			return ast
		else:
			return InjectFrom(type(ast.value).__name__, ast)

	elif isinstance(ast, Assign):
		r = explicate(ast.expr)
		l = ast.nodes[0]
		if isinstance(l, AssName):
			return Assign(nodes=ast.nodes, expr=r)
		elif isinstance(l, Subscript):
			a = explicate(l.expr)
			b = explicate(l.subs[0])
			return Discard(SetSubscript(a, b, r))
		else:
			print "PANIC in explicate assign"

	elif isinstance(ast, Name):
		if ast.name == 'True':
			return InjectFrom('bool', Const(True))
		elif ast.name == 'False':
			return InjectFrom('bool', Const(False))
		elif ast.name == 'input':
			return Name('input_int')
		else:
			return ast

	elif isinstance(ast, Add):
		lExpr = explicate(ast.left)
		rExpr = explicate(ast.right)

		def result(l, r):
			return IfExp(Compare(GetTag(l), [('==', Const(tag['int']))]),
						InjectFrom('int', Add((ProjectTo('int', l), \
											ProjectTo('int', r)))),
						IfExp(Compare(GetTag(l), [('==', Const(tag['bool']))]),
								InjectFrom('int', Add((ProjectTo('int', l), \
											ProjectTo('int', r)))),
							InjectFrom('big', CallFunc(Name('add'), [ProjectTo('big', l), ProjectTo('big', r)]))))

		return letify(lExpr, lambda l: letify(rExpr, lambda r: result(l, r)))

	elif isinstance(ast, List):
		nodes = map(explicate, ast.nodes)
		lName = name_gen("listy_")  #########Need to generate a name here...
		listElements = Name(lName)
		ii=len(nodes)-1
		for nn in reversed(nodes):
			#todo: generate name and subscript for every element
			elementName = name_gen("element_")
			k = explicate(Const(ii))
			listElements = Let(elementName, SetSubscript(Name(lName), k, nn), listElements)
			ii = ii-1
		ast = InjectFrom('int', Const(len(nodes)))
		return Let(lName, InjectFrom('big', CallFunc(Name('create_list'), [ast])), listElements) 

	elif isinstance(ast, Dict):
		items = [(explicate(k), explicate(v)) for (k, v) in ast.items]
		dName = name_gen("dict")  ##change this
		dictElements = Name(dName)
		for (k, v) in reversed(items):
			elementName = name_gen("_")
			dictElements = Let(elementName, SetSubscript(Name(dName), k, v), dictElements)
		return Let(dName, InjectFrom('big', CallFunc(Name('create_dict'), [])),dictElements)

	elif isinstance(ast, Subscript):
		expr = explicate(ast.expr)
		subs = map(explicate, ast.subs)    ###CHECK THIS
		return Subscript(expr, ast.flags, subs)

	elif isinstance(ast, And):
		lExpr = explicate(ast.nodes[0])
		rExpr = explicate(ast.nodes[1])
		return letify(lExpr, lambda l: IfExp(is_true(l), rExpr, l))

	elif isinstance(ast, Or):
		lExpr = explicate(ast.nodes[0])
		rExpr = explicate(ast.nodes[1])
		return letify(lExpr, lambda l: IfExp(is_true(l), l, rExpr))

	elif isinstance(ast, IfExp):
		test = explicate(ast.test)
		then = explicate(ast.then)
		else_ = explicate(ast.else_)
		return IfExp(letify(test, lambda t: is_true(t)), then, else_)

	elif isinstance(ast, Not):
		expr = explicate(ast.expr)
		return InjectFrom('bool', Compare(Const(0), [('==', letify(expr, lambda t: is_true(t)))]))

	elif isinstance(ast, Compare):
		left = explicate(ast.expr)
		op = ast.ops[0][0]
		right = explicate(ast.ops[0][1])
		if op == 'is':
			return InjectFrom('bool', Compare(left, [('is', right)]))
		else:
			op2fun = {'==':'equal', '!=':'not_equal'}
			def result(l, r):
				return IfExp(Compare(GetTag(l), [('==', Const(tag['int']))]),
								InjectFrom('bool', Compare(ProjectTo('int', l), \
															[(op, ProjectTo('int', r))])),
								IfExp(Compare(GetTag(l), [('==', Const(tag['bool']))]),
										InjectFrom('bool', Compare(ProjectTo('int', l),
															[(op, ProjectTo('int', r))])),
										InjectFrom('bool', CallFunc(Name(op2fun[op]), [ProjectTo('big', l), ProjectTo('big', r)]))))

			return letify(left, lambda l: letify(right, lambda r: result(l, r)))

	elif isinstance(ast, CallFunc):
		node = explicate(ast.node)
		args = map(explicate, ast.args)
		if isinstance(node, Name) and node.name in builtin_functions:
			if return_type[node.name] == 'pyobj':
				return CallFunc(node, args)
			else:
				return InjectFrom(return_type[node.name], CallFunc(node, args))
		else:
			return CallFunc(node, args)

	elif isinstance(ast, UnarySub):
		if isinstance(ast.expr, Const) and (isinstance(ast.expr.value, int) or isinstance(ast.expr.value, long)):
			return InjectFrom('int', Const(int(-ast.expr.value)))
		else:
			expr = explicate(ast.expr)
			return InjectFrom('int', UnarySub(ProjectTo('int', expr)))


	elif isinstance(ast, Discard):
		# print explicate(ast.expr), ast.expr
		expr1 = explicate(ast.expr)
		# print "EXPRRRRRR = ",expr1 
		return Discard(expr1)

	# elif isinstance(ast, None)

	else:
		print "PANIC IN THE EXPLICATE"

		



# inputFile = sys.argv[1]
# ast = compiler.parseFile(inputFile)

# print ast
# print ''
# explicit=explicate(ast)
# print explicit