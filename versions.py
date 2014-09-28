
class Version(object):
	def __init__(self, major, minor, sub):
		assert(isinstance(major, int))
		assert(isinstance(minor, int))
		assert(isinstance(sub, int))
		
		self.major = major
		self.minor = minor
		self.sub = sub
		self.tuple = (self.major, self.minor, self.sub)
	
	def __repr__(self):
		return '%d.%d.%d' % self.tuple
	
	def __lt__(self, other):
		if isinstance(other, Version):
			return self.tuple < other.tuple
		else:
			return NotImplemented
	def __eq__(self, other):
		if isinstance(other, Version):
			return self.tuple == other.tuple
		else:
			return NotImplemented
	def __ne__(self, other):
		if isinstance(other, Version):
			return self.tuple != other.tuple
		else:
			return NotImplemented
	def __gt__(self, other):
		if isinstance(other, Version):
			return self.tuple > other.tuple
		else:
			return NotImplemented
	def __le__(self, other):
		return self < other or self == other
	def __ge__(self, other):
		return self > other or self == other

version = Version(0, 5, 3)

