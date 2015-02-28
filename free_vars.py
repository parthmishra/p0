# from compiler_utilities import *
from class86 import *
from ExplicitClass import *
# from compiler import *
from find_locals import findLocals

def freeVars(ast):
    if isinstance(ast, Name):
        if ast.name in builtin_functions:
            return set([])
        else:
            return set([ast.name])

    elif isinstance(ast, Const):
        return set([])

    elif isinstance(ast, Add):
        return freeVars(ast.left) | freeVars(ast.right)

    elif isinstance(ast, UnarySub):
        return freeVars(ast.expr)

    elif isinstance(ast, CallFunc):
        sss = [freeVars(arg) for arg in ast.args]
        ss = reduce(lambda a,b: a | b, sss, set([]))
        return ss | freeVars(ast.node)

    elif isinstance(ast, Lambda):
        local_vars = findLocals(ast.code)
        return (freeVars(ast.code) - local_vars) - set(ast.argnames)

    elif isinstance(ast, IfExp):
        return freeVars(ast.test) | freeVars(ast.then) | freeVars(ast.else_)        

    elif isinstance(ast, Compare):
        return freeVars(ast.expr) | freeVars(ast.ops[0][1])

    elif isinstance(ast, Subscript):
        return freeVars(ast.expr) | freeVars(ast.subs[0])

    elif isinstance(ast, GetTag):
        return freeVars(ast.arg)

    elif isinstance(ast, InjectFrom):
        return freeVars(ast.arg)

    elif isinstance(ast, ProjectTo):
        return freeVars(ast.arg)

    elif isinstance(ast, Let):
        return freeVars(ast.rhs) | (freeVars(ast.body) - set([ast.var]))

    elif isinstance(ast, SetSubscript):
        return freeVars(ast.container) | freeVars(ast.key) | freeVars(ast.val)

    elif isinstance(ast, Stmt):
        sss  = [freeVars(s) for s in ast.nodes]
        return reduce(lambda a,b: a | b, sss, set([]))

    elif isinstance(ast, Printnl):
        return freeVars(ast.nodes[0])

    elif isinstance(ast, Assign):
        return freeVars(ast.expr)

    elif isinstance(ast, Discard):
        return freeVars(ast.expr)

    elif isinstance(ast, Return):
        return freeVars(ast.value)

    elif isinstance(ast, InjectFrom):
        return freeVars(ast.arg)

    elif isinstance(ast, ProjectTo):
        return freeVars(ast.arg)

    elif isinstance(ast, GetTag):
        return freeVars(ast.arg)

    elif isinstance(ast, Let):
        rhs = freeVars(ast.rhs)
        body = freeVars(ast.body)
        return rhs | (body - set([ast.var]))
