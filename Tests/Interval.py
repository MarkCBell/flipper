
from Flipper.Kernel.Interval import interval_from_string

def main():
	w = interval_from_string('1.14576001')
	x = interval_from_string('1.14576')
	y = interval_from_string('1.14571')
	z = interval_from_string('1.00000')
	a = interval_from_string('-1.200000')
	b = interval_from_string('1.4142135623730951')
	
	if not (x > y):
		return False
	if not (y > z):
		return False
	if not (x +y > y + z):
		return False
	if not (x * 3 > 3 * y):
		return False
	if not (max([x,y,z]) == x):
		return False
	if not (max([z,x,y]) == x):
		return False
	if not (sorted([x,y,z,a]) == [a, z, y, x]):
		return False
	if not (w > y):
		return False
	if not (2 in (b * b)):
		return False
	
	return True

if __name__ == '__main__':
	print(main())