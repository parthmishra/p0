import compiler
from compiler.ast import *


class GetTag(Node):
    """Call code to determine if 'arg' is of type 'typ'"""
    def __init__(self, arg):
        self.arg = arg
    
    def getChildren(self):
        return [self.arg]

    def getChildNodes(self):
        return [self.arg]

    def __repr__(self):
        return "GetTag(%s)" % repr(self.arg)

class InjectFrom(Node):
    """Convert result of 'arg' from 'typ' to pyobj"""
    def __init__(self, typ, arg):
        self.typ = typ
        self.arg = arg
    
    def getChildren(self):
        return [self.arg]

    def getChildNodes(self):
        return [self.arg]

    def __repr__(self):
        return "InjectFrom(%s, %s)" % (self.typ, repr(self.arg))

class ProjectTo(Node):
    """Convert result of 'arg' from pyobj to 'typ'"""
    def __init__(self, typ, arg):
        self.typ = typ
        self.arg = arg
    
    def getChildren(self):
        return [self.arg]

    def getChildNodes(self):
        return [self.arg]

    def __repr__(self):
        return "ProjectTo(%s, %s)" % (self.typ, repr(self.arg))

class Let(Node):
    """Evaluate 'var' = 'rhs', than run body referencing 'var'"""
    def __init__(self, var, rhs, body):
        self.var = var
        self.rhs = rhs
        self.body = body

    def getChildren(self):
        return self.rhs, self.body

    def getChildNodes(self):
        return self.rhs, self.body

    def __repr__(self):
        return "Let(%s, %s, %s)" % \
               (self.var, repr(self.rhs), repr(self.body))

class SetSubscript(Node):
    def __init__(self, container, key, val):
        self.container = container
        self.key = key
        self.val = val
    
    def getChildren(self):
        return self.container, self.key, self.val

    def getChildNodes(self):
        return self.container, self.key, self.val

    def __repr__(self):
        return "SetSubscript(%s, %s, %s)" % \
               (repr(self.container), repr(self.key), repr(self.val))

# How to make these modular?

param_types = {
    'is_true' : ['pyobj'],
    'add' : ['big','big'],
    'equal' : ['big','big'],
    'not_equal' : ['big','big'],
    'create_list' : ['pyobj'],
    'create_dict' : [],
    'input_int' : [],
    'input' : [],    
    'get_attr' : ['pyobj', 'str'],
    'set_attr' : ['pyobj', 'str', 'pyobj'],
    'create_class' : ['pyobj'],
    'create_object' : ['pyobj'],
    'get_class' : ['pyobj'],
    'is_class' : ['pyobj'],
    'has_attr' : ['pyobj', 'str'],
    'get_function' : ['pyobj'],
    'get_receiver' : ['pyobj'],
    'is_bound_method' : ['pyobj'],
    'is_unbound_method' : ['pyobj']
    }

return_type = {
    'is_true' : 'bool',
    'add' : 'big',
    'equal' : 'bool',
    'not_equal' : 'bool',
    'create_list' : 'big',
    'create_dict' : 'big',
    'input_int' : 'pyobj',
    'input' : 'int',
    'get_attr' : 'pyobj',
    'set_attr' : 'pyobj',
    'create_class' : 'big',
    'create_object' : 'big',
    'get_class' : 'big',
    'is_class' : 'bool',
    'has_attr' : 'bool',
    'get_function' : 'big',
    'get_receiver' : 'big',
    'is_bound_method' : 'bool',
    'is_unbound_method' : 'bool'
    }