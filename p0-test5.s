.globl main
main:
pushl %ebp
movl %esp, %ebp
subl $8, %esp
movl $3, -8(%ebp)
addl $4, -8(%ebp)
movl -8(%ebp), %eax
addl $5, %eax
movl $0, %eax
leave
ret
