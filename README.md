# Experimenting with `numpy.f2py`

This repository contains a few small experiments to better understand the behaviour of `numpy.f2py` (shortened to `f2py` hereafter) when used to import into Python a functionality that is coded in Fortran.

To do so, the [example of the Fibonacci series](https://docs.scipy.org/doc/numpy/f2py/getting-started.html) provided in the official documentation is used as the functionality to be imported, where the first elements of the Fibonacci series are generated using a Fortran subroutine, and the subroutine is called from a Python script. The initial subroutine used is the following:

```fortran
subroutine series(n, Z)
    ! calculates first n elements of the Fibonacci series
    implicit none

    integer, intent(in) :: n
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
end subroutine series
```

This simple functionality coded in Fortran 90 will be used and complexified while going through the following three experiments:

* the [first experiment](./1_fib_array_intent) explores the different intentions for Fortran subroutine array arguments.

* the [second experiment](./2_fib_array_datatype) explores the different datatypes for Fortran subroutine array arguments.

* the [third experiment](./3_fib_array_alloc) explores the different ways of allocating memory for Fortran allocatable arrays.

All experiments are conducted using Python 3.7.5, and numpy 1.17.3, and GNU Fortran 95 compiler 8.2.0.
