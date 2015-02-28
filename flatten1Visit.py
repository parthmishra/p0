from ir import *
from visitor86 import Visitor
from class86 import *
from ExplicitClass import *

# Input: an AST for P_1


def make_assign(lhs, rhs):
    return Assign(nodes=[AssName(name=lhs, flags='OP_ASSIGN')], expr=rhs)

class flattenVisit(Visitor):

    def visitModule(self, n):
        ss = self.dispatch(n.node)
        return Module(n.doc, Stmt(ss))

    def visitNone(self, n):
        return (n, [])

    def visitStmt(self, n):
        sss  = [self.dispatch(s) for s in n.nodes]
        return reduce(lambda a,b: a + b, sss, [])

    def visitPrintnl(self, n):
        (e,ss) = self.dispatch(n.nodes[0], True)
        return ss + [Printnl([e], n.dest)]

    def visitAssign(self, n):
        lhs = n.nodes[0].name
        (rhs,ss) = self.dispatch(n.expr, True)
        return ss + [Assign(n.nodes, rhs)]

    def visitDiscard(self, n):
        (e, ss) = self.dispatch(n.expr, True)
        return ss

    def visitConst(self, n, needs_to_be_simple):
        return (n, [])

    def visitName(self, n, needs_to_be_simple):
        return (n, [])

    def visitAdd(self, n, needs_to_be_simple):
        (left, ss1) = self.dispatch(n.left, True)
        (right, ss2) = self.dispatch(n.right, True)
        if needs_to_be_simple:
            tmp = name_gen('tmp')
            return (Name(tmp), ss1 + ss2 + [make_assign(tmp, Add((left, right)))])
        else:
            return (Add((left, right)), ss1 + ss2)            

    def visitUnarySub(self, n, needs_to_be_simple):
        (expr,ss) = self.dispatch(n.expr, True)
        if needs_to_be_simple:
            tmp = name_gen('tmp')
            return (Name(tmp), ss + [make_assign(tmp, UnarySub(expr))])
        else:
            return (UnarySub(expr), ss)

    def visitCallFunc(self, n, needs_to_be_simple):
        # print "NNNNNNNNNNNNNNNNNNNN=",n
        if isinstance(n.node, Name):
            args_sss = [self.dispatch(arg, True) for arg in n.args]
            args = [arg for (arg,ss) in args_sss]
            ss = reduce(lambda a,b: a + b, [ss for (arg,ss) in args_sss], [])
            if needs_to_be_simple:
                tmp = name_gen('tmp')
                return (Name(tmp), ss + [make_assign(tmp, CallFunc(n.node, args))])
            else:
                return (CallFunc(n.node, args), ss)
        else:
            raise Exception('flatten1: only calls to named functions allowed')

    def visitIfExp(self, n, needs_to_be_simple):
        (test, test_ss) = self.dispatch(n.test, True)
        (then, then_ss) = self.dispatch(n.then, True)
        # print ''
        # print "ELSE: ",n.else_
        (else_, else_ss) = self.dispatch(n.else_, True)   
        # print "HEREHEREHREHRHERHEHRH"
        # print "elseExpr = ", else_
        # print "elseStmts = ", else_ss     
        tmp = name_gen('tmp')
        return (Name(tmp), test_ss + [If([(test, Stmt(then_ss + [make_assign(tmp, then)]))],
                                         Stmt(else_ss + [make_assign(tmp, else_)]))])

    def visitCompare(self, n, needs_to_be_simple):
        (left,ss1) = self.dispatch(n.expr, True)
        op = n.ops[0][0]
        (right,ss2) = self.dispatch(n.ops[0][1], True)
        compare = Compare(expr=left, ops=[(op,right)])
        if needs_to_be_simple:
            tmp = name_gen('tmp')
            return (Name(tmp), ss1 + ss2 + [make_assign(tmp, compare)])
        else:
            return (compare, ss1 + ss2)            

    def visitSubscript(self, n, needs_to_be_simple):
        (c_result, c_ss) = self.dispatch(n.expr, True)
        (k_result, k_ss) = self.dispatch(n.subs[0], True)
        rhs = Subscript(expr=c_result, flags=n.flags, subs=[k_result])
        if needs_to_be_simple:
            tmp = name_gen('tmp')
            return (Name(tmp), c_ss + k_ss + [make_assign(tmp, rhs)])
        else:
            return (rhs, c_ss + k_ss)            

    # Made-up AST nodes

    def visitGetTag(self, n, needs_to_be_simple):
        (e, ss) = self.dispatch(n.arg, True)
        tmp = name_gen('tmp')
        rhs = GetTag(e)
        return (Name(tmp), ss + [make_assign(tmp, rhs)])

    def visitInjectFrom(self, n, needs_to_be_simple):
        (arg, ss) = self.dispatch(n.arg, True)
        tmp = name_gen('tmp')
        rhs = InjectFrom(n.typ, arg)
        return (Name(tmp), ss + [make_assign(tmp, rhs)])

    def visitProjectTo(self, n, needs_to_be_simple):
        (arg, ss) = self.dispatch(n.arg, True)
        tmp = name_gen('tmp')
        rhs = ProjectTo(n.typ, arg)
        return (Name(tmp), ss + [make_assign(tmp, rhs)])

    def visitLet(self, n, needs_to_be_simple):
        (rhs_result, rhs_ss) = self.dispatch(n.rhs, False)
        (body_result, body_ss) = self.dispatch(n.body, True)
        return (body_result, rhs_ss + [make_assign(n.var, rhs_result)] + body_ss)

    def visitSetSubscript(self, n, needs_to_be_simple):
        (c_result, c_ss) = self.dispatch(n.container, True)
        (k_result, k_ss) = self.dispatch(n.key, True)
        (v_result, v_ss) = self.dispatch(n.val, True)
        tmp = name_gen('tmp')
        rhs = SetSubscript(c_result, k_result, v_result)
        return (Name(tmp), c_ss + k_ss + v_ss + [make_assign(tmp, rhs)])

    def visitFunction(self, n):
        ss = self.dispatch(n.code)
        return [Function(n.decorators, n.name, n.argnames, n.defaults, n.flags, n.doc, Stmt(ss))]

    def visitReturn(self, n):
        (e,ss) = self.dispatch(n.value, True)
        return ss + [Return(e)]

    def visitIndirectCallFunc(self, n, needs_to_be_simple):
        (node, ss1) = self.dispatch(n.node, True)
        args_sss = [self.dispatch(arg, True) for arg in n.args]
        args = [arg for (arg,ss) in args_sss]
        ss2 = reduce(lambda a,b: a + b, [ss for (arg,ss) in args_sss], [])

        if needs_to_be_simple:
            tmp = generate_name('tmp')
            return (Name(tmp), ss1 + ss2 + [make_assign(tmp, IndirectCallFunc(node, args))])
        else:
            return (IndirectCallFunc(node, args), ss1 + ss2)

    # def visitCallFunc(self, n, needs_to_be_simple):
    #     if isinstance(n.node, FunName):
    #         args_sss = [self.dispatch(arg, True) for arg in n.args]
    #         args = [arg for (arg,ss) in args_sss]
    #         ss = reduce(lambda a,b: a + b, [ss for (arg,ss) in args_sss], [])
    #         if needs_to_be_simple:
    #             tmp = generate_name('tmp')
    #             return (Name(tmp), ss + [make_assign(tmp, CallFunc(n.node, args))])
    #         else:
    #             return (CallFunc(n.node, args), ss)
    #     else:
    #         raise Exception('flatten3: only calls to named functions allowed, not %s' % repr(n.node))