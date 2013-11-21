
# An exception for aborting computations with. This is thrown by clicking 'cancel' on a progress box.

class AbortError(Exception):
	def __init__(self, code=None):
		self.code = code
	def __str__(self):
		return repr(self.code)

# An exception for when computations fail.

class ComputationError(Exception):
	def __init__(self, code=None):
		self.code = code
	def __str__(self):
		return repr(self.code)