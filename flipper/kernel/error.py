
''' A module for the various different errors that can be raised. '''

class AbortError(Exception):
	''' An exception for aborting computations with.
	
	This is thrown by clicking 'cancel' on a progress box. '''
	
	def __init__(self, message=None):
		super(AbortError, self).__init__()
		self.message = message
	def __str__(self):
		return str(self.message)

class ComputationError(Exception):
	''' An exception for when computations fail. '''
	
	def __init__(self, message=None):
		super(ComputationError, self).__init__()
		self.message = message
	def __str__(self):
		return str(self.message)

class AssumptionError(Exception):
	''' An exception for when an assumptions is false. '''
	
	def __init__(self, message=None):
		super(AssumptionError, self).__init__()
		self.message = message
	def __str__(self):
		return str(self.message)

class ApproximationError(Exception):
	''' An exception for when a calculation has been done to insufficient accuracy. '''
	
	def __init__(self, message=None):
		super(ApproximationError, self).__init__()
		self.message = message
	def __str__(self):
		return str(self.message)

class FatalError(Exception):
	''' An exception for when we reach something mathematically impossible.
	
	This indicates that the implementation of the algorithm differs from the theory. '''
	
	def __init__(self, message=None):
		super(FatalError, self).__init__()
		self.message = message
	def __str__(self):
		return str(self.message)

