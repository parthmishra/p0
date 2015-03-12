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

    def visitConst(self, n, constOrName):
        return (n, [])

    def visitName(self, n, constOrName):
        return (n, [])

    def visitAdd(self, n, constOrName):
        (left, ss1) = self.dispatch(n.left, True)
        (right, ss2) = self.dispatch(n.right, True)
        if constOrName:
            tmp = name_gen('tmp')
            return (Name(tmp), ss1 + ss2 + [make_assign(tmp, Add((left, right)))])
        else:
            return (Add((left, right)), ss1 + ss2)            

    def visitUnarySub(self, n, constOrName):
        (expr,ss) = self.dispatch(n.expr, True)
        if constOrName:
            tmp = name_gen('tmp')
            return (Name(tmp), ss + [make_assign(tmp, UnarySub(expr))])
        else:
            return (UnarySub(expr), ss)

    def visitCallFunc(self, n, constOrName):
        # print "NNNNNNNNNNNNNNNNNNNN=",n
        if isinstance(n.node, Name):
            args_sss = [self.dispatch(arg, True) for arg in n.args]
            args = [arg for (arg,ss) in args_sss]
            ss = reduce(lambda a,b: a + b, [ss for (arg,ss) in args_sss], [])
            if constOrName:
                tmp = name_gen('tmp')
                return (Name(tmp), ss + [make_assign(tmp, CallFunc(n.node, args))])
            else:
                return (CallFunc(n.node, args), ss)

    def visitIfExp(self, n, constOrName):
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

    def visitCompare(self, n, constOrName):
        (left,ss1) = self.dispatch(n.expr, True)
        op = n.ops[0][0]
        (right,ss2) = self.dispatch(n.ops[0][1], True)
        compare = Compare(expr=left, ops=[(op,right)])
        if constOrName:
            tmp = name_gen('tmp')
            return (Name(tmp), ss1 + ss2 + [make_assign(tmp, compare)])
        else:
            return (compare, ss1 + ss2)            

    def visitSubscript(self, n, constOrName):
        (c_result, c_ss) = self.dispatch(n.expr, True)
        (k_result, k_ss) = self.dispatch(n.subs[0], True)
        rhs = Subscript(expr=c_result, flags=n.flags, subs=[k_result])
        if constOrName:
            tmp = name_gen('tmp')
            return (Name(tmp), c_ss + k_ss + [make_assign(tmp, rhs)])
        else:
            return (rhs, c_ss + k_ss)            

    # Made-up AST nodes

    def visitGetTag(self, n, constOrName):
        (e, ss) = self.dispatch(n.arg, True)
        tmp = name_gen('tmp')
        rhs = GetTag(e)
        return (Name(tmp), ss + [make_assign(tmp, rhs)])

    def visitInjectFrom(self, n, constOrName):
        (arg, ss) = self.dispatch(n.arg, True)
        tmp = name_gen('tmp')
        rhs = InjectFrom(n.typ, arg)
        return (Name(tmp), ss + [make_assign(tmp, rhs)])

    def visitProjectTo(self, n, constOrName):
        (arg, ss) = self.dispatch(n.arg, True)
        tmp = name_gen('tmp')
        rhs = ProjectTo(n.typ, arg)
        return (Name(tmp), ss + [make_assign(tmp, rhs)])

    def visitLet(self, n, constOrName):
        (rhs_result, rhs_ss) = self.dispatch(n.rhs, False)
        (body_result, body_ss) = self.dispatch(n.body, True)
        return (body_result, rhs_ss + [make_assign(n.var, rhs_result)] + body_ss)

    def visitSetSubscript(self, n, constOrName):
        (c_result, c_ss) = self.dispatch(n.container, True)
        (k_result, k_ss) = self.dispatch(n.key, True)
        (v_result, v_ss) = self.dispatch(n.val, True)
        tmp = name_gen('tmp')
        rhs = SetSubscript(c_result, k_result, v_result)
        return (Name(tmp), c_ss + k_ss + v_ss + [make_assign(tmp, rhs)])

