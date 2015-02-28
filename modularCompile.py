# from flatten1 import *
# from explicate1 import *
from selectVisit3 import *
from explicate1Visit import explicateVisit
from visitor86 import Visitor
from flatten1Visit import *
from selectVisit3 import *
from registerAlloc3 import RegisterAlloc3
from print_visitor3 import PrintVisitor3
from removeControl import RemoveStructuredControl
from generate_x86_3 import GenX86Visitor3, string_constants
from generate_x86_1 import fun_prefix
import sys
from os.path import splitext



# from selectVisit1 import *

inputFile = sys.argv[1]
ast = compiler.parseFile(inputFile)

# print preorder(ast)
# ast=explicate(ast)
ast = explicateVisit().preorder(ast)
# print ast
# print ''
# ast=cc(ast)
# print ast
flat=flattenVisit().preorder(ast)
# print flat
# ast=select(flat)
# print ast
instr = InstrSelVisitor3().preorder(flat)
# print instr
# print ''
# print ''
# for item in instr:
# 	print PrintVisitor3().preorder(item)


latest=[]
for inst in instr:
    latest += [RegisterAlloc3().allocate_registers(inst,inputFile + '_' + inst.name)]
                                                     
instr = latest

for item in instr:
	item.code = RemoveStructuredControl().preorder(item.code)

for item in instr:
	print PrintVisitor3().preorder(item)

x86 = GenX86Visitor3().preorder(Stmt(instr))

x86 = ('.globl %smain' % fun_prefix) + x86

if len(string_constants.keys()) > 0:
    if sys.platform == 'darwin':
        strings = '''\n\t.cstring\n'''
    else:
        strings = ''
    for (var,str) in string_constants.items():
        if sys.platform == 'darwin':
            strings += ('''%s:\n\t.ascii "%s\\0"\n''' % (var, str)) 
        else:
            strings += ('''\n%s:\n\t.string "%s"\n''' % (var, str))
else:
    strings = ''
x86 = strings + '\t.text\n' + x86
asm_file = open(splitext(inputFile)[0] + '.s', 'w')
print >>asm_file, x86
