import fibonacci
import numpy as np


n = 7

a = np.zeros((n,), order='F', dtype=np.float32) + 1
m = np.zeros((n,), order='F', dtype=np.float32) + 1

m_, z = fibonacci.fib.series(n, a, m)

print('The array "m" and its memory address')
print(m)
print(hex(id(m)))

print('The array "m_" and its memory address')
print(m_)
print(hex(id(m_)))
