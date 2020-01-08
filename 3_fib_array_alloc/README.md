## Experimenting with the f2py and Fortran allocatble arrays

### 1 - Allocate memory for Fortran allocatable arrays with Fortran

The Fortran source code used in this experiment is based on the section 5a of the [first experiment](../1_fib_array_intent) where the subroutine `series` takes four arguments: the dimension of the arrays `n`, an input array `A`, an input/output array `M`, and an output array `Z`. However, this time we define the array `M` as an allocatable array in the module `fib`: it will not be required to provide it as an argument in the new interface to the module, rather it will remain a variable internal to the module. 

This new interface is given by the subroutine `calc`. It only takes `n`, `A`, and `Z` as arguments while using the array `M` declared internally in the module. Finally, a third subroutine `init` is defined to allocate memory for the array `M` and initialise it with zeros. The Fortran source code implementing these three subroutines is provided below: 

```fortran
! file: fib.f90

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
            
        end subroutine series

end module fib
```

Once the static library is generated (more details on this in section 1 of the [first experiment](../1_fib_array_intent)), the following Python script can be used to generate the Fibonacci series of the required length `n`:

```python
# file: test1.py
import fibonacci
import numpy as np

n = 7

a = np.ones((n,), order='F', dtype=np.float32)

print('___________ 1ST CALL ___________')
# call the wrapper 'calc' a first time
z1 = fibonacci.fib.calc(n, a)

print(z1)
print(fibonacci.fib.m)

print('___________ 2ND CALL ___________')
# call the wrapper 'calc' a second time
z2 = fibonacci.fib.calc(n, a)

print(z2)
print(fibonacci.fib.m)
```

However, running this script yields an error:

```bash
$ python test1.py
___________ 1ST CALL ___________

Process finished with exit code 139 (interrupted by signal 11: SIGSEGV)
```

This is due to a [segmentation violation](https://en.wikipedia.org/wiki/Segmentation_fault), because the array `M` is not allocated memory prior its use in the program. Indeed, the subroutine `init` was not invoked in *test1.py*.

Now, if we invoke the `init` subroutine before invoking the `calc` subroutine:
```python
# file: test2.py
import fibonacci
import numpy as np

n = 7

a = np.ones((n,), order='F', dtype=np.float32)

# allocate and initialise the internal allocatable array 'M' with Fortran
fibonacci.fib.init(n)

print('___________ 1ST CALL ___________')
# call the wrapper 'calc' a first time
z1 = fibonacci.fib.calc(n, a)

print(z1)
print(fibonacci.fib.m)

print('___________ 2ND CALL ___________')
# call the wrapper 'calc' a second time
z2 = fibonacci.fib.calc(n, a)

print(z2)
print(fibonacci.fib.m)
```

The following result is obtained:
```bash
$ python test2.py
___________ 1ST CALL ___________
[0. 1. 1. 2. 3. 5. 8.]
[1. 2. 2. 3. 4. 6. 9.]
___________ 2ND CALL ___________
[0. 1. 1. 2. 3. 5. 8.]
[ 2.  4.  4.  6.  8. 12. 18.]
```

The expected behaviour is now achieved: the Fibonacci series is generated after each call, and the array `M` defined in Fortran is indeed modified inplace and its values updated after each call to the `calc` subroutine.

### 2 - Allocate memory for Fortran allocatable arrays with Python

The memory allocation of the allocatable array can also be done directly in Python. By re-using the Fortran code in the section 1 above, and once the static library is generated, the following Python script can be used: 

```python
# file: test.py
import fibonacci
import numpy as np

n = 7

a = np.ones((n,), order='F', dtype=np.float32)

# allocate and initialise the internal allocatable array 'M' with Python
fibonacci.fib.m = np.zeros((n,), order='F', dtype=np.float32)

print('___________ 1ST CALL ___________')
# call the wrapper 'calc' a first time
z1 = fibonacci.fib.calc(n, a)

print(z1)
print(fibonacci.fib.m)

print('___________ 2ND CALL ___________')
# call the wrapper 'calc' a second time
z2 = fibonacci.fib.calc(n, a)

print(z2)
print(fibonacci.fib.m)
```

```bash
$ python test.py
___________ 1ST CALL ___________
[0. 1. 1. 2. 3. 5. 8.]
[1. 2. 2. 3. 4. 6. 9.]
___________ 2ND CALL ___________
[0. 1. 1. 2. 3. 5. 8.]
[ 2.  4.  4.  6.  8. 12. 18.]
```

The same, expected, behaviour as in section 1 is now obtained without requiring an `init` subroutine in Fortran. The internal array `M` declared in the Fortran module can be allocated simply by assigning it a numpy array of the relevant dimension.

Note that when assigning and inspecting variables defined internally in the Fortran module, like above with the variable `M`, the default behaviour of `f2py` is to lower all cases as stated in its [documentation](https://numpy.org/devdocs/f2py/signature-file.html):
> In general, the contents of signature files is case-sensitive. When scanning Fortran codes and writing a signature file, F2PY lowers all cases automatically except in multiline blocks or when --no-lower option is used.

This means that accessing in Python the Fortran variable `M` in the module `fib` cannot be done using `fibonacci.fib.M`, but only `fibonacci.fib.m`, since this is how it is defined in the signature file.
