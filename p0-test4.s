.globl main
main:
pushl %ebp
movl %esp, %ebp
subl $4, %esp
movl $3, %eax
addl $4, %eax
movl $0, %eax
leave
ret
