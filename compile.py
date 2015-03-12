# from flatten1 import *
# from explicate1 import *
from explicate1Visit import explicateVisit
from explicate1 import is_true, constOrName, letify, explicate
from visitor86 import Visitor
from flatten1Visit import *
from flatten1 import flattener
from selectVisit3 import *
from registerAlloc3 import RegisterAlloc3
from print_visitor3 import PrintVisitor3
from removeControl import RemoveStructuredControl
from generate_x86_3 import GenX86Visitor3, string_constants
from generate_x86_2 import GenX86Visitor2
from generate_x86_1 import fun_prefix
import sys
from os.path import splitext



# from selectVisit1 import *

inputFile = sys.argv[1]
ast = compiler.parseFile(inputFile)
# print ast
# print ''

ast = explicate(ast)
# print ast
# print ''
# print PrintASTVisitor2().preorder(ast)

flat=flattener(ast, False)
# print "In Compile = "
# print flat
# print ''

# flat=flattenVisit().preorder(ast)
# print flat

# print ast
instr = SelectVisit3().preorder(flat)
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
    item.code = RemoveStructuredControl(item.code)

# for item in instr:
# 	print PrintVisitor3().preorder(item)

x86 = GenX86Visitor3().preorder(Stmt(instr))

x86 = ('.globl %smain' % fun_prefix) + x86

strings = ''
x86 = strings + '\t.text\n' + x86
asm_file = open(splitext(inputFile)[0] + '.s', 'w')
print >>asm_file, x86
