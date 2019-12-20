import fibonacci
import numpy as np

n = 8
a = np.array([1, 1, 1, 1, 1, 1, 1], order='F', dtype=float)

z = fibonacci.fib.series(a)
print(z)

z = fibonacci.fib.series(a, n=n)
print(z)
