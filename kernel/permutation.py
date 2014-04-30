
from itertools import permutations, combinations

import flipper

# Represents a permutation on N elements.
class Permutation(object):
	''' This represents a permutation in Sym(n). '''
	def __init__(self, permutation):
		assert(set(permutation) == set(range(len(permutation))))
		self.permutation = tuple(permutation)
	def __str__(self):
		return str(self.permutation)
	def __iter__(self):
		return iter(self.permutation)
	def __getitem__(self, index):
		return self.permutation[index]
	def __len__(self):
		return len(self.permutation)
	def __hash__(self):
		return hash(self.permutation)
	def __mul__(self, other):
		assert(len(self) == len(other))
		return Permutation([self[other[i]] for i in range(len(self))])
	# !?! Add in __pow__?
	def __eq__(self, other):
		return self.permutation == other.permutation
	def __ne__(self, other):
		return self.permutation != other.permutation
	def inverse(self):
		return Permutation([j for i in range(len(self)) for j in range(len(self)) if self[j] == i])
	def is_even(self):
		return len([(i, j) for j, i in combinations(range(len(self)), 2) if self[j] > self[i]]) % 2 == 0
	def order(self):
		ID = Id_Permutation(len(self))
		order = 1
		product = self
		while product != ID:
			product = product * self
			order += 1
		return order
	def embed(self, n):
		# Returns the permutation given by including this permutation into Sym(n). Assumes n >= len(self).
		if n < len(self):
			raise flipper.AssumptionError('Cannot embed permutation into smaller symmetric group.')
		return Permutation(list(self.permutation) + list(range(len(self), n)))
	def matrix(self):
		# Returns a matrix M such that M*e_i == e_{self[i]}.
		dim = len(self)
		return flipper.kernel.Matrix([[1 if i == self[j] else 0 for j in range(dim)] for i in range(dim)])

#### Some special Permutations we know how to build.

def Id_Permutation(n):
	return Permutation(range(n))

def cyclic_permutation(cycle, n):
	return Permutation([(cycle + i) % n for i in range(n)])

def all_permutations(n):
	return [Permutation(perm) for perm in permutations(range(n), n)]

def permutation_from_mapping(n, mapping, even):
	for P in all_permutations(n):
		if P.is_even() == even and all(P[source] == target for (source, target) in mapping):
			return P
	
	raise TypeError('Not a valid permutation.')

