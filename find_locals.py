from compiler.ast import *

def findLocals(ast):
    if isinstance(ast, Stmt):
        sss  = [findLocals(s) for s in ast.nodes]
        return reduce(lambda a,b: a | b, sss, set([]))

    elif isinstance(ast, Printnl):
        return set([])

    elif isinstance(ast, Assign):
        if isinstance(ast.nodes[0], AssName):
            return set([ast.nodes[0].name])
        else:
            return set([])

    elif isinstance(ast, Discard):
        return set([])
    
    elif isinstance(ast, Return):
        return set([])

    elif isinstance(ast, Function):
        return set([ast.name])

    elif isinstance(ast, If):
        return findLocals(ast.tests[0][1]) | findLocals(ast.else_)

    elif isinstance(ast, While):
        return findLocals(ast.body)

    elif isinstance(ast, Class):
        return set([ast.name])
