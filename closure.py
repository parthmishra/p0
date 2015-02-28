
from ExplicitClass import *
from explicate1 import letify
from class86 import *
from free_vars import freeVars
from find_locals import findLocals

class FunName(Node):
    def __init__(self, name, lineno=None):
        self.name = name
        self.lineno = lineno

    def getChildren(self):
        return self.name,

    def getChildNodes(self):
        return ()

    def __repr__(self):
        return "FunName(%s)" % (repr(self.name),)

class IndirectCallFunc(Node):
    def __init__(self, node, args):
        self.node = node
        self.args = args

    def getChildren(self):
        children = []
        childreast.append(self.node)
        children.extend(flatten(self.args))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.append(self.node)
        nodelist.extend(flatten_nodes(self.args))
        return tuple(nodelist)

    def __repr__(self):
        return "IndirectCallFunc(%s, %s)" % (repr(self.node), repr(self.args))




def cc(ast):
    if isinstance(ast, Name):
        if ast.name in builtin_functions:
            return (FunName(ast.name), [])
        else:
            return (ast, [])

    elif isinstance(ast, Const):
        return (ast, [])

    elif isinstance(ast, Add):
        (left, fs1) = cc(ast.left)
        (right, fs2) = cc(ast.right)
        return (Add((left, right)), fs1 + fs2)

    elif isinstance(ast, UnarySub):
        (expr, fs) = cc(ast.expr)
        return (UnarySub(expr), fs)

    elif isinstance(ast, CallFunc):
        args_fs = [cc(arg) for arg in ast.args]
        args = [arg for (arg,ss) in args_fs]
        fs1 = reduce(lambda x,y: x + y, [fs for (arg,fs) in args_fs], [])
        (node, fs2) = cc(ast.node)

        if isinstance(node, FunName) and node.name in builtin_functions:
            return (CallFunc(node, args), fs1 + fs2)
        else:
            return (letify(node, lambda fun_expr:
                           IndirectCallFunc(CallFunc(FunName('get_fun_ptr'), [fun_expr]),
                                            [CallFunc(FunName('get_free_vars'), [fun_expr])]
                                            + args)),
                fs1 + fs2)

    elif isinstance(ast, Lambda):
        (code, fs) = cc(ast.code)
        local_vars = findLocals(ast.code)
        fvs = freeVars(ast.code) - set(ast.argnames) - local_vars
        fun_name = label_gen('lambda_')
        fvs_var = name_gen('free_vars_')
        fvs_inits = []
        i = 0
        for fv in fvs:
            fvs_inits += [Assign([AssName(fv, 'OP_ASSIGN')],
                                 Subscript(Name(fvs_var), None,
                                           [InjectFrom('int', Const(i))]))]
            i += 1
        body = Stmt(fvs_inits + code.nodes)
        func = Function(None, fun_name, [fvs_var] + ast.argnames, None, 0, None, body)
        
        fvs_list = ExplicateVisitor2().preorder(List([Name(fv) for fv in fvs]))
        (fvs_list, fs2) = cc(fvs_list)
        closure = InjectFrom('big', CallFunc(FunName('create_closure'), [FunName(fun_name), fvs_list]))
        return (closure, fs + [func])

    elif isinstance(ast, IfExp):
        (test, fs1) = cc(ast.test)
        (then, fs2) = cc(ast.then)
        (else_, fs3) = cc(ast.else_)
        return (IfExp(test, then, else_), fs1 + fs2 + fs3)

    elif isinstance(ast, Compare):
        (left, fs1) = cc(ast.expr)
        (right, fs2) = cc(ast.ops[0][1])
        return (Compare(left, [(ast.ops[0][0], right)]), fs1 + fs2)

    elif isinstance(ast, Subscript):
        (c, fs1) = cc(ast.expr)
        (k, fs2) = cc(ast.subs[0])
        return (Subscript(expr=c, flags=ast.flags, subs=[k]),
                fs1 + fs2)

    elif isinstance(ast, GetTag):
        (arg, fs) = cc(ast.arg)
        return (GetTag(arg), fs)

    elif isinstance(ast, InjectFrom):
        (arg, fs) = cc(ast.arg)
        return (InjectFrom(ast.typ, arg), fs)

    elif isinstance(ast, ProjectTo):
        (arg, fs) = cc(ast.arg)
        return (ProjectTo(ast.typ, arg), fs)

    elif isinstance(ast, Let):
        (rhs, fs1) = cc(ast.rhs)
        (body, fs2) = cc(ast.body)
        return (Let(ast.var, rhs, body), fs1 + fs2)

    elif isinstance(ast, SetSubscript):
        (c, fs1) = cc(ast.container)
        (k, fs2) = cc(ast.key)
        (v, fs3) = cc(ast.val)
        tmp = name_gen('SetSubscript_')
        return (SetSubscript(c, k, v),
                fs1 + fs2 + fs3)

    # statements
    
    elif isinstance(ast, Stmt):
        ss_fss  = [cc(s) for s in ast.nodes]
        ss = [s for (s,fs) in ss_fss]
        fs = reduce(lambda a,b: a + b, [fs for (s,fs) in ss_fss], [])
        return (Stmt(ss), fs)

    elif isinstance(ast, Printnl):
        (e,fs) = cc(ast.nodes[0])
        return (Printnl([e], ast.dest), fs)

    elif isinstance(ast, Assign):
        (rhs,fs) = cc(ast.expr)
        return (Assign(ast.nodes, rhs), fs)

    elif isinstance(ast, Discard):
        (expr, fs) = cc(ast.expr)
        return (Discard(expr), fs)

    elif isinstance(ast, Return):
        (value, fs)  = cc(ast.value)
        return (Return(value), fs)

    elif isinstance(ast, If):
        (test, ss1) = cc(ast.tests[0][0])
        (then, ss2) = cc(ast.tests[0][1])
        (else_, ss3) = cc(ast.else_)
        return (If([(test,then)], else_), ss1 + ss2 + ss3)

    elif isinstance(ast, While):
        (test, ss1) = cc(ast.test)
        (body, ss2) = cc(ast.body)
        return (While(test,body, ast.else_), ss1 + ss2)

    elif isinstance(ast, Module):
        (node, fs) = cc(ast.node)
        return Module(ast.doc, Stmt(fs + node.nodes))
