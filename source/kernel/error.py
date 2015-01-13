
''' A module for the various different errors that can be raised. '''

class AbortError(Exception):
	''' An exception for aborting computations with.
	
	This is thrown by clicking 'cancel' on a progress box. '''
	
	def __init__(self, code=None):
		super(AbortError, self).__init__()
		self.code = code
	def __str__(self):
		return str(self.code)

class ComputationError(Exception):
	''' An exception for when computations fail. '''
	
	def __init__(self, code=None):
		super(ComputationError, self).__init__()
		self.code = code
	def __str__(self):
		return str(self.code)

class AssumptionError(Exception):
	''' An exception for when an assumptions is false. '''
	
	def __init__(self, code=None):
		super(AssumptionError, self).__init__()
		self.code = code
	def __str__(self):
		return str(self.code)

class ApproximationError(Exception):
	''' An exception for when a calculation has been done to insufficient accuracy. '''
	
	def __init__(self, code=None):
		super(ApproximationError, self).__init__()
		self.code = code
	def __str__(self):
		return str(self.code)
