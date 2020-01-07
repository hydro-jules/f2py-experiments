import fibonacci
import numpy as np


n = 7

a = np.ones((n,), order='F', dtype=np.float32)
m = np.ones((n,), order='F', dtype=np.int32)

z = fibonacci.fib.series(n, a, m)

print(a)
print(a.dtype)

print(m)
print(m.dtype)

print(z)
print(z.dtype)
