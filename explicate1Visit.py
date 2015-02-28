#explicate

import compiler
from compiler.ast import *
from class86 import *
from ExplicitClass import *
from visitor86 import Visitor

import sys
# import compiler
import re


def gen_is_true(e):
    if True:
        return IfExp(Compare(GetTag(e), [('==', Const(tag['int']))]),
                     Compare(Const(0), [('!=', ProjectTo('int', e))]),
                     IfExp(Compare(GetTag(e), [('==', Const(tag['bool']))]),
                           Compare(Const(0),
                                   [('!=', ProjectTo('int', e))]),
                           CallFunc(Name('is_true'), [e])))
    else:
        return CallFunc(Name('is_true'), [e])


# the following is overly conservative
def pure(expr):
    return isinstance(expr, Name) or isinstance(expr, Const)

def letify(expr, k):
    if pure(expr):
        return k(expr)
    else:
        # n = generate_name('letify')
        n = name_gen('letify_')
        return Let(n, expr, k(Name(n)))

class explicateVisit(Visitor):

	def visitModule(self,ast):
		return Module(ast.doc, self.dispatch(ast.node))

	def visitStmt(self, ast):
		fnodes = map(self.dispatch, ast.nodes)
		return Stmt(fnodes)

	def visitPrintnl(self, ast):
		e=self.dispatch(ast.nodes[0])
		return Printnl([e],ast.dest)

	def visitConst(self, ast):
		if isinstance(ast.value, str):
			return ast
		else:
			return InjectFrom(type(ast.value).__name__, ast)

	def visitAssign(self, ast):
		r = self.dispatch(ast.expr)
		l = ast.nodes[0]
		if isinstance(l, AssName):
			return Assign(nodes=ast.nodes, expr=r)
		elif isinstance(l, Subscript):
			a = self.dispatch(l.expr)
			b = self.dispatch(l.subs[0])
			return Discard(SetSubscript(a, b, r))
		else:
			print "PANIC in explicate assign"

	def visitName(self, ast):
		if ast.name == 'True':
			return InjectFrom('bool', Const(True))
		elif ast.name == 'False':
			return InjectFrom('bool', Const(False))
		elif ast.name == 'input':
			return Name('input_int')
		else:
			return ast

	def visitAdd(self, ast):
		lExpr = self.dispatch(ast.left)
		rExpr = self.dispatch(ast.right)

		def result(l, r):
			return IfExp(Compare(GetTag(l), [('==', Const(tag['int']))]),
						InjectFrom('int', Add((ProjectTo('int', l), \
											ProjectTo('int', r)))),
						IfExp(Compare(GetTag(l), [('==', Const(tag['bool']))]),
								InjectFrom('int', Add((ProjectTo('int', l), \
											ProjectTo('int', r)))),
							InjectFrom('big', CallFunc(Name('add'), [ProjectTo('big', l), ProjectTo('big', r)]))))

		return letify(lExpr, lambda l: letify(rExpr, lambda r: result(l, r)))

	def visitList(self, ast):
		nodes = map(self.dispatch, ast.nodes)
		lName = name_gen("listy_")  #########Need to generate a name here...
		listElements = Name(lName)
		ii=len(nodes)-1
		for nn in reversed(nodes):
			#todo: generate name and subscript for every element
			elementName = name_gen("element_")
			k = self.dispatch(Const(ii))
			listElements = Let(elementName, SetSubscript(Name(lName), k, nn), listElements)
			ii = ii-1
		ast = InjectFrom('int', Const(len(nodes)))
		return Let(lName, InjectFrom('big', CallFunc(Name('create_list'), [ast])), listElements) 
	
	def visitDict(self, ast):
		items = [(self.dispatch(k), self.dispatch(e)) for (k, e) in ast.items]
		d = name_gen('dict')
		fill_dict = Name(d)
		for (k, v) in reversed(items):
			bogus = name_gen('_')
			fill_dict = Let(bogus, SetSubscript(Name(d), k, v), fill_dict)
		return Let(d, InjectFrom('big', CallFunc(Name('create_dict'), [])), fill_dict)

	def visitSubscript(self, ast):
		expr = self.dispatch(ast.expr)
		subs = map(self.dispatch, ast.subs)    ###CHECK THIS
		return Subscript(expr, ast.flags, subs)

	def visitAnd(self, ast):
		lExpr = self.dispatch(ast.nodes[0])
		rExpr = self.dispatch(ast.nodes[1])
		return letify(lExpr, lambda l: IfExp(gen_is_true(l), rExpr, l))

	def visitOr(self, ast):
		lExpr = self.dispatch(ast.nodes[0])
		rExpr = self.dispatch(ast.nodes[1])
		return letify(lExpr, lambda l: IfExp(gen_is_true(l), l, rExpr))

	def visitIfExp(self, ast):
		test = self.dispatch(ast.test)
		then = self.dispatch(ast.then)
		else_ = self.dispatch(ast.else_)
		return IfExp(letify(test, lambda t: gen_is_true(t)), then, else_)

	def visitNot(self, ast):
		expr = self.dispatch(ast.expr)
		return InjectFrom('bool', Compare(Const(0), [('==', letify(expr, lambda t: gen_is_true(t)))]))

	def visitCompare(self, ast):
		left = self.dispatch(ast.expr)
		op = ast.ops[0][0]
		right = self.dispatch(ast.ops[0][1])
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

	def visitCallFunc(self, ast):
		node = self.dispatch(ast.node)
		args = map(self.dispatch, ast.args)
		if isinstance(node, Name) and node.name in builtin_functions:
			if return_type[node.name] == 'pyobj':
				return CallFunc(node, args)
			else:
				return InjectFrom(return_type[node.name], CallFunc(node, args))
		else:
			return CallFunc(node, args)


	def visitUnarySub(self, ast):
		if isinstance(ast.expr, Const) and (isinstance(ast.expr.value, int) or isinstance(ast.expr.value, long)):
			return InjectFrom('int', Const(int(-ast.expr.value)))
		else:
			expr = self.dispatch(ast.expr)
			return InjectFrom('int', UnarySub(ProjectTo('int', expr)))


	def visitDiscard(self, ast):
		return Discard(self.dispatch(ast.expr))


# 	# else:
# 	# 	print "PANIC IN THE EXPLICATE"



# inputFile = sys.argv[1]
# ast = compiler.parseFile(inputFile)

# print ast
# print ''
# explicit=explicate(ast)
# print explicit