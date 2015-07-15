
''' A module for representing basic ways of changing triangulations.

Provides two classes: EdgeFlip and LinearTransformation. '''

import flipper

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
			
			return flipper.kernel.Lamination(self.target_triangulation, geometric, algebraic)
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
			
			return flipper.kernel.Lamination(self.target_triangulation, geometric, algebraic)
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

