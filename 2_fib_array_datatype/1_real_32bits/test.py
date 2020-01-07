import fibonacci
import numpy as np


n = 7

a = np.ones((n,), order='F', dtype=np.float32)
m = np.ones((n,), order='F', dtype=np.float32)

z = fibonacci.fib.series(n, a, m)

print(z)
print(z.dtype)
