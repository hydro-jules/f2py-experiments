import fibonacci
import numpy as np


n = 7

a = np.ones((n,), order='F', dtype=np.float64)
m = np.ones((n,), order='F', dtype=np.float64)

z = fibonacci.fib.series(n, a, m)

print(z)
print(z.dtype)
