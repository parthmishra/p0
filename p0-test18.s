.globl main
main:
pushl %ebp
movl %esp, %ebp
subl $24, %esp
call input
movl %eax, -4(%ebp)
movl $5, %eax
addl -8(%ebp), %eax
movl %eax, -12(%ebp)
movl $6, %eax
negl %eax
movl %eax, -16(%ebp)
movl -12(%ebp), %eax
addl %eax, -16(%ebp)
call input
movl %eax, -20(%ebp)
movl -20(%ebp), %eax
addl %eax, -24(%ebp)
pushl -24(%ebp)
call print_int_nl
addl $4, %esp
movl $0, %eax
leave
ret
