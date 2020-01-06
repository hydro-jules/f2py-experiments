import fibonacci
import numpy as np


n = 7
a = np.ones((n,), order='F', dtype=np.float32)

# first option: let f2py infer the value of 'n' from the dimension of 'a'
print('First option:')
z = fibonacci.fib.series(a)
print(z)

# second option: explicit set the value of 'n'
# and let f2py check if the dimension of 'a' is compatible with 'n'
print('Second option:')
z = fibonacci.fib.series(a, n=n)
print(z)
