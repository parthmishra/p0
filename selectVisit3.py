from ir import *
from class86 import *
from ExplicitClass import *
from selectVisit2 import InstrSelVisitor2, name_or_reg

callee_saves = ['ebx', 'edx', 'esi', 'edi']


def align_call(push_args):
    if len(push_args) % 4 != 0:
        n = 4 - (len(push_args) % 4)
        for i in range(0,n):
            push_args = [Push(Const(0))] + push_args 
    return push_args

class InstrSelVisitor3(InstrSelVisitor2):
    def visitModule(self, n):
        if isinstance(n.node, Stmt):
            funs = [self.dispatch(fun) for fun in n.node.nodes if isinstance(fun, Function)]
            rest = [s for s in n.node.nodes if not isinstance(s, Function)]
            main = Function(None, "main", [], None, 0, None,
                            Stmt(rest + [Return(Const(0))]))
            main = self.dispatch(main)
            return funs + [main]
        else:
            raise Exception('in InstrSelVisitor4, expected Stmt inside Module')

    def visitReturn(self, n):
        restore_callee_saves = []
        for r in reversed(callee_saves):
            restore_callee_saves += [PopValue(Register(r))]
        return restore_callee_saves + [n]

    def visitFunction(self, n):
        code = self.dispatch(n.code)
        if isinstance(code, Stmt):
            # save the callee-save registers!
            push_callee_saves = [Push(Register(r)) for r in callee_saves]
            
            # load the parameters into temporary variables (hopefully registers)
            param_moves = []
            offset = 8
            for param in n.argnames:
                param_moves += [IntMoveInstr(Name(param), [StackLoc(offset)])]
                offset += 4

            return Function(n.decorators, n.name, n.argnames, n.defaults,
                            n.flags, n.doc, Stmt(push_callee_saves + param_moves + code.nodes))
        else:
            raise Exception('in InstrSelVisitor4, expected Stmt inside Function')


    def visitIf(self, n):
        test = n.tests[0][0]
        then = self.dispatch(n.tests[0][1])
        return [If([(test,then)], 
                   self.dispatch(n.else_))]

    def visitWhile(self, n):
        test = n.test
        body = self.dispatch(n.body)
        return [While(test, body, n.else_)]

    # Using eax! ('al' is part of 'eax') Must keep eax in reserve!
    def visitCompare(self, n, lhs):
        left = n.expr
        op = n.ops[0][0]
        right = n.ops[0][1]
        if op == '==' or op == 'is':
            return [CMPLInstr(None, [left, right]),
                    SetIfEqInstr(Register('al')),
                    IntMoveZeroExtendInstr(Name(lhs), [Register('al')])]
        elif op == '!=':
            return [CMPLInstr(None, [left, right]),
                    SetIfNotEqInstr(Register('al')),
                    IntMoveZeroExtendInstr(Name(lhs), [Register('al')])]
        else:
            raise Exception('unhandled comparison operator: %s' % op)

    def visitSubscript(self, n, lhs):
        push_args = [Push(n.subs[0]), Push(n.expr)]
        push_args = align_call(push_args)
        return push_args + [CallX86('get_subscript'),
                            Pop(4 * len(push_args)),
                            IntMoveInstr(Name(lhs), [Register('eax')])]


    def visitGetTag(self, n, lhs):
        # lhs = n.arg & mask
        return [IntMoveInstr(Name(lhs), [n.arg]),
                IntAndInstr(Name(lhs), [Const(mask)])]

    def visitInjectFrom(self, n, lhs):
        if n.typ == 'big':
            # For pointers to big stuff, do the following
            # lhs = n.arg
            # lhs |= BIG_TAG
            return [IntMoveInstr(Name(lhs), [n.arg]),
                    IntOrInstr(Name(lhs), [Const(tag['big'])])]
        else:
            # For int and bool, do the following
            # lhs = n.arg << shift[n.typ]
            # lhs |= tag[n.typ]
            return [IntMoveInstr(Name(lhs), [n.arg]),
                    ShiftLeftInstr(Name(lhs), [Const(shift[n.typ])]),
                    IntOrInstr(Name(lhs), [Const(tag[n.typ])])]

    def visitProjectTo(self, n, lhs):
        if n.typ == 'big':
            # n.arg & ~MASK
            return [IntMoveInstr(Name(lhs), [Const(mask)]),
                    IntNotInstr(Name(lhs), []),
                    IntAndInstr(Name(lhs), [n.arg])]
        else:
            return [IntMoveInstr(Name(lhs), [n.arg]),
                    ShiftRightInstr(Name(lhs), [Const(shift[n.typ])])]

    def visitSetSubscript(self, n, lhs):
        push_args = [Push(n.val), Push(n.key), Push(n.container)]
        push_args = align_call(push_args)
        return push_args + [CallX86('set_subscript'),
                            Pop(4 * len(push_args)),
                            IntMoveInstr(Name(lhs), [Register('eax')])]


    def visitPrintnl(self, n):
        push_args = [Push(n.nodes[0])]
        push_args = align_call(push_args)
        pop = [Pop(4 * len(push_args))]
        return push_args + [CallX86('print_any')] + pop
