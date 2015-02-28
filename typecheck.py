

inputFile = sys.argv[1]
ast = compiler.parseFile(inputFile)

explicit=explicate(ast)
typ = typeCheck(explicit)
print typ
print ''
