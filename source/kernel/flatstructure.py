
''' A module for representing a triangulation with a preferred flat structure.

Provides two classes: Vector2 and FlatStructure.
	An Vector2 is a vector in RR^2
	A FlatStructure is a triangulation with an assignment of vectors to each edge. '''

import flipper

class Vector2(object):
	''' This represents a point in RR^2. '''
	
	# Warning: This needs to be updated if the interals of this class ever change.
	__slots__ = ['x', 'y']
	
	def __init__(self, x, y):
		self.x, self.y = x, y
	def __str__(self):
		return "(%s, %s)" % (self.x, self.y)
	def __repr__(self):
		return str(self)
	def __iter__(self):
		return iter([self.x, self.y])
	def __eq__(self, other):
		return self.x == other.x and self.y == other.y
	def __ne__(self, other):
		return not (self == other)
	def __neg__(self):
		return Vector2(-self.x, -self.y)
	def __add__(self, other):
		return Vector2(self.x + other.x, self.y + other.y)
	def __sub__(self, other):
		return self + -other
	def __mul__(self, other):
		return Vector2(self.x * other, self.y * other)

class FlatStructure(object):
	''' This represents a triangulation with a flat structure.
	
	It is specified by a triangulation together with a map taking each edge to a Vector2.
	These should satisfy some standard relations like:
		vector[~edge] = -vector[edge], and
		sum(vector[edge] for edge in triangle) == 0.
	These vectors describe the flat structure of self.canonical() and can be used to build a flat surface for self.canonical().
	This is based off of code supplied by Shannon Horrigan.
	'''
	def __init__(self, triangulation, edge_vectors):
		assert(isinstance(triangulation, flipper.kernel.Triangulation))
		assert(isinstance(edge_vectors, dict))
		assert(all(edge in edge_vectors for edge in triangulation.edges))
		assert(all(isinstance(edge_vectors[edge], Vector2) for edge in triangulation.edges))
		
		assert(all(edge_vectors[~edge] == -edge_vectors[edge] for edge in triangulation.edges))
		assert(all(sum([edge_vectors[edge] for edge in triangle], Vector2(0, 0)) == Vector2(0, 0) for triangle in triangulation))
		
		self.triangulation = triangulation
		self.edge_vectors = edge_vectors
	def __str__(self):
		return '\n'.join('%s --> %s' % (edge, self.edge_vectors[edge]) for edge in sorted(self.triangulation.positive_edges, key=lambda e: e.index))
	def __repr__(self):
		return str(self)

