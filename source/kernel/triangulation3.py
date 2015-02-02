
''' A module for representing triangulations of 3--manifolds.

Provides two classes: Tetrahedron and Triangulation3. '''

# We use right-handed tetrahedra, see SnapPy/headers/kernel_typedefs.h.
#
# We follow the orientation conventions in SnapPy/headers/kernel_typedefs.h L:154
# and SnapPy/kernel/peripheral_curves.c.

import flipper

from itertools import permutations, combinations, product

# Edge veerings:
VEERING_UNKNOWN, VEERING_LEFT, VEERING_RIGHT = None, 0, 1
# Peripheral curve types:
PERIPHERAL_TYPES = list(range(3))
LONGITUDES, MERIDIANS, TEMPS = PERIPHERAL_TYPES
# Tetrahedron geometry:
# This order was chosen so they appear ordered anti-clockwise from the cusp.
VERTICES_MEETING = {0: (1, 2, 3), 1: (0, 3, 2), 2: (0, 1, 3), 3: (0, 2, 1)}
# If you enter cusp a through side b then EXIT_CUSP_LEFT[(a, b)] is the side to your left.
EXIT_CUSP_LEFT = {
	(0, 1): 3, (0, 2): 1, (0, 3): 2,
	(1, 0): 2, (1, 2): 3, (1, 3): 0,
	(2, 0): 3, (2, 1): 0, (2, 3): 1,
	(3, 0): 1, (3, 1): 2, (3, 2): 0
	}
# Similarly EXIT_CUSP_RIGHT[(a, b)] is the side to your right.
EXIT_CUSP_RIGHT = {
	(0, 1): 2, (0, 2): 3, (0, 3): 1,
	(1, 0): 3, (1, 2): 0, (1, 3): 2,
	(2, 0): 1, (2, 1): 3, (2, 3): 0,
	(3, 0): 2, (3, 1): 0, (3, 2): 1
	}

class Tetrahedron(object):
	''' This represents a tetrahedron. '''
	def __init__(self, label):
		assert(isinstance(label, flipper.IntegerType))
		
		self.label = label
		self.glued_to = [None] * 4  # Each entry is either: None or (Tetrahedron, permutation).
		self.cusp_indices = [-1, -1, -1, -1]
		self.peripheral_curves = [[[0, 0, 0, 0] for _ in range(4)] for _ in PERIPHERAL_TYPES]
		self.edge_labels = dict((vertex_pair, VEERING_UNKNOWN) for vertex_pair in combinations(range(4), r=2))
		self.vertex_labels = [None, None, None, None]
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return 'Label: %s, Gluings: %s' % (self.label, self.glued_to)
	
	def glue(self, side, target, permutation):
		''' Glue the given side of this tetrahedron to target via the given permutation.
		
		You are not supposed to unglue tetrahedra as they automatically install a lot
		of additional structure.'''
		
		if self.glued_to[side] is None:
			assert(self.glued_to[side] is None)
			assert(target.glued_to[permutation(side)] is None)
			assert(not permutation.is_even())
			
			self.glued_to[side] = (target, permutation)
			target.glued_to[permutation(side)] = (self, permutation.inverse())
			
			# Move across the edge veerings too.
			for a, b in combinations(VERTICES_MEETING[side], 2):
				x, y = permutation(a), permutation(b)
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
	
	def get_edge_label(self, a, b):
		''' Return the label on edge (a) -- (b) of this tetrahedron. '''
		
		a, b = min(a, b), max(a, b)
		return self.edge_labels[(a, b)]
	
	def set_edge_label(self, a, b, value):
		''' Set the label on edge (a) -- (b) of this tetrahedron. '''
		
		a, b = min(a, b), max(a, b)
		self.edge_labels[(a, b)] = value
	
	def snappy_string(self):
		''' Return the SnapPy string describing this tetrahedron. '''
		
		strn = ''
		strn += '%4d %4d %4d %4d \n' % tuple([tetrahedra.label for tetrahedra, gluing in self.glued_to])
		strn += ' %4s %4s %4s %4s\n' % tuple([gluing.compressed_string() for tetrahedra, gluing in self.glued_to])
		strn += '%4d %4d %4d %4d \n' % tuple(self.cusp_indices)
		strn += ' %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d\n' % tuple(cusp for meridian in self.peripheral_curves[MERIDIANS] for cusp in meridian)
		strn += '  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0\n'
		strn += ' %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d %2d\n' % tuple(cusp for longitude in self.peripheral_curves[LONGITUDES] for cusp in longitude)
		strn += '  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0\n'
		strn += '  0.000000000000 0.000000000000\n'
		return strn

class Triangulation3(object):
	''' This represents triangulation, that is a collection of tetrahedra. '''
	def __init__(self, num_tetrahedra):
		assert(isinstance(num_tetrahedra, flipper.IntegerType))
		
		self.num_tetrahedra = num_tetrahedra
		self.tetrahedra = [Tetrahedron(i) for i in range(self.num_tetrahedra)]
		self.num_cusps = -1
		self.real_cusps = []
		self.fibre_slopes = []
		self.degeneracy_slopes = []
	
	def copy(self):
		''' Return a copy of this triangulation.
		
		We guarantee that the tetrahedra in the copy will come in the same order. '''
		
		new_triangulation = Triangulation3(self.num_tetrahedra)
		forwards = dict(zip(self, new_triangulation))
		
		for tetrahedron in self:
			for side in range(4):
				if tetrahedron.glued_to[side] is not None:
					neighbour, permutation = tetrahedron.glued_to[side]
					forwards[tetrahedron].glue(side, forwards[neighbour], permutation)
			
			forwards[tetrahedron].cusp_indices = list(tetrahedron.cusp_indices)
			forwards[tetrahedron].peripheral_curves = [[list(tetrahedron.peripheral_curves[curve_type][side]) for side in range(4)] for curve_type in PERIPHERAL_TYPES]
			forwards[tetrahedron].edge_labels = dict(tetrahedron.edge_labels)
			forwards[tetrahedron].vertex_labels = tetrahedron.vertex_labels
		
		return new_triangulation
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		return '\n'.join(str(tetrahedron) for tetrahedron in self)
	
	def __iter__(self):
		return iter(self.tetrahedra)
	
	def clear_temp_peripheral_structure(self):
		''' Remove all TEMP peripheral curves. '''
		
		for tetrahedron in self.tetrahedra:
			tetrahedron.peripheral_curves[TEMPS] = [[0, 0, 0, 0] for _ in range(4)]
	
	def is_closed(self):
		''' Return if this triangulation is closed. '''
		
		return all(tetrahedron.glued_to[side] is not None for tetrahedron in self for side in range(4))
	
	def assign_cusp_indices(self):
		''' Assign the tetrahedra in this triangulation their cusp indices and return the list of corners in the same cusp.
		
		This triangulation must be closed. '''
		
		assert(self.is_closed())
		
		vertex_classes = []
		remaining_vertices = list(product(self, range(4)))
		while remaining_vertices:
			# We do a depth first search to find all vertices in this cusp.
			new_vertex = remaining_vertices.pop()
			new_vertex_class = [new_vertex]
			# This is a stack of triangles that may still have consequences.
			to_explore = [new_vertex]
			while to_explore:
				current_tetrahedron, current_side = to_explore.pop()
				for side in VERTICES_MEETING[current_side]:
					neighbour_tetrahedron, permutation = current_tetrahedron.glued_to[side]
					neighbour_side = permutation(current_side)
					neighbour_vertex = neighbour_tetrahedron, neighbour_side
					if neighbour_vertex in remaining_vertices:
						to_explore.append(neighbour_vertex)
						new_vertex_class.append(neighbour_vertex)
						remaining_vertices.remove(neighbour_vertex)
			
			vertex_classes.append(new_vertex_class)
		
		# Then iterate through each one assigning cusp indices.
		for index, vertex_class in enumerate(vertex_classes):
			for tetrahedron, side in vertex_class:
				tetrahedron.cusp_indices[side] = index
		
		self.num_cusps = len(vertex_classes)
		self.real_cusps = [None] * self.num_cusps
		self.fibre_slopes = [(0, 0)] * self.num_cusps
		self.degeneracy_slopes = [(0, 0)] * self.num_cusps
		
		return vertex_classes
	
	def cusp_identification_map(self):
		''' Return a dictionary pairing the sides of the peripheral triangles. '''
		
		cusp_pairing = dict()
		for tetrahedron in self.tetrahedra:
			for side in range(4):
				for other in VERTICES_MEETING[side]:
					neighbour_tetrahedron, permutation = tetrahedron.glued_to[other]
					neighbour_side, neighbour_other = permutation(side), permutation(other)
					cusp_pairing[(tetrahedron, side, other)] = (neighbour_tetrahedron, neighbour_side, neighbour_other)
		
		return cusp_pairing
	
	def intersection_number(self, peripheral_type_a, peripheral_type_b, cusp=None):
		''' Return the algebraic intersection number between the specified peripheral types.
		
		See SnapPy/kernel_code/intersection_numbers.c for more information.
		
		Convention:
		    B
		    ^
		    |
		 ---+---> A
		    |
		    |
		has intersection +1. '''
		
		# This is the number of strands flowing from A to B. It is negative if they go in the opposite direction.
		flow = lambda A, B: 0 if (A < 0) == (B < 0) else (A if (A < 0) != (A < -B) else -B)
		
		if cusp is None: cusp = product(self.tetrahedra, range(4))
		
		intersection_number = 0
		# Count intersection numbers along edges.
		for tetrahedron, side in cusp:
			periph_a = tetrahedron.peripheral_curves[peripheral_type_a]
			periph_b = tetrahedron.peripheral_curves[peripheral_type_b]
			
			for other in VERTICES_MEETING[side]:
				intersection_number -= periph_a[side][other] * periph_b[side][other]
		
		intersection_number = intersection_number // 2
		
		# and then within each face.
		for tetrahedron, side in cusp:
			periph_a = tetrahedron.peripheral_curves[peripheral_type_a]
			periph_b = tetrahedron.peripheral_curves[peripheral_type_b]
			
			for other in VERTICES_MEETING[side]:
				left = EXIT_CUSP_LEFT[(side, other)]
				right = EXIT_CUSP_RIGHT[(side, other)]
				
				intersection_number += flow(periph_a[side][other], periph_a[side][left]) * flow(periph_b[side][other], periph_b[side][left])
				intersection_number += flow(periph_a[side][other], periph_a[side][right]) * flow(periph_b[side][other], periph_b[side][left])
		
		return intersection_number
	
	def install_peripheral_curves(self):
		''' Assign a longitude and meridian to each cusp. '''
		
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
			T = flipper.kernel.create_triangulation(edge_labels)
			
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
							current_tetrahedron, current_side, arrive = next_tetrahedron, perm(current_side), perm(leave)
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
	
	def slope(self):
		''' Return the slope of the peripheral curve in TEMPS relative to the set meridians and longitudes.
		
		Assumes that the meridian and longitude on this cusp have been set. '''
		
		longitude_intersection = self.intersection_number(LONGITUDES, TEMPS)
		meridian_intersection = self.intersection_number(MERIDIANS, TEMPS)
		
		# So the number of copies of the longitude and the meridian that we need to represent the path is:
		longitude_copies = -meridian_intersection
		meridian_copies = longitude_intersection
		
		return (meridian_copies, longitude_copies)
	
	def snappy_string(self, name='flipper triangulation', filled=True):
		''' Return the SnapPy string describing this triangulation.
		
		If filled=True then the fake cusps that we had to install are filled
		along the fibre slope.
		
		This triangulation must be closed. '''
		
		assert(isinstance(name, flipper.StringType))
		assert(isinstance(filled, bool))
		
		assert(self.is_closed())
		
		strn = ''
		strn += '% Triangulation\n'
		strn += '%s\n' % name
		strn += 'not_attempted 0.0\n'
		strn += 'oriented_manifold\n'
		strn += 'CS_unknown\n'
		strn += '\n'
		strn += '%d 0\n' % self.num_cusps
		for i in range(self.num_cusps):
			if filled and not self.real_cusps[i]:
				strn += '    torus %16.12f %16.12f\n' % self.fibre_slopes[i]
			else:
				strn += '    torus   0.000000000000   0.000000000000\n'
		strn += '\n'
		strn += '%d\n' % self.num_tetrahedra
		for tetrahedra in self:
			strn += tetrahedra.snappy_string() + '\n'
		
		return strn

