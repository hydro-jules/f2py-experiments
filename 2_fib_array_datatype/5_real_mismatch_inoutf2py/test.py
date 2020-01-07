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
