
from fractions import Fraction
from math import log10 as log

import Flipper

# In Python3 we can just do round(fraction, precision) however this
# doesn't exist in Python2 so we recreate it here. 
def round_fraction(fraction, precision):
	shift = 10**precision
	shifted = fraction * shift
	floor, remainder = divmod(shifted.numerator, shifted.denominator)
	
	if remainder * 2 < shifted.denominator or (remainder * 2 == shifted.denominator and floor % 2 == 0):
		numerator = floor
	else:
		numerator = floor + 1
	
	return (numerator, precision)

class Polynomial(object):
	def __init__(self, coefficients):
		self.coefficients = coefficients
		self.height = max(abs(x) for x in self.coefficients) if self.coefficients else 1
		self.log_height = log(self.height)
		self.degree = len(self.coefficients) - 1
		self.old_root = None
		self.root = Fraction(self.height * self.degree, 1)
	
	def __call__(self, other):
		return sum(coefficient * other**index for index, coefficient in enumerate(self.coefficients))
	
	def derivative(self):
		return Polynomial([index * coefficient for index, coefficient in enumerate(self.coefficients)][1:]) 
	
	def find_leading_root(self, precision):
		f = self
		f_prime = self.derivative()
		while self.old_root is None or log(abs(self.root - self.old_root)) > -precision:
			self.old_root, self.root = self.root, self.root - f(self.root) / f_prime(self.root)
		
		return self.root
	
	def algebraic_approximate_leading_root(self, precision=None, power=1):
		# Returns an algebraic approximation of this polynomials leading root
		# which is correct to at least precision decimal places.
		numerator, precision = round_fraction(self.find_leading_root(precision), 2*precision)
		
		return Flipper.kernel.algebraicapproximation.algebraic_approximation_from_fraction(numerator, precision, self.degree, self.log_height)


if __name__ == '__main__':
	f = Polynomial([-2, 0, 1])
	print(f.find_leading_root(10))
	print(f.algebraic_approximate_leading_root(10))
