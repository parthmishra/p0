.globl main
main:
pushl %ebp
movl %esp, %ebp
subl $8, %esp
movl $3, -4(%ebp)
addl $4, -4(%ebp)
movl -4(%ebp), %eax
movl %eax, -8(%ebp)
addl $5, -8(%ebp)
pushl -8(%ebp)
call print_int_nl
addl $4, %esp
movl $0, %eax
leave
ret
