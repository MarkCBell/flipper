
from sage.all import QQ, NumberField

def test(polynomial_coefficients, max_degree=10):
	[x] = QQ['x'].gens()
	# Build the polynomial.
	f = sum(coeff * x**index for index, coeff in enumerate(polynomial_coefficients))
	# and the corresponding number field.
	K = NumberField(f, 'y')
	[y] = K.gens()
	G = K.unit_group()
	print(G(y))
	
	roots = []
	for i in range(2, max_degree):
		try:
			y.nth_root(i)
			roots.append(i)
		except ValueError:
			pass
	
	return roots

if __name__ == '__main__':
	print(test([1, -7, 1], 100))
	print(test([1, -3, 1], 100))
	print(test([-1, -1, 1], 100))

