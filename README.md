# Experimenting with `numpy.f2py`

This repository contains a few of small experiments to explore the interface to Fortran code offered by `numpy.f2py` in Python. To do so, the [example generating a Fibonacci series](https://docs.scipy.org/doc/numpy/f2py/getting-started.html) provided in the official documentation is used:

```fortran
subroutine series(n, Z)
    ! calculates first n elements of the Fibonacci series
    implicit none

    integer, intent(in) :: n
    real, intent(out), dimension(n) :: Z
    integer i

    do i = 1, n
        if (i == 1) then
            Z(i) = 0.0
        else if (i == 2) then
            Z(i) = 1.0
        else
            Z(i) = Z(i - 2) + Z(i - 1)
        end if
    end do
end subroutine series
```

The [first experiment](fib_intent/fib_intent.md) consists in exploring the different intents for Fortran subroutine arguments.

The [second experiment](fib_datatype/fib_datatype.md) consists in exploring the different datatypes for Fortran subroutine numerical arguments.

The [third experiment](fib_alloc/fib_alloc.md) consists in exploring the different ways of allocating memory for Fortran allocatable arrays.

All experiments are conducted using Python 3.7, and numpy 1.17.3, and GNU Fortran 95 compiler 8.2.0.
