import fibonacci
import numpy as np


n = 7

a = np.ones((n,), order='F', dtype=np.float32)

print('\n___ BEFORE MEMORY ALLOCATION ____')
mb = fibonacci.fib.m
print('Memory address of "mb" (Python): {}'.format(id(mb)))
print('Values in "mb": {!s}'.format(mb))

print('\n___ AFTER MEMORY ALLOCATION _____')
ma = np.zeros((n,), order='F', dtype=np.float32)
fibonacci.fib.m = ma
m0 = fibonacci.fib.m
print('Memory address of "m0" (Python): {}'.format(id(m0)))
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
