
import Flipper

def main():
	f = Flipper.Polynomial([-2, 0, 1])
	AA = f.algebraic_approximate_leading_root(10)
	if (AA * AA) != 2:
		print(f, AA)
		return False
	
	BB = f.algebraic_approximate_leading_root(10, power=2)
	if BB != 2:
		print(f, BB)
		return False
	
	return True

if __name__ == '__main__':
	print(main())
