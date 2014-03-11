
# An exception for aborting computations with. This is thrown by clicking 'cancel' on a progress box.
class AbortError(Exception):
	def __init__(self, code=None):
		super(AbortError, self).__init__()
		self.code = code
	def __str__(self):
		return repr(self.code)

# An exception for when computations fail.
class ComputationError(Exception):
	def __init__(self, code=None):
		super(ComputationError, self).__init__()
		self.code = code
	def __str__(self):
		return repr(self.code)

# An exception for when a function notices that one of its assumptions is false.
class AssumptionError(Exception):
	def __init__(self, code=None):
		super(AssumptionError, self).__init__()
		self.code = code
	def __str__(self):
		return repr(self.code)

class ApproximationError(Exception):
	def __init__(self, code=None):
		super(ApproximationError, self).__init__()
		self.code = code
	def __str__(self):
		return repr(self.code)
