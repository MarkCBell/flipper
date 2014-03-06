
from itertools import permutations, combinations

# Represents a permutation on N elements.
class Permutation(object):
	def __init__(self, permutation):
		assert(set(permutation) == set(range(len(permutation))))
		self.permutation = tuple(permutation)
	def __repr__(self):
		return str(self.permutation)
	def __iter__(self):
		return iter(self.permutation)
	def __getitem__(self, index):
		return self.permutation[index]
	def __len__(self):
		return len(self.permutation)
	def __mul__(self, other):
		assert(len(self) == len(other))
		return Permutation([self[other[i]] for i in range(len(self))])
	def __str__(self):
		return ''.join(str(p) for p in self.permutation)
	def __eq__(self, other):
		return self.permutation == other.permutation
	def inverse(self):
		return Permutation([j for i in range(len(self)) for j in range(len(self)) if self[j] == i])
	def is_even(self):
		even = True
		for j, i in combinations(range(len(self)), 2):
			if self[j] > self[i]: even = not even
		return even
	def embed(self, n):
		# Returns the permutation given by including this permutation into Sym(n). Assumes n >= len(self).
		assert(n >= len(self))
		return Permutation(list(self.permutation) + list(range(len(self), n)))

#### Some special Permutations we know how to build.

def Id_Permutation(n):
	return Permutation(range(n))

def cyclic_permutation(cycle, n):
	return Permutation([(cycle + i) % n for i in range(n)])

def permutation_from_mapping(n, mapping, even):
	# v = [None] * (len(mapping) + 2)
	# for (source, target) in mapping:
		# v[source] = target
	
	# sources, targets = zip(*mapping)
	# a, b = list(set(range(len(v))).difference(set(sources)))
	# p, q = list(set(range(len(v))).difference(set(targets)))
	# v1, v2 = list(v), list(v)
	# v1[a] = p
	# v1[b] = q
	# P1 = Permutation(v1)
	# if P1.is_even() == even: return P1
	
	# v2[a] = q
	# v2[b] = p
	# P2 = Permutation(v2)
	# if P2.is_even() == even: return P2
	
	for perm in permutations(range(n), n):
		P = Permutation(perm)
		if P.is_even() == even and all(P[source] == target for (source, target) in mapping):
			return P
	
	raise TypeError('Not a valid permutation.')  # !?! To Do.
