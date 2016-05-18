
''' A module for representing and manipulating maps between Triangulations.

Provides one class: Encoding. '''

import flipper

try:
	from Queue import Queue
except ImportError:
	from queue import Queue
from itertools import product

NT_TYPE_PERIODIC = 'Periodic'
NT_TYPE_REDUCIBLE = 'Reducible'  # Strictly this  means "reducible and not periodic".
NT_TYPE_PSEUDO_ANOSOV = 'Pseudo-Anosov'

class Encoding(object):
	''' This represents a map between two Triagulations.
	
	If it maps to and from the same triangulation then it represents
	a mapping class. This can be checked using self.is_mapping_class().
	
	The map is given by a sequence of EdgeFlips, LinearTransformations
	and Isometries which act from right to left.
	
	>>> import flipper
	>>> S = flipper.load('S_1_1')
	>>> aB = S.mapping_class('aB')
	>>> bA = S.mapping_class('bA')
	>>> ab = S.mapping_class('ab')
	>>> i = S.mapping_class('')
	>>> a = S.mapping_class('a')
	>>> a
	a
	>>> x = S.triangulation.encode([1])
	>>> x
	[Flip 1]
	'''
	def __init__(self, sequence, _cache=None):
		assert(isinstance(sequence, (list, tuple)))
		assert(len(sequence) > 0)
		assert(all(isinstance(item, flipper.kernel.Move) for item in sequence))
		# We used to also test:
		#  assert(all(x.source_triangulation == y.target_triangulation for x, y in zip(sequence, sequence[1:])))
		# However this makes composing Encodings a quadratic time algorithm!
		
		self.sequence = sequence
		
		self.source_triangulation = self.sequence[-1].source_triangulation
		self.target_triangulation = self.sequence[0].target_triangulation
		self.zeta = self.source_triangulation.zeta
		
		self._cache = {'name': ''} if _cache is None else _cache  # For caching hard to compute results.
	
	def without_cache(self):
		return Encoding(self.sequence, _cache={'name': self._cache['name']})
	
	def is_mapping_class(self):
		''' Return if this encoding is a mapping class.
		
		That is, if it maps to the triangulation it came from.
		
		>>> aB.is_mapping_class(), bA.is_mapping_class()
		(True, True)
		>>> x.is_mapping_class()
		False
		'''
		
		return self.source_triangulation == self.target_triangulation
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return self._cache['name'] if 'name' in self._cache else str(self.sequence)  # A backup name.
	def __iter__(self):
		return iter(self.sequence)
	def __len__(self):
		return len(self.sequence)
	def package(self):
		''' Return a small amount of info that self.source_triangulation can use to reconstruct this triangulation. '''
		return [item.package() for item in self]
	def __reduce__(self):
		return (create_encoding, (self.source_triangulation, self.package(), self._cache))
	def flip_length(self):
		''' Return the number of flips needed to realise this sequence. '''
		
		return sum(item.flip_length for item in self)
	def __getitem__(self, value):
		if isinstance(value, slice):
			# It turns out that handling all slices correctly is really hard.
			# We need to be very careful with "empty" slices. As Encodings require
			# non-empty sequences, we have to return just the id_encoding. This
			# ensures the Encoding that we return satisfies:
			#   self == self[:i] * self[i:j] * self[j:]
			# even when i == j.
			
			start = 0 if value.start is None else value.start if value.start >= 0 else len(self) + value.start
			stop = len(self) if value.stop is None else value.stop if value.stop >= 0 else len(self) + value.stop
			if start == stop:
				if 0 <= start < len(self):
					return self.sequence[start].target_triangulation.id_encoding()
				else:
					raise IndexError('list index out of range')
			return Encoding(self.sequence[value])
		elif isinstance(value, flipper.IntegerType):
			return self.sequence[value]
		else:
			return NotImplemented
	
	def __eq__(self, other):
		if isinstance(other, Encoding):
			if self.source_triangulation != other.source_triangulation or \
				self.target_triangulation != other.target_triangulation:
				raise ValueError('Cannot compare Encodings between different triangulations.')
			
			return all(self(curve) == other(curve) for curve in self.source_triangulation.key_curves())
		else:
			return NotImplemented
	def __ne__(self, other):
		return not (self == other)
	def is_homologous_to(self, other):
		''' Return if this encoding is homologous to other.
		
		Two maps are homologous if and only if they induce the same map
		from H_1(source_triangulation) to H_1(target_triangulation).
		
		>>> aB.is_homologous_to(aB), aB.is_homologous_to(bA), bA.is_homologous_to(ab), aB.is_homologous_to(i)
		(True, False, False, False)
		'''
		
		if isinstance(other, Encoding):
			if self.source_triangulation != other.source_triangulation or \
				self.target_triangulation != other.target_triangulation:
				raise ValueError('Cannot compare Encodings between different triangulations.')
			
			return all(self(curve).is_homologous_to(other(curve)) for curve in self.source_triangulation.key_curves())
		else:
			return NotImplemented
	
	def __call__(self, other):
		if isinstance(other, flipper.kernel.Lamination):
			if self.source_triangulation != other.triangulation:
				raise ValueError('Cannot apply an Encoding to a Lamination on a triangulation other than source_triangulation.')
			
			geometric = other.geometric
			algebraic = other.algebraic
			
			for item in reversed(self.sequence):
				geometric = item.apply_geometric(geometric)
				algebraic = item.apply_algebraic(algebraic)
			
			return self.target_triangulation.lamination(geometric, algebraic, remove_peripheral=False)
		else:
			return NotImplemented
	def __mul__(self, other):
		if isinstance(other, Encoding):
			if self.source_triangulation != other.target_triangulation:
				raise ValueError('Cannot compose Encodings over different triangulations.')
			
			return Encoding(self.sequence + other.sequence, _cache=dict() if 'name' not in self._cache or 'name' not in other._cache else {'name': self._cache['name'] + '.' + other._cache['name']})
		else:
			return NotImplemented
	def __pow__(self, k):
		assert(self.is_mapping_class())
		
		if k == 0:
			return self.source_triangulation.id_encoding()
		elif k > 0:
			return Encoding(self.sequence * k, _cache=dict() if 'name' not in self._cache else {'name': '(%s)^%d' % (self._cache['name'], k)})
		else:
			return self.inverse()**abs(k)
	
	def inverse(self):
		''' Return the inverse of this encoding.
		
		>>> aB.inverse() == bA, ab == ab.inverse(), i == i.inverse()
		(True, False, True)
		'''
		
		return Encoding([item.inverse() for item in reversed(self.sequence)], _cache=dict() if 'name' not in self._cache else {'name': '(%s)^-1' % self._cache['name']})
	
	def closing_isometries(self):
		''' Return all the possible isometries from self.target_triangulation to self.source_triangulation.
		
		These are the maps that can be used to close this into a mapping class. '''
		
		return self.target_triangulation.isometries_to(self.source_triangulation)
	
	def order(self):
		''' Return the order of this mapping class.
		
		If this has infinite order then return 0.
		
		This encoding must be a mapping class.
		
		>>> aB.order(), a.order()
		(0, 0)
		>>> i.order(), ab.order()
		(1, 6)
		'''
		
		assert(self.is_mapping_class())
		
		# We could do:
		# for i in range(1, self.source_triangulation.max_order + 1):
		#	if self**i == self.source_triangulation.id_encoding():
		#		return i
		# But this is quadratic in the order so instead we do:
		curves = self.source_triangulation.key_curves()
		possible_orders = set(range(1, self.source_triangulation.max_order+1))
		for curve in curves:
			curve_image = curve
			for i in range(1, max(possible_orders)+1):
				curve_image = self(curve_image)
				if curve_image != curve:
					possible_orders.discard(i)
					if not possible_orders: return 0  # No finite orders remain so we are infinite order.
		
		return min(possible_orders)
	
	def is_identity(self):
		''' Return if this encoding is the identity map.
		
		>>> i.is_identity()
		True
		>>> aB.is_identity()
		False
		'''
		
		return self.is_mapping_class() and all(self(curve) == curve for curve in self.source_triangulation.key_curves())
	
	def is_periodic(self):
		''' Return if this encoding has finite order.
		
		This encoding must be a mapping class.
		
		>>> aB.is_periodic(), a.is_periodic()
		(False, False)
		>>> i.is_periodic(), ab.is_periodic()
		(True, True)
		'''
		
		return self.order() > 0
	
	def is_reducible(self):
		''' Return if this encoding is reducible and NOT periodic.
		
		This encoding must be a mapping class.
		
		>>> aB.is_reducible(), a.is_reducible()
		(False, True)
		>>> i.is_reducible(), ab.is_reducible()
		(False, False)
		'''
		
		return self.nielsen_thurston_type() == NT_TYPE_REDUCIBLE
	
	def is_pseudo_anosov(self):
		''' Return if this encoding is pseudo-Anosov.
		
		This encoding must be a mapping class.
		
		>>> aB.is_pseudo_anosov(), a.is_pseudo_anosov()
		(True, False)
		>>> i.is_pseudo_anosov(), ab.is_pseudo_anosov()
		(False, False)
		'''
		
		return self.nielsen_thurston_type() == NT_TYPE_PSEUDO_ANOSOV
	
	def applied_geometric(self, lamination):
		''' Return the action and condition matrices describing the PL map
		applied to the geometric coordinates of the given lamination. '''
		
		assert(isinstance(lamination, flipper.kernel.Lamination))
		
		As = flipper.kernel.id_matrix(self.zeta)
		Cs = flipper.kernel.zero_matrix(self.zeta, 1)
		for item in reversed(self.sequence):  # We can't just reverse self as reversed requires a list not an iterator.
			# This now uses the improved sparse matrix representation.
			As, C = item.applied_geometric(lamination, As)
			Cs = Cs.join(C)
			lamination = item(lamination)
		
		return As, Cs
	
	def pl_action(self):
		''' Yield each of the action, condition matrix pairs describing the action of this Encoding
		on ML. '''
		
		for sequence in product(*[range(len(item)) for item in self]):
			As = flipper.kernel.id_matrix(self.zeta)
			Cs = flipper.kernel.zero_matrix(self.zeta, 1)
			for item, index in reversed(list(zip(self, sequence))):
				# This now uses the improved sparse matrix representation.
				As, C = item.pl_action(index, action=As)
				Cs = Cs.join(C)
		
			yield (As, Cs)
		
		return
	
	def pml_fixedpoint_uncached(self, starting_curve=None):
		''' Return a rescaling constant and projectively invariant lamination.
		
		Assumes that the mapping class is pseudo-Anosov.
		
		To find this we start with a curve on the surface and repeatedly apply
		the map until it appear to be projectively similar to a previous iteration.
		Finally it uses:
			flipper.kernel.symboliccomputation.perron_frobenius_eigen()
		to find the nearby projective fixed point. If this fails after some number
		of iterations then we fall back to computing the action inside of every
		cell of the PL action. Generically this is exponentially slow.
		
		Note: In most pseudo-Anosov cases < 15 iterations are needed, if it fails
		to converge after many iterations then it is extremely likely that the
		mapping class was not pseudo-Anosov. Also note that the number of iterations
		done before switching technique is (currently) only dependent on the topology
		of the underlying surface.
		
		This encoding must be a mapping class. '''
		
		# Suppose that f_1, ..., f_m, g_1, ..., g_n, t_1, ..., t_k, p is the Thurston decomposition of self.
		# That is: f_i are pA on subsurfaces, g_i are periodic on subsurfaces, t_i are Dehn twist along the curve of
		# the canonical curve system and p is a permutation of the subsurfaces.
		# Additionally, let S_i be the subsurface corresponding to f_i, P_i correspond to g_i and A_i correspond to t_i.
		# Finally, let x_0 be a curve on the surface and define x_i := self(x_{i-1}).
		#
		# The algorithm covers 3 cases:  (Note we reorder the subsurfaces for ease of notation.)
		#  1) x_0 meets at S_1, ..., S_m',
		#  2) x_0 meets no S_i but meets A_1, ..., A_k', and
		#  3) x_0 meets no S_i or A_i, that is x_0 is contained in a P_1.
		#
		# In the first case, x_i will converge exponentially to the stable laminations of f_1, ..., f_m'.
		# Here the convergence is so fast we need only a few iterations.
		#
		# In the second case x_i will converge linearly to c, the cores of A_1, ..., A_k'. To speed this up
		# we note that x_i = i*c + O(1), so rescale x_i by 1/i, round and check if this is c.
		#
		# Finally, the third case happens if and only if x_i is periodic. In this case self must be
		# periodic or reducible. We test for periodicity at the beginning hence if we ever find a curve
		# fixed by a power of self then we must reducible.
		
		# Possible future improvements:
		#  - Store the checked cells in a hash map to prevent rerunning the expensive symboliccomputation.directed_eigenvector.
		#  - Automatically update to a finer RESOLUTION whenever you fail to get a lamination from symboliccomputation.directed_eigenvector.
		
		assert(self.is_mapping_class())
		
		# We will use a hash to significantly speed up the algorithm.
		resolution = 200
		def curve_hash(curve, resolution):
			''' A simple hash mapping cuves to a coarse lattice in PML. '''
			# Hmmm, this can suffer from // always rounding down.
			w = curve.weight()
			return (resolution,) + tuple([entry * resolution // w for entry in curve])
		
		# We start with a fast test for periodicity.
		# This isn't needed but it means that if we ever discover that
		# self is not pA then it must be reducible.
		if self.is_periodic():
			raise flipper.AssumptionError('Mapping class is periodic.')
		
		triangulation = self.source_triangulation
		max_order = triangulation.max_order
		if starting_curve is None: starting_curve = triangulation.key_curves()[0]
		curves = [starting_curve]
		seen = {curve_hash(curves[0], resolution): [0]}
		tested = set()
		# Experimentally this is a good number to do.
		# Should it be max_order**2 or even depend on len(self)?
		for i in range(max(10 * max_order, 100)):
			new_curve = self(curves[-1])
			curves.append(new_curve)
			
			hsh = curve_hash(new_curve, resolution)
			# print(i, new_curve, hsh)
			if hsh in seen:
				for j in reversed(seen[hsh]):  # Better to work backwards as the later ones are likely to be longer and so projectively closer.
					# Check if we have seen this curve before.
					if new_curve == curves[j]:  # self**(i-j)(new_curve) == new_curve, so self is reducible.
						raise flipper.AssumptionError('Mapping class is reducible.')
					# Average the last few curves in case they have 'spiralled' around the fixedpoint.
					average_curve = sum(curves[j:])
					action_matrix, condition_matrix = self.applied_geometric(average_curve)
					# We'll store condition_matrix in a set to ensure that we never test the same cell twice.
					if condition_matrix not in tested:
						tested.add(condition_matrix)
						try:
							eigenvalue, eigenvector = flipper.kernel.symboliccomputation.directed_eigenvector(
								action_matrix, condition_matrix)
						except flipper.ComputationError:
							pass  # Could not find an eigenvector in the cone.
						except flipper.AssumptionError:
							raise flipper.AssumptionError('Mapping class is reducible.')
						else:
							invariant_lamination = triangulation.lamination(eigenvector)
							if not invariant_lamination.is_empty():  # But it might have been entirely peripheral.
								return eigenvalue, invariant_lamination
				
				seen[hsh].append(i+1)
			else:
				seen[hsh] = [i+1]
			
			# We now have an extra test to handle the case when self is reducible and curve lies only in periodic parts.
			if len(seen[hsh]) > 4 or i % max_order == 0:  # This is still slow (quadratic in max_order) so don't do it often.
				for j in reversed(range(max(len(curves) - max_order, 0), len(curves)-1)):
					# A good guess for the reducing curve is the (additive) growth rate.
					vector = [x - y for x, y in zip(new_curve, curves[j])]
					new_small_curve = small_curve = triangulation.lamination(vector, algebraic=[0] * self.zeta)
					if not small_curve.is_empty():
						for k in range(1, max_order+1):
							new_small_curve = self(new_small_curve)
							if new_small_curve == small_curve:
								if k == 1:
									# We could raise an AssumptionError in this case too as this also shows that self is reducible.
									return 1, small_curve
								else:
									raise flipper.AssumptionError('Mapping class is reducible.')
			
			if len(seen[hsh]) > 6:
				# Recompute seen to a higher resolution.
				# This reduces the chances that we will get false positives that need
				# to have an expensive directed_eigenvector calculation done on them.
				resolution = resolution * 10  # Crank up exponentially.
		
		# If all else fails then just check every cell of the PL action. There can be exponentially many cells
		# (and generically there are) so this process is extremely slow. However it is guaranteed to terminate
		# with an invariant lamination or prove that the mapping class is reducible.
		for action_matrix, condition_matrix in self.pl_action():
			if condition_matrix not in tested:  # We may as well skip cells that we've already tested.
				try:
					eigenvalue, eigenvector = flipper.kernel.symboliccomputation.directed_eigenvector(
						action_matrix, condition_matrix)
				except flipper.ComputationError:
					pass  # Could not find an eigenvector in the cone.
				except flipper.AssumptionError:
					raise flipper.AssumptionError('Mapping class is reducible.')
				else:
					invariant_lamination = triangulation.lamination(eigenvector)
					if not invariant_lamination.is_empty():  # But it might have been entirely peripheral.
						return eigenvalue, invariant_lamination
		
		# If none of the cells contained a projective fixed-point with eigenvalue > 1 then this mapping class
		# must be reducible.
		raise flipper.AssumptionError('Mapping class is reducible.')
	
	def pml_fixedpoint(self):
		''' A version of self.invariant_lamination_uncached with caching. '''
		
		if 'invariant_lamination' not in self._cache:
			try:
				self._cache['invariant_lamination'] = self.pml_fixedpoint_uncached()
			except flipper.AssumptionError as error:
				self._cache['invariant_lamination'] = error
		
		if isinstance(self._cache['invariant_lamination'], Exception):
			raise self._cache['invariant_lamination']
		else:
			return self._cache['invariant_lamination']
	
	def invariant_lamination(self):
		''' Return a projectively invariant lamination of this mapping class.
		
		This encoding must be a mapping class.
		
		Assumes that this encoding is pseudo-Anosov. '''
		
		_, lamination = self.pml_fixedpoint()
		return lamination
	
	def dilatation(self):
		''' Return the dilatation of this mapping class.
		
		This encoding must be a mapping class. '''
		
		if self.nielsen_thurston_type() != NT_TYPE_PSEUDO_ANOSOV:
			return flipper.kernel.NumberField().one  # This is equivalent to ZZ[1].one.
		else:
			lmbda, _ = self.pml_fixedpoint()
			return lmbda
	
	def splitting_sequences(self, take_roots=False):
		''' Return a list of splitting sequences associated to this mapping class.
		
		Assumes (and checks) that the mapping class is pseudo-Anosov.
		
		This encoding must be a mapping class. '''
		
		if self.is_periodic():  # Actually this test is redundant but it is faster to test it now.
			raise flipper.AssumptionError('Mapping class is not pseudo-Anosov.')
		
		dilatation, lamination = self.pml_fixedpoint()
		try:
			splittings = lamination.splitting_sequences(dilatation=None if take_roots else dilatation)
		except flipper.AssumptionError:  # Lamination is not filling.
			raise flipper.AssumptionError('Mapping class is not pseudo-Anosov.')
		
		return splittings
	
	def splitting_sequence(self):
		''' Return the splitting sequence associated to this mapping class.
		
		Assumes (and checks) that the mapping class is pseudo-Anosov.
		
		This encoding must be a mapping class. '''
		
		# We get a list of all possible splitting sequences from
		# self.splitting_sequences(). From there we use the fact that each
		# of these differ by a periodic mapping class, which cannot be in the
		# Torelli subgroup and so acts non-trivially on H_1(S).
		# Thus we look for the map whose action on H_1(S) is conjugate to self
		# via splitting.preperiodic.
		
		# To do this we take sufficiently many curves (the key_curves() of the
		# underlying triangulation) and look for the splitting sequence in which
		# they are mapped to homologous curves by:
		#	preperiodic . self and periodic . preperiodic.
		# Note that we no longer use self.inverse() as periodic now goes in the
		# same direction as self.
		
		homology_splittings = [splitting for splitting in self.splitting_sequences()
			if (splitting.preperiodic * self).is_homologous_to(splitting.mapping_class * splitting.preperiodic)]
		
		if len(homology_splittings) == 0:
			raise flipper.FatalError('Mapping class is not homologous to any splitting sequence.')
		elif len(homology_splittings) == 1:
			return homology_splittings[0]
		else:
			raise flipper.FatalError('Mapping class is homologous to multiple splitting sequences.')
	
	def canonical(self):
		''' Return the canonical form of this mapping class. '''
		
		return self.splitting_sequence().mapping_class
	
	def nielsen_thurston_type(self):
		''' Return the Nielsen--Thurston type of this encoding.
		
		This encoding must be a mapping class.
		
		>>> ab.nielsen_thurston_type(), a.nielsen_thurston_type(), aB.nielsen_thurston_type()
		('Periodic', 'Reducible', 'Pseudo-Anosov')
		'''
		
		if self.is_periodic():
			return NT_TYPE_PERIODIC
		
		try:
			# We could do any of self.splitting_sequence(), self.canonical(), ...
			# but this involves the least calculation and so is fastest.
			self.splitting_sequences()
		except flipper.AssumptionError:
			return NT_TYPE_REDUCIBLE
		
		return NT_TYPE_PSEUDO_ANOSOV
	
	def is_abelian(self):
		''' Return if this mapping class corresponds to an Abelian differential.
		
		This is an Abelian differential (rather than a quadratic differential) if and
		only if its stable lamination is orientable.
		
		Assumes (and checks) that the mapping class is pseudo-Anosov.
		
		This encoding must be a mapping class.
		
		>>> aB.is_abelian()
		True
		>>> ab.is_abelian()  # doctest: +ELLIPSIS
		Traceback (most recent call last):
		    ...
		AssumptionError: ...
		>>> a.is_abelian()  # doctest: +ELLIPSIS
		Traceback (most recent call last):
		    ...
		AssumptionError: ...
		'''
		
		return self.splitting_sequence().lamination.is_orientable()
	
	def is_primitive(self):
		''' Return if this mapping class is primitive.
		
		This encoding must be a mapping class.
		
		Assumes (and checks) that this mapping class is pseudo-Anosov. '''
		
		return self.splitting_sequences(take_roots=True).open_periodic.flip_length() == self.canonical().flip_length()
	
	def is_conjugate_to(self, other):
		''' Return if this mapping class is conjugate to other.
		
		It would also be straightforward to check if self^i ~~ other^j
		for some i, j.
		
		Both encodings must be mapping classes.
		
		Currently assumes that at least one mapping class is pseudo-Anosov. '''
		
		assert(isinstance(other, Encoding))
		
		# Nielsen-Thurston type is a conjugacy invariant.
		if self.nielsen_thurston_type() != other.nielsen_thurston_type():
			return False
		
		if self.nielsen_thurston_type() == NT_TYPE_PERIODIC:
			if self.order() != other.order():
				return False
			
			# We could also use action on H_1(S) as a conjugacy invaraiant.
			
			raise flipper.AssumptionError('Mapping class is periodic.')
		elif self.nielsen_thurston_type() == NT_TYPE_REDUCIBLE:
			# There's more to do here.
			
			raise flipper.AssumptionError('Mapping class is reducible.')
		elif self.nielsen_thurston_type() == NT_TYPE_PSEUDO_ANOSOV:
			# Two pseudo-Anosov mapping classes are conjugate if and only if
			# there canonical forms are cyclically conjugate via an isometry.
			f = self.canonical()
			g = other.canonical()
			# We should start by quickly checking some invariants.
			# For example they should have the same dilatation.
			if self.dilatation() != other.dilatation():
				return False
			
			for i in range(len(f)):
				# Conjugate around.
				f_cycled = f[i:] * f[:i]
				# g_cycled = g[i:] * g[:i]  # Could cycle g instead.
				for isom in f_cycled.source_triangulation.isometries_to(g.source_triangulation):
					if isom.encode() * f_cycled == g * isom.encode():
						return True
			
			return False
	
	def stratum(self):
		''' Return a dictionary mapping each singularity to its stratum order.
		
		This is the number of bipods incident to the vertex.
		
		Assumes (and checks) that this mapping class is pseudo-Anosov.
		
		This encoding must be a mapping class. '''
		
		# This can fail with an flipper.AssumptionError.
		return self.splitting_sequence().lamination.stratum()
	
	def hitting_matrix(self):
		''' Return the hitting matrix of the underlying train track. '''
		
		# This can fail with an flipper.AssumptionError.
		h = self.canonical()
		
		M = flipper.kernel.id_matrix(h.zeta)
		lamination = h.invariant_lamination()
		# Lamination defines a train track with a bipod in each triangle. We
		# follow the sequence of folds (and isometries) which this train track
		# undergoes and track how the edges are mapped using M.
		for item in reversed(h.sequence):
			if isinstance(item, flipper.kernel.EdgeFlip):
				triangulation = lamination.triangulation
				a, b, c, d = triangulation.square_about_edge(item.edge_label)
				
				# Work out which way the train track is pointing.
				if lamination.is_bipod(triangulation.corner_of_edge(a.label)):
					assert(lamination.is_bipod(triangulation.corner_of_edge(c.label)))
					M = M.elementary(item.edge_index, b.index)
					M = M.elementary(item.edge_index, d.index)
				elif lamination.is_bipod(triangulation.corner_of_edge(b.label)):
					assert(lamination.is_bipod(triangulation.corner_of_edge(d.label)))
					M = M.elementary(item.edge_index, a.index)
					M = M.elementary(item.edge_index, c.index)
				else:
					raise flipper.FatalError('Incompatible bipod.')
			elif isinstance(item, flipper.kernel.Isometry):
				M = flipper.kernel.Permutation([item.index_map[i] for i in range(h.zeta)]).matrix() * M
			else:
				raise flipper.FatalError('Unknown item in canonical sequence.')
			
			# Move the lamination onto the next triangulation.
			lamination = item(lamination)
		
		return M
	
	def bundle(self, canonical=True, _safety=True):
		''' Return the bundle associated to this mapping class.
		
		This method can be run in two different modes:
		If canonical=True:
			Then the bundle returned is triangulated by a veering, layered
			triangulation and has at most 6g+5n-6 additional loops drilled
			from it, as described by Agol. These additional cusps are marked
			as fake cusps and can be dealt with by filling along their
			fibre slope.
			
			Assumes (and checks) that this mapping class is pseudo-Anosov.
		If canonical=False:
			Then the bundle returned is triangulated by a layered triangulation
			obtained by stacking flat tetrahedra, one for each edge flip in
			self.
			
			Assumes (and checks) that the resulting triangulation is an ideal
			triangulation of a manifold and that the fibre surface immerses
			into the two skeleton. If _safety=True then this should always happen.
		
		This encoding must be a mapping class. '''
		
		assert(self.is_mapping_class())
		triangulation = self.source_triangulation
		
		if canonical:
			# This can fail with an flipper.AssumptionError if self is not pseudo-Anosov.
			return self.canonical().bundle(canonical=False, _safety=False)
		
		if _safety:
			# We should add enough flips to ensure the triangulation is a manifold.
			# Flipping and then unflipping every edge is certainly enough.
			# However, we still have to be careful as there may be non-flippable edges.
			
			# Start by adding a flip and unflip each flippable edge.
			safe_encoding = self
			for i in triangulation.flippable_edges():
				extra = triangulation.encode_flip(i)
				safe_encoding = extra.inverse() * extra * safe_encoding
			# Then add a flip and unflip for each non-flippable edge.
			for i in triangulation.indices:
				if not triangulation.is_flippable(i):
					# To do this we must first flip the boundary edge.
					boundary_edge = triangulation.nonflippable_boundary(i)
					# This edge is always flippable and, after flipping it, i is too.
					extra = triangulation.encode([i, boundary_edge])
					safe_encoding = extra.inverse() * extra * safe_encoding
			
			return safe_encoding.bundle(canonical=False, _safety=False)
		
		VEERING_LEFT, VEERING_RIGHT = flipper.kernel.triangulation3.VEERING_LEFT, flipper.kernel.triangulation3.VEERING_RIGHT
		id_perm3 = flipper.kernel.Permutation((0, 1, 2))
		
		
		lower_triangulation, upper_triangulation = triangulation, triangulation
		
		triangulation3 = flipper.kernel.Triangulation3(self.flip_length())
		# These are maps taking triangles of lower (respectively upper) triangulation to either:
		#  - A pair (triangle, permutation) where triangle is in upper (resp. lower) triangulation, or
		#  - A pair (tetrahedron, permutation) of triangulation3.
		# We start with no tetrahedra, so these maps are just the identity map between the two triangulations.
		lower_map = dict((triangleA, (triangleB, id_perm3)) for triangleA, triangleB in zip(lower_triangulation, upper_triangulation))
		upper_map = dict((triangleB, (triangleA, id_perm3)) for triangleA, triangleB in zip(lower_triangulation, upper_triangulation))
		
		# We also use these two functions to quickly tell what a triangle maps to.
		maps_to_triangle = lambda X: isinstance(X[0], flipper.kernel.Triangle)
		maps_to_tetrahedron = lambda X: not maps_to_triangle(X)
		
		tetra_count = 0
		for item in reversed(self.sequence):
			assert(item.source_triangulation == upper_triangulation)
			
			try:
				tetra_count, upper_triangulation, upper_map, lower_map = \
					item.extend_bundle(triangulation3, tetra_count, upper_triangulation, lower_triangulation, upper_map, lower_map)
			except AttributeError:
				# We have no way to handle any other type that appears.
				# Currently this means there was a LinearTransform and so this is not a mapping class.
				raise flipper.FatalError('Unknown move %s encountered while building bundle.' % item)
		
		# We're now back to the starting triangulation.
		assert(lower_triangulation == upper_triangulation)
		
		# This is a map which send each triangle of upper_triangulation via isometry to a pair:
		#	(triangle, permutation)
		# where triangle in lower_triangulation and maps_to_tetrahedron(lower_map[triangle]).
		full_forwards = dict()
		for source_triangle in upper_triangulation:
			target_triangle, perm = source_triangle, id_perm3
			
			c = 0
			while maps_to_triangle(lower_map[target_triangle]):
				target_triangle, new_perm = lower_map[target_triangle]
				perm = new_perm * perm
				
				c += 1
				assert(c <= 3 * upper_triangulation.zeta)
			full_forwards[source_triangle] = (target_triangle, perm)
		
		# Now close the bundle up.
		for source_triangle in upper_triangulation:
			if maps_to_tetrahedron(upper_map[source_triangle]):
				A, perm_A = upper_map[source_triangle]
				target_triangle, perm = full_forwards[source_triangle]
				B, perm_B = lower_map[target_triangle]
				A.glue(perm_A(3), B, perm_B * perm.embed(4) * perm_A.inverse())
		
		# There are now no unglued faces.
		assert(triangulation3.is_closed())
		
		# Install longitudes and meridians. This also calls Triangulation3.assign_cusp_indices().
		triangulation3.install_peripheral_curves()
		
		# Construct an immersion of the fibre surface into the closed bundle.
		fibre_immersion = dict()
		for source_triangle in lower_triangulation:
			if maps_to_triangle(lower_map[source_triangle]):
				upper_triangle, upper_perm = lower_map[source_triangle]
				target_triangle, perm = full_forwards[upper_triangle]
				B, perm_B = lower_map[target_triangle]
				fibre_immersion[source_triangle] = (B, perm_B * (perm * upper_perm).embed(4))
			else:
				B, perm_B = lower_map[source_triangle]
				fibre_immersion[source_triangle] = lower_map[source_triangle]
		
		return flipper.kernel.Bundle(lower_triangulation, triangulation3, fibre_immersion)
	
	def flat_structure(self):
		''' Return the flat structure associated to self.canonical().
		
		Assumes that this mapping class is pseudo-Anosov.
		
		This encoding must be a mapping class. '''
		
		assert(self.is_mapping_class())
		
		stable_lamination = self.splitting_sequence().lamination
		unstable_lamination = self.splitting_sequence().mapping_class.inverse().invariant_lamination()
		periodic_triangulation = self.splitting_sequence().triangulation
		
		queue = Queue()  # The edges whose vectors are decided but whose triangles have not been inspected.
		edge_vectors = dict()  # A dictionary mapping edges to their corresponding vectors. 
		
		while len(edge_vectors) < self.zeta:
			# We fix an edge to start the procedure.
			e = [edge for edge in periodic_triangulation.edges if edge not in edge_vectors][0]
			
			# Fill in the basic information for this edge (and its inverse).
			edge_vectors[e] = flipper.kernel.Vector2(stable_lamination(e), unstable_lamination(e))
			edge_vectors[~e] = flipper.kernel.Vector2(-stable_lamination(e), -unstable_lamination(e))
			
			queue.put(e)
			queue.put(~e)
			
			while not queue.empty():
				edge_1 = queue.get()  # Get an unchecked edge.
				# Moving anticlockwise around the triangle from edge_1 brings you to edge_2 then edge_3
				#          /\
				#         /  \
				#        /    \
				#  e_3  v      ^  e_2
				#      /        \
				#     /          \
				#     ------>-----
				#         e_1
				corner = periodic_triangulation.corner_lookup[edge_1.label]
				edge_2, edge_3 = corner.edges[1], corner.edges[2]
				
				if edge_2 in edge_vectors and edge_3 not in edge_vectors:  # If two of the edges are known we can calculate the third using the formula: edge_1  + edge_2  + edge_3 == 0.
					edge_vectors[edge_3] = -(edge_vectors[edge_1] + edge_vectors[edge_2])
					edge_vectors[~edge_3] = -edge_vectors[edge_3]
					queue.put(~edge_3)
				elif edge_2 not in edge_vectors and edge_3 in edge_vectors:  # The other possibility if two edges are known.
					edge_vectors[edge_2] = -(edge_vectors[edge_1] + edge_vectors[edge_3])
					edge_vectors[~edge_2] = -edge_vectors[edge_2]
					queue.put(~edge_2)
				elif edge_2 not in edge_vectors and edge_3 not in edge_vectors:  # If edge_2 and edge_3 are both unknown:
					# Here we just choose positive signs in anticipation of changing them later if need be.
					s_1, u_1 = stable_lamination(edge_1), unstable_lamination(edge_1)
					s_2, u_2 = stable_lamination(edge_2), unstable_lamination(edge_2)
					s_3, u_3 = stable_lamination(edge_3), unstable_lamination(edge_3)
					
					edge_vectors[edge_2] = flipper.kernel.Vector2(
						-s_2 if (s_1 == s_2 + s_3 and edge_vectors[edge_1].x >= 0) or \
							(s_2 == s_1 + s_3 and edge_vectors[edge_1].x >= 0) or \
							(s_3 == s_1 + s_2 and edge_vectors[edge_1].x < 0) else s_2,
						-u_2 if (u_1 == u_2 + u_3 and edge_vectors[edge_1].y >= 0) or \
							(u_2 == u_1 + u_3 and edge_vectors[edge_1].y >= 0) or \
							(u_3 == u_1 + u_2 and edge_vectors[edge_1].y < 0) else u_2
						)
					
					edge_vectors[edge_3] = flipper.kernel.Vector2(
						-s_3 if (s_1 == s_2 + s_3 and edge_vectors[edge_1].x >= 0) or \
							(s_2 == s_1 + s_3 and edge_vectors[edge_1].x < 0) or \
							(s_3 == s_1 + s_2 and edge_vectors[edge_1].x >= 0) else s_3,
						-u_3 if (u_1 == u_2 + u_3 and edge_vectors[edge_1].y >= 0) or \
							(u_2 == u_1 + u_3 and edge_vectors[edge_1].y < 0) or \
							(u_3 == u_1 + u_2 and edge_vectors[edge_1].y >= 0) else u_3
						)
					
					# Put the inverses in too.
					edge_vectors[~edge_2] = -edge_vectors[edge_2]
					edge_vectors[~edge_3] = -edge_vectors[edge_3]
					queue.put(~edge_2)
					queue.put(~edge_3)
				# The final case is: edge_2 in edge_vectors and edge_3 in edge_vectors. However here there is nothing to do as all of the edges are known.
		
		return flipper.kernel.FlatStructure(periodic_triangulation, edge_vectors)

def create_encoding(source_triangulation, sequence, _cache=None):
	''' Return the encoding defined by sequence starting at source_triangulation.
	
	This is only really here to help with pickling. Users should use
	source_triangulation.encode(sequence) directly. '''
	
	assert(isinstance(source_triangulation, flipper.kernel.Triangulation))
	
	return source_triangulation.encode(sequence, _cache=_cache)

def doctest_globs():
	''' Return the globals needed to run doctest on this module. '''
	
	S = flipper.load('S_1_1')
	aB = S.mapping_class('aB')
	bA = S.mapping_class('bA')
	ab = S.mapping_class('ab')
	i = S.mapping_class('')
	a = S.mapping_class('a')
	x = S.triangulation.encode([1])
	
	return {'aB': aB, 'bA': bA, 'ab': ab, 'i': i, 'a': a, 'x': x}

