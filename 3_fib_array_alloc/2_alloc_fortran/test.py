import fibonacci
import numpy as np


n = 7

a = np.ones((n,), order='F', dtype=np.float32)

# allocate and initialise the internal allocatable array 'M' with Python
fibonacci.fib.m = np.zeros((n,), order='F', dtype=np.float32)

print('___________ 1ST CALL ___________')
# call the wrapper 'calc' a first time
z1 = fibonacci.fib.calc(n, a)

print(z1)
print(fibonacci.fib.m)

print('___________ 2ND CALL ___________')
# call the wrapper 'calc' a second time
z2 = fibonacci.fib.calc(n, a)

print(z2)
print(fibonacci.fib.m)
