
''' A module for representing basic ways of changing triangulations.

Provides three classes: Isometry, EdgeFlip and LinearTransformation.

Perhaps in the future we will add a Spiral move so that curves can be
shortened in polynomial time. '''

import flipper

class Move(object):
	def __repr__(self):
		return str(self)
	
	def __call__(self, other):
		if isinstance(other, flipper.kernel.Lamination):
			if other.triangulation != self.source_triangulation:
				raise TypeError('Cannot apply Isometry to a lamination not on the source triangulation.')
			
			return self.target_triangulation.lamination(
				self.apply_geometric(other.geometric),
				self.apply_algebraic(other.algebraic),
				remove_peripheral=False)
		else:
			return NotImplemented
	
	def encode(self):
		''' Return the Encoding induced by this isometry. '''
		
		return flipper.kernel.Encoding([self])

class Isometry(Move):
	''' This represents an isometry from one Triangulation to another.
	
	Triangulations can create the isometries between themselves and this
	is the standard way users are expected to create these. '''
	def __init__(self, source_triangulation, target_triangulation, label_map):
		''' This represents an isometry from source_triangulation to target_triangulation.
		
		It is given by a map taking each edge label of source_triangulation to a label of target_triangulation. '''
		
		assert(isinstance(source_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(target_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(label_map, dict))
		
		self.flip_length = 0  # The number of flips needed to realise this move.
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.zeta = self.source_triangulation.zeta
		
		self.label_map = dict(label_map)
		
		# If we are missing any labels then use a depth first search to find the missing ones.
		# Hmmm, should always we do this just to check consistency?
		for i in self.source_triangulation.labels:
			if i not in self.label_map:
				raise flipper.AssumptionError('This label_map not defined on edge %d.' % i)
		
		self.index_map = dict((i, flipper.kernel.norm(self.label_map[i])) for i in self.source_triangulation.indices)
		# Store the inverses too while we're at it.
		self.inverse_label_map = dict((self.label_map[i], i) for i in self.source_triangulation.labels)
		self.inverse_index_map = dict((i, flipper.kernel.norm(self.inverse_label_map[i])) for i in self.source_triangulation.indices)
		self.inverse_signs = dict((i, +1 if self.inverse_index_map[i] == self.inverse_label_map[i] else -1) for i in self.source_triangulation.indices)
	
	def __str__(self):
		return 'Isometry ' + str([self.target_triangulation.edge_lookup[self.label_map[i]] for i in self.source_triangulation.indices])
	def __reduce__(self):
		return (self.__class__, (self.source_triangulation, self.target_triangulation, self.label_map))
	def __len__(self):
		return 1  # The number of pieces of this move.
	def package(self):
		''' Return a small amount of data such that self.source_triangulation.encode([data]) == self.encode(). '''
		
		if not all(self.label_map[i] == i for i in self.source_triangulation.indices):  # If self is not the identity isometry.
			return {i: self.label_map[i] for i in self.source_triangulation.labels}
		else:
			return None
	
	def apply_geometric(self, vector):
		return [vector[self.inverse_index_map[i]] for i in range(self.zeta)]
	def apply_algebraic(self, vector):
		return [vector[self.inverse_index_map[i]] * self.inverse_signs[i] for i in range(self.zeta)]
	
	def inverse(self):
		''' Return the inverse of this isometry. '''
		
		# inverse_corner_map = dict((self(corner), corner) for corner in self.corner_map)
		return Isometry(self.target_triangulation, self.source_triangulation, self.inverse_label_map)
	
	def applied_geometric(self, lamination, action):
		''' Return the action and condition matrices describing the PL map
		applied to the geometric coordinates of the given lamination after
		post-multiplying by the action matrix. '''
		
		assert(isinstance(lamination, flipper.kernel.Lamination))
		assert(isinstance(action, flipper.kernel.Matrix))
		
		return flipper.kernel.Matrix([action[self.inverse_index_map[i]] for i in range(self.zeta)]), flipper.kernel.zero_matrix(0)
	
	def pl_action(self, index, action):
		''' Return the action and condition matrices describing the PL map
		applied to the geometric coordinates by the cell of the specified index
		after post-multiplying by the action matrix. '''
		
		assert(isinstance(index, flipper.IntegerType))
		assert(isinstance(action, flipper.kernel.Matrix))
		
		return (flipper.kernel.Matrix([action[self.inverse_index_map[i]] for i in range(self.zeta)]), flipper.kernel.zero_matrix(0))
	
	def extend_bundle(self, triangulation3, tetra_count, upper_triangulation, lower_triangulation, upper_map, lower_map):
		''' Modify triangulation3 to extend the embedding of upper_triangulation via upper_map under this move. '''
		
		maps_to_triangle = lambda X: isinstance(X[0], flipper.kernel.Triangle)
		maps_to_tetrahedron = lambda X: not maps_to_triangle(X)
		
		# These are the new maps onto the upper and lower boundary that we will build.
		new_upper_map = dict()
		new_lower_map = dict()  # We are allowed to leave blanks in new_lower_map.
		
		for triangle in upper_triangulation:
			new_triangle = self.target_triangulation.triangle_lookup[self.label_map[triangle.labels[0]]]
			new_corner = self.target_triangulation.corner_lookup[self.label_map[triangle.corners[0].label]]
			perm = flipper.kernel.permutation.cyclic_permutation(new_corner.side - 0, 3)
			old_target, old_perm = upper_map[triangle]
			
			if maps_to_triangle(upper_map[triangle]):
				new_upper_map[new_triangle] = (old_target, old_perm * perm.inverse())
				# Don't forget to update the lower_map too.
				new_lower_map[old_target] = (new_triangle, perm * old_perm.inverse())
			else:
				new_upper_map[new_triangle] = (old_target, old_perm * perm.inverse().embed(4))
		
		# Remember to rebuild the rest of lower_map, which hasn't changed.
		for triangle in lower_triangulation:
			if triangle not in new_lower_map:
				new_lower_map[triangle] = lower_map[triangle]
		
		return tetra_count, self.target_triangulation, new_upper_map, new_lower_map

class EdgeFlip(Move):
	''' Represents the change to a lamination caused by flipping an edge. '''
	def __init__(self, source_triangulation, target_triangulation, edge_label):
		assert(isinstance(source_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(target_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(edge_label, flipper.IntegerType))
		
		self.flip_length = 1  # The number of flips needed to realise this move.
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.edge_label = edge_label
		self.edge_index = flipper.kernel.norm(self.edge_label)
		self.zeta = self.source_triangulation.zeta
		assert(self.source_triangulation.is_flippable(self.edge_index))
		
		self.square = self.source_triangulation.square_about_edge(self.edge_label)
	
	def __str__(self):
		return 'Flip %s%d' % ('' if self.edge_index == self.edge_label else '~', self.edge_index)
	def __reduce__(self):
		return (self.__class__, (self.source_triangulation, self.target_triangulation, self.edge_label))
	def __len__(self):
		return 2  # The number of pieces of this move.
	def package(self):
		''' Return a small amount of data such that self.source_triangulation.encode([data]) == self.encode(). '''
		
		return self.edge_label
	
	def apply_geometric(self, vector):
		a, b, c, d = self.square
		m = max(vector[a.index] + vector[c.index], vector[b.index] + vector[d.index]) - vector[self.edge_index]
		return [vector[i] if i != self.edge_index else m for i in range(self.zeta)]
	def apply_algebraic(self, vector):
		a, b, c, d = self.square
		m = b.sign() * vector[b.index] + c.sign() * vector[c.index]
		return [vector[i] if i != self.edge_index else m for i in range(self.zeta)]
	
	def inverse(self):
		''' Return the inverse of this map. '''
		
		return EdgeFlip(self.target_triangulation, self.source_triangulation, ~self.edge_label)
	
	def applied_geometric(self, lamination, action):
		''' Return the action and condition matrices describing the PL map
		applied to the geometric coordinates of the given lamination after
		post-multiplying by the action matrix. '''
		
		assert(isinstance(lamination, flipper.kernel.Lamination))
		assert(isinstance(action, flipper.kernel.Matrix))
		
		a, b, c, d, e = [edge.index for edge in self.square] + [self.edge_index]
		
		rows = [list(row) for row in action]
		if lamination(a) + lamination(c) >= lamination(b) + lamination(d):
			rows[e] = [rows[a][i] + rows[c][i] - rows[e][i] for i in range(self.zeta)]
			Cs = flipper.kernel.Matrix([[action[a][i] + action[c][i] - action[b][i] - action[d][i] for i in range(self.zeta)]])
		else:
			rows[e] = [rows[b][i] + rows[d][i] - rows[e][i] for i in range(self.zeta)]
			Cs = flipper.kernel.Matrix([[action[b][i] + action[d][i] - action[a][i] - action[c][i] for i in range(self.zeta)]])
		return flipper.kernel.Matrix(rows), Cs
	
	def pl_action(self, index, action):
		''' Return the action and condition matrices describing the PL map
		applied to the geometric coordinates by the cell of the specified index
		after post-multiplying by the action matrix. '''
		
		assert(isinstance(index, flipper.IntegerType))
		assert(isinstance(action, flipper.kernel.Matrix))
		
		a, b, c, d, e = [edge.index for edge in self.square] + [self.edge_index]
		
		rows = [list(row) for row in action]
		if index == 0:
			rows[e] = [rows[a][i] + rows[c][i] - rows[e][i] for i in range(self.zeta)]
			Cs = flipper.kernel.Matrix([[action[a][i] + action[c][i] - action[b][i] - action[d][i] for i in range(self.zeta)]])
		elif index == 1:
			rows[e] = [rows[b][i] + rows[d][i] - rows[e][i] for i in range(self.zeta)]
			Cs = flipper.kernel.Matrix([[action[b][i] + action[d][i] - action[a][i] - action[c][i] for i in range(self.zeta)]])
		else:
			raise IndexError('Index out of range.')
		return flipper.kernel.Matrix(rows), Cs
	
	def extend_bundle(self, triangulation3, tetra_count, upper_triangulation, lower_triangulation, upper_map, lower_map):
		
		''' Modify triangulation3 to extend the embedding of upper_triangulation via upper_map under this move. '''
		
		assert(upper_triangulation == self.source_triangulation)
		
		# We use these two functions to quickly tell what a triangle maps to.
		maps_to_triangle = lambda X: isinstance(X[0], flipper.kernel.Triangle)
		maps_to_tetrahedron = lambda X: not maps_to_triangle(X)
		
		# These are the new maps onto the upper and lower boundary that we will build.
		new_upper_map = dict()
		new_lower_map = dict()
		# We are allowed to leave blanks in new_lower_map.
		# These will be filled in at the end using lower_map.
		new_upper_triangulation = self.target_triangulation
		VEERING_LEFT, VEERING_RIGHT = flipper.kernel.triangulation3.VEERING_LEFT, flipper.kernel.triangulation3.VEERING_RIGHT
		
		# Get the next tetrahedra to add.
		tetrahedron = triangulation3.tetrahedra[tetra_count]
		
		# Setup the next tetrahedron.
		tetrahedron.edge_labels[(0, 1)] = VEERING_RIGHT
		tetrahedron.edge_labels[(1, 2)] = VEERING_LEFT
		tetrahedron.edge_labels[(2, 3)] = VEERING_RIGHT
		tetrahedron.edge_labels[(0, 3)] = VEERING_LEFT
		
		edge_label = self.edge_label  # The edge to flip.
		
		# We'll glue it into the core_triangulation so that it's 1--3 edge lies over edge_label.
		# WARNINNG: This is reliant on knowing how flipper.kernel.Triangulation.flip_edge() relabels things!
		cornerA = upper_triangulation.corner_of_edge(edge_label)
		cornerB = upper_triangulation.corner_of_edge(~edge_label)
		
		# We'll need to swap sides on an inverse edge so our convertions below work.
		if edge_label != self.edge_index: cornerA, cornerB = cornerB, cornerA
		
		(A, side_A), (B, side_B) = (cornerA.triangle, cornerA.side), (cornerB.triangle, cornerB.side)
		if maps_to_tetrahedron(upper_map[A]):
			tetra, perm = upper_map[A]
			tetrahedron.glue(2, tetra, flipper.kernel.permutation.permutation_from_pair(0, perm(side_A), 2, perm(3)))
		else:
			tri, perm = upper_map[A]
			new_lower_map[tri] = (tetrahedron, flipper.kernel.permutation.permutation_from_pair(perm(side_A), 0, 3, 2))
		
		if maps_to_tetrahedron(upper_map[B]):
			tetra, perm = upper_map[B]
			# The permutation needs to: 2 |--> perm(3), 0 |--> perm(side_A), and be odd.
			tetrahedron.glue(0, tetra, flipper.kernel.permutation.permutation_from_pair(2, perm(side_B), 0, perm(3)))
		else:
			tri, perm = upper_map[B]
			new_lower_map[tri] = (tetrahedron, flipper.kernel.permutation.permutation_from_pair(perm(side_B), 2, 3, 0))
		
		# Rebuild the upper_map.
		new_cornerA = new_upper_triangulation.corner_of_edge(edge_label)
		new_cornerB = new_upper_triangulation.corner_of_edge(~edge_label)
		new_A, new_B = new_cornerA.triangle, new_cornerB.triangle
		# Most of the triangles have stayed the same.
		# This relies on knowing how the upper_triangulation.flip_edge() function works.
		old_fixed_triangles = [triangle for triangle in upper_triangulation if triangle != A and triangle != B]
		new_fixed_triangles = [triangle for triangle in new_upper_triangulation if triangle != new_A and triangle != new_B]
		for old_triangle, new_triangle in zip(old_fixed_triangles, new_fixed_triangles):
			new_upper_map[new_triangle] = upper_map[old_triangle]
			if maps_to_triangle(upper_map[old_triangle]):  # Don't forget to update the lower_map too.
				target_triangle, perm = upper_map[old_triangle]
				new_lower_map[target_triangle] = (new_triangle, perm.inverse())
		
		# This relies on knowing how the upper_triangulation.flip_edge() function works.
		perm_A = flipper.kernel.permutation.cyclic_permutation(new_upper_triangulation.corner_of_edge(edge_label).side, 3)
		perm_B = flipper.kernel.permutation.cyclic_permutation(new_upper_triangulation.corner_of_edge(~edge_label).side, 3)
		new_upper_map[new_A] = (tetrahedron, flipper.kernel.Permutation((3, 0, 2, 1)) * perm_A.embed(4).inverse())
		new_upper_map[new_B] = (tetrahedron, flipper.kernel.Permutation((1, 2, 0, 3)) * perm_B.embed(4).inverse())
		
		# Remember to rebuild the rest of lower_map, which hasn't changed.
		for triangle in lower_triangulation:
			if triangle not in new_lower_map:
				new_lower_map[triangle] = lower_map[triangle]
		
		return tetra_count+1, self.target_triangulation, new_upper_map, new_lower_map

class Spiral(Move):
	''' This represents a spiral around a short curve. '''
	def __init__(self, source_triangulation, target_triangulation, edge_label, power):
		''' This represents spiralling around a short curve passing through edge_label.
		
		The number of spirals is determined by power and the compact form of this move
		means that the amount of work to compute the image of a lamination under this move
		is logorithmic in the power.
		
		Because this is a mapping class, source_triangulation and target_triangulation should be equal. '''
		
		assert(isinstance(source_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(target_triangulation, flipper.kernel.Triangulation))
		assert(source_triangulation == target_triangulation)
		
		self.flip_length = abs(power)  # The number of flips needed to realise this move.
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.zeta = self.source_triangulation.zeta
		
		self.edge_label = edge_label
		self.edge_index = flipper.kernel.norm(self.edge_label)
		# Find a, b, c & e automatically.
		self.square = self.source_triangulation.square_about_edge(self.edge_label)
		a, b, c, d = self.square
		assert(b == ~d)
		# Assert that b == d.
		self.power = power
	
	def __str__(self):
		return 'Spiral^%d %s' % (self.power, self.edge_label)
	def __reduce__(self):
		return (self.__class__, (self.source_triangulation, self.target_triangulation, self.edge_label, self.power))
	def __len__(self):
		return abs(self.power) + 3  # The number of pieces of this move.
	def package(self):
		''' Return a small amount of data such that self.source_triangulation.encode([data]) == self.encode(). '''
		
		return (self.edge_label, self.power)
	
	def mat(self, config, t):
		k = abs(self.power)
		if k == 0: return flipper.kernel.id_matrix(4)
		
		def F(n):  # Note F(0) == Id.
			return flipper.kernel.Matrix([
				[1,0,  0,  0],
				[0,1,  0,  0],
				[0,0,n+1, -n],
				[0,0,  n,1-n]
				])  # (Un)Stable transitions.
		G = flipper.kernel.Matrix([
			[1,0,0, 0],
			[0,1,0, 0],
			[1,1,0,-1],
			[0,0,1, 0]])  # Temp transitions.
		
		# Take k steps in the graph. Leave unstable after t steps.
		if config == 1:  # Stable.
			M = F(k)
		elif config == 2:  # Transition.
			M = F(k-1) * G
		elif config == 3:  # Unstable.
			if k <= t:  # k steps in unstable
				M = F(k)
			elif k == t+1:  # t steps in unstable, then into transition.
				M = G * F(t)
			elif k == t+2:  # t steps in unstable, into transition, then out of transition.
				M = G * G * F(t)
			else:  # t+2 < k:  # t steps in unstable, into transition, out of transition, then the remaining steps in stable.
				M = F(k - (t + 2)) * G * G * F(t)
		
		return M
	
	def apply_geometric(self, vector):
		# We will begin with an easy case so we can later assume self.power != 0.
		
		ai, bi, ci, di = [edge.index for edge in self.square]
		ei = self.edge_index
		a, b, c, d = [vector[edge.index] for edge in self.square]
		e = vector[self.edge_index]
		
		# Determine the number of strands passing through the annulus.
		x = max(b - e, a + c - b - e, e - b)
		# Use that to determine the configuration we're in.
		# There are three possible stats:
		#  1: Stable
		#  2: Transitioning
		#  3: Unstable
		# We use this slightly unusual ordering to ensure this gives the
		# same preference (a + c >= b + d) as EdgeFlip.
		state = 2 if x == a+c-b-e else 1 if x == b-e else 3
		
		k = abs(self.power)
		
		# Compute action on a, b, c, e.
		# Note that if self.power > 0 then we use the ordering a, c, b, e
		# and otherwise we use a, c, e, d. This allows us to do two calculations
		# with only one matrix.
		# Additionally d == b so we dont need to compute new_d.
		
		# The maximum number of times you can perform the unstable state.
		# WLOG 0 <= t <= k.
		
		if self.power > 0:
			config = state
			t = min(max((2*b - a - c) // (2*(e - b)) + 1, 0), k) if e != b else k
			M = self.mat(config, t)  # t only matters if in the unstable, that is, if config == 3.
			_, _, new_b, new_e = M([a, c, b, e])
		else:
			# Reverse the configuration if we are taking a negative power.
			config = 4 - state
			t = min(max((2*e - a - c) // (2*(b - e)) + 1, 0), k) if e != b else k
			M = self.mat(config, t)  # t only matters if in the unstable, that is, if config == 3.
			_, _, new_e, new_b = M([a, c, e, b])
		
		return [new_b if i == bi else new_e if i == ei else vector[i] for i in range(self.zeta)]
	
	def apply_algebraic(self, vector):
		a, b, c, d = self.square
		e = self.source_triangulation.edge_lookup[self.edge_label]
		new_b = vector[b.index] + b.sign() * c.sign() * vector[c.index] * self.power
		new_e = vector[e.index] - e.sign() * c.sign() * vector[c.index] * self.power
		return [new_b if i == b.index else new_e if i == self.edge_index else vector[i] for i in range(self.zeta)]
	
	def inverse(self):
		''' Return the inverse of this isometry. '''
		
		# inverse_corner_map = dict((self(corner), corner) for corner in self.corner_map)
		return Spiral(self.target_triangulation, self.source_triangulation, self.edge_label, -self.power)
	
	def applied_geometric(self, lamination, action):
		''' Return the action and condition matrices describing the PL map
		applied to the geometric coordinates of the given lamination after
		post-multiplying by the action matrix. '''
		
		assert(isinstance(lamination, flipper.kernel.Lamination))
		assert(isinstance(action, flipper.kernel.Matrix))
		
		a, b, c, d, e = [lamination(edge) for edge in self.square] + [lamination(self.edge_index)]
		x = max(b - e, a + c - b - e, e - b)
		state = 2 if x == a+c-b-e else 1 if x == b-e else 3
		config = state if self.power >= 0 else 4 - state
		k = abs(self.power)
		
		if self.power > 0:
			t = min(max((2*b - a - c) // (2*(e - b)) + 1, 0), k) if e != b else k
		else:
			t = min(max((2*e - a - c) // (2*(b - e)) + 1, 0), k) if e != b else k
		
		index = 0 if config == 1 else 1 if config == 2 else t + 2
		
		return self.pl_action(index, action)
	
	def pl_action(self, index, action):
		''' Return the action and condition matrices describing the PL map
		applied to the geometric coordinates by the cell of the specified index
		after post-multiplying by the action matrix. '''
		
		assert(isinstance(index, flipper.IntegerType))
		assert(isinstance(action, flipper.kernel.Matrix))
		
		if index == 0:
			config, t = 1, 0
		elif index == 1:
			config, t = 2, 0
		else:  # index >= 2.
			config, t = 3, index - 2
		
		state = config if self.power > 0 else 4 - config
		
		ai, bi, ci, di = [edge.index for edge in self.square]
		ei = self.edge_index
		k = abs(self.power)
		
		if self.power >= 0:
			M = self.mat(config, t)  # t only matters if in the unstable, that is, if config == 3.
			new_b_row = [M[2][0]*action[ai][i] + M[2][1]*action[ci][i] + M[2][2]*action[bi][i] + M[2][3]*action[ei][i] for i in range(self.zeta)]
			new_e_row = [M[3][0]*action[ai][i] + M[3][1]*action[ci][i] + M[3][2]*action[bi][i] + M[3][3]*action[ei][i] for i in range(self.zeta)]
		else:
			M = self.mat(config, t)  # t only matters if in the unstable, that is, if config == 3.
			new_e_row = [M[2][0]*action[ai][i] + M[2][1]*action[ci][i] + M[2][2]*action[ei][i] + M[2][3]*action[bi][i] for i in range(self.zeta)]
			new_b_row = [M[3][0]*action[ai][i] + M[3][1]*action[ci][i] + M[3][2]*action[ei][i] + M[3][3]*action[bi][i] for i in range(self.zeta)]
		A = flipper.kernel.Matrix([new_b_row if i == bi else new_e_row if i == ei else action[i] for i in range(self.zeta)])
		
		if config == 1:
			if state == 1:
				Cs = flipper.kernel.Matrix([
					[2*action[bi][i] - action[ai][i] - action[ci][i] for i in range(self.zeta)],
					[action[bi][i] - action[ei][i] for i in range(self.zeta)]
					])
			else:  # state == 3.
				Cs = flipper.kernel.Matrix([
					[2*action[ei][i] - action[ai][i] - action[ci][i] for i in range(self.zeta)],
					[action[ei][i] - action[bi][i] for i in range(self.zeta)]
					])
		elif config == 2:
			Cs = flipper.kernel.Matrix([
				[-2*action[bi][i] + action[ai][i] + action[ci][i] for i in range(self.zeta)],
				[-2*action[ei][i] + action[ai][i] + action[ci][i] for i in range(self.zeta)],
				])
		else:  # config == 3.
			# Construct Cs so t has the correct value.
			if state == 1:
				Cs = flipper.kernel.Matrix([
					[2*action[bi][i] - action[ai][i] - action[ci][i] for i in range(self.zeta)],
					[action[bi][i] - action[ei][i] for i in range(self.zeta)]
					])
				if t != 0:
					Cs = Cs.join(flipper.kernel.Matrix([
						[-2*(t-1)*action[bi][i] - action[ai][i] - action[ci][i] + 2*t*action[ei][i] for i in range(self.zeta)]
						]))
				if t != k:
					Cs = Cs.join(flipper.kernel.Matrix([
						[2*t*action[bi][i] + action[ai][i] + action[ci][i] - 2*(t+1)*action[ei][i] for i in range(self.zeta)]
						]))
			else:  # state == 3.
				Cs = flipper.kernel.Matrix([
					[2*action[ei][i] - action[ai][i] - action[ci][i] for i in range(self.zeta)],
					[action[ei][i] - action[bi][i] for i in range(self.zeta)]
					])
				if t != 0:
					Cs = Cs.join(flipper.kernel.Matrix([
						[-2*(t-1)*action[ei][i] - action[ai][i] - action[ci][i] + 2*t*action[bi][i] for i in range(self.zeta)]
						]))
				if t != k:
					Cs = Cs.join(flipper.kernel.Matrix([
						[2*t*action[ei][i] + action[ai][i] + action[ci][i] - 2*(t+1)*action[bi][i] for i in range(self.zeta)]
						]))
		
		return A, Cs
	
	def extend_bundle(self, triangulation3, tetra_count, upper_triangulation, lower_triangulation, upper_map, lower_map):
		''' Modify triangulation3 to extend the embedding of upper_triangulation via upper_map under this move. '''
		
		# These are the new maps onto the upper and lower boundary that we will build.
		
		if self.power == 0:
			return tetra_count, upper_triangulation, upper_map, lower_map
		
		bi, ei = self.square[1].index, self.edge_index
		k = abs(self.power)
		
		if self.power > 0:
			sequence = ([bi, ei] * k)[-k:]
		else:  # self.power < 0:
			sequence = ([ei, bi] * k)[-k:]
		
		twist = upper_triangulation.encode([{i: i for i in upper_triangulation.indices if i not in [ei, bi]}] + sequence)
		for item in reversed(twist.sequence):
			tetra_count, upper_triangulation, upper_map, lower_map = \
				item.extend_bundle(triangulation3, tetra_count, upper_triangulation, lower_triangulation, upper_map, lower_map)
		
		assert(upper_triangulation == self.target_triangulation)
		
		return tetra_count, self.target_triangulation, upper_map, lower_map

class LinearTransformation(Move):
	''' Represents the change to a lamination caused by a linear map. '''
	def __init__(self, source_triangulation, target_triangulation, geometric, algebraic):
		assert(isinstance(source_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(target_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(geometric, flipper.kernel.Matrix))
		assert(isinstance(algebraic, flipper.kernel.Matrix))
		
		self.flip_length = 0  # The number of flips needed to realise this move.
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.geometric = geometric
		self.algebraic = algebraic
	
	def __str__(self):
		return str(self.geometric) + str(self.algebraic)
	def __len__(self):
		return 1  # The number of pieces of this move.
	def package(self):
		''' Return a small amount of data such that self.source_triangulation.encode([data]) == self.encode(). '''
		
		return self
	
	def apply_geometric(self, vector):
		return self.geometric(vector)
	def apply_algebraic(self, vector):
		return self.algebraic(vector)
	
	def inverse(self):
		''' Return the inverse of this map.
		
		Note that these do not exist and so NotImplemented is returned. '''
		
		return NotImplemented
	
	def applied_geometric(self, lamination, action):
		''' Return the action and condition matrices describing the PL map
		applied to the geometric coordinates of the given lamination after
		post-multiplying by the action matrix. '''
		
		assert(isinstance(lamination, flipper.kernel.Lamination))
		assert(isinstance(action, flipper.kernel.Matrix))
		
		return self.geometric * action, flipper.kernel.zero_matrix(0)
	
	def pl_action(self, index, action):
		''' Return the action and condition matrices describing the PL map
		applied to the geometric coordinates by the cell of the specified index
		after post-multiplying by the action matrix. '''
		
		assert(isinstance(index, flipper.IntegerType))
		assert(isinstance(action, flipper.kernel.Matrix))
		
		return (self.geometric * action, flipper.kernel.zero_matrix(0))

