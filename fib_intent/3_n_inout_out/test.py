import fibonacci
import numpy as np


n = 7
m = np.array([1, 1, 1, 1, 1, 1, 1], order='F', dtype=np.float32)

print('First call of the subroutine:')
z = fibonacci.fib.series(m, n=n)
print(m)

print('Second call of the subroutine:')
z = fibonacci.fib.series(m, n=n)
print(m)
