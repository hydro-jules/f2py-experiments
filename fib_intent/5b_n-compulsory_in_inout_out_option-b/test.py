import fibonacci
import numpy as np


n = 7

a = np.zeros((n,), order='F', dtype=np.float32) + 1
m = np.zeros((n,), order='F', dtype=np.float32) + 1
print(m)

z = fibonacci.fib.series(n, a, m)

print(z)
print(m)
