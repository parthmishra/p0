.globl main
main:
pushl %ebp
movl %esp, %ebp
subl $20, %esp
call input
movl %eax, -12(%ebp)
call input
movl %eax, -8(%ebp)
movl -8(%ebp), %eax
negl %eax
movl %eax, -16(%ebp)
movl -12(%ebp), %eax
movl %eax, -20(%ebp)
addl -16(%ebp), -20(%ebp)
pushl -20(%ebp)
call print_int_nl
addl $4, %esp
movl $0, %eax
leave
ret
