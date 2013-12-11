
# We follow the orientation conventions in SnapPy/headers/kernel_typedefs.h L:154
# and SnapPy/kernel/peripheral_curves.c.

# Warning: Layered_Triangulation modifies itself in place!
# Perhaps when I'm feeling purer I'll come back and redo this.

from itertools import permutations, combinations, product
from time import sleep
try:
	from Queue import Queue
except ImportError: # Python 3
	from queue import Queue

try:
	from Source.Error import AssumptionError
except ImportError:
	from Error import AssumptionError

try:
	from Source.Permutation import Permutation, Id_Permutation
except ImportError:
	from Permutation import Permutation, Id_Permutation

all_permutations = [Permutation(perm) for perm in permutations(range(4), 4)]
even_permutations = [perm for perm in all_permutations if perm.is_even()]
odd_permutations = [perm for perm in all_permutations if not perm.is_even()]

def permutation_from_mapping(i, i_image, j, j_image, even):
	return [perm for perm in (even_permutations if even else odd_permutations) if perm[i] == i_image and perm[j] == j_image][0]

# Edge veerings:
UNKNOWN = None
LEFT = 0
RIGHT = 1
vertices_meeting = {0:(1,2,3), 1:(0,3,2), 2:(0,1,3), 3:(0,2,1)}  # This order was chosen so they appear ordered anti-clockwise from the cusp.

class Tetrahedron:
	def __init__(self, label=None):
		self.label = label
		self.glued_to = [None] * 4  # None or (Tetrahedron, permutation).
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
				a, b = sorted([a, b])
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
		s += ' %s %s %s %s\n' % tuple([str(gluing) for tetrahedra, gluing in self.glued_to])
		s += '%4d %4d %4d %4d \n' % tuple(self.cusp_indices)
		s += ' %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d\n' % tuple(cusp for meridian in self.meridians for cusp in meridian)
		s += '  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0\n'
		s += ' %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d\n' % tuple(cusp for longitude in self.longitudes for cusp in longitude)
		s += '  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0\n'
		s += '  0.000000000000   0.000000000000\n'
		return s

class Triangulation:
	def __init__(self, num_tetrahedra, name='Flipper_triangulation'):
		self.num_tetrahedra = num_tetrahedra
		self.tetrahedra = [Tetrahedron(i) for i in range(self.num_tetrahedra)]
		self.num_cusps = 0
		self.name = name
	
	def copy(self):
		# Returns a copy of this triangulation. We guarantee that the tetrahedra in the copy will come in the same order.
		new_triangulation = Triangulation(self.num_tetrahedra, self.name)
		forwards = dict(zip(self, new_triangulation))
		
		for tetrahedron in self:
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
		return '\n'.join(str(tetrahedron) for tetrahedron in self)
	
	def __iter__(self):
		return iter(self.tetrahedra)
	
	def __contains__(self, other):
		return other in self.tetrahedra
	
	def create_tetrahedra(self):
		self.tetrahedra.append(Tetrahedron(self.num_tetrahedra))
		self.num_tetrahedra += 1
		return self.tetrahedra[-1]
	
	def destroy_tetrahedra(self, tetrahedron):
		for side in range(4):
			tetrahedron.unglue(side)
		self.tetrahedra.remove(tetrahedron)
		self.num_tetrahedra -= 1
	
	def reindex(self):
		for index, tetrahedron in enumerate(self):
			tetrahedron.label = index
	
	def is_closed(self):
		return all(tetrahedron.glued_to[side] is not None for tetrahedron in self for side in range(4))
	
	def assign_cusp_indices(self):
		# Find the vertex classes.
		remaining_vertices = set(product(self, range(4)))
		
		vertex_classes = []
		while len(remaining_vertices) > 0:
			new_vertex_class = set([])
			to_explore = Queue()
			to_explore.put(remaining_vertices.pop())
			while not to_explore.empty():
				current_vertex = to_explore.get()
				new_vertex_class.add(current_vertex)
				current_tetrahedron, current_side = current_vertex
				for side in vertices_meeting[current_side]:
					if current_tetrahedron.glued_to[side] is not None:
						neighbour_tetrahedron, permutation = current_tetrahedron.glued_to[side]
						neighbour_side = permutation[current_side]
						neighbour_vertex = neighbour_tetrahedron, neighbour_side
						if neighbour_vertex in remaining_vertices:
							to_explore.put(neighbour_vertex)
							remaining_vertices.remove(neighbour_vertex)
			
			vertex_classes.append(list(new_vertex_class))
		
		# Then iterate through each one assigning cusp indices.
		for index, vertex_class in enumerate(vertex_classes):
			for tetrahedron, side in vertex_class:
				tetrahedron.cusp_indices[side] = index
		
		self.num_cusps = len(vertex_classes)
		
		return vertex_classes
	
	def SnapPy_string(self):
		if not self.is_closed(): raise AssumptionError('Layered triangulation is not closed.')
		# First make sure that all of the labellings are good.
		self.reindex()
		s = ''
		s += '% Triangulation\n'
		s += '%s\n' % self.name
		s += 'not_attempted  0.0\n'
		s += 'oriented_manifold\n'
		s += 'CS_unknown\n'
		s += '\n'
		s += '%d 0\n' % self.num_cusps
		for i in range(self.num_cusps):
			s += '    torus   0.000000000000   0.000000000000\n'
		s += '\n'
		s += '%d\n' % self.num_tetrahedra
		for tetrahedra in self:
			s += tetrahedra.SnapPy_string() + '\n'
		
		return s

# A class to represent a layered triangulation over a surface specified by an Abstract_Triangulation.
class Layered_Triangulation:
	def __init__(self, abstract_triangulation, name='Flipper_triangulation'):
		self.lower_triangulation = abstract_triangulation.copy()
		self.upper_triangulation = abstract_triangulation.copy()
		self.core_triangulation = Triangulation(2 * abstract_triangulation.num_triangles, name)
		
		lower_tetrahedra = self.core_triangulation.tetrahedra[:abstract_triangulation.num_triangles]
		upper_tetrahedra = self.core_triangulation.tetrahedra[abstract_triangulation.num_triangles:]
		for lower, upper in zip(lower_tetrahedra, upper_tetrahedra):
			lower.glue(3, upper, Permutation((0,2,1,3)))
		
		# We store two maps, one from the lower triangulation and one from the upper.
		# Each is a dictionary sending each Abstract_Triangle of lower/upper_triangulation to a pair (Tetrahedron, permutation).
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
	
	def flip(self, edge_index):
		# MEGA WARNINNG: This is reliant on knowing how Abstract_Triangulation.flip() relabels things!
		assert(self.upper_triangulation.edge_is_flippable(edge_index))
		
		# Get a new tetrahedra.
		new_tetrahedron = self.core_triangulation.create_tetrahedra()
		new_tetrahedron.edge_labels[(0,1)] = RIGHT
		new_tetrahedron.edge_labels[(1,2)] = LEFT
		new_tetrahedron.edge_labels[(2,3)] = RIGHT
		new_tetrahedron.edge_labels[(0,3)] = LEFT
		
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
		new_tetrahedron.glue(2, below_A, new_glue_perm_A)
		new_tetrahedron.glue(0, below_B, new_glue_perm_B)
		
		new_tetrahedron.glue(1, object_A, Permutation((2,3,1,0)))
		new_tetrahedron.glue(3, object_B, Permutation((1,0,2,3)))
		
		# Get the new upper triangulation
		new_upper_triangulation = self.upper_triangulation.flip_edge(edge_index)
		# Rebuild the upper_map.
		new_upper_map = dict()
		
		(new_A, new_side_A), (new_B, new_side_B) = new_upper_triangulation.find_edge(edge_index)
		for old_triangle, new_triangle in zip([triangle for triangle in self.upper_triangulation if triangle != A and triangle != B], [triangle for triangle in new_upper_triangulation if triangle != new_A and triangle != new_B]):
			new_upper_map[new_triangle] = self.upper_map[old_triangle]
		
		# This relies on knowing how the upper_triangulation.flip_edge() function works.
		new_upper_map[new_A] = (object_A, Permutation((0,2,1,3)))
		new_upper_map[new_B] = (object_B, Permutation((0,2,1,3)))
		
		# Finally, install the new objects.
		self.upper_triangulation = new_upper_triangulation
		self.upper_map = new_upper_map
		
		return self
	
	def flips(self, sequence):
		for edge_index in sequence:
			self.flip(edge_index)
	
	def close(self, isometry):
		isometry = isometry.adapt_isometry(self.upper_triangulation, self.lower_triangulation)  # This hides involutions of S_1_1!
		
		# Duplicate the bundle.
		closed_triangulation = self.core_triangulation.copy()
		# The tetrahedra in the closed triangulation are guaranteed to be in the same order so we can get away with this.
		forwards = dict(zip(self.core_triangulation, closed_triangulation))
		upper_tetrahedra = [self.upper_map[triangle][0] for triangle in self.upper_map]
		
		# Remove the boundary tetrahedra.
		for triangle in self.upper_triangulation:
			A, perm_A = self.upper_map[triangle]
			closed_triangulation.destroy_tetrahedra(forwards[A])
		for triangle in self.lower_triangulation:
			B, perm_B = self.lower_map[triangle]
			closed_triangulation.destroy_tetrahedra(forwards[B])
		
		# These are maps which push the upper and lower triangulations in just a bit.
		core_lower_map = dict()
		for triangle in self.lower_triangulation:
			B, perm_B = self.lower_map[triangle]
			above_B, perm_up = B.glued_to[3]
			core_lower_map[triangle] = (above_B, perm_up * perm_B)
		
		core_upper_map = dict()
		for triangle in self.upper_triangulation:
			A, perm_A = self.upper_map[triangle]
			below_A, perm_down = A.glued_to[3]
			core_upper_map[triangle] = (below_A, perm_down * perm_A)
		
		paired = dict()
		# This is a map which send each triangle of self.upper_triangulation via isometry to a pair:
		#	(triangle, permutation)
		# where triangle is either a triangle in self.lower_triangulation or a triangle in
		# self.upper_triangulation, if it is directly paired with one.
		for source_triangle in self.upper_triangulation:
			target_triangle, perm = isometry[source_triangle]
			B, perm_B = core_lower_map[target_triangle]
			
			if B in upper_tetrahedra:
				hit_triangle = [T for T in self.upper_triangulation if self.upper_map[T][0] == B][0]
				A, perm_A = self.upper_map[hit_triangle]
				paired[source_triangle] = (hit_triangle, perm_A.inverse() * perm_B * perm.embed(4))
			else:
				paired[source_triangle] = (target_triangle, perm.embed(4))
		
		# Now close the bundle up.
		for source_triangle in self.upper_triangulation:
			target_triangle, perm = paired[source_triangle]
			
			# We might have to map repeatedly until we get back to the core part of the triangulation.
			while target_triangle in self.upper_triangulation:
				new_target_triangle, new_perm = paired[target_triangle]
				target_triangle = new_target_triangle
				perm = new_perm * perm
			
			A, perm_A = core_upper_map[source_triangle]
			B, perm_B = core_lower_map[target_triangle]
			if forwards[A] in closed_triangulation:
				forwards[A].glue(perm_A[3], forwards[B], perm_B * perm * perm_A.inverse())
		
		# Install the cusp indices.
		cusps = closed_triangulation.assign_cusp_indices()
		
		# Install some longitude and meridian on each cusp.
		# We will choose ones that come from pushing some curve embedded in the one-skeleton of the cusp torus triangulation 
		# off in some direction.
		if False:
			longitude_installed = dict((corner, False) for cusp in cusps for corner in cusp)
			# We'll define some maps to help us move around.
			exit_cusp_left  = {(0,1):3, (0,2):1, (0,3):2, (1,0):2, (1,2):3, (1,3):0, (2,0):3, (2,1):0, (2,3):1, (3,0):1, (3,1):2, (3,2):0}
			exit_cusp_right = {(0,1):2, (0,2):3, (0,3):1, (1,0):3, (1,2):0, (1,3):2, (2,0):1, (2,1):3, (2,3):0, (3,0):2, (3,1):0, (3,2):1}
			
			for cusp in cusps:
				all_edges = [(tetrahedron, side, other) for tetrahedron, side in cusp for other in vertices_meeting[side]]
				pair = dict()
				for tetrahedron, side, other in all_edges:
					other_tetrahedron, perm = tetrahedron.glued_to[other]
					pair[(tetrahedron, side, other)] = (other_tetrahedron, perm[side], perm[other])
				
				# Find a basis for homology.
				
				labels = dict((key, min(key, pair[key])) for key in pair)
		
			# Now figure out what slope the boundary of the fibre has. (And the degeneracy slope?)
			# Find the fibre and degeneracy slope on each cusp.
			# We'll work on each cusp one at a time.
			for corner_class in self.lower_triangulation.corner_classes:
				for triangle, side in corner_class:
					tetrahedron, permutation = immerse_fibre_map[triangle]
			
			for cusp in cusps:
				# Find just the right starting spot. We want one such that when we do one step to the left we don't pass through the fibre.
				for starting_tetrahedron, starting_side in cusp:
					if (starting_side == 0 and (starting_tetrahedron, 2) in fibre_surface) or (starting_side == 2 and (starting_tetrahedron, 0) in fibre_surface):
						# Put in the meridian.
						current_tetrahedron, current_side = starting_tetrahedron, starting_side
						
						arrive = 3 if starting_side == 0 else 1
						leave = UNKNOWN
						path = [(starting_tetrahedron, starting_side, arrive, leave, UNKNOWN)]
						
						while len(path) <= 1 or current_tetrahedron != starting_tetrahedron or current_side != starting_side:
							current_tetrahedron, current_side, arrive, leave, turn = path[-1]
							if turn == UNKNOWN:
								leave = exit_cusp_left[(current_side, arrive)]
								path[-1] = (current_tetrahedron, current_side, arrive, leave, LEFT)
								if (current_tetrahedron, leave) not in fibre_surface:
									current_tetrahedron, permutation = current_tetrahedron.glued_to[leave]
									current_side = permutation[current_side]
									arrive = permutation[leave]
									leave = UNKNOWN
									path.append((current_tetrahedron, current_side, arrive, leave, UNKNOWN))
							elif turn == LEFT:
								leave = exit_cusp_right[(current_side, arrive)]
								path[-1] = (current_tetrahedron, current_side, arrive, leave, RIGHT)
								if (current_tetrahedron, leave) not in fibre_surface:
									current_tetrahedron, permutation = current_tetrahedron.glued_to[leave]
									current_side = permutation[current_side]
									arrive = permutation[leave]
									leave = UNKNOWN
									path.append((current_tetrahedron, current_side, arrive, leave, UNKNOWN))
							elif turn == RIGHT:
								assert(len(path) > 0)
								path.pop()
						
						for tetrahedron, side, arrive, leave, turn in path[:-1]:
							tetrahedron.meridians[side][arrive] = +1
							tetrahedron.meridians[side][leave] = -1
						
						# Put in the longitude.
						current_tetrahedron, current_side = starting_tetrahedron, starting_side
						
						# Go upwards until you reach a cusp which contains the meridian.
						arrive = 3
						passed_through_fibre_surface = False
						while not passed_through_fibre_surface or current_tetrahedron.meridians[current_side] == [0,0,0,0]:
							leave = 1
							current_tetrahedron.longitudes[current_side][leave] = -1
							current_tetrahedron, permutation = current_tetrahedron.glued_to[leave]
							current_side = permutation[current_side]
							arrive = permutation[leave]
							current_tetrahedron.longitudes[current_side][arrive] = +1
							if (current_tetrahedron, arrive) not in fibre_surface: passed_through_fibre_surface = True
						
						# Then follow through whatever side the meridian leaves through until you reach the starting cusp again.
						while current_tetrahedron != starting_tetrahedron or current_side != starting_side:
							# print(starting_tetrahedron, starting_side, current_tetrahedron, current_side)
							# print(current_tetrahedron.meridians[current_side])
							leave = [side for side in range(4) if current_tetrahedron.meridians[current_side][side] == -1][0]
							current_tetrahedron.longitudes[current_side][leave] = -1
							current_tetrahedron, permutation = current_tetrahedron.glued_to[leave]
							current_side = permutation[current_side]
							arrive = permutation[leave]
							current_tetrahedron.longitudes[current_side][arrive] = +1
						
						break
		
		# Compute degeneracy slopes.
		degeneracy_slopes = []
		
		return closed_triangulation, degeneracy_slopes

if __name__ == '__main__':
	from Lamination import invariant_lamination
	from Examples import Example_S_1_1 as Example, build_example_mapping_class
	# from Examples import Example_12 as Example, build_example_mapping_class
	
	# Get an example mapping class - this one we know is pseudo-Anosov.
	word, mapping_class = build_example_mapping_class(Example, word='aB')
	# If this computation fails it will throw an AssumptionError - the map _is_ reducible
	# or a ComputationError - the map is probably reducible.
	# At the minute we just assume that it doesn't.
	lamination, dilatation = invariant_lamination(mapping_class, exact=True)
	# If this computation fails it will throw an AssumptionError - the lamination is not filling and so our map is not pseudo-Anosov.
	# At the minute we just assume that it doesn't.
	preperiodic, periodic, new_dilatation, correct_lamination, isometries = lamination.splitting_sequence()
	
	L = Layered_Triangulation(correct_lamination.abstract_triangulation, word)
	L.flips(periodic)
	M, degeneracy_slopes = L.close(isometries[0])  # There may be more than one isometry, for now let's just pick the first. We'll worry about this eventually.
	print(M.SnapPy_string())
