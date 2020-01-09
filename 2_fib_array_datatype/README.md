## Experimenting with the different datatypes for Fortran subroutine array arguments

To experiment with the behaviour of `f2py` when there exists mismatches in datatypes between Python and Fortran arrays, the following Fortran subroutine is used (identical to the one used in section 5a of the [first experiment](../1_fib_array_intent)):

```fortran
! file: fib.f90

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
```

From this Fortran source code, a signature file and then a static library are generated, as per the [smart way](https://docs.scipy.org/doc/numpy/f2py/getting-started.html) example in the official `f2py` documentation:
```bash
$ python -m numpy.f2py -m fibonacci -h fib.pyf --overwrite-signature fib.f90
```

```bash
$ python -m numpy.f2py -c fib.pyf fib.f90
```

The following sections deal with mismatches in precision of floating point numbers, but the same conclusions apply to differences in precision for other type of numbers (e.g. between `np.int16` and `np.int32`), and across different type of numbers (e.g. casting from integers to floating point numbers).

### 1 - Array of 32-bit real numbers

Using the static library generated (i.e. *fibonacci.so*), we can now call the `series` subroutine:

```python
# file: test.py
import fibonacci
import numpy as np

n = 7

a = np.ones((n,), order='F', dtype=np.float32)
m = np.ones((n,), order='F', dtype=np.float32)

z = fibonacci.fib.series(n, a, m)

print(z)
print(z.dtype)
```

Now, running the python script above, we get:
```text
$ python test.py
[0. 1. 1. 2. 3. 5. 8.]
float32
```

In this example, Fortran defines all of the arrays `intent(in)`, `intent(inout)`, and `intent(out)` as simple precision real numbers, while Python is passing numpy arrays of `dtype=np.float32`. Since both datatypes are matching, i.e. they are real numbers occupying 32 bits in computer memory, the Python script runs as expected, and the datatype of the returned array `z` is also a simple precision floating point number stored on 32 bits.

### 2 - Array of 64-bit real numbers

The same exercise is repeated with double precision floating point numbers occupying 64 bits of computer memory. These correspond to `double precision` and `np.float64` (or the Python built-in `float`), in Fortran and Python, respectively. The modified Fortran subroutine is as follows:

```fortran
! file: fib.f90

module fib
    contains
        subroutine series(n, A, M, Z)
            ! calculates first n elements of the Fibonacci series,
            ! adds it to the existing input/output array, and adds the
            ! input array to it
            implicit none

            integer, intent(in) :: n
            double precision, intent(in), dimension(n) :: A
            !f2py depend(n) A
            double precision, intent(inout), dimension(n) :: M
            !f2py depend(n) M
            double precision, intent(out), dimension(n) :: Z
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
```

And the corresponding Python script:
```python
# file: test.py
import fibonacci
import numpy as np

n = 7

a = np.ones((n,), order='F', dtype=np.float64)
m = np.ones((n,), order='F', dtype=np.float64)

z = fibonacci.fib.series(n, a, m)

print(z)
print(z.dtype)
```

Which results in:
Now, running the python script above, we get:
```text
$ python test.py
[0. 1. 1. 2. 3. 5. 8.]
float64
```

### 3 - Mismatch in datatypes for the array with `intent(in)`

Re-using the Fortran code in section 1, we now provide an input array containing 64-bit real numbers when Fortran is expecting 32-bit real numbers:
```python
import fibonacci
import numpy as np

n = 7

a = np.ones((n,), order='F', dtype=np.float64)
m = np.ones((n,), order='F', dtype=np.float32)

z = fibonacci.fib.series(n, a, m)

print(a)
print(a.dtype)

print(m)
print(m.dtype)

print(z)
print(z.dtype)
```

Running this script yields the following output:
```text
$ python test.py
[1. 1. 1. 1. 1. 1. 1.]
float64
[ 2.  3.  3.  4.  5.  7. 10.]
float32
[0. 1. 1. 2. 3. 5. 8.]
float32
```

Surprisingly, the script terminates without any error despite the mismatch in datatypes for the input array `a`. This implies that `f2py` was able to cast the numpy array from 64-bit to 32-bit numbers. But, as can be seen the `dtype` of the array `a` is unchanged after the call of the subroutine `series`. The `dtype` of `m` is unchanged, while the returned array `z` is still containing 32-bit real numbers.

While this casting may be convenient, it is probably safer to provide the appropriate datatype in the first place, or to carry out the casting in Python beforehand, in order to avoid any surprise.

Noteworthy, providing an input array of integers would result in the same behaviour as above (i.e. `f2py` would cast the integers to real numbers).

### 4 - Mismatch in datatypes for the array with `intent(inout)`

Re-using again the Fortran code in section 1, we now provide an array with `intent(inout)` containing 64-bit real numbers when Fortran is expecting 32-bit real numbers:
```python
# file: test.py
import fibonacci
import numpy as np

n = 7

a = np.ones((n,), order='F', dtype=np.float32)
m = np.ones((n,), order='F', dtype=np.float64)

z = fibonacci.fib.series(n, a, m)


print(a)
print(a.dtype)

print(m)
print(m.dtype)

print(z)
print(z.dtype)
```

Running this script results in the following error:
```text
$ python test.py
Traceback (most recent call last):
  File "~/f2py_experiments/fib_datatype/4_real_mismatch_inout/test.py", line 10, in <module>
    z = fibonacci.fib.series(n, a, m)
ValueError: failed to initialize intent(inout) array -- expected elsize=4 but got 8
```

This time the mismatch in datatypes resulted in an error. Since the array `m` needs to be modified in place (because of the `intent(inout)` defined in Fortran), `f2py` prevents the implicit casting from 64-bit to 32-bit real numbers that was allowed when dealing with `intent(in)` arrays.

### 5 - Mismatch in datatypes for the array with `intent(in,out)`

`f2py` offers the possibility to define special intentions for variables that are specific to `f2py`. As introduced in section 6 of the [first experiment](../1_fib_array_intent), `!f2py intent(in,out)` can be used to return the `intent(inout)` variable, that would otherwise only be given as an input in a Python script.

This special `f2py` intent can be used to overcome the error encountered in section 4 (above). To do so, the Fortran source code presented in the foreword of this experiment needs to be modified to make use of the `intent(in,out)` for `M`:
```fortran
! file: fib.f90

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
            !f2py intent(in,out) M
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
```

Now, the following Python script is used to understand the behaviour for datatype mismatches with this special intention:

```python
# file: test.py
import fibonacci
import numpy as np

n = 7

a = np.ones((n,), order='F', dtype=np.float32)
m0 = np.ones((n,), order='F', dtype=np.float64)

print('The array "m0", its datatype, and its memory address before first call:')
print(m0)
print(m0.dtype)
print(hex(id(m0)))

print('___________ 1ST CALL ___________')

m1, z1 = fibonacci.fib.series(n, a, m0)

print('The array "m0", its datatype, and its memory address after first call:')
print(m0)
print(m0.dtype)
print(hex(id(m0)))

print('The array "m1", its datatype, and its memory address after first call:')
print(m1)
print(m1.dtype)
print(hex(id(m1)))

print('___________ 2ND CALL ___________')

m2, z2 = fibonacci.fib.series(n, a, m1)

print('The array "m0", its datatype, and its memory address after second call:')
print(m0)
print(m0.dtype)
print(hex(id(m0)))

print('The array "m1", its datatype, and its memory address after second call:')
print(m1)
print(m1.dtype)
print(hex(id(m1)))

print('The array "m2", its datatype, and its memory address after second call:')
print(m2)
print(m2.dtype)
print(hex(id(m2)))
```

Running this script yields:
```text
$ python test.py
The array "m0", its datatype, and its memory address before first call:
[1. 1. 1. 1. 1. 1. 1.]
float64
0x10147e080
___________ 1ST CALL ___________
The array "m0", its datatype, and its memory address after first call:
[1. 1. 1. 1. 1. 1. 1.]
float64
0x10147e080
The array "m1", its datatype, and its memory address after first call:
[ 2.  3.  3.  4.  5.  7. 10.]
float32
0x108909170
___________ 2ND CALL ___________
The array "m0", its datatype, and its memory address after second call:
[1. 1. 1. 1. 1. 1. 1.]
float64
0x10147e080
The array "m1", its datatype, and its memory address after second call:
[ 3.  5.  5.  7.  9. 13. 19.]
float32
0x108909170
The array "m2", its datatype, and its memory address after second call:
[ 3.  5.  5.  7.  9. 13. 19.]
float32
0x108909170
```

The variable `m0` is initialised as an array of ones with the datatype `np.float64` (i.e. double precision), and given to the Fortran subroutine which is expecting a simple precision real numbers array. Unlike in section 4, no error was raised after the call to the `series` subroutine. However, one can notice that after the first call, the variable `m0` was not modified, instead the modifications are only provided in the returned variable `m1`, located at a different memory address, and with single precision. In other words, the `intent(inout)` variable was not modified in place, and a new array was created and returned.

When we call the `series` subroutine a second time with this newly created array assigned to `m1`, we now notice that the values in `m1` are now modified after the second call, and they match the values found in the returned variable `m2`. In fact, the memory address of `m2` is the same as of `m1`, i.e. `m2` is an alias for `m1`. In other words, during the second call of the subroutine, the `intent(inout)` array was modified inplace, and the subroutine returned a pointer to the array given as an input in the call.

If only one variable `m` rather than the three variables `m1`, `m2`, and `m3` was used, once the initial array with `dtype=np.float64` is not referenced by any variable anymore (because `m` would be assigned the newly created array by `f2py` after the first call), its space in memory will automatically be released by Python. However, given the fact that the space it occupies in memory will only be released for reuse in the Python session (i.e. not reusable by another application running on the computer), this can become a problem when dealing with large arrays, where the Python application will monopolise twice the memory space it actually needs.

### 6 - Mismatch in datatype for the array with `intent(inplace)`

However, `f2py` features another special intention `intent(inplace)` which can be used to overcome the problem of an unnecessarily created array encountered in the first call of the `series` subroutine in section 5 above. Let's modify the Fortran source code to include this special intention instead of `intent(in,out)` previously used:
```fortran
! file: fib.f90

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
```

The following Python script can now be used to demonstrate the new behaviour with `!f2py intent(inplace)`:
```python
# file: test.py
import fibonacci
import numpy as np

n = 7

a = np.ones((n,), order='F', dtype=np.float32)
m = np.ones((n,), order='F', dtype=np.float64)

print('The array "m", its datatype, and its memory address before call:')
print(m)
print(m.dtype)
print(hex(id(m)))

print('___________ CALL ___________')

z = fibonacci.fib.series(n, a, m)

print('The array "m", its datatype, and its memory address after call:')
print(m)
print(m.dtype)
print(hex(id(m)))
```

Running the above script results in:
```text
$ python test.py
The array "m", its datatype, and its memory address before call:
[1. 1. 1. 1. 1. 1. 1.]
float64
0x10d29be40
___________ CALL ___________
The array "m", its datatype, and its memory address after call:
[ 2.  3.  3.  4.  5.  7. 10.]
float32
0x10d29be40
```

This time, the variable `m` is modified inplace: after the call to the `series` subroutine, both its datatype is cast to `np.float32`, and its items are modified accordingly as well.

Note, if there is no mismatch in datatypes for `intent(inout)` initially, the use of `intent(in,out)` or `intent(inplace)` is not required, as experienced in Sections 1 and 2. Sections 5 and 6 are only provided to better understand the behaviour of `f2py` and its special intentions for variables.

It is strongly recommended to use matching datatypes between the Python and the Fortran sides in order to avoid execution errors or memory issues due to unnecessarily created arrays.

### 4 - Lessons learnt

* As long as there is not mismatch in datatypes, `f2py` does not create unnecessary copies of arrays.
* If there is a datatype mismatch, `intent(in)` arrays are silently cast by `f2py` to the datatype the Fortran subroutine is expecting, while `intent(inout) arrays are not.
