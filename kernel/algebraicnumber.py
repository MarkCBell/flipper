
from math import log10 as log

import flipper

class AlgebraicNumber(object):
	def __init__(self, polynomial, interval, degree=None):
		# Assumes that polynomial has exactly one root in interval.
		assert(isinstance(polynomial, flipper.kernel.Polynomial))
		assert(isinstance(interval, flipper.kernel.Interval))
		self.polynomial = polynomial
		self.interval = interval
		self.degree = degree if degree is not None else self.polynomial.degree
		self.height = self.polynomial.height + 2 * log(self.degree)
		
		if self.polynomial.num_roots(self.interval) != 1:
			raise flipper.AssumptionError('%d roots in interval, not one.' % self.polynomial.num_roots(self.interval))
	
	def __repr__(self):
		return '%s' % str(self.interval)
	
	def algebraic_approximation(self, accuracy=0):
		accuracy_needed = int(self.height) + int(log(self.degree)) + 2
		
		accuracy = max(accuracy, accuracy_needed)
		if self.interval.accuracy < accuracy:
			self.interval = self.polynomial.converge_iterate(self.interval, accuracy)
		
		return flipper.kernel.AlgebraicApproximation(self.interval, self.degree, self.height)

