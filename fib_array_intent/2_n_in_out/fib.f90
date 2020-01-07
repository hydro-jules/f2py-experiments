! Fibonacci program

module fib
    contains
        subroutine series(n, A, Z)
            ! calculates first n elements of the Fibonacci series
            ! and adds the input array to it
            implicit none

            integer, intent(in) :: n
            real, intent(in), dimension(n) :: A
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
                Z(i) = Z(i) + A(i)
            end do

        end subroutine series
end module fib
