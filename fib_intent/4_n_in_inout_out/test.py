import fibonacci
import numpy as np


n = 7

a = np.array([1, 1, 1, 1, 1, 1, 1], order='F', dtype=float)
m = np.array([1, 1, 1, 1, 1, 1, 1], order='F', dtype=np.float32)

z = fibonacci.fib.series(a, m, n=n)

print(z)
print(z.dtype)

print(m)
