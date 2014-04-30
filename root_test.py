
from sage.all import *

R = ZZ['x']
[x] = R.gens()
f = x**2 - x + 1
K = NumberField(f, 'y')
[y] = K.gens()

for i in range(2, 100):
	try:
		a = y.nth_root(i)
		print(i)
	except ValueError:
		pass

