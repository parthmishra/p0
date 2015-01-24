.globl main
main:
pushl %ebp
movl %esp, %ebp
subl $16, %esp
movl $2, -4(%ebp)
movl $1, -12(%ebp)
addl !!!2, -12(%ebp)
movl -12(%ebp), %eax
negl %eax
movl %eax, -16(%ebp)
pushl -16(%ebp)
call print_int_nl
addl $4, %esp
movl $0, %eax
leave
ret
