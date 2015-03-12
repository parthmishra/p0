from compiler.ast import *
from ir import *
from class86 import *
from ExplicitClass import *


def RemoveStructuredControl(ast):
    #Gets rid of if statements in x86 IR.

    if isinstance(ast, Module):
        return Module(ast.doc, Stmt(RemoveStructuredControl(ast.node)))

    elif isinstance(ast, Stmt):
        sss = [RemoveStructuredControl(s) for s in ast.nodes]
        return Stmt(reduce(lambda a,b: a + b, sss, []))

    elif isinstance(ast, If):
        # if has tests[0][0], tests[0][1], else_
        test = ast.tests[0][0]
        then = RemoveStructuredControl(ast.tests[0][1])
        else_ = RemoveStructuredControl(ast.else_)
        else_label = name_gen('else')
        end_label = name_gen('if_end')
        return [CMPLInstr(None, [Const(0), test]),
                JumpEqInstr(else_label)] + \
                [then] + \
                [Goto(end_label)] + \
                [Label(else_label)] + \
                [else_] + \
                [Label(end_label)]

    else:
        return [ast]
