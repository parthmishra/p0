#Aaron Holt
#CSCI 5525
#Homework 2
#P0 lexer

import ply.lex as lex

#tokens and regex for tokens from the PLY simple example
#P0 tokens:
tokens=['PRINT','INPUT','PLUS','MINUS','EQUALS','INT','NAME','LPAREN','RPAREN',]

reserved = {'print':'PRINT','input':'INPUT',}

#Regex for tokens:
t_PRINT = r'print'
t_INPUT = r'input'
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_EQUALS  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'



#INT newline and error given from book
def t_INT(t):
    r'\d+'
    try:
    	t.value = int(t.value)
    except ValueError:
    	print "Integer value too large", t.value
    	t.value = 0
    return t

def t_newline(t):
	r'\n+'
	t.lexer.lineno += len(t.value)

#Ignore spaces and tabs. Ignore comments.
t_ignore  = ' \t'
t_ignore_COMMENT = r'\#.*'

def t_error(t):
	print "Illegal character '%s'" % t.value[0]
	t.lexer.skip(1)

l=lex.lex()

# test='''
# x=7
# y=4
# z=x+y+4
# '''

# l.input(test)

# #Print out tokens, break when no more input available
# while True:
#     tok = l.token()
#     if not tok: break    
#     print tok