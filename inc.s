.globl main
main:
	pushl %ebp
	movl %esp, %ebp
	subl $24, %esp
	call input
	movl %eax, -16(%ebp)
	movl -16(%ebp), %eax
	negl %eax
	movl %eax, -8(%ebp)
	movl -8(%ebp), %eax
	negl %eax
	movl %eax, -12(%ebp)
	movl -12(%ebp), %eax
	negl %eax
	movl %eax, -4(%ebp)
	subl $12, %esp
	pushl -4(%ebp)
	call print_int_nl
	addl $16, %esp
	movl $0, %eax
	leave
	ret
