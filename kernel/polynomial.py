
from math import log10 as log

import Flipper

# This class represents an integral polynomial. In various places we will assume that it is 
# irreducible and / or monic. We use this as an efficient way of representing an algebraic number.
# See symboliccomputation.py for more information.
class Polynomial(object):
	def __init__(self, coefficients):
		self.coefficients = coefficients[:min(i for i in range(len(coefficients)+1) if not any(coefficients[i:]))]
		self.height = max(abs(x) for x in self.coefficients) if self.coefficients else 1
		self.log_height = log(self.height)
		self.degree = len(self.coefficients) - 1
		self.algebraic_approximation = self.degree * self.height
		self.accuracy = 0
	
	def __iter__(self):
		return iter(self.coefficients)
	
	def __getitem__(self, item):
		return self.coefficients[item]
	
	def is_monic(self):
		return abs(self[-1]) == 1
	
	def increase_accuracy(self, accuracy):
		# Eventually we will find the interval ourselves, however at the minute sage is much faster so
		# we'll just use that.
		if self.accuracy < accuracy:
			self.algebraic_approximation = Flipper.kernel.symboliccomputation.algebraic_approximation_largest_root(self, accuracy)
			self.accuracy = accuracy
	
	def algebraic_approximate_leading_root(self, accuracy, power=1):
		# Returns an algebraic approximation of this polynomials leading root raised to the requested power
		# which is correct to at least accuracy decimal places.
		min_accuracy = int(log(self.degree)) + int(self.log_height) + 2 
		accuracy_needed = max(accuracy, min_accuracy)
		accuracy_requested = accuracy_needed + power * int(log(float(self.algebraic_approximation)) + 1)
		
		self.increase_accuracy(accuracy_requested)
		AA = self.algebraic_approximation**power
		assert(AA.interval.accuracy >= accuracy)  # Let's just make sure.
		return AA
	
	def companion_matrix(self):
		# Assumes that this polynomial is irreducible and monic.
		if not self.is_monic():
			raise Flipper.AssumptionError('Cannot construct companion matrix for non monic polynomial.')
		
		scale = -1 if self[-1] == 1 else 1
		return Flipper.Matrix([[(scale * self[i]) if j == self.degree-1 else 1 if j == i-1 else 0 for j in range(self.degree)] for i in range(self.degree)], self.degree)
