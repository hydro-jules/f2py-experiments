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
print('Values in "m0": {!s}'.format(m0))
print('Values in "m1": {!s}'.format(m1))
print('Values in "m2": {!s}'.format(m2))
print('Values in "m_": {!s}'.format(m_))

print('\n_________ MODIFY "m2" __________')
m2[1] = 0.0
print('Values in "M": {!s}'.format(fibonacci.fib.m))
print('Values in "m0": {!s}'.format(m0))
print('Values in "m1": {!s}'.format(m1))
print('Values in "m2": {!s}'.format(m2))
print('Values in "m_": {!s}'.format(m_))

print('\n_________ MODIFY "M" ___________')
fibonacci.fib.m[2] = 0.0
print('Values in "M": {!s}'.format(fibonacci.fib.m))
print('Values in "m0": {!s}'.format(m0))
print('Values in "m1": {!s}'.format(m1))
print('Values in "m2": {!s}'.format(m2))
print('Values in "m_": {!s}'.format(m_))
