
from Flipper.Kernel.Error import ApproximationError

# This class represents rationals of the form p / 10^q. That is, decimals correct to q places.
class Decimal:
	def __init__(self, p, q):
		self.p = p
		self.q = q
	def __repr__(self):
		s = str(self.p).zfill(self.q + (1 if self.p >= 0 else 2))  # Take into account that the - sign uses a character.
		return '%s.%s' % (s[:len(s)-self.q], s[len(s)-self.q:])
		# return '%s*10^-%s' % (self.p, self.q)
	def demote(self, new_q):
		# Assumes that we are requesting less precision.
		if new_q > self.q:
			raise ApproximationError
		
		return Decimal(self.p // 10**(self.q - new_q), new_q)
	def negate(self):
		return Decimal(-self.p, self.q)
	def __add__(self, other):
		if isinstance(other, Decimal):
			common_precision = min(self.q, other.q)
			return Decimal(self.demote(common_precision).p + other.demote(common_precision).p, common_precision)
		elif isinstance(other, int):
			return Decimal(self.p + other * 10**self.q, self.q)
		return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, Decimal):
			common_precision = min(self.q, other.q)
			return Decimal(self.demote(common_precision).p - other.demote(common_precision).p, common_precision)
		elif isinstance(other, int):
			return Decimal(self.p - other * 10**self.q, self.q)
		return NotImplemented
	def __rsub__(self, other):
		return (self - other).negate()
	def __mul__(self, other):
		if isinstance(other, Decimal):
			common_precision = min(self.q, other.q)
			return Decimal(self.demote(common_precision).p * other.demote(common_precision).p // 10**common_precision, common_precision)
		elif isinstance(other, int):
			return Decimal(self.p * other, self.q)
		return NotImplemented
	def __rmul__(self, other):
		return self * other
	def sign(self):
		return -1 if self.p < 0 else 0 if self.p == 0 else +1
	def __lt__(self, other):
		return (self-other).sign() < 0
	def __eq__(self, other):
		return (self-other).sign() == 0
	def __gt__(self, other):
		return (self-other).sign() > 0

#### Some special Decimals we know how to build.

def decimal_from_string(string):
	i, r = string.split('.') if '.' in string else (string, '')
	return Decimal(int(i + r), len(r))

if __name__ == '__main__':
	w = decimal_from_string('1')
	x = decimal_from_string('1.14576')
	y = decimal_from_string('1.14571')
	z = decimal_from_string('1.')
	
	print(x - x == 0)
	print(x - y == 0)
	print(y + x == x + y)
	print(x * 3)
	print(sorted([y, x, z]))
	print(max([x,y,z]))
	print(max([z,x,y]))
	a = decimal_from_string('1.4142135623730951')
	print(a * a)
	print(a * a == 2)
	print()

