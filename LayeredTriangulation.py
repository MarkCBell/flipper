
# We follow the orientation conventions in SnapPy/headers/kernel_typedefs.h L:154.

from itertools import permutations, combinations
from AbstractTriangulation import Abstract_Triangulation

class Permutation:
	def __init__(self, permutation):
		self.permutation = permutation
	def __repr__(self):
		return str(self.permutation)
	def __getitem__(self, index):
		return self.permutation[index]
	def __mul__(self, other):
		return Permutation([self[other[i]] for i in range(4)])
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

class Tetrahedra:
	def __init__(self, label=None):
		self.label = label
		self.glued_to = [None] * 4  # None or (Tetrahedra, permutation).
	
	def __repr__(self):
		return str(self.label)
	
	def __str__(self):
		return '%s: %s' % (self.label, self.glued_to)
	
	def glue(self, side, target, permutation):
		assert(self.glued_to[side] is None)
		assert(target.glued_to[permutation[side]] is None)
		assert(not permutation.is_even())
		
		self.glued_to[side] = (target, permutation)
		target.glued_to[permutation[side]] = (self, permutation.inverse())
	
	def unglue(self, side):
		if self.glued_to[side] is not None:
			other, perm = self.glued_to[side]
			other.glued_to[perm[side]] = None
			self.glued_to[side] = None

# A class to represent a layered triangulation over a surface specified by an Abstract_Triangulation.
# Warning: Layered_Triangulation modifies itself in place!
# Perhaps when I'm feeling purer I'll come back and redo this.
class Layered_Triangulation:
	def __init__(self, abstract_triangulation):
		self.lower_triangulation = abstract_triangulation.copy()
		self.upper_triangulation = abstract_triangulation.copy()
		
		lower_tetrahedra = [Tetrahedra(i) for i in range(abstract_triangulation.num_triangles)]
		upper_tetrahedra = [Tetrahedra(i + abstract_triangulation.num_triangles) for i in range(abstract_triangulation.num_triangles)]
		for lower, upper in zip(lower_tetrahedra, upper_tetrahedra):
			lower.glue(3, upper, Permutation((0,2,1,3)))
		
		self.core_triangulation = lower_tetrahedra + upper_tetrahedra
		
		# We store two maps, one from the lower triangulation and one from the upper.
		# Each is a dictionary sending each Abstract_Triangle of lower/upper_triangulation to a pair (Tetrahedra, permutation).
		self.lower_map = dict((lower, (lower_tetra, Permutation((0,1,2,3)))) for lower, lower_tetra in zip(self.lower_triangulation, lower_tetrahedra))
		self.upper_map = dict((upper, (upper_tetra, Permutation((0,2,1,3)))) for upper, upper_tetra in zip(self.upper_triangulation, upper_tetrahedra))
	
	def __repr__(self):
		s = 'Core tri:\n'
		s += '\n'.join(str(tetra) for tetra in self.core_triangulation)
		s += '\nUpper tri:\n' + str(self.upper_triangulation)
		s += '\nLower tri:\n' + str(self.lower_triangulation)
		s += '\nUpper map: ' + str(self.upper_map)
		s += '\nLower map: ' + str(self.lower_map)
		return s
	
	def new_tetrahedra(self):
		self.core_triangulation.append(Tetrahedra(len(self.core_triangulation)))
		return self.core_triangulation[-1]
	
	def delete_tetrahedra(self, tetra):
		for i in range(4):
			tetra.unglue(i)
		self.core_triangulation.remove(tetra)
	
	def flip(self, edge_index):
		# MEGA WARNINNG: This is reliant on knowing how Abstract_Triangulation.flip() relabels things!
		assert(self.upper_triangulation.edge_is_flippable(edge_index))
		
		# Get a new tetrahedra.
		new_tetrahedra = self.new_tetrahedra()
		
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
		
		(new_A, new_side_A), (new_B, new_side_B) = new_upper_triangulation.find_edge(edge_index)
		new_upper_map[new_A] = (object_A, Permutation((0,2,1,3)))
		new_upper_map[new_B] = (object_B, Permutation((0,2,1,3)))
		
		# Finally, install the new objects.
		self.upper_triangulation = new_upper_triangulation
		self.upper_map = new_upper_map
	
	def close(self, isometry):
		for triangle in self.upper_triangulation:
			matching_triangle, cycle = isometry[triangle]
			perm = Permutation([cycle, (cycle+1)%3, (cycle+2)%3, 3])
			
			A, perm_A = self.upper_map[triangle]
			B, perm_B = self.lower_map[matching_triangle]
			
			below_A, perm_down_A = A.glued_to[3]
			below_B, perm_down_B = B.glued_to[3]
			
			self.delete_tetrahedra(A)
			self.delete_tetrahedra(B)
			below_A.glue(perm_down_A[3], below_B, perm_down_B * perm_B * perm * perm_A.inverse() * perm_down_A.inverse())
		
		# The maps are now (almost) meaningless so get rid of them.
		self.upper_map = {}
		self.lower_map = {}

if __name__ == '__main__':
	L = Layered_Triangulation(Abstract_Triangulation([[0,2,1], [0,2,1]]))
	print(L)
	L.flip(2)
	L.flip(1)
	L.flip(1)
	print('------------------------------')
	print(L)
	isoms = L.upper_triangulation.all_isometries(L.lower_triangulation)
	isom = isoms[0]
	print('------------------------------')
	print('Isometry: ', isom)
	L.close(isom)
	print('------------------------------')
	print(L)
	
