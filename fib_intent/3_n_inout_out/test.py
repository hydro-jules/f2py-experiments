import fibonacci
import numpy as np


n = 7
m = np.ones((n,), order='F', dtype=np.float32)

print('First call of the subroutine:')
z = fibonacci.fib.series(m, n=n)
print(m)

print('Second call of the subroutine:')
z = fibonacci.fib.series(m, n=n)
print(m)
