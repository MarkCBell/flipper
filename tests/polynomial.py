
import Flipper

def main():
	f = Flipper.Polynomial([-2, 0, 1])
	try:
		AA = f.algebraic_approximate_leading_root(10)
		if (AA * AA) != 2:
			print(f, AA)
			return False
	except ImportError:
		print('Symbolic computation library required but unavailable, test skipped.')
	
	try:
		BB = f.algebraic_approximate_leading_root(10, power=2)
		if BB != 2:
			print(f, BB)
			return False
	except ImportError:
		print('Symbolic computation library required but unavailable, test skipped.')
	
	return True

if __name__ == '__main__':
	print(main())
