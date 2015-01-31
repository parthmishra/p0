.globl main
main:
pushl %ebp
movl %esp, %ebp
subl $0, %esp
pushl $42
call print_int_nl
addl $4, %esp
movl $0, %eax
leave
ret
