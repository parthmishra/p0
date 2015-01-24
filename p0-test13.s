.globl main
main:
pushl %ebp
movl %esp, %ebp
subl $8, %esp
movl $1, %eax
negl %eax
movl %eax, -8(%ebp)
pushl -8(%ebp)
call print_int_nl
addl $4, %esp
movl $0, %eax
leave
ret
