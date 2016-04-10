
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
		return 'Spiral ' + str((self.b, self.e))
	def __reduce__(self):
		return (self.__class__, (self.source_triangulation, self.target_triangulation, self.edge_label, self.power))
	def __len__(self):
		return abs(self.power) + 3  # The number of pieces of this move.
	def package(self):
		''' Return a small amount of data such that self.source_triangulation.encode([data]) == self.encode(). '''
		
		return (self.edge_label, self.power)
	
	def mat(self, config, k, t):
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
		state = 1 if x == b-e else 2 if x == a+c-b-e else 3
		# Reverse the configuration if we are taking a negative power.
		config = state if self.power > 0 else 4 - state
		
		k = abs(self.power)
		
		# Compute action on a, b, c, e.
		# Note that if self.power > 0 then we use the ordering a, c, b, e
		# and otherwise we use a, c, e, d. This allows us to do two calculations
		# with only one matrix.
		# Additionally d == b so we dont need to compute new_d.
		
		# The maximum number of times you can perform the unstable state.
		# WLOG 0 <= t <= k.
		t = min(max((2*(b if self.power > 0 else e) - a - c) // (2*abs(e - b)), 0), k) if e != b else k
		M = self.mat(config, k, t)  # t only matters if in the unstable, that is, if config == 3.
		
		if self.power > 0:
			_, _, new_b, new_e = M([a, c, b, e])
		else:
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
		
		ai, bi, ci, di = [edge.index for edge in self.square]
		ei = self.edge_index
		a, b, c, d = [lamination(edge) for edge in self.square]
		e = lamination(self.edge_index)
		x = max(b - e, a + c - b - e, e - b)
		state = 1 if x == b-e else 2 if x == a+c-b-e else 3
		config = state if self.power > 0 else 4 - state
		
		k = abs(self.power)
		t = min(max((2*(b if self.power > 0 else e) - a - c) // (2*abs(e - b)), 0), k) if e != b else k
		M = self.mat(config, k, t)
		
		A = action.copy()
		if self.power >= 0:
			new_b_row = [M[2][0]*action[ai][i] + M[2][1]*action[ci][i] + M[2][2]*action[bi][i] + M[2][3]*action[ei][i] for i in range(self.zeta)]
			new_e_row = [M[3][0]*action[ai][i] + M[3][1]*action[ci][i] + M[3][2]*action[bi][i] + M[3][3]*action[ei][i] for i in range(self.zeta)]
		else:
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
					[action[bi][i] - action[ei][i] for i in range(self.zeta)],
					[2*(1-t)*action[bi][i] - action[ai][i] - action[ci][i] + 2*t*action[ei][i] for i in range(self.zeta)],
					[2*t*action[bi][i] + action[ai][i] + action[ci][i] - 2*(t+1)*action[ei][i] for i in range(self.zeta)],
					])
			else:  # state == 3.
				Cs = flipper.kernel.Matrix([
					[2*action[ei][i] - action[ai][i] - action[ci][i] for i in range(self.zeta)],
					[action[ei][i] - action[bi][i] for i in range(self.zeta)],
					[2*(1-t)*action[ei][i] - action[ai][i] - action[ci][i] + 2*t*action[bi][i] for i in range(self.zeta)],
					[2*t*action[ei][i] + action[ai][i] + action[ci][i] - 2*(t+1)*action[bi][i] for i in range(self.zeta)],
					])
		
		return A, Cs
	
	def pl_action(self, index, action):
		''' Return the action and condition matrices describing the PL map
		applied to the geometric coordinates by the cell of the specified index
		after post-multiplying by the action matrix. '''
		
		assert(isinstance(index, flipper.IntegerType))
		assert(isinstance(action, flipper.kernel.Matrix))
		
		pass
		k = abs(self.power)
		Ms = [self.mat(1, k, 0), self.mat(2, k, 0)] + [self.mat(3, k, t) for t in range(0, k+1)]
		if self.power > 0:
			for M in Ms:
				pass
			
			_, _, new_b, new_e = M([a, c, b, e])
			
		else:
			pass
		
		pass

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

