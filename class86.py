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


# class Live_vars:
#     def __init__(self, before, after):
#         self.before = before
#         self.after = after
#     def add_before(self, vars):
#         self.before = self.before | vars

#     def add_after(self, vars):
#         self.after = self.after | vars

#     def __str__(self):
#         return '('+ str(self.before)+','+str(self.after)+')'
        
# class ColorTable:
#     def __init__(self, var_list):
#         self.tbl = {}
#         for key in var_list:
#             if key == 'eax':
#                 self.tbl[key] = 3
#             elif key == 'ecx':
#                 self.tbl[key] = 4
#             elif key == 'edx':
#                 self.tbl[key] = 5
#             else:
#                 self.tbl[key] = -1
#     def get_color(self,node):
#         return self.tbl[node]
#     def set_color(self,node,color):
#         self.tbl[node] = color


# class X86Arg:
#     def __str__(self):
#         return self.mnemonic()
    
# class Const86(X86Arg):
#     def __init__(self, value):
#         self.value = value
#     def mnemonic(self):
#         return '$' + str(self.value)

# class Reg86(X86Arg):
#     def __init__(self, register):
#         self.register = register
#     def mnemonic(self):
#         return '%' + self.register

# class Mem86(X86Arg):
#     def __init__(self, offset, register):
#         self.offset = offset
#         self.register = register
#     def mnemonic(self):
#         return ('-%d(%s)' % (self.offset, self.register.mnemonic()))

# class Var(X86Arg):
#     def  __init__(self, name, color):
#         self.name = name
#         self.color = color
#     def mnemonic(self):
#         return '' + self.name
    
# class X86Inst:
#     def __str__(self):
#         return self.mnemonic()

# class Push86(X86Inst):
#     def __init__(self, value):
#         self.value = value
#     def mnemonic(self):
#         return 'pushl ' + self.value.mnemonic() 

# class Move86(X86Inst):
#     def __init__(self, value, target):
#         self.value = value
#         self.target = target
#     def mnemonic(self):
#         return ('movl %s, %s' % (self.value.mnemonic(), self.target.mnemonic()))

# class Sub86(X86Inst):
#     def __init__(self, value, target):
#         self.value = value
#         self.target = target
#     def mnemonic(self):
#         return ('subl %s, %s' % (self.value.mnemonic(), self.target.mnemonic()))

# class Add86(X86Inst):
#     def __init__(self, value, target):
#         self.value = value
#         self.target = target
#     def mnemonic(self):
#         return ('addl %s, %s' % (self.value.mnemonic(), self.target.mnemonic()))

# class Neg86(X86Inst):
#     def __init__(self, target):
#         self.target = target
#     def mnemonic(self):
#         return 'negl ' + self.target.mnemonic()

# class Call86(X86Inst):
#     def __init__(self, function):
#         self.function = function
#     def mnemonic(self):
#         return 'call ' + self.function

# class Leave86(X86Inst):
#     def mnemonic(self):
#         return 'leave'

# class Ret86(X86Inst):
#     def mnemonic(self):
#         return 'ret'

