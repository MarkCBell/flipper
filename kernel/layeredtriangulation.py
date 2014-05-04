
# We follow the orientation conventions in SnapPy/headers/kernel_typedefs.h L:154
# and SnapPy/kernel/peripheral_curves.c.

# Warning: LayeredTriangulation3 modifies itself in place!
# Perhaps when I'm feeling purer I'll come back and redo this.

from itertools import permutations, combinations, product
from copy import deepcopy
try:
	from Queue import Queue
except ImportError: # Python 3
	from queue import Queue

import flipper

# Edge veerings:
VEERING_UNKNOWN = None
VEERING_LEFT = 0
VEERING_RIGHT = 1
SOURCE = -1
# Peripheral curve types:
PERIPHERAL_TYPES = list(range(3))
LONGITUDES, MERIDIANS, TEMPS = PERIPHERAL_TYPES
# Tetrahedron geometry:
VERTICES_MEETING = {0:(1, 2, 3), 1:(0, 3, 2), 2:(0, 1, 3), 3:(0, 2, 1)} # This order was chosen so they appear ordered anti-clockwise from the cusp.
EXIT_CUSP_LEFT = {(0, 1):3, (0, 2):1, (0, 3):2, (1, 0):2, (1, 2):3, (1, 3):0, (2, 0):3, (2, 1):0, (2, 3):1, (3, 0):1, (3, 1):2, (3, 2):0}
EXIT_CUSP_RIGHT = {(0, 1):2, (0, 2):3, (0, 3):1, (1, 0):3, (1, 2):0, (1, 3):2, (2, 0):1, (2, 1):3, (2, 3):0, (3, 0):2, (3, 1):0, (3, 2):1}

class Tetrahedron(object):
	''' This represents a tetrahedron. '''
	def __init__(self, label=None):
		self.label = label
		self.glued_to = [None] * 4 # Each entry is either: None or (Tetrahedron, permutation).
		self.cusp_indices = [-1, -1, -1, -1]
		self.peripheral_curves = [[[0, 0, 0, 0] for _ in range(4)] for _ in PERIPHERAL_TYPES]
		self.edge_labels = dict((vertex_pair, VEERING_UNKNOWN) for vertex_pair in combinations(range(4), r=2))
		self.vertex_labels = [None, None, None, None]
	
	def __repr__(self):
		return str(self.label)
	
	def __str__(self):
		return 'Label: %s, Gluings: %s' % (self.label, self.glued_to) #, Edge labels: %s' % (self.label, self.glued_to, [self.edge_labels[i] for i in combinations(range(4), 2)])
	
	def glue(self, side, target, permutation):
		if self.glued_to[side] is None:
			assert(self.glued_to[side] is None)
			assert(target.glued_to[permutation[side]] is None)
			assert(not permutation.is_even())
			
			self.glued_to[side] = (target, permutation)
			target.glued_to[permutation[side]] = (self, permutation.inverse())
			
			# Move across the edge veerings too.
			for a, b in combinations(VERTICES_MEETING[side], 2):
				x, y = permutation[a], permutation[b]
				my_edge_veering = self.get_edge_label(a, b)
				his_edge_veering = target.get_edge_label(x, y)
				if my_edge_veering == VEERING_UNKNOWN and his_edge_veering != VEERING_UNKNOWN:
					self.set_edge_label(a, b, his_edge_veering)
				elif my_edge_veering != VEERING_UNKNOWN and his_edge_veering == VEERING_UNKNOWN:
					target.set_edge_label(x, y, my_edge_veering)
				elif my_edge_veering != VEERING_UNKNOWN and his_edge_veering != VEERING_UNKNOWN:
					assert(my_edge_veering == his_edge_veering)
		else:
			assert((target, permutation) == self.glued_to[side])
	
	def unglue(self, side):
		if self.glued_to[side] is not None:
			other, perm = self.glued_to[side]
			other.glued_to[perm[side]] = None
			self.glued_to[side] = None
	
	def get_edge_label(self, a, b):
		a, b = min(a, b), max(a, b)
		return self.edge_labels[(a, b)]
	
	def set_edge_label(self, a, b, value):
		a, b = min(a, b), max(a, b)
		self.edge_labels[(a, b)] = value
	
	def snappy_string(self):
		s = ''
		s += '%4d %4d %4d %4d \n' % tuple([tetrahedra.label for tetrahedra, gluing in self.glued_to])
		s += ' %s %s %s %s\n' % tuple([gluing.compressed_string() for tetrahedra, gluing in self.glued_to])
		s += '%4d %4d %4d %4d \n' % tuple(self.cusp_indices)
		s += ' %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d\n' % tuple(cusp for meridian in self.peripheral_curves[MERIDIANS] for cusp in meridian)
		s += ' 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n'
		s += ' %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d\n' % tuple(cusp for longitude in self.peripheral_curves[LONGITUDES] for cusp in longitude)
		s += ' 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n'
		s += ' 0.000000000000 0.000000000000\n'
		return s

class Triangulation3(object):
	''' This represents triangulation, that is a collection of tetrahedra. '''
	def __init__(self, num_tetrahedra):
		self.num_tetrahedra = num_tetrahedra
		self.tetrahedra = [Tetrahedron(i) for i in range(self.num_tetrahedra)]
		self.num_cusps = 0
		self.cusp_types = []
		self.fibre_slopes = []
		self.degeneracy_slopes = []
	
	def copy(self):
		# Returns a copy of this triangulation. We guarantee that the tetrahedra in the copy will come in the same order.
		new_triangulation = Triangulation3(self.num_tetrahedra)
		forwards = dict(zip(self, new_triangulation))
		
		for tetrahedron in self:
			for side in range(4):
				if tetrahedron.glued_to[side] is not None:
					neighbour, permutation = tetrahedron.glued_to[side]
					forwards[tetrahedron].glue(side, forwards[neighbour], permutation)
			
			forwards[tetrahedron].cusp_indices = list(tetrahedron.cusp_indices)
			forwards[tetrahedron].peripheral_curves = deepcopy(tetrahedron.peripheral_curves)
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
		self.num_tetrahedra -= 1 # !?! This makes tetrahedron names non-unique.
	
	def reindex(self):
		for index, tetrahedron in enumerate(self):
			tetrahedron.label = index
	
	def clear_temp_peripheral_structure(self):
		for tetrahedron in self.tetrahedra:
			tetrahedron.peripheral_curves[TEMPS] = [[0, 0, 0, 0] for _ in range(4)]
	
	def is_closed(self):
		return all(tetrahedron.glued_to[side] is not None for tetrahedron in self for side in range(4))
	
	def assign_cusp_indices(self):
		# Find the vertex classes.
		remaining_vertices = list(product(self, range(4)))
		
		vertex_classes = []
		while len(remaining_vertices) > 0:
			new_vertex_class = []
			to_explore = Queue()
			to_explore.put(remaining_vertices.pop())
			while not to_explore.empty():
				current_vertex = to_explore.get()
				new_vertex_class.append(current_vertex)
				current_tetrahedron, current_side = current_vertex
				for side in VERTICES_MEETING[current_side]:
					if current_tetrahedron.glued_to[side] is not None:
						neighbour_tetrahedron, permutation = current_tetrahedron.glued_to[side]
						neighbour_side = permutation[current_side]
						neighbour_vertex = neighbour_tetrahedron, neighbour_side
						if neighbour_vertex in remaining_vertices:
							to_explore.put(neighbour_vertex)
							remaining_vertices.remove(neighbour_vertex)
			
			vertex_classes.append(new_vertex_class)
		
		# Then iterate through each one assigning cusp indices.
		for index, vertex_class in enumerate(vertex_classes):
			for tetrahedron, side in vertex_class:
				tetrahedron.cusp_indices[side] = index
		
		self.num_cusps = len(vertex_classes)
		
		return vertex_classes
	
	def cusp_identification_map(self):
		cusp_pairing = dict()
		for tetrahedron in self.tetrahedra:
			for side in range(4):
				for other in VERTICES_MEETING[side]:
					neighbour_tetrahedron, permutation = tetrahedron.glued_to[other]
					neighbour_side, neighbour_other = permutation[side], permutation[other]
					cusp_pairing[(tetrahedron, side, other)] = (neighbour_tetrahedron, neighbour_side, neighbour_other)
		
		return cusp_pairing
	
	def intersection_number(self, peripheral_type_a, peripheral_type_b, cusp=None):
		# Computes the algebraic intersection number between the specified peripheral types.
		# See SnapPy/kernel_code/intersection_numbers.c for how to do this.
		
		# Convention:
		# B
		# ^
		# |
		# ---+---> A
		# |
		# |
		# has intersection +1.
		
		# This is the number of strands flowing from A to B. It is negative if they go in the opposite direction.
		flow = lambda A, B: 0 if (A < 0) == (B < 0) else (A if (A < 0) != (A < -B) else -B)
		
		if cusp is None: cusp = product(self.tetrahedra, range(4))
		
		intersection_number = 0
		# Count intersection numbers along edges.
		for tetrahedron, side in cusp:
			for other in VERTICES_MEETING[side]:
				intersection_number -= tetrahedron.peripheral_curves[peripheral_type_a][side][other] * tetrahedron.peripheral_curves[peripheral_type_b][side][other]
		
		intersection_number = intersection_number // 2
		
		# and then within each face.
		for tetrahedron, side in cusp:
			for other in VERTICES_MEETING[side]:
				left = EXIT_CUSP_LEFT[(side, other)]
				right = EXIT_CUSP_RIGHT[(side, other)]
				intersection_number += flow(tetrahedron.peripheral_curves[peripheral_type_a][side][other], tetrahedron.peripheral_curves[peripheral_type_a][side][left]) * flow(tetrahedron.peripheral_curves[peripheral_type_b][side][other], tetrahedron.peripheral_curves[peripheral_type_b][side][left])
				intersection_number += flow(tetrahedron.peripheral_curves[peripheral_type_a][side][other], tetrahedron.peripheral_curves[peripheral_type_a][side][right]) * flow(tetrahedron.peripheral_curves[peripheral_type_b][side][other], tetrahedron.peripheral_curves[peripheral_type_b][side][left])
		
		return intersection_number
	
	def install_longitudes_and_meridians(self):
		# Install the cusp indices.
		cusps = self.assign_cusp_indices()
		cusp_pairing = self.cusp_identification_map()
		
		# Blank out the longitudes and meridians.
		for peripheral_type in [LONGITUDES, MERIDIANS]:
			for tetrahedron in self.tetrahedra:
				for side in range(4):
					for other in range(4):
						tetrahedron.peripheral_curves[peripheral_type][side][other] = 0
		
		# Install a longitude and meridian on each cusp one at a time.
		for cusp in cusps:
			# Build a triangulation of the cusp neighbourhood.
			label = 0
			edge_label_map = dict()
			for tetrahedron, side in cusp:
				for other in VERTICES_MEETING[side]:
					key = (tetrahedron, side, other)
					if key not in edge_label_map:
						edge_label_map[key] = label
						edge_label_map[cusp_pairing[key]] = ~label
						label += 1
			
			edge_labels = [[edge_label_map[(tetrahedron, side, other)] for other in VERTICES_MEETING[side]] for tetrahedron, side in cusp]
			T = flipper.AbstractTriangulation(edge_labels)
			
			# Get a basis for H_1.
			homology_basis_paths = T.homology_basis()
			
			# Install the longitude and meridian. # !?! Double check and optimise this.
			for peripheral_type in [LONGITUDES, MERIDIANS]:
				first, last = homology_basis_paths[peripheral_type][0], homology_basis_paths[peripheral_type][-1]
				# Find a starting point.
				for tetrahedron, side in cusp:
					for a, b in permutations(VERTICES_MEETING[side], 2):
						if edge_label_map[(tetrahedron, side, a)] == ~first and edge_label_map[(tetrahedron, side, b)] == last:
							current_tetrahedron, current_side, arrive = tetrahedron, side, b
				
				for other in homology_basis_paths[peripheral_type]:
					for a in VERTICES_MEETING[current_side]:
						if edge_label_map[(current_tetrahedron, current_side, a)] == ~other:
							leave = a
							current_tetrahedron.peripheral_curves[peripheral_type][current_side][arrive] += 1
							current_tetrahedron.peripheral_curves[peripheral_type][current_side][leave] -= 1
							next_tetrahedron, perm = current_tetrahedron.glued_to[leave]
							current_tetrahedron, current_side, arrive = next_tetrahedron, perm[current_side], perm[leave]
							break
			
			# Compute the algebraic intersection number between the longitude and meridian we just installed.
			# If the it is -1 then we need to reverse the direction of the meridian.
			# See SnapPy/kernel_code/intersection_numbers.c for how to do this.
			intersection_number = self.intersection_number(LONGITUDES, MERIDIANS, cusp)
			assert(abs(intersection_number) == 1)
			
			# We might need to reverse the orientation of .
			# If the it is -1 then we need to reverse the direction of one of them (we choose the meridian).
			if intersection_number < 0:
				for tetrahedron, side in cusp:
					for other in VERTICES_MEETING[side]:
						tetrahedron.peripheral_curves[MERIDIANS][side][other] = -tetrahedron.peripheral_curves[MERIDIANS][side][other]
		
		return cusps
	
	def slope(self, path):
		# Returns the slope of the peripheral curve given by path relative to the set meridians and longitudes. 
		# Assumes that the meridian and longitude on this cusp have been set.
		
		# These are the algebraic intersection numbers between the path and the meridian and longitude.
		meridian_intersection = sum(tetrahedron.peripheral_curves[MERIDIANS][side][other] for (tetrahedron, side, other) in path)
		longitude_intersection = sum(tetrahedron.peripheral_curves[LONGITUDES][side][other] for (tetrahedron, side, other) in path)
		
		# So the number of copies of the longitude and the meridian that we need to represent the path is:
		longitude_copies = -meridian_intersection
		meridian_copies = longitude_intersection
		
		return (meridian_copies, longitude_copies)
	
	def slope_TEMPS(self):
		# Returns the slope of the peripheral curve in TEMPS relative to the set meridians and longitudes. 
		# Assumes that the meridian and longitude on this cusp have been set.
		
		# See Triangulation3.slope(path).
		longitude_intersection = self.intersection_number(LONGITUDES, TEMPS)
		meridian_intersection = self.intersection_number(MERIDIANS, TEMPS)
		longitude_copies = -meridian_intersection
		meridian_copies = longitude_intersection
		
		return (meridian_copies, longitude_copies)
	
	def snappy_string(self, name='flipper triangulation'):
		if not self.is_closed(): raise flipper.AssumptionError('Layered triangulation is not closed.')
		# First make sure that all of the labellings are good.
		self.reindex()
		s = ''
		s += '% Triangulation3\n'
		s += '%s\n' % name
		s += 'not_attempted 0.0\n'
		s += 'oriented_manifold\n'
		s += 'CS_unknown\n'
		s += '\n'
		s += '%d 0\n' % self.num_cusps
		s += ' torus 0.000000000000 0.000000000000\n' * self.num_cusps
		s += '\n'
		s += '%d\n' % self.num_tetrahedra
		for tetrahedra in self:
			s += tetrahedra.snappy_string() + '\n'
		
		return s

# A class to represent a layered triangulation over a surface specified by a flipper.kernel.AbstractTriangulation.
class LayeredTriangulation(object):
	''' This represents a Triangulation3 which has maps from a pair of AbstractTriangulations into is boundary. ''' 
	def __init__(self, abstract_triangulation):
		self.lower_triangulation = abstract_triangulation.copy()
		self.upper_triangulation = abstract_triangulation.copy()
		self.core_triangulation = Triangulation3(2 * abstract_triangulation.num_triangles)
		
		lower_tetrahedra = self.core_triangulation.tetrahedra[:abstract_triangulation.num_triangles]
		upper_tetrahedra = self.core_triangulation.tetrahedra[abstract_triangulation.num_triangles:]
		for lower, upper in zip(lower_tetrahedra, upper_tetrahedra):
			lower.glue(3, upper, flipper.kernel.Permutation((0, 2, 1, 3)))
		
		# We store two maps, one from the lower triangulation and one from the upper.
		# Each is a dictionary sending each AbstractTriangle of lower/upper_triangulation to a pair (Tetrahedron, permutation).
		self.lower_map = dict((lower, (lower_tetra, flipper.kernel.Permutation((0, 1, 2, 3)))) for lower, lower_tetra in zip(self.lower_triangulation, lower_tetrahedra))
		self.upper_map = dict((upper, (upper_tetra, flipper.kernel.Permutation((0, 2, 1, 3)))) for upper, upper_tetra in zip(self.upper_triangulation, upper_tetrahedra))
	
	def __repr__(self):
		s = 'Core tri:\n'
		s += '\n'.join(str(tetra) for tetra in self.core_triangulation)
		s += '\nUpper tri:\n' + str(self.upper_triangulation)
		s += '\nLower tri:\n' + str(self.lower_triangulation)
		s += '\nUpper map: ' + str(self.upper_map)
		s += '\nLower map: ' + str(self.lower_map)
		return s
	
	def flip(self, edge_index):
		# MEGA WARNINNG: This is reliant on knowing how flipper.kernel.AbstractTriangulation.flip_edge() relabels things!
		assert(self.upper_triangulation.is_flippable(edge_index))
		
		# Get a new tetrahedra.
		new_tetrahedron = self.core_triangulation.create_tetrahedra()
		new_tetrahedron.edge_labels[(0, 1)] = VEERING_RIGHT
		new_tetrahedron.edge_labels[(1, 2)] = VEERING_LEFT
		new_tetrahedron.edge_labels[(2, 3)] = VEERING_RIGHT
		new_tetrahedron.edge_labels[(0, 3)] = VEERING_LEFT
		
		# We'll glue it into the core_triangulation so that it's 1--3 edge lies over edge_index.
		cornerA = self.upper_triangulation.find_edge(edge_index)
		cornerB = self.upper_triangulation.find_edge(~edge_index)
		(A, side_A), (B, side_B) = (cornerA.triangle, cornerA.side), (cornerB.triangle, cornerB.side)
		object_A, perm_A = self.upper_map[A]
		object_B, perm_B = self.upper_map[B]
		
		below_A, down_perm_A = object_A.glued_to[perm_A[3]]
		below_B, down_perm_B = object_B.glued_to[perm_A[3]]
		
		object_A.unglue(3)
		object_B.unglue(3)
		
		# Do some gluings.
		new_glue_perm_A = flipper.kernel.permutation.permutation_from_mapping(4, [(0, down_perm_A[perm_A[side_A]]), (2, down_perm_A[perm_A[3]])], even=False)
		new_glue_perm_B = flipper.kernel.permutation.permutation_from_mapping(4, [(2, down_perm_B[perm_B[side_B]]), (0, down_perm_B[perm_A[3]])], even=False)
		new_tetrahedron.glue(2, below_A, new_glue_perm_A)
		new_tetrahedron.glue(0, below_B, new_glue_perm_B)
		
		new_tetrahedron.glue(1, object_A, flipper.kernel.Permutation((2, 3, 1, 0)))
		new_tetrahedron.glue(3, object_B, flipper.kernel.Permutation((1, 0, 2, 3)))
		
		# Get the new upper triangulation
		new_upper_triangulation = self.upper_triangulation.flip_edge(edge_index)
		
		# Rebuild the upper_map.
		new_upper_map = dict()
		cornerA = new_upper_triangulation.find_edge(edge_index)
		cornerB = new_upper_triangulation.find_edge(~edge_index)
		(new_A, new_side_A), (new_B, new_side_B) = (cornerA.triangle, cornerA.side), (cornerB.triangle, cornerB.side)
		# Most of the triangles have stayed the same.
		old_fixed_triangles = [triangle for triangle in self.upper_triangulation if triangle != A and triangle != B]
		new_fixed_triangles = [triangle for triangle in new_upper_triangulation if triangle != new_A and triangle != new_B]
		for old_triangle, new_triangle in zip(old_fixed_triangles, new_fixed_triangles):
			new_upper_map[new_triangle] = self.upper_map[old_triangle]
		
		# This relies on knowing how the upper_triangulation.flip_edge() function works.
		new_upper_map[new_A] = (object_A, flipper.kernel.Permutation((0, 2, 1, 3)))
		new_upper_map[new_B] = (object_B, flipper.kernel.Permutation((0, 2, 1, 3)))
		
		# Finally, install the new objects.
		self.upper_triangulation = new_upper_triangulation
		self.upper_map = new_upper_map
		
		return self
	
	def flips(self, sequence):
		for edge_index in sequence:
			self.flip(edge_index)
	
	def upper_lower_isometries(self):
		# Returns a list of all isometries that can currently be used to close the layered triangulation
		# up into a bundle.
		return self.upper_triangulation.all_isometries(self.lower_triangulation)
	
	def close(self, isometry):
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
		
		# This is a map which send each triangle of self.upper_triangulation via isometry to a pair:
		#	(triangle, permutation)
		# where triangle is either a triangle in self.lower_triangulation or a triangle in
		# self.upper_triangulation, if it is directly paired with one.
		paired = dict()
		for source_triangle in self.upper_triangulation:
			target_triangle, perm = isometry.triangle_image(source_triangle)
			B, perm_B = core_lower_map[target_triangle]
			
			if B in upper_tetrahedra:
				hit_triangle = [T for T in self.upper_triangulation if self.upper_map[T][0] == B][0]
				A, perm_A = self.upper_map[hit_triangle]
				paired[source_triangle] = (hit_triangle, perm_A.inverse() * perm_B * perm.embed(4))
			else:
				paired[source_triangle] = (target_triangle, perm.embed(4))
		
		# This is the map obtained by repeatedly applying the paired map until you land in the lower triangulation.
		full_fowards = dict()
		for source_triangle in self.upper_triangulation:
			target_triangle, perm = paired[source_triangle]
			
			# We might have to map repeatedly until we get back to the lower triangulation.
			while target_triangle not in self.lower_triangulation:
				new_target_triangle, new_perm = paired[target_triangle]
				target_triangle = new_target_triangle
				perm = new_perm * perm
			
			full_fowards[source_triangle] = (target_triangle, perm)
		
		# Now close the bundle up.
		for source_triangle in self.upper_triangulation:
			target_triangle, perm = full_fowards[source_triangle]
			
			A, perm_A = core_upper_map[source_triangle]
			B, perm_B = core_lower_map[target_triangle]
			if forwards[A] in closed_triangulation:
				forwards[A].glue(perm_A[3], forwards[B], perm_B * perm * perm_A.inverse())
		
		# Construct an immersion of the fibre surface into the closed bundle.
		fibre_immersion = dict()
		for source_triangle in self.upper_triangulation:
			target_triangle, perm = full_fowards[source_triangle]
			
			B, perm_B = core_lower_map[target_triangle]
			fibre_immersion[source_triangle] = (forwards[B], perm_B * perm)
		
		# Install longitudes and meridians.
		cusps = closed_triangulation.install_longitudes_and_meridians()
		
		# Now identify each the type of each cusp.
		cusp_types = [None] * closed_triangulation.num_cusps
		for triangle in self.upper_triangulation:
			tetrahedron, permutation = fibre_immersion[triangle]
			for side in range(3):
				label = 0 if triangle.corner_labels[side] == 0 else 1
				if cusp_types[tetrahedron.cusp_indices[permutation[side]]] is None:
					cusp_types[tetrahedron.cusp_indices[permutation[side]]] = label
				else:
					assert(cusp_types[tetrahedron.cusp_indices[permutation[side]]] == label)
		
		# Compute longitude slopes.
		fibre_slopes = [None] * closed_triangulation.num_cusps
		for index, cusp in enumerate(cusps):
			for vertex in self.upper_triangulation.vertices:
				corner = vertex[0]
				tetra, perm = fibre_immersion[corner.triangle]
				if tetra.cusp_indices[perm[corner.side]] == index:
					fibre_path = []
					for corner in vertex:
						tetra, perm = fibre_immersion[corner.triangle]
						fibre_path.append((tetra, perm[corner.side], perm[3]))
					fibre_slopes[index] = closed_triangulation.slope(fibre_path)
					break
			else:
				assert(False)
		
		# Compute degeneracy slopes.
		degeneracy_slopes = [None] * closed_triangulation.num_cusps
		cusp_pairing = closed_triangulation.cusp_identification_map()
		for index, cusp in enumerate(cusps):
			closed_triangulation.clear_temp_peripheral_structure()
			
			# Set the degeneracy curve into the TEMPS peripheral structure.
			start_tetrahedron, start_side = cusp[0]
			NV = VERTICES_MEETING[start_side]
			start_other = NV[min(i for i in range(3) if start_tetrahedron.get_edge_label(start_side, NV[(i+1) % 3]) == VEERING_RIGHT and start_tetrahedron.get_edge_label(start_side, NV[(i+2) % 3]) == VEERING_LEFT)]
			
			current_tetrahedron, current_side, current_other = start_tetrahedron, start_side, start_other
			while True:
				current_tetrahedron.peripheral_curves[TEMPS][current_side][current_other] += 1
				leave = (EXIT_CUSP_LEFT if start_tetrahedron.get_edge_label(current_side, current_other) == VEERING_LEFT else EXIT_CUSP_RIGHT)[(current_side, current_other)]
				current_tetrahedron.peripheral_curves[TEMPS][current_side][leave] -= 1
				current_tetrahedron, current_side, current_other = cusp_pairing[(current_tetrahedron, current_side, leave)]
				if (current_tetrahedron, current_side, current_other) == (start_tetrahedron, start_side, start_other):
					break
			
			degeneracy_slopes[index] = closed_triangulation.slope_TEMPS()
		
		closed_triangulation.cusp_types = cusp_types
		closed_triangulation.fibre_slopes = fibre_slopes
		closed_triangulation.degeneracy_slopes = degeneracy_slopes
		
		return closed_triangulation

