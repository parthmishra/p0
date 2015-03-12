from ir import *

counter = 0

def name_gen(x):
    global counter
    name = x + str(counter)
    counter = counter + 1
    return name

def label_gen(x):
    global counter
    name = x + '_' + str(counter)
    counter = counter + 1
    return name

shift = { 'int' : 2, 'bool' : 2, 'big' : 2 }
tag = { 'int' : 0, 'bool' : 1, 'big' : 3 }
mask = 3

builtin_functions = ['input_int', 'input', 'print_any', 'create_dict', 'create_list',
                     'add', 'is_true', 'equal', 'not_equal',
                     'get_fun_ptr', 'get_free_vars',
                     'create_class', 'get_attr', 'set_attr', 'has_attr',
                     'create_object', 'get_class', 'is_class',
                     'get_function', 'get_receiver', 'is_bound_method', 'is_unbound_method']

class Push(Node):
    def __init__(self, arg):
        self.arg = arg

    def getChildren(self):
        return [arg]

    def getChildNodes(self):
        return [arg]

    def __repr__(self):
        return "Push(%s)" % repr(self.arg)

class Pop(Node):
    def __init__(self, bytes):
        self.bytes = bytes

    def getChildren(self):
        return []

    def getChildNodes(self):
        return []

    def __repr__(self):
        return "Pop(%s)" % repr(self.bytes)

class PopValue(Node):
    def __init__(self, target):
        self.target = target

    def getChildren(self):
        return []

    def getChildNodes(self):
        return []

    def __repr__(self):
        return "PopValue(%s)" % repr(self.target)

class CallX86(Node):
    def __init__(self, name):
        self.name = name

    def getChildren(self):
        return []

    def getChildNodes(self):
        return []

    def __repr__(self):
        return "call %s" % self.name


class CMPLInstr(ArithInstr):
    def __init__(self, lhs, rhs):
        ArithInstr.__init__(self, lhs, rhs)

# lhs must be a single byte register (such as the AL part of EAX).
class SetIfEqInstr(ArithInstr):
    def __init__(self, lhs, rhs=[]):
        ArithInstr.__init__(self, lhs, rhs)

class SetIfNotEqInstr(ArithInstr):
    def __init__(self, lhs, rhs=[]):
        ArithInstr.__init__(self, lhs, rhs)

class IntMoveZeroExtendInstr(ArithInstr):
    def __init__(self, lhs, rhs):
        ArithInstr.__init__(self, lhs, rhs)

class JumpEqInstr(Node):
    def __init__(self, dest):
        self.dest = dest

    def getChildren(self):
        return []

    def getChildNodes(self):
        return []

    def __repr__(self):
        return "je(%s)" % self.dest

class IntNotInstr(ArithInstr):
    def __init__(self, lhs, rhs):
        ArithInstr.__init__(self, lhs, rhs)


