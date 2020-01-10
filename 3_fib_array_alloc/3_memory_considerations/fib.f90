! Fibonacci program

module fib
    implicit none

    real, dimension(:), allocatable :: M

    contains

        subroutine calc(n, A, Z)
            ! wraps the call to the Fibonacci series subroutine while providing the internal array M
            implicit none

            integer, intent(in) :: n
            real, intent(in), dimension(n) :: A
            !f2py depend(n) A
            real, intent(out), dimension(n) :: Z
            !f2py depend(n) Z

            call series(n, A, M, Z)

        end subroutine calc

        subroutine init(n)
            ! allocates the required memory space for the Fibonacci series and initialises it with zeros
            implicit none

            integer, intent(in) :: n
            integer :: i

            if (.not. allocated(M)) allocate(M(n))

            do i = 1, n
                M(i) = 0.0
            end do

        end subroutine init

        subroutine series(n, A, M, Z)
            ! calculates first n elements of the Fibonacci series
            implicit none

            integer, intent(in) :: n
            real, intent(in), dimension(n) :: A
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
                M(i) = M(i) + A(i) + Z(i)
            end do

            print '(A, I15)', 'Memory address of "M" (Fortran): ', loc(M)

        end subroutine series

end module fib
