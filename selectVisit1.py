from class86 import *
from ir import *
from visitor86 import Visitor
# from flatten1 import *

def make_arith(klass, lhs, rhs):
    if isinstance(lhs, Name) and isinstance(rhs, Name):
        return [IntMoveInstr(Register('eax'), [rhs]),
                klass(lhs, [Register('eax')])]
    else:
        return [klass(lhs, [rhs])]

def name_or_reg(n):
    return isinstance(n, Name) or isinstance(n, Register)

class SelectVisit1(Visitor):

    def __init__(self):
        Visitor.__init__(self)
    
    def visitModule(self, n):
        ss = self.dispatch(n.node)
        return Module(n.doc, ss)

    def visitStmt(self, n):
        # print n.nodes
        sss  = [self.dispatch(s) for s in n.nodes]
        # print "SSSSSSSSSSSSS", sss
        return Stmt(reduce(lambda a,b: a + b, sss, []))

    def visitAdd(self, n, lhs):
        left = n.left
        right = n.right
        if name_or_reg(left) and left.name == lhs:
            return make_arith(IntAddInstr, Name(lhs), right)
        elif name_or_reg(right) and right.name == lhs:
            return make_arith(IntAddInstr, Name(lhs), left)
        else:
            return [IntMoveInstr(Register('eax'), [left]),
                    IntAddInstr(Register('eax'), [right]),
                    IntMoveInstr(Name(lhs), [Register('eax')])]
        # else:
        #     return make_arith(IntMoveInstr, Name(lhs), left) + \
        #            make_arith(IntAddInstr, Name(lhs), right)

    def visitUnarySub(self, n, lhs):
        return [IntMoveInstr(Register('eax'), [n.expr]),
                IntNegInstr(Register('eax'), []),
                IntMoveInstr(Name(lhs), [Register('eax')])]

    def visitName(self, n, lhs):
        if lhs == n.name:
            return []
        else:
            return make_arith(IntMoveInstr, Name(lhs), n)
        
    def visitConst(self, n, lhs):
        return [IntMoveInstr(Name(lhs), [n])]

    def visitCallFunc(self, n, lhs):
        push_args = [Push(a) for a in reversed(n.args)]
        align = 4 * (4 - len(n.args) % 4)
        pop_amount = (4 * len(n.args)) + align
        if align != 0:
            push_args = [IntSubInstr(Register('esp'), [Const(align)])] + push_args 
        if 0 < pop_amount:
            pop = [Pop(pop_amount)]
        else:
            pop = []
        return push_args + [CallX86(n.node.name)] + pop \
               + [IntMoveInstr(Name(lhs), [Register('eax')])]

    def visitAssign(self, n):
        lhs = n.nodes[0].name
        return self.dispatch(n.expr, lhs)

    def visitPrintnl(self, n):
        push_args = [Push(n.nodes[0])]
        if len(push_args) % 4 != 0:
            n = 4 - (len(push_args) % 4)
            for i in range(0,n):
                push_args = [Push(Const(0))] + push_args 
        pop = [Pop(4 * len(push_args))]
        return push_args + [CallX86('print_int_nl')] + pop

