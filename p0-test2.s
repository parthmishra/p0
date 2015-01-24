.globl main
main:
pushl %ebp
movl %esp, %ebp
subl $8, %esp
call input
movl $0, %eax
leave
ret
