
from Flipper.Kernel.Error import ApproximationError

# The common denominator to amount to 
HASH_DENOMINATOR = 5

# This class represents a number in the interval (lower / 10^q, upper / 10^q). That is, a decimal correct to q places.
class Interval:
	def __init__(self, lower, upper, q):
		assert(lower < upper)
		self.lower = lower
		self.upper = upper
		self.q = q
	def __repr__(self):
		# Remember to take into account that the - sign uses a character.
		s = str(self.lower).zfill(self.q + (1 if self.lower >= 0 else 2))
		t = str(self.upper).zfill(self.q + (1 if self.upper >= 0 else 2))
		return '[%s.%s, %s.%s]' % (s[:len(s)-self.q], s[len(s)-self.q:], t[:len(t)-self.q], t[len(t)-self.q:])
	def change_denominator(self, new_q):
		d = new_q - self.q
		if d > 0:
			return Interval(self.lower * 10**d, self.upper * 10**d, new_q)
		elif d == 0:
			return self
		elif d < 0:
			return Interval(self.lower // 10**(-d), 1 + self.upper // 10**(-d), new_q)
	def __contains__(self, other):
		if isinstance(other, Interval):
			return self.lower < other.lower and other.upper < self.upper
		elif isinstance(other, int):
			return self.lower < other * 10**self.q < self.upper
		else:
			return NotImplemented
	def __neg__(self):
		return Interval(-self.upper, -self.lower, self.q)
	def __add__(self, other):
		if isinstance(other, Interval):
			common_precision = max(self.q, other.q)
			P, Q = self.change_denominator(common_precision), other.change_denominator(common_precision)
			new_lower = P.lower + Q.lower
			new_upper = P.upper + Q.upper
			return Interval(new_lower, new_upper, common_precision)
		elif isinstance(other, int):
			return Interval(self.lower + other * 10**self.q, self.upper + other * 10**self.q, self.q)
		else:
			return NotImplemented
	def __radd__(self, other):
		return self + other
	def __sub__(self, other):
		if isinstance(other, Interval):
			common_precision = max(self.q, other.q)
			P, Q = self.change_denominator(common_precision), other.change_denominator(common_precision)
			new_lower = P.lower - Q.upper
			new_upper = P.upper - Q.lower
			return Interval(new_lower, new_upper, common_precision)
		elif isinstance(other, int):
			return Interval(self.lower - other * 10**self.q, self.upper - other * 10**self.q, self.q)
		else:
			return NotImplemented
	def __rsub__(self, other):
		return -(self - other)
	def __mul__(self, other):
		if isinstance(other, Interval):
			common_precision = max(self.q, other.q)
			P, Q = self.change_denominator(common_precision), other.change_denominator(common_precision)
			values = [P.lower * Q.lower, P.upper * Q.lower, P.lower * Q.upper, P.upper * Q.upper]
			return Interval(min(values), max(values), 2*common_precision)
		elif isinstance(other, int):
			return Interval(self.lower * other, self.upper * other, self.q)
		else:
			return NotImplemented
	def __rmul__(self, other):
		return self * other
	def __div__(self, other):
		if isinstance(other, Interval):
			common_precision = max(self.q, other.q)
			P, Q = self.change_denominator(common_precision), other.change_denominator(common_precision)
			# !?! RECHECK THESE!
			values = [P.lower * 10**common_precision // Q.lower, P.upper * 10**common_precision // Q.lower, P.lower * 10**common_precision // Q.upper, P.upper * 10**common_precision // Q.upper]
			return Interval(min(values), max(values), common_precision)
		elif isinstance(other, int):
			return Interval(self.lower // other, self.upper // other, self.q)
		else:
			return NotImplemented
	def __rdiv__(self, other):
		if isinstance(other, int):
			pass
		else:
			return NotImplemented
	def __abs__(self):
		new_lower = 0
		new_upper = max(abs(self.lower), abs(self.upper))
		return Interval(new_lower, new_upper, self.q)
	def sign(self):
		if self.upper < 0:
			return -1
		elif self.lower > 0:
			return +1
		else:
			raise ApproximationError('Not enough precision available to determine sign.')
	def __lt__(self, other):
		return (self-other).sign() < 0
	def __gt__(self, other):
		return (self-other).sign() > 0
	def possibly_equal(self, other):
		try:
			(self-other).sign()
			return False
		except ApproximationError:
			return True
	def __hash__(self):
		return hash((self.lower, self.upper, self.q))

#### Some special Intervals we know how to build.

def interval_from_string(string):
	i, r = string.split('.') if '.' in string else (string, '')
	return Interval(int(i + r)-1, int(i + r)+1, len(r))

def interval_epsilon(integer, precision):
	return Interval(10**(precision - integer)-1, 10**(precision - integer)+1, precision)

if __name__ == '__main__':
	w = interval_from_string('1.14576001')
	x = interval_from_string('1.14576')
	y = interval_from_string('1.14571')
	z = interval_from_string('1.00000')
	a = interval_from_string('-1.200000')
	
	print(x)
	print(x.change_denominator(3))
	print(x.change_denominator(30))
	print(w)
	print(w.change_denominator(3))
	print(w.change_denominator(30))
	
	print(x > y)
	print(y > z)
	print(x +y > y + z)
	print(x * 3 > 3 * y)
	print(max([x,y,z]) == x)
	print(max([z,x,y]) == x)
	a = interval_from_string('1.4142135623730951')
	print(2 in (a * a))
	print(w > y)
	print(x.possibly_equal(w))
	print(not x.possibly_equal(y))
