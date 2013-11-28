
# We follow the orientation conventions in SnapPy/headers/kernel_typedefs.h L:154
# and SnapPy/kernel/peripheral_curves.c.

# Warning: Layered_Triangulation modifies itself in place!
# Perhaps when I'm feeling purer I'll come back and redo this.

from itertools import permutations, combinations
try:
	from Source.Error import AbortError, ComputationError, AssumptionError
except ImportError:
	from Error import AbortError, ComputationError, AssumptionError

class Permutation:
	def __init__(self, permutation):
		self.permutation = permutation
	def __repr__(self):
		return str(self.permutation)
	def __getitem__(self, index):
		return self.permutation[index]
	def __mul__(self, other):
		return Permutation([self[other[i]] for i in range(4)])
	def __str__(self):
		return '%d%d%d%d' % tuple(self.permutation)
	def __eq__(self, other):
		return self.permutation == other.permutation
	def inverse(self):
		return Permutation(tuple([j for i in range(4) for j in range(4) if self[j] == i]))
	def is_even(self):
		even = True
		for j, i in combinations(range(4),2):
			if self[j] > self[i]: even = not even
		return even

all_permutations = [Permutation(perm) for perm in permutations(range(4), 4)]
even_permutations = [perm for perm in all_permutations if perm.is_even()]
odd_permutations = [perm for perm in all_permutations if not perm.is_even()]

def permutation_from_mapping(i, i_image, j, j_image, even):
	return [perm for perm in (even_permutations if even else odd_permutations) if perm[i] == i_image and perm[j] == j_image][0]

# Edge veerings:
UNKNOWN = None
LEFT = 0
RIGHT = 1
vertices_meeting = {0:(1,2,3), 1:(0,2,3), 2:(0,1,3), 3:(0,1,2)}

class Tetrahedra:
	def __init__(self, label=None):
		self.label = label
		self.glued_to = [None] * 4  # None or (Tetrahedra, permutation).
		self.cusp_indices = [-1, -1, -1, -1]
		self.meridians = [[0,0,0,0] for i in range(4)]
		self.longitudes = [[0,0,0,0] for i in range(4)]
		self.edge_labels = {(0,1):UNKNOWN, (0,2):UNKNOWN, (0,3):UNKNOWN, (1,2):UNKNOWN, (1,3):UNKNOWN, (2,3):UNKNOWN}
		self.vertex_labels = [None, None, None, None]
	
	def __repr__(self):
		return str(self.label)
	
	def __str__(self):
		return 'Label: %s, Gluings: %s, Edge labels: %s' % (self.label, self.glued_to, [self.edge_labels[i] for i in combinations(range(4), 2)])
	
	def glue(self, side, target, permutation):
		if self.glued_to[side] is None:
			assert(self.glued_to[side] is None)
			assert(target.glued_to[permutation[side]] is None)
			assert(not permutation.is_even())
			
			self.glued_to[side] = (target, permutation)
			target.glued_to[permutation[side]] = (self, permutation.inverse())
			
			# Move across the edge veerings too.
			for a, b in combinations(vertices_meeting[side], 2):
				x, y = sorted([permutation[a], permutation[b]])
				my_edge_veering = self.edge_labels[(a, b)]
				his_edge_veering = target.edge_labels[(x, y)]
				if my_edge_veering == UNKNOWN and his_edge_veering != UNKNOWN:
					self.edge_labels[(a, b)] = his_edge_veering
				elif my_edge_veering != UNKNOWN and his_edge_veering == UNKNOWN:
					target.edge_labels[(x, y)] = my_edge_veering
				elif my_edge_veering != UNKNOWN and his_edge_veering != UNKNOWN:
					assert(my_edge_veering == his_edge_veering)
		else:
			assert((target, permutation) == self.glued_to[side])
	
	def unglue(self, side):
		if self.glued_to[side] is not None:
			other, perm = self.glued_to[side]
			other.glued_to[perm[side]] = None
			self.glued_to[side] = None
	
	def SnapPy_string(self):
		s = ''
		s += '%4d %4d %4d %4d \n' % tuple([tetrahedra.label for tetrahedra, gluing in self.glued_to])
		s += '%s %s %s %s\n' % tuple([str(gluing) for tetrahedra, gluing in self.glued_to])
		s += '%4d %4d %4d %4d \n' % tuple(self.cusp_indices)
		for i in range(4):
			s += '  0  0  0  0 %2d %2d %2d %2d  0  0  0  0  %2d %2d %2d %2d\n' % tuple(self.meridians[i] + self.longitudes[i])
		s += '  0.000000000000   0.000000000000\n'
		return s

class Triangulation:
	def __init__(self, num_tetrahedra):
		self.num_tetrahedra = num_tetrahedra
		self.tetrahedra = [Tetrahedra(i) for i in range(self.num_tetrahedra)]
		self.num_cusps = 1  # 0
	
	def copy(self):
		# Returns a copy of this triangulation. We guarantee that the tetrahedra in the copy will come in the same order.
		new_triangulation = Triangulation(self.num_tetrahedra)
		forwards = dict(zip(self.tetrahedra, new_triangulation.tetrahedra))
		
		for tetrahedron in self.tetrahedra:
			for side in range(4):
				if tetrahedron.glued_to[side] is not None:
					neighbour, permutation = tetrahedron.glued_to[side]
					forwards[tetrahedron].glue(side, forwards[neighbour], permutation)
			
			forwards[tetrahedron].cusp_indices = list(tetrahedron.cusp_indices)
			forwards[tetrahedron].meridians = [list(meridian) for meridian in tetrahedron.meridians]
			forwards[tetrahedron].longitudes = [list(longitude) for longitude in tetrahedron.longitudes]
			forwards[tetrahedron].edge_labels = dict(tetrahedron.edge_labels)
			forwards[tetrahedron].vertex_labels = tetrahedron.vertex_labels
		
		return new_triangulation
	
	def __repr__(self):
		return '\n'.join(str(tetrahedron) for tetrahedron in self.tetrahedra)
	
	def create_tetrahedra(self):
		self.tetrahedra.append(Tetrahedra(self.num_tetrahedra))
		self.num_tetrahedra += 1
		return self.tetrahedra[-1]
	
	def destroy_tetrahedra(self, tetrahedron):
		for side in range(4):
			tetrahedron.unglue(side)
		self.tetrahedra.remove(tetrahedron)
		self.num_tetrahedra -= 1
	
	def reindex(self):
		for index, tetrahedron in enumerate(self.tetrahedra):
			tetrahedron.label = index
	
	def is_closed(self):
		return all(tetrahedron.glued_to[side] is not None for tetrahedron in self.tetrahedra for side in range(4))
	
	def SnapPy_string(self):
		if not self.is_closed(): raise AssumptionError('Layered triangulation is not closed.')
		# First make sure that all of the labellings are good.
		self.reindex()
		s = ''
		s += '% Triangulation\n'
		s += 'Flipper_triangulation\n'
		s += 'not_attempted  0.0\n'
		s += 'oriented_manifold\n'
		s += 'CS_unknown\n'
		s += '\n'
		s += '%d 0\n' % self.num_cusps
		for i in range(self.num_cusps):
			s += '    torus   0.000000000000   0.000000000000\n'
		s += '\n'
		s += '%d\n' % self.num_tetrahedra
		for tetrahedra in self.tetrahedra:
			s += tetrahedra.SnapPy_string() + '\n'
		
		return s

# A class to represent a layered triangulation over a surface specified by an Abstract_Triangulation.
class Layered_Triangulation:
	def __init__(self, abstract_triangulation):
		self.closed = False
		self.lower_triangulation = abstract_triangulation.copy()
		self.upper_triangulation = abstract_triangulation.copy()
		self.core_triangulation = Triangulation(2 * abstract_triangulation.num_triangles)
		
		lower_tetrahedra = self.core_triangulation.tetrahedra[:abstract_triangulation.num_triangles]
		upper_tetrahedra = self.core_triangulation.tetrahedra[abstract_triangulation.num_triangles:]
		for lower, upper in zip(lower_tetrahedra, upper_tetrahedra):
			lower.glue(3, upper, Permutation((0,2,1,3)))
		
		# We store two maps, one from the lower triangulation and one from the upper.
		# Each is a dictionary sending each Abstract_Triangle of lower/upper_triangulation to a pair (Tetrahedra, permutation).
		self.lower_map = dict((lower, (lower_tetra, Permutation((0,1,2,3)))) for lower, lower_tetra in zip(self.lower_triangulation, lower_tetrahedra))
		self.upper_map = dict((upper, (upper_tetra, Permutation((0,2,1,3)))) for upper, upper_tetra in zip(self.upper_triangulation, upper_tetrahedra))
	
	def __repr__(self):
		s = 'Core tri:\n'
		s += '\n'.join(str(tetra) for tetra in self.core_triangulation.tetrahedra)
		s += '\nUpper tri:\n' + str(self.upper_triangulation)
		s += '\nLower tri:\n' + str(self.lower_triangulation)
		s += '\nUpper map: ' + str(self.upper_map)
		s += '\nLower map: ' + str(self.lower_map)
		return s
	
	def flip(self, edge_index):
		# MEGA WARNINNG: This is reliant on knowing how Abstract_Triangulation.flip() relabels things!
		assert(self.upper_triangulation.edge_is_flippable(edge_index))
		
		# Get a new tetrahedra.
		new_tetrahedra = self.core_triangulation.create_tetrahedra()
		new_tetrahedra.edge_labels[(0,1)] = RIGHT
		new_tetrahedra.edge_labels[(1,2)] = LEFT
		new_tetrahedra.edge_labels[(2,3)] = RIGHT
		new_tetrahedra.edge_labels[(0,3)] = LEFT
		
		# We'll glue it into the core_triangulation so that it's 1--3 edge lies over edge_index.
		(A, side_A), (B, side_B) = self.upper_triangulation.find_edge(edge_index)
		object_A, perm_A = self.upper_map[A]
		object_B, perm_B = self.upper_map[B]
		
		below_A, down_perm_A = object_A.glued_to[3]
		below_B, down_perm_B = object_B.glued_to[3]
		
		object_A.unglue(3)
		object_B.unglue(3)
		
		# Do some gluings.
		new_glue_perm_A = permutation_from_mapping(0, down_perm_A[perm_A[side_A]], 2, down_perm_A[3], even=False)
		new_glue_perm_B = permutation_from_mapping(2, down_perm_B[perm_B[side_B]], 0, down_perm_B[3], even=False)
		new_tetrahedra.glue(2, below_A, new_glue_perm_A)
		new_tetrahedra.glue(0, below_B, new_glue_perm_B)
		
		new_tetrahedra.glue(1, object_A, Permutation((2,3,1,0)))
		new_tetrahedra.glue(3, object_B, Permutation((1,0,2,3)))
		
		# Get the new upper triangulation
		new_upper_triangulation = self.upper_triangulation.flip_edge(edge_index)
		# Rebuild the upper_map.
		new_upper_map = dict()
		for triangle in self.upper_triangulation:
			if edge_index not in triangle.edge_indices:
				corresponding_triangle = new_upper_triangulation.find_triangle(triangle.edge_indices)
				new_upper_map[corresponding_triangle] = self.upper_map[triangle]
		
		# This relies on knowing how the upper_triangulation.flip_edge() function works.
		(new_A, new_side_A), (new_B, new_side_B) = new_upper_triangulation.find_edge(edge_index)
		new_upper_map[new_A] = (object_A, Permutation((0,2,1,3)))
		new_upper_map[new_B] = (object_B, Permutation((0,2,1,3)))
		
		# Finally, install the new objects.
		self.upper_triangulation = new_upper_triangulation
		self.upper_map = new_upper_map
	
	def flips(self, sequence):
		for edge_index in sequence:
			self.flip(edge_index)
	
	def close(self, isometry):
		# Should assume that all edges of the underlying triangulation have been flipped.
		
		closed_triangulation = self.core_triangulation.copy()
		# The tetrahedra in the closed triangulation are guaranteed to be in the same order so we can get away with this.
		forwards = dict(zip(self.core_triangulation.tetrahedra, closed_triangulation.tetrahedra))
		# Probably should install longitudes and meridians now.
		
		for triangle in self.upper_triangulation:
			matching_triangle, cycle = isometry[triangle]
			perm = Permutation([cycle, (cycle+1)%3, (cycle+2)%3, 3])
			
			A, perm_A = self.upper_map[triangle]
			B, perm_B = self.lower_map[matching_triangle]
			
			below_A, perm_down_A = A.glued_to[3]
			below_B, perm_down_B = B.glued_to[3]
			
			closed_triangulation.destroy_tetrahedra(forwards[A])
			closed_triangulation.destroy_tetrahedra(forwards[B])
			forwards[below_A].glue(perm_down_A[3], forwards[below_B], perm_down_B * perm_B * perm * perm_A.inverse() * perm_down_A.inverse())
		
		return closed_triangulation

if __name__ == '__main__':
	from Examples import Example_S_1_1
	
	T, twists = Example_S_1_1()
	L = Layered_Triangulation(T)
	L.flips([2, 1, 2, 1])
	print('------------------------------')
	print(L)
	isom = L.upper_triangulation.all_isometries(L.lower_triangulation)[0]
	print('------------------------------')
	print('Isometry: ', isom)
	print('------------------------------')
	M = L.close(isom)
	print(M)
	print('M is closed: %s' % M.is_closed())
	print('M\'s SnapPy string:')
	print(M.SnapPy_string())
