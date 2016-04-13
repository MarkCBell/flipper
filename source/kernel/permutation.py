
''' A module for representing permutations in Sym(n).

Provides one class: Permutation.

There are also two helper functions: Id_permutation and cyclic_permutation. '''

import flipper

from itertools import permutations, combinations

class Permutation(object):
	''' This represents a permutation in Sym(n). '''
	def __init__(self, permutation):
		assert(isinstance(permutation, (list, tuple)))
		assert(all(isinstance(entry, flipper.IntegerType) for entry in permutation))
		assert(set(permutation) == set(range(len(permutation))))
		
		self.permutation = tuple(permutation)
	def __repr__(self):
		return str(self)
	def __str__(self):
		return self.compressed_string()
	def compressed_string(self):
		''' Return this permutation as a single concatenated string. '''
		
		return ''.join(str(p) for p in self.permutation)
	
	def __iter__(self):
		return iter(self.permutation)
	def __call__(self, index):
		return self.permutation[index]
	def __len__(self):
		return len(self.permutation)
	def __hash__(self):
		return hash(self.permutation)
	def __mul__(self, other):
		assert(isinstance(other, Permutation))
		assert(len(self) == len(other))
		
		return Permutation([self(other(i)) for i in range(len(self))])
	def __eq__(self, other):
		return self.permutation == other.permutation
	def __ne__(self, other):
		return not (self.permutation == other.permutation)
	def inverse(self):
		''' Return the inverse of this permutation. '''
		
		return Permutation([j for i in range(len(self)) for j in range(len(self)) if self(j) == i])
	def is_even(self):
		''' Return if this permutation is even. '''
		
		return len([(i, j) for j, i in combinations(range(len(self)), 2) if self(j) > self(i)]) % 2 == 0
	def order(self):
		''' Return the order of this permutation. '''
		
		id_perm = id_permutation(len(self))
		order = 1
		product = self
		while product != id_perm:
			product = product * self
			order += 1
		return order
	def embed(self, new_n):
		''' Return the inclusion of this permutation into Sym(new_n).
		
		new_n must be at least len(self). '''
		
		assert(new_n >= len(self))  # Cannot embed permutation into smaller symmetric group.
		
		return Permutation(list(self.permutation) + list(range(len(self), new_n)))
	def matrix(self):
		''' Return the corresponding permutation matrix.
		
		That is, a matrix M such that M * e_i == e_{self[i]}. '''
		
		return flipper.kernel.Matrix([[1 if i == self(j) else 0 for j in range(len(self))] for i in range(len(self))])

#### Some special Permutations we know how to build.

def id_permutation(n):
	''' Return the identity permutation in Sym(n). '''
	
	return Permutation(range(n))

def cyclic_permutation(cycle, n):
	''' Return the cyclic permutation sending 1 |--> cycle in Sym(n). '''
	
	return Permutation([(cycle + i) % n for i in range(n)])

def all_permutations(n, odd=True, even=True):
	''' Return a list containing all permutations on n elements.
	
	If even is False then even permutations are omitted. If odd is False
	them odd permutations are omitted. '''
	
	all_perms = [Permutation(perm) for perm in permutations(range(n), n)]
	return [perm for perm in all_perms if (odd and not perm.is_even()) or (even and perm.is_even())]

def permutation_from_pair(a, to_a, b, to_b):
	''' Return the odd permutation in Sym(4) which sends a to to_a and b to to_b. '''
	
	try:
		c, d = set(range(4)) - set([a, b])
		to_c, to_d = set(range(4)) - set([to_a, to_b])
		
		p = {a: to_a, b: to_b, c: to_c, d: to_d}
		P = Permutation([p[i] for i in range(4)])
		if not P.is_even(): return P
		
		p = {a: to_a, b: to_b, c: to_d, d: to_c}
		P = Permutation([p[i] for i in range(4)])
		return P
	except IndexError:
		raise ValueError('Does not represent a gluing.')

