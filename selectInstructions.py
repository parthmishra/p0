from class86 import *
from ir import *
from flatten1 import *

lhs=[]

def make_arith(klass, lhs, rhs):
    if isinstance(lhs, Name) and isinstance(rhs, Name):
        return [IntMoveInstr(Register('eax'), [rhs]),
                klass(lhs, [Register('eax')])]
    else:
        return [klass(lhs, [rhs])]

def name_or_reg(n):
    return isinstance(n, Name) or isinstance(n, Register)


def select(ast):    
    global lhs
    if isinstance(ast,Module):
        ss = select(ast.node)
        return Module(ast.doc, ss)

    elif isinstance(ast,Stmt):
    	print ast.nodes
    	print ''
        # sss = []
        # for s in ast.nodes:
        #     sss.append(select)
        # sss  = [select(s) for s in ast.nodes]
        sss = map(select, ast.nodes)
        print "SSSSSSSSSSSS", sss
        return Stmt(reduce(lambda a,b: a + b, sss, []))

    elif isinstance(ast,Add):
        left = ast.left
        right = ast.right
        if name_or_reg(left) and left.name == lhs:
            return make_arith(IntAddInstr, Name(lhs), right)
        elif name_or_reg(right) and right.name == lhs:
            return make_arith(IntAddInstr, Name(lhs), left)
        else:
            return [IntMoveInstr(Register('eax'), [left]),
                    IntAddInstr(Register('eax'), [right]),
                    IntMoveInstr(Name(lhs), [Register('eax')])]

    elif isinstance(ast,UnarySub):
        return [IntMoveInstr(Register('eax'), [ast.expr]),
                IntNegInstr(Register('eax'), []),
                IntMoveInstr(Name(lhs), [Register('eax')])]

    elif isinstance(ast, Name):
        if lhs == ast.name:
            return []
        else:
            return make_arith(IntMoveInstr, Name(lhs), ast)
        
    elif isinstance(ast, Const):
        return [IntMoveInstr(Name(lhs), [n])]

    elif isinstance(ast, CallFunc):
        push_args = [Push(a) for a in reversed(ast.args)]
        # Align stack to 16-bytes for MacOS X
        align = 4 * (4 - len(ast.args) % 4)
        pop_amount = (4 * len(ast.args)) + align
        if align != 0:
            push_args = [IntSubInstr(Register('esp'), [Const(align)])] + push_args 
        if 0 < pop_amount:
            pop = [Pop(pop_amount)]
        else:
            pop = []
        return push_args + [CallX86(ast.node.name)] + pop \
               + [IntMoveInstr(Name(lhs), [Register('eax')])]

    elif isinstance(ast, Assign):
        lhs = ast.nodes[0].name
        return select(ast.expr)

    elif isinstance(ast, Printnl):
        push_args = [Push(ast.nodes[0])]
        # Align stack to 16-bytes for MacOS X
        if len(push_args) % 4 != 0:
            n = 4 - (len(push_args) % 4)
            for i in range(0,n):
                push_args = [Push(Const(0))] + push_args 
        pop = [Pop(4 * len(push_args))]
        return push_args + [CallX86('print_int_nl')] + pop