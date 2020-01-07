! Fibonacci program

module fib
    contains
        subroutine series(n, M, Z)
            ! calculates first n elements of the Fibonacci series
            ! and adds it to the existing input/output array
            implicit none

            integer, intent(in) :: n
            real, intent(inout), dimension(n) :: M
            real, intent(out), dimension(n) :: Z
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
                M(i) = M(i) + Z(i)
            end do

        end subroutine series
end module fib
