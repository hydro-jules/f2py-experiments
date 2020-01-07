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
