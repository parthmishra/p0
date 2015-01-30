#Aaron Holt & Parth Mishra
#CSCI 5525
#Homework 2
#P0 parser

# Grammar:
# 0. start ::= statement
# 1. statement ::= PRINT expression
# 2. expression ::= expression PLUS expression
# 3. expression ::= INT

# tokens=['PRINT','INPUT','PLUS','MINUS','EQUALS','INT','NAME','LPAREN','RPAREN',]

# reserved = {'print':'PRINT','input':'INPUT',}

# #Regex for tokens:
# t_PRINT = r'print'
# t_INPUT = r'input'
# t_PLUS    = r'\+'
# t_MINUS   = r'-'
# t_EQUALS  = r'='
# t_LPAREN  = r'\('
# t_RPAREN  = r'\)'
# t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'

import sys
import ply.yacc as yacc

from compiler.ast import *
from lexer import reserved
from lexer import tokens

# precedence = (
#     ('left', 'PLUS'),
#     ('right', 'UMINUS'),)

precedence = (
    ('left', 'PLUS'),)

def p_module(t):
	'module : statement_list'
	t[0] = Module(None, Stmt(t[1]))

def p_statement_list(t):
	'statement_list : statementlist statement'
	t[0] = t[1] + [t[2]]

def p_statement(t):
	'statement_list : statement'
	t[0] = [t[1]]


#Functions From Book
def p_print_statement(t):
	'statement : PRINT expression'
	t[0] = Printnl([t[2]], None)
def p_plus_expression(t):
	'expression : expression PLUS expression'
	t[0] = Add((t[1], t[3]))
def p_int_expression(t):
	'expression : INT'
	t[0] = Const(t[1])
def p_error(t):
	print "Syntax error at '%s''" % t.value


yacc.yacc()

test='''
7
'''

ast=yac.parse(test)
print ast