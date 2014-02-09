
import Flipper

algebraic_approximation_from_string = Flipper.Kernel.AlgebraicApproximation.algebraic_approximation_from_string

def main():
	x = algebraic_approximation_from_string('1.4142135623730951', 2, 2)
	y = algebraic_approximation_from_string('1.41421356237', 2, 2)
	z = algebraic_approximation_from_string('1.000000', 2, 2)
	
	if not (z != y):
		return False
	if not (x == y):
		return False
	if not (x + y == x + x):
		return False
	if not (x * x == 2):
		return False
	if not (y * y == 2):
		return False
	if not (y * y + x == 2 + x):
		return False
	if not (y * (y + y) == 4):
		return False
	if not (x * x == y * y):
		return False
	if not ((x + x) > 0):
		return False
	if not (-(x + x) < 0):
		return False
	
	return True

if __name__ == '__main__':
	print(main())