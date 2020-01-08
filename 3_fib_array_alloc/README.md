## Experimenting with the f2py and Fortran allocatable arrays

### 1 - Allocating memory for Fortran allocatable arrays with Fortran

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

```text
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
```text
$ python test2.py
___________ 1ST CALL ___________
[0. 1. 1. 2. 3. 5. 8.]
[1. 2. 2. 3. 4. 6. 9.]
___________ 2ND CALL ___________
[0. 1. 1. 2. 3. 5. 8.]
[ 2.  4.  4.  6.  8. 12. 18.]
```

The expected behaviour is now achieved: the Fibonacci series is generated after each call, and the array `M` defined in Fortran is indeed modified inplace and its values updated after each call to the `calc` subroutine.

### 2 - Allocating memory for Fortran allocatable arrays with Python

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

```text
$ python test.py
___________ 1ST CALL ___________
[0. 1. 1. 2. 3. 5. 8.]
[1. 2. 2. 3. 4. 6. 9.]
___________ 2ND CALL ___________
[0. 1. 1. 2. 3. 5. 8.]
[ 2.  4.  4.  6.  8. 12. 18.]
```

The same, expected, behaviour as in section 1 is now obtained without requiring the invocation of the `init` subroutine in Fortran. The internal array `M` declared in the Fortran module can be allocated simply by assigning it a numpy array of the appropriate dimension.

Note that when assigning and inspecting variables defined internally in the Fortran module, like above with the variable `M`, the default behaviour of `f2py` is to lower all cases as stated in its [documentation](https://numpy.org/devdocs/f2py/signature-file.html):
> In general, the contents of signature files is case-sensitive. When scanning Fortran codes and writing a signature file, F2PY lowers all cases automatically except in multiline blocks or when --no-lower option is used.

This means that accessing in Python the Fortran variable `M` in the module `fib` cannot be done using `fibonacci.fib.M`, but only `fibonacci.fib.m`, since this is how it is defined in the signature file.

### 3 - Exploring the memory address of the allocatable array

Once again, we reuse the Fortran file presented in the section 1 above, except that we add the following print statement at the very end of the `series` subroutine:
```fortran
print '(A, Z0)', 'Memory address of "M" (Fortran): ', loc(M)
```

This allows to track the memory location of the array from the Fortran side.

Once the new static library is generated, we can use the following Python script to illustrate what happens to the memory address of the allocatable array when allocated/initialised, modified, or simply retrieved:
```python
import fibonacci
import numpy as np

n = 7

a = np.ones((n,), order='F', dtype=np.float32)

print('\n______ MEMORY ALLOCATION _______')
m_ = np.zeros((n,), order='F', dtype=np.float32)
fibonacci.fib.m = m_
m0 = fibonacci.fib.m
print('Memory address of "m0" (Python): {}'.format(hex(id(m0))))
print('Values in "m0": {!s}'.format(m0))

print('\n___________ 1ST CALL ___________')
z1 = fibonacci.fib.calc(n, a)
m1 = fibonacci.fib.m
print('Memory address of "m1" (Python): {}'.format(hex(id(m1))))
print('Values in "m1": {!s}'.format(m1))

print('\n___________ 2ND CALL ___________')
z2 = fibonacci.fib.calc(n, a)
m2 = fibonacci.fib.m
print('Memory address of "m2" (Python): {}'.format(hex(id(m2))))
print('Values in "m2": {!s}'.format(m2))

print('\n_________ MODIFY "m1" __________')
m1[0] = 0.0
print('Values in "M": {!s}'.format(fibonacci.fib.m))
print('Values in "m1": {!s}'.format(m1))
print('Values in "m2": {!s}'.format(m2))
print('Values in "m_": {!s}'.format(m_))

print('\n_________ MODIFY "m2" __________')
m2[1] = 0.0
print('Values in "M": {!s}'.format(fibonacci.fib.m))
print('Values in "m1": {!s}'.format(m1))
print('Values in "m2": {!s}'.format(m2))
print('Values in "m_": {!s}'.format(m_))

print('\n_________ MODIFY "M" ___________')
fibonacci.fib.m[2] = 0.0
print('Values in "M": {!s}'.format(fibonacci.fib.m))
print('Values in "m1": {!s}'.format(m1))
print('Values in "m2": {!s}'.format(m2))
print('Values in "m_": {!s}'.format(m_))
```

When the script is executed, the following outputs are given:

```text
$ python test.py

______ MEMORY ALLOCATION _______
Memory address of "m0" (Python): 0x10a54f8a0
Values in "m0": [0. 0. 0. 0. 0. 0. 0.]

___________ 1ST CALL ___________
Memory address of "M" (Fortran): 7FEFFBD441D0
Memory address of "m1" (Python): 0x10a54f990
Values in "m1": [1. 2. 2. 3. 4. 6. 9.]

___________ 2ND CALL ___________
Memory address of "M" (Fortran): 7FEFFBD441D0
Memory address of "m2" (Python): 0x10bd05da0
Values in "m2": [ 2.  4.  4.  6.  8. 12. 18.]

_________ MODIFY "m1" __________
Values in "M": [ 0.  4.  4.  6.  8. 12. 18.]
Values in "m1": [ 0.  4.  4.  6.  8. 12. 18.]
Values in "m2": [ 0.  4.  4.  6.  8. 12. 18.]
Values in "m_": [0. 0. 0. 0. 0. 0. 0.]

_________ MODIFY "m2" __________
Values in "M": [ 0.  0.  4.  6.  8. 12. 18.]
Values in "m1": [ 0.  0.  4.  6.  8. 12. 18.]
Values in "m2": [ 0.  0.  4.  6.  8. 12. 18.]
Values in "m_": [0. 0. 0. 0. 0. 0. 0.]

_________ MODIFY "M" ___________
Values in "M": [ 0.  0.  0.  6.  8. 12. 18.]
Values in "m1": [ 0.  0.  0.  6.  8. 12. 18.]
Values in "m2": [ 0.  0.  0.  6.  8. 12. 18.]
Values in "m_": [0. 0. 0. 0. 0. 0. 0.]
```

After the memory allocation, the Fortran array `M` is retrieved, and `f2py` returns it as a numpy array that we assign to the variable `m0`. In this way, one can see that the array exists, is of the right dimension, and is initialised with zeros (as expected).

Now, after calling the `calc` subroutine twice, we can explore how the memory addresses evolve. First, we can see that each time we retrieve the Fortran array `M`, it has a new memory address in Python. We will come back to this later. On the other hand, the memory address of `M` in Fortran is the same between the two calls. Also, one can notice by looking at the evolution of the values in `M` (through retrieving it in `m1`, then in `m2`) that they are updated as expected (i.e. it keeps memory of the state of `M` after the call to the subroutine `calc` that modifies `m`).

Note, the memory addresses in Fortran and in Python are not represented in the same way, so that they are not compared directly here.

Now, by modifying successively `m1`, `m2`, and `M` directly, and looking at the evolution of the values in `M`, `m1`, and `m2`, we notice that when we modify an item in one, they are all modified at the same time. So why do `m0`, `m1`, and `m2` have different memory addresses then? This is because each time the Fortran array `M` is retrieved, `f2py` returns a new view of the same array, not a copy of the array. 

Moreover, it is important to note that the values in `m_`, the original array that was used to allocate memory and initialise with zeros the Fortran array `M` is not modified. This means that `f2py` makes a copy of the data contained in the numpy array it is been given, rather than pointing to the inner data contained in the array given.
