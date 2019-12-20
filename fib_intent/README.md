## Experimenting with the different Fortran and f2py intent options for subroutine arguments

### 1 - Simple case with one input integer and one output array

The Fortran subroutine that we will use takes only the required length `n` of the Fibonacci series, and it returns this series as an array:

```fortran
! file: fib.f90

module fib
    contains
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
end module fib
```

From this Fortran source code, we will use `numpy.f2py` to create a static library that we will import in Python. First, we create a signature file to understand what interface to the Fortran code will be known on the Python side:
```bash
python -m numpy.f2py -m fibonacci -h fib.pyf --overwrite-signature fib.f90
```

The created signature file looks like this:
```
! file: fib.pyf

python module fibonacci ! in 
    interface  ! in :fibonacci
        module fib ! in :fibonacci:fib.f90
            subroutine series(n,z) ! in :fibonacci:fib.f90:fib
                integer intent(in) :: n
                real dimension(n),intent(out),depend(n) :: z
            end subroutine series
        end module fib
    end interface 
end python module fibonacci
```

We can see that the module to be imported in Python is named `fibonacci`, that it contains a Fortran module named `fib`, itself containing a Fortran subroutine named `series` that takes two arguments, an integer and an array of real numbers.

Now, we compile the Fortran program using the unmodified signature file that we have just created. The following instruction will generate a static library fibonacci.so:
```bash
python -m numpy.f2py -c fib.pyf fib.f90


Finally we can use this static library and import it just like a normal Python module:

```python
# file: test.py
import fibonacci

n = 11
z = fibonacci.fib.series(n)
print(z)
```

We can notice that the array with `intent(out)` is not given as an argument to the function call, instead it is returned from the function call.

If we run this python, this will output the following numpy array:
```
[ 0.  1.  1.  2.  3.  5.  8. 13. 21. 34. 55.]
```

### 2 - Providing an array as input

The Fibonacci subroutine is now modified to take another input, a numpy array of dimension `n` that will be added to the generated Fibonacci series. This demonstrates a behaviour of `f2py` with array dimensions.

```fortran
! file: fib.f90

module fib
    contains
        subroutine series(n, A, Z)
            ! calculates first n elements of the Fibonacci series
            ! and adds the input array to it
            implicit none

            integer, intent(in) :: n
            real, intent(in), dimension(n) :: A
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

            do i = 1, n
                Z(i) = Z(i) + A(i)
            end do

        end subroutine series
end module fib
```

When generating the signature file, we can see that `f2py` created an interface where the dimension `n` becomes an optional argument, and it is inferred from the dimension of the input array `a`.

```
! file: fib.pyf

python module fibonacci ! in 
    interface  ! in :fibonacci
        module fib ! in :fibonacci:fib.f90
            subroutine series(n,a,z) ! in :fibonacci:fib.f90:fib
                integer, optional,intent(in),check(len(a)>=n),depend(a) :: n=len(a)
                real dimension(n),intent(in) :: a
                real dimension(n),intent(out),depend(n) :: z
            end subroutine series
        end module fib
    end interface 
end python module fibonacci
```

Once the static library is compiled, we can use this interface to call the Fortran subroutine. Note that we use the keyword argument `order='F'` to create a Fortran-contiguous array that will be given as the input. The default behaviour of `numpy` is to create a C-contiguous array, so is not given a Fortran-contiguous array, `f2py` may create a copy of this array, which can become a problem for large multi-dimensional arrays. So it is safer to specify the order explicitly. 

```python
import fibonacci
import numpy as np

n = 7
a = np.array([1, 1, 1, 1, 1, 1, 1], order='F', dtype=float)

# first option: let f2py infer the value of 'n' from the dimension of 'a'
print('First option:')
z = fibonacci.fib.series(a)
print(z)

# second option: explicit set the value of 'n'
# and let f2py check if the dimension of 'a' is compatible with 'n'
print('Second option:')
z = fibonacci.fib.series(a, n=n)
print(z)
```

Both of the options above work and return a numpy array of dinension 'n':

```
First option:
[1. 2. 2. 3. 4. 6. 9.]
Second option:
[1. 2. 2. 3. 4. 6. 9.]
```

However, if the value of 'n' given (e.g. n=8) is incompatible (because length of a is 7 < 8), an error is raised.

### 3 - Providing an array as input and output

In the previous example, the arguments of the function call are with intent(in), which means that they cannot be modified. `f2py` can also work with the intent(inout) of Fortran so that the given variables can be used and changed in the Fortran subroutine.

```fortran
! file: fib.f90

module fib
    contains
        subroutine series(n, M, Z)
            ! calculates first n elements of the Fibonacci series
            ! and adds it to the existing input/output array
            implicit none

            integer, intent(in) :: n
            real, intent(inout), dimension(n) :: M
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

            do i = 1, n
                M(i) = M(i) + Z(i)
            end do

        end subroutine series
end module fib
```

Again, the signature file shows that f2py turned the argument `n` as optional:

```
! file: fib.pyf

python module fibonacci ! in 
    interface  ! in :fibonacci
        module fib ! in :fibonacci:fib.f90
            subroutine series(n,m,z) ! in :fibonacci:fib.f90:fib
                integer, optional,intent(in),check(len(m)>=n),depend(m) :: n=len(m)
                real dimension(n),intent(inout) :: m
                real dimension(n),intent(out),depend(n) :: z
            end subroutine series
        end module fib
    end interface 
end python module fibonacci
```

When the static library is called in Python, we can see that the argument with intent(inout) initial values are used and modified:
```python
import fibonacci
import numpy as np


n = 7
m = np.array([1, 1, 1, 1, 1, 1, 1], order='F', dtype=np.float32)

print('First call of the subroutine:')
z = fibonacci.fib.series(m, n=n)
print(m)

print('Second call of the subroutine:')
z = fibonacci.fib.series(m, n=n)
print(m)
```

If we run the script below, we can see that each time the subroutine `series` is called, the variable `m` is updated (i.e. the Fibonacci series is added to its existing values):
```
First call of the subroutine:
[1. 2. 2. 3. 4. 6. 9.]
Second call of the subroutine:
[ 1.  3.  3.  5.  7. 11. 17.]
```

### 4 - Using intent(in), intent(inout), and intent(out), all at once

Now, let's create a Fortran subroutine that takes a variable for each type of intent:

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
            real, intent(inout), dimension(n) :: M
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

            do i = 1, n
                M(i) = M(i) + A(i) + Z(i)
            end do

        end subroutine series
end module fib
```

The signature file (below) shows that `f2py` is, again, inferring the value of `n`, and it uses the first array argument of the call to the subroutine to do so (i.e. the input array `a`). If the intent(inout) array `m` were specified before the input array `a`, `m` would be used to infer the value of `n` instead.

```
! file: fib.pyf

python module fibonacci ! in 
    interface  ! in :fibonacci
        module fib ! in :fibonacci:fib.f90
            subroutine series(n,a,m,z) ! in :fibonacci:fib.f90:fib
                integer, optional,intent(in),check(len(a)>=n),depend(a) :: n=len(a)
                real dimension(n),intent(in) :: a
                real dimension(n),intent(inout),depend(n) :: m
                real dimension(n),intent(out),depend(n) :: z
            end subroutine series
        end module fib
    end interface 
end python module fibonacci
```

### 5 - Making the dimension of the arrays a required argument

If one wants to make sure that the subroutine works on arrays of the expected dimension, rather than letting the subroutine infer the dimension from the first array given, two options are possible.

#### a - By modifying the Fortran source code

To help `f2py` infer the right interface for the Fortran subroutine, comment lines starting with !f2py can be used. Because they are comments, they will be ignored by a Fortran compiler, but they will be read and used by `f2py`. By indicating that all the array arguments depend on the value of the variable `n`, the variable `n` cannot be optional anymore, and `f2py` will now expect for `n` to be provided when calling the subroutine.

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

            do i = 1, n
                M(i) = M(i) + A(i) + Z(i)
            end do

        end subroutine series
end module fib
```

As can be seen in the signature file, the variable `n` is not flagged as optional anymore:
```
! file: fib.pyf

python module fibonacci ! in 
    interface  ! in :fibonacci
        module fib ! in :fibonacci:fib.f90
            subroutine series(n,a,m,z) ! in :fibonacci:fib.f90:fib
                integer intent(in) :: n
                real dimension(n),intent(in),depend(n) :: a
                real dimension(n),intent(inout),depend(n) :: m
                real dimension(n),intent(out),depend(n) :: z
            end subroutine series
        end module fib
    end interface 
end python module fibonacci
```

#### b - By changing the signature file

If the Fortran source code cannot be modified to add the `f2py` comments, the fact that we are generating the static library in two steps allows us to tailor the interface to the Fortran subroutine. After the signature file is generated, and before the static library is compiled, the inferred interface can be adjusted manually directly in the signature file.

If the automatically generated signature file is as follows:
```
! file fib.pyf

python module fibonacci ! in 
    interface  ! in :fibonacci
        module fib ! in :fibonacci:fib.f90
            subroutine series(n,a,m,z) ! in :fibonacci:fib.f90:fib
                integer, optional,intent(in),check(len(a)>=n),depend(a) :: n=len(a)
                real dimension(n),intent(in) :: a
                real dimension(n),intent(inout),depend(n) :: m
                real dimension(n),intent(out),depend(n) :: z
            end subroutine series
        end module fib
    end interface 
end python module fibonacci
```

And the modified signature file is as follows:
```
! file: fib_mod.pyf

python module fibonacci ! in 
    interface  ! in :fibonacci
        module fib ! in :fibonacci:fib.f90
            subroutine series(n,a,m,z) ! in :fibonacci:fib.f90:fib
                integer intent(in) :: n
                real dimension(n),intent(in),depend(n) :: a
                real dimension(n),intent(inout),depend(n) :: m
                real dimension(n),intent(out),depend(n) :: z
            end subroutine series
        end module fib
    end interface 
end python module fibonacci
```

The modified signature file can now be used to teach `f2py` what the interface to the subroutine should be, without never having to modify the source code.
