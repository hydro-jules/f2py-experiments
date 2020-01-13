## Experimenting with the f2py and Fortran allocatable arrays

### 1 - Allocating memory for Fortran allocatable arrays with Fortran

The Fortran source code used in this third experiment is based on the section 5a of the [first experiment](../1_fib_array_intent) where the subroutine `series` takes four arguments: the dimension of the arrays `n`, an input array `A`, an input/output array `M`, and an output array `Z`. However, this time we define the array `M` as an allocatable array in the module `fib`: it will not be required to provide it as an argument in the new interface to the module, rather it will remain a variable internal to the module. 

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

The memory allocation of the allocatable array can also be done directly in Python. By reusing the Fortran code in the section 1 above, and once the static library is generated, the following Python script can be used: 
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

When run, it yields:
```text
$ python test.py
___________ 1ST CALL ___________
[0. 1. 1. 2. 3. 5. 8.]
[1. 2. 2. 3. 4. 6. 9.]
___________ 2ND CALL ___________
[0. 1. 1. 2. 3. 5. 8.]
[ 2.  4.  4.  6.  8. 12. 18.]
```

The same, expected, behaviour as in section 1 is now obtained without requiring the invocation of the `init` subroutine in Fortran. The internal array `M` declared in the Fortran module can be allocated simply by assigning it a numpy array of the appropriate datatype and dimension.

Note that when assigning and inspecting variables defined internally in the Fortran module, like above with the variable `M`, the default behaviour of `f2py` is to lower all cases as stated in its [documentation](https://numpy.org/devdocs/f2py/signature-file.html):
> In general, the contents of signature files is case-sensitive. When scanning Fortran codes and writing a signature file, F2PY lowers all cases automatically except in multiline blocks or when --no-lower option is used.

This means that accessing in Python the Fortran variable `M` in the module `fib` cannot be done using `fibonacci.fib.M`, but only `fibonacci.fib.m`, since this is how it is defined in the signature file.

### 3 - Exploring the memory address of the allocatable array

Once again, we reuse the Fortran file presented in the section 1 above, except that we add the following print statement at the very end of the `series` subroutine:
```fortran
print '(A, I15)', 'Memory address of "M" (Fortran): ', loc(M)
```

This allows to track the memory location of the array from the Fortran side.

Once the new static library is generated, we can use the following Python script to illustrate what happens to the memory address of the allocatable array when allocated/initialised, modified, or simply retrieved:
```python
import fibonacci
import numpy as np

n = 7

a = np.ones((n,), order='F', dtype=np.float32)

print('\n___ BEFORE MEMORY ALLOCATION ____')
mb = fibonacci.fib.m
print('Memory address of "mb" (Python): {}'.format(hex(id(mb))))
print('Values in "mb": {!s}'.format(mb))

print('\n___ AFTER MEMORY ALLOCATION _____')
ma = np.zeros((n,), order='F', dtype=np.float32)
fibonacci.fib.m = ma
m0 = fibonacci.fib.m
print('Memory address of "m0" (Python): {}'.format(hex(id(m0))))
print('Values in "m0": {!s}'.format(m0))

print('\n___________ 1ST CALL ___________')
z1 = fibonacci.fib.calc(n, a)
m1 = fibonacci.fib.m
print('Memory address of "m1" (Python): {}'.format(id(m1)))
print('Values in "m1": {!s}'.format(m1))

print('\n___________ 2ND CALL ___________')
z2 = fibonacci.fib.calc(n, a)
m2 = fibonacci.fib.m
print('Memory address of "m2" (Python): {}'.format(id(m2)))
print('Values in "m2": {!s}'.format(m2))

print('\n________ MODIFY ARRAYS _________')
m1[0] = -1.0
m2[1] = -2.0
fibonacci.fib.m[2] = -3.0

print('Values in "ma": {!s}'.format(ma))
print('Values in "M": {!s}'.format(fibonacci.fib.m))
print('Values in "m0": {!s}'.format(m0))
print('Values in "m1": {!s}'.format(m1))
print('Values in "m2": {!s}'.format(m2))

print('\n__ VIEWS OF THE SAME ARRAY ? __')
print('Does "m0" own its own memory? {}'.format(m0.base is None))
print('Does "m1" own its own memory? {}'.format(m1.base is None))
print('Does "m2" own its own memory? {}'.format(m2.base is None))

print('\n______ SHARING MEMORY ? _______')
print('Do "m0" and "m1" share memory? {}'.format(np.shares_memory(m0, m1)))
print('Do "m1" and "m2" share memory? {}'.format(np.shares_memory(m1, m2)))
print('Do "m0" and "m2" share memory? {}'.format(np.shares_memory(m0, m2)))

print('\n___ POINTING TO SAME DATA ? ___')
print('The area storing the first element of data for "m0": {}'.format(m0.__array_interface__['data'][0]))
print('The area storing the first element of data for "m1": {}'.format(m1.__array_interface__['data'][0]))
print('The area storing the first element of data for "m2": {}'.format(m2.__array_interface__['data'][0]))
print('The area storing the first element of data for "ma": {}'.format(ma.__array_interface__['data'][0]))
```

When the script is executed, the following outputs are given:
```text
$ python test.py

___ BEFORE MEMORY ALLOCATION ____
Memory address of "mb" (Python): 0x10e9fa058
Values in "mb": None

___ AFTER MEMORY ALLOCATION _____
Memory address of "m0" (Python): 0x10ecf5da0
Values in "m0": [0. 0. 0. 0. 0. 0. 0.]

___________ 1ST CALL ___________
Memory address of "M" (Fortran): 140256456790048
Memory address of "m1" (Python): 4666664080
Values in "m1": [1. 2. 2. 3. 4. 6. 9.]

___________ 2ND CALL ___________
Memory address of "M" (Fortran): 140256456790048
Memory address of "m2" (Python): 4666654112
Values in "m2": [ 2.  4.  4.  6.  8. 12. 18.]

________ MODIFY ARRAYS _________
Values in "ma": [0. 0. 0. 0. 0. 0. 0.]
Values in "M": [-1. -2. -3.  6.  8. 12. 18.]
Values in "m0": [-1. -2. -3.  6.  8. 12. 18.]
Values in "m1": [-1. -2. -3.  6.  8. 12. 18.]
Values in "m2": [-1. -2. -3.  6.  8. 12. 18.]

__ VIEWS OF THE SAME ARRAY ? __
Does "m0" own its own memory? True
Does "m1" own its own memory? True
Does "m2" own its own memory? True

______ SHARING MEMORY ? _______
Do "m0" and "m1" share memory? True
Do "m1" and "m2" share memory? True
Do "m0" and "m2" share memory? True

___ POINTING TO SAME DATA ? ___
The area storing the first element of data for "m0": 140256456790048
The area storing the first element of data for "m1": 140256456790048
The area storing the first element of data for "m2": 140256456790048
The area storing the first element of data for "ma": 140256457034512
```

Let's go through this, step by step, first looking at the values in the array `M`, then looking at the memory location of the array.

In terms of values:
* Before the memory allocation, the Fortran array `M` is retrieved using `fibonacci.fib.m`, but it returns None, because no memory was allocated for the allocatable array yet.

* After the memory allocation, the Fortran array `M` is retrieved using `fibonacci.fib.m`, `f2py` returns a numpy array which is assigned to the variable `m0`: an array now exists, it is of the right dimension, and it is initialised with zeros (as expected). 

* After calling the `calc` subroutine twice (see sections *"1st call"* and *"2nd call"* above), one can notice that the values in the array `M` are modified accordingly, i.e. it keeps memory of the state of `M` after the previous call to the subroutine `calc` to calculate its new state.

* By modifying successively `m1`, `m2`, and `M` directly (see section *"modify arrays"* above), and looking at the evolution of the values in `M`, `m0`, `m1`, and `m2`, we notice that when we modify an item in one, they are all modified at the same time. 

* Moreover, it is important to note that the values in `ma`, the original array that was used to allocate memory and to initialise with zeros the Fortran array `M`, is not modified. This means that `f2py` makes a copy of the data contained in the numpy array it is been given, rather than pointing to the inner data contained in the numpy array given. From a memory standpoint, it is then preferable to favour the allocation of the memory with Fortran rather than with Python.

Now, we can explore how the memory addresses evolve. First, we can see that each time we retrieve the Fortran array `M` using `fibonacci.fib.m`, it has a new memory address in Python (see `id(m0)`, `id(m1)`, and `id(m2)`), i.e. it instantiates a new object rather than aliasing an existing one. On the other hand, the memory address of `M` in Fortran is the same between the two calls.

After modifying one item in `m1`, `m2`, and `M`, we saw that `M`, `m0`, `m1`, and `m2` were all modified as a result. So why do `m0`, `m1`, and `m2` have different memory addresses then? One could assume that `f2py` returns a [view](https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.view.html) of the same numpy array. But, by looking at the [base attribute](https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.base.html#numpy.ndarray.base) of these numpy arrays (see section *"views of the same array?"* above), we can see that all of them own their own memory, so they are not views because a view has a base evaluating to another numpy array (not `None`). 

However, when using the [numpy.shares_memory](https://docs.scipy.org/doc/numpy/reference/generated/numpy.shares_memory.html) method, it indicates that they do share memory. This is confirmed when looking at the item [data](https://docs.scipy.org/doc/numpy/reference/arrays.interface.html#__array_interface__) in the array interface of each of these arrays: their first element of data are all at same memory location. This explains why they are all modified when one of them is modified. Moreover, this memory location is indeed the same as the memory location of the Fortran array. So, it proves that `f2py` does not create unnecessary copies of the data.

The item data for the variable `ma` also confirms that its inner data array is distinct from the inner data array of the Fortran array `M`. This is why it remains pristine despite the two calls to the `calc` subroutine, and the subsequent manual modifications of it.

To wrap up, `f2py` returns a new numpy.ndarray each time the Fortran array `M` is inspected in Python, for numpy it is not a view of another array (according to the base attribute), yet it behaves just like one because it shares the memory of the inner data array it points to (according to the item data in the \_\_array_interface\_\_ dictionary).

### 4 - Lessons learnt

* Allocatable arrays can be allocated memory and initialised with Python by assigning it a numpy array.
* When inspecting an array defined only in Fortran, `f2py` returns a new numpy array object, but the inner data array in this object points to the memory area of the array allocated in Fortran.
* It is preferable to allocate memory for allocatable arrays in Fortran because it avoids the creation of a numpy array in Python only for its data to be copied to the Fortran array.
