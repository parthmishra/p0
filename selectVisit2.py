from class86 import *
from selectVisit1 import SelectVisit1, name_or_reg

def make_arith(klass, lhs, rhs):
    return [klass(lhs, [rhs])]

class SelectVisit2(SelectVisit1):

    def visitAdd(self, n, lhs):
        left = n.left
        right = n.right
        # print n.left
        # print n.right
        if name_or_reg(left) and left.name == lhs:
            return make_arith(IntAddInstr, Name(lhs), right)
        elif name_or_reg(right) and right.name == lhs:
            return make_arith(IntAddInstr, Name(lhs), left)
        # else:
        #     return [IntMoveInstr(Register('eax'), [left]),
        #             IntAddInstr(Register('eax'), [right]),
        #             IntMoveInstr(Name(lhs), [Register('eax')])]
        else:
            return make_arith(IntMoveInstr, Name(lhs), left) + \
                   make_arith(IntAddInstr, Name(lhs), right)

    def visitUnarySub(self, n, lhs):
        return make_arith(IntMoveInstr, Name(lhs), n.expr) + \
               [IntNegInstr(Name(lhs), [])]

    def visitName(self, n, lhs):
        # print 'HRERERERERERE visitName instr select'
        if lhs == n.name:
            return []
        else:
            return make_arith(IntMoveInstr, Name(lhs), n)
