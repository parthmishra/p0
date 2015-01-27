.globl main
main:
pushl %ebp
movl %esp, %ebp
subl $4, %esp
call input
movl %eax, -4(%ebp)
pushl -4(%ebp)
call print_int_nl
addl $4, %esp
movl $0, %eax
leave
ret
