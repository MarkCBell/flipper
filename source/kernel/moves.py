
''' A module for representing basic ways of changing triangulations.

Provides three classes: Isometry, EdgeFlip and LinearTransformation. '''

import flipper

class Isometry(object):
	''' This represents an isometry from one Triangulation to another.
	
	Triangulations can create the isometries between themselves and this
	is the standard way users are expected to create these. '''
	def __init__(self, source_triangulation, target_triangulation, label_map, respect_fillings=True):
		''' This represents an isometry from source_triangulation to target_triangulation.
		
		It is given by a map taking each edge label of source_triangulation to a label of target_triangulation.
		The entire map does not need to be given and will be automatically extended to any missing labels.
		
		Assumes (and checks) that there is a unique extension of label_map to an Isometry. '''
		
		assert(isinstance(source_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(target_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(label_map, (list, tuple, dict)))
		assert(isinstance(respect_fillings, bool))
		
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.zeta = self.source_triangulation.zeta
		
		if isinstance(label_map, (list, tuple)):
			self.label_map = dict(enumerate(label_map))
		else:
			self.label_map = dict(label_map)
		
		# If we are missing any labels then use a depth first search to find the missing ones.
		# Hmmm, should always we do this just to check consistency?
		if any(i not in self.label_map for i in range(self.zeta)) or any(~i not in self.label_map for i in range(self.zeta)):
			source_orders = dict([(corner.label, len(corner_class)) for corner_class in self.source_triangulation.corner_classes for corner in corner_class])
			target_orders = dict([(corner.label, len(corner_class)) for corner_class in self.target_triangulation.corner_classes for corner in corner_class])
			# We do a depth first search extending the corner map across the triangulation.
			# This is a stack of labels that may still have consequences to check.
			to_process = [(edge_from_label, self.label_map[edge_from_label]) for edge_from_label in self.label_map]
			while to_process:
				from_label, to_label = to_process.pop()
				
				neighbours = [
					(~from_label, ~to_label),
					(self.source_triangulation.corner_lookup[from_label].labels[1], self.target_triangulation.corner_lookup[to_label].labels[1])
					]
				for new_from_label, new_to_label in neighbours:
					if new_from_label in self.label_map:
						# Check that this map is still consistent.
						if new_to_label != self.label_map[new_from_label]:
							raise flipper.AssumptionError('This label_map does not extend to an isometry.')
					else:
						# Extend the map.
						if source_orders[new_from_label] != target_orders[new_to_label] or \
							respect_fillings and self.source_triangulation.vertex_lookup[new_from_label].filled != self.target_triangulation.vertex_lookup[new_to_label].filled:
							raise flipper.AssumptionError('This label_map does not extend to an isometry.')
						self.label_map[new_from_label] = new_to_label
						to_process.append((new_from_label, new_to_label))
			
			if any(i not in self.label_map for i in range(self.zeta)) or any(~i not in self.label_map for i in range(self.zeta)):
				raise flipper.AssumptionError('This label_map does not determine an isometry.')
		
		self.index_map = dict((i, flipper.kernel.norm(self.label_map[i])) for i in range(self.zeta))
		# Store the inverses too while we're at it.
		self.inverse_label_map = dict((self(i), i) for i in range(-self.zeta, self.zeta))
		self.inverse_index_map = dict((i, flipper.kernel.norm(self.inverse_label_map[i])) for i in range(self.zeta))
		self.inverse_signs = dict((i, +1 if self.inverse_index_map[i] == self.inverse_label_map[i] else -1) for i in range(self.zeta))
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return 'Isometry ' + str([self.target_triangulation.edge_lookup[self(i)] for i in range(self.zeta)])
	def __reduce__(self):
		return (self.__class__, (self.source_triangulation, self.target_triangulation, self.label_map))
	
	def __call__(self, other):
		if isinstance(other, flipper.kernel.Lamination):
			if other.triangulation != self.source_triangulation:
				raise TypeError('Cannot apply Isometry to a lamination not on the source triangulation.')
			
			geometric = [other.geometric[self.inverse_index_map[i]] for i in range(self.zeta)]
			algebraic = [other.algebraic[self.inverse_index_map[i]] * self.inverse_signs[i] for i in range(self.zeta)]
			return self.target_triangulation.lamination(geometric, algebraic, remove_peripheral=False)
		elif isinstance(other, flipper.kernel.Vertex):
			pass
		elif isinstance(other, flipper.kernel.Edge):
			if other not in self.source_triangulation:
				raise ValueError('Edge not in source triangulation.')
			return self.target_triangulation.edge_lookup[self(other.label)]
		elif isinstance(other, flipper.kernel.Triangle):
			if other not in self.source_triangulation:
				raise ValueError('Triangle not in source triangulation.')
			return self.target_triangulation.triangle_lookup[self(other.labels[0])]
		elif isinstance(other, flipper.kernel.Corner):
			if other not in self.source_triangulation:
				raise ValueError('Corner not in source triangulation.')
			return self.target_triangulation.corner_lookup[self(other.label)]
		elif isinstance(other, flipper.IntegerType):  # Integers are assumed to be labels.
			return self.label_map[other]
		else:
			return NotImplemented
	def inverse(self):
		''' Return the inverse of this isometry. '''
		
		# inverse_corner_map = dict((self(corner), corner) for corner in self.corner_map)
		return Isometry(self.target_triangulation, self.source_triangulation, self.inverse_label_map)
	
	def applied_geometric(self, lamination):
		''' Return the action and condition matrices describing the isometry
		applied to the geometric coordinates of the given lamination. '''
		
		return flipper.kernel.Permutation([self.index_map[i] for i in range(self.zeta)]).matrix(), flipper.kernel.zero_matrix(0)
	
	def encode(self):
		''' Return the Encoding induced by this isometry. '''
		
		return flipper.kernel.Encoding([self])
	
	def flip_length(self):
		''' Return the number of flips needed to realise this move. '''
		
		return 0

class EdgeFlip(object):
	''' Represents the change to a lamination caused by flipping an edge. '''
	def __init__(self, source_triangulation, target_triangulation, edge_label):
		assert(isinstance(source_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(target_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(edge_label, flipper.IntegerType))
		
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.edge_label = edge_label
		self.edge_index = flipper.kernel.norm(self.edge_label)
		self.zeta = self.source_triangulation.zeta
		assert(self.source_triangulation.is_flippable(self.edge_index))
		
		self.square = self.source_triangulation.square_about_edge(self.edge_label)
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return 'Flip %s%d' % ('' if self.edge_index == self.edge_label else '~', self.edge_index)
	def __reduce__(self):
		return (self.__class__, (self.source_triangulation, self.target_triangulation, self.edge_label))
	
	def __call__(self, other):
		if isinstance(other, flipper.kernel.Lamination):
			if other.triangulation != self.source_triangulation:
				raise TypeError('Cannot apply EdgeFlip to a lamination not on the source triangulation.')
			
			a, b, c, d = self.square
			geometric = list(other.geometric)
			algebraic = list(other.algebraic)
			m = max(geometric[a.index] + geometric[c.index], geometric[b.index] + geometric[d.index])
			geometric[self.edge_index] = m - geometric[self.edge_index]
			algebraic[self.edge_index] = b.sign() * algebraic[b.index] + c.sign() * algebraic[c.index]
			
			return self.target_triangulation.lamination(geometric, algebraic, remove_peripheral=False)
		else:
			return NotImplemented
	
	def inverse(self):
		''' Return the inverse of this map. '''
		
		return EdgeFlip(self.target_triangulation, self.source_triangulation, ~self.edge_label)
	
	def applied_geometric(self, lamination):
		''' Return the action and condition matrices describing the PL map
		applied to the geometric coordinates of the given lamination. '''
		
		assert(isinstance(lamination, flipper.kernel.Lamination))
		
		I = flipper.kernel.id_matrix(self.zeta)
		Z = flipper.kernel.zero_matrix(self.zeta, 1)
		a, b, c, d, e = [edge.index for edge in self.square] + [self.edge_index]
		geometric = list(lamination.geometric)
		if geometric[a] + geometric[c] >= geometric[b] + geometric[d]:
			return I.tweak([(e, a), (e, c)], [(e, e), (e, e)]), Z.tweak([(0, a), (0, c)], [(0, b), (0, d)])
		else:
			return I.tweak([(e, b), (e, d)], [(e, e), (e, e)]), Z.tweak([(0, b), (0, d)], [(0, a), (0, c)])
	
	def encode(self):
		''' Return the Encoding induced by this EdgeFlip. '''
		
		return flipper.kernel.Encoding([self])
	
	def flip_length(self):
		''' Return the number of flips needed to realise this move. '''
		
		return 1

class LinearTransformation(object):
	''' Represents the change to a lamination caused by a linear map. '''
	def __init__(self, source_triangulation, target_triangulation, geometric, algebraic):
		assert(isinstance(source_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(target_triangulation, flipper.kernel.Triangulation))
		assert(isinstance(geometric, flipper.kernel.Matrix))
		assert(isinstance(algebraic, flipper.kernel.Matrix))
		
		self.source_triangulation = source_triangulation
		self.target_triangulation = target_triangulation
		self.geometric = geometric
		self.algebraic = algebraic
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return str(self.geometric) + str(self.algebraic)
	
	def __call__(self, other):
		if isinstance(other, flipper.kernel.Lamination):
			if other.triangulation != self.source_triangulation:
				raise TypeError('Cannot apply LinearTransformation to a lamination not on the source triangulation.')
			
			geometric = self.geometric(other.geometric)
			algebraic = self.algebraic(other.algebraic)
			
			return self.target_triangulation.lamination(geometric, algebraic, remove_peripheral=False)
		else:
			return NotImplemented
	
	def inverse(self):
		''' Return the inverse of this map.
		
		Note that these do not exist and so NotImplemented is returned. '''
		
		return NotImplemented
	
	def applied_geometric(self, lamination):
		''' Return the action and condition matrices describing the PL map
		applied to the geometric coordinates of the given lamination. '''
		
		assert(isinstance(lamination, flipper.kernel.Lamination))
		
		return self.geometric, flipper.kernel.zero_matrix(0)
	
	def encode(self):
		''' Return the Encoding induced by this linear map. '''
		
		return flipper.kernel.Encoding([self])
	
	def flip_length(self):
		''' Return the number of flips needed to realise this move. '''
		
		return 0

