! Fibonacci program

module fib
    contains
        subroutine series(n, A, M, Z)
            ! calculates first n elements of the Fibonacci series,
            ! adds it to the existing input/output array, and adds the
            ! input array to it
            implicit none

            integer, intent(in) :: n
            real, intent(in), dimension(n) :: A
            !f2py depend(n) A
            real, intent(inout), dimension(n) :: M
            !f2py intent(inplace) M
            !f2py depend(n) M
            real, intent(out), dimension(n) :: Z
            !f2py depend(n) Z
            integer :: i

            do i = 1, n
                if (i == 1) then
                    Z(i) = 0.0
                else if (i == 2) then
                    Z(i) = 1.0
                else
                    Z(i) = Z(i - 2) + Z(i - 1)
                end if
            end do

            do i = 1, n
                M(i) = M(i) + A(i) + Z(i)
            end do

        end subroutine series
end module fib
