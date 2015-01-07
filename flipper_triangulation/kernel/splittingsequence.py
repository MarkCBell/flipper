
''' A module for representing a splitting sequence of a triangulation.

Provides one class: SplittingSequence. '''

import flipper

def permutation_from_pair(a, to_a, b, to_b):
	''' Return the odd permutation in Sym(4) which sends a to to_a and b to to_b. '''
	
	image = [None] * 4
	image[a] = to_a
	image[b] = to_b
	c, d = set(range(4)).difference([a, b])
	to_c, to_d = set(range(4)).difference([to_a, to_b])
	
	perm1 = flipper.kernel.Permutation([{a: to_a, b: to_b, c: to_c, d: to_d}[i] for i in range(4)])
	perm2 = flipper.kernel.Permutation([{a: to_a, b: to_b, c: to_d, d: to_c}[i] for i in range(4)])
	if not perm1.is_even():
		return perm1
	elif not perm2.is_even():
		return perm2
	else:
		raise ValueError('Does not represent a gluing.')

class SplittingSequence(object):
	''' This represents a sequence of flips of an Triangulation. '''
	def __init__(self, laminations, encodings, isometry, index):
		assert(isinstance(laminations, (list, tuple)))
		assert(all(isinstance(lamination, flipper.kernel.Lamination) for lamination in laminations))
		assert(isinstance(encodings, (list, tuple)))
		assert(all(edge_index is None or isinstance(edge_index, flipper.IntegerType) for edge_index, _ in encodings))
		assert(all(isinstance(encoding, flipper.kernel.Encoding) for _, encoding in encodings))
		assert(isinstance(isometry, flipper.kernel.Isometry))
		assert(isinstance(index, flipper.IntegerType))
		
		self.laminations = laminations
		self.edge_flips, self.encodings = zip(*encodings)
		self.isometry = isometry
		
		self.index = index
		self.lamination = self.laminations[index]
		self.triangulation = self.lamination.triangulation
		self.periodic_flips = self.edge_flips[self.index:]
		
		self.preperiodic = flipper.kernel.product(self.encodings[:self.index])
		self.periodic = flipper.kernel.product(self.encodings[self.index:])
		self.mapping_class = self.isometry.encode() * self.periodic
		
		self.preperiodic_length = sum(1 for edge in self.edge_flips[:self.index] if edge is not None)
		self.periodic_length = len(self.edge_flips) - self.index  # == sum(1 for edge in self.edge_flips[self.index:] if edge is not None)
	
	def dilatation(self):
		''' Return the dilatation of the corresponding mapping class (as a float). '''
		
		return float(self.periodic(self.lamination).weight()) / float(self.lamination.weight())
	
	def bundle(self):
		''' Return the corresponding veering layered triangulation of the corresponding mapping torus. '''
		
		# Move over a lot of data.
		VEERING_LEFT, VEERING_RIGHT = flipper.kernel.triangulation3.VEERING_LEFT, flipper.kernel.triangulation3.VEERING_RIGHT
		LONGITUDES, MERIDIANS = flipper.kernel.triangulation3.LONGITUDES, flipper.kernel.triangulation3.MERIDIANS
		TEMPS = flipper.kernel.triangulation3.TEMPS
		VERTICES_MEETING = flipper.kernel.triangulation3.VERTICES_MEETING
		EXIT_CUSP_LEFT, EXIT_CUSP_RIGHT = flipper.kernel.triangulation3.EXIT_CUSP_LEFT, flipper.kernel.triangulation3.EXIT_CUSP_RIGHT
		
		triangulation3 = flipper.kernel.Triangulation3(len(self.periodic_flips))
		lower_triangulation = self.triangulation.copy()
		upper_triangulation = self.triangulation.copy()
		
		# These are maps taking triangles of lower (respectively upper) triangulation to either:
		#  - A triangle of upper (resp. lower) triangulation, or
		#  - A triple (tetrahedron, permutation) of triangulation3.
		# We start with no tetrahedra, so these maps are just the identity map between the two triangulations.
		lower_map = dict((triangleA, triangleB) for triangleA, triangleB in zip(lower_triangulation, upper_triangulation))
		upper_map = dict((triangleB, triangleA) for triangleA, triangleB in zip(lower_triangulation, upper_triangulation))
		
		# We also use these two functions to quickly tell what a triangle maps to.
		maps_to_triangle = lambda X: isinstance(X, flipper.kernel.Triangle)
		maps_to_tetrahedron = lambda X: isinstance(X, tuple)  # == not maps_to_triangle(X).
		
		for tetrahedron, edge_index in zip(triangulation3, self.periodic_flips):
			# Get the new upper triangulation
			# The given edge_index must be flippable.
			new_upper_triangulation = upper_triangulation.flip_edge(edge_index)
			
			# Setup the next tetrahedron.
			tetrahedron.edge_labels[(0, 1)] = VEERING_RIGHT
			tetrahedron.edge_labels[(1, 2)] = VEERING_LEFT
			tetrahedron.edge_labels[(2, 3)] = VEERING_RIGHT
			tetrahedron.edge_labels[(0, 3)] = VEERING_LEFT
			
			# We'll glue it into the core_triangulation so that it's 1--3 edge lies over edge_index.
			# WARNINNG: This is reliant on knowing how flipper.kernel.Triangulation.flip_edge() relabels things!
			cornerA = upper_triangulation.corner_of_edge(edge_index)
			cornerB = upper_triangulation.corner_of_edge(~edge_index)
			(A, side_A), (B, side_B) = (cornerA.triangle, cornerA.side), (cornerB.triangle, cornerB.side)
			if maps_to_tetrahedron(upper_map[A]):
				tetra, perm = upper_map[A]
				# The permutation needs to: 2 |--> perm(3), 0 |--> perm(side_A), and be odd.
				tetrahedron.glue(2, tetra, permutation_from_pair(0, perm(side_A), 2, perm(3)))
			else:
				lower_map[upper_map[A]] = (tetrahedron, permutation_from_pair(side_A, 0, 3, 2))
			
			if maps_to_tetrahedron(upper_map[B]):
				tetra, perm = upper_map[B]
				# The permutation needs to: 2 |--> perm(3), 0 |--> perm(side_A), and be odd.
				tetrahedron.glue(0, tetra, permutation_from_pair(2, perm(side_B), 0, perm(3)))
			else:
				lower_map[upper_map[B]] = (tetrahedron, permutation_from_pair(side_B, 2, 3, 0))
			
			# Rebuild the upper_map.
			new_upper_map = dict()
			new_cornerA = new_upper_triangulation.corner_of_edge(edge_index)
			new_cornerB = new_upper_triangulation.corner_of_edge(~edge_index)
			new_A, new_B = new_cornerA.triangle, new_cornerB.triangle
			# Most of the triangles have stayed the same.
			# This relies on knowing how the upper_triangulation.flip_edge() function works.
			old_fixed_triangles = [triangle for triangle in upper_triangulation if triangle != A and triangle != B]
			new_fixed_triangles = [triangle for triangle in new_upper_triangulation if triangle != new_A and triangle != new_B]
			for old_triangle, new_triangle in zip(old_fixed_triangles, new_fixed_triangles):
				new_upper_map[new_triangle] = upper_map[old_triangle]
				if maps_to_triangle(upper_map[old_triangle]):  # Don't forget to update the lower_map too.
					lower_map[upper_map[old_triangle]] = new_triangle
			
			# This relies on knowing how the upper_triangulation.flip_edge() function works.
			new_upper_map[new_A] = (tetrahedron, flipper.kernel.Permutation((3, 0, 2, 1)))
			new_upper_map[new_B] = (tetrahedron, flipper.kernel.Permutation((1, 2, 0, 3)))
			
			# Finally, install the new objects.
			upper_triangulation = new_upper_triangulation
			upper_map = new_upper_map
		
		isometry = self.isometry.adapt(upper_triangulation, lower_triangulation)
		
		# This is a map which send each triangle of upper_triangulation via isometry to a pair:
		#	(triangle, permutation)
		# where triangle in lower_triangulation and lower_map[triangle] is NOT a triangle of
		# upper_triangulation.
		full_forwards = dict()
		for source_triangle in upper_triangulation:
			target_corner = isometry(source_triangle.corners[0])
			target_triangle = target_corner.triangle
			perm = flipper.kernel.permutation.cyclic_permutation(target_corner.side-0, 3)
			
			while maps_to_triangle(lower_map[target_triangle]):
				new_target_corner = isometry(lower_map[target_triangle].corners[0])
				target_triangle = new_target_corner.triangle
				perm = flipper.kernel.permutation.cyclic_permutation(new_target_corner.side-0, 3) * perm
			full_forwards[source_triangle] = (target_triangle, perm)
		
		# Now close the bundle up.
		for source_triangle in upper_triangulation:
			if maps_to_tetrahedron(upper_map[source_triangle]):
				A, perm_A = upper_map[source_triangle]
				target_triangle, perm = full_forwards[source_triangle]
				B, perm_B = lower_map[target_triangle]
				A.glue(perm_A(3), B, perm_B * perm.embed(4) * perm_A.inverse())
		
		# There should now be no unglued faces.
		assert(all(tetra.glued_to[side] is not None for tetra in triangulation3 for side in range(4)))
		
		# Construct an immersion of the fibre surface into the closed bundle.
		fibre_immersion = dict()
		for source_triangle in upper_triangulation:
			target_triangle, perm = full_forwards[source_triangle]
			
			B, perm_B = lower_map[target_triangle]
			fibre_immersion[source_triangle] = (B, perm_B * perm.embed(4))
		
		# Install longitudes and meridians.
		# This calls Triangulation3.assign_cusp_indices() which initialises:
		#  - Triangulation3.real_cusps
		#  - Triangulation3.fibre_slopes
		#  - Triangulation3.degeneracy_slopes
		cusps = triangulation3.install_peripheral_curves()
		
		# Now identify each the type of each cusp.
		for corner_class in upper_triangulation.corner_classes:
			vertex = corner_class[0].vertex
			label = vertex.label >= 0
			for corner in corner_class:
				tetrahedron, permutation = fibre_immersion[corner.triangle]
				index = tetrahedron.cusp_indices[permutation(corner.side)]
				if triangulation3.real_cusps[index] is None:
					triangulation3.real_cusps[index] = label
				else:
					assert(triangulation3.real_cusps[index] == label)
		
		# Compute fibre slopes.
		for index, cusp in enumerate(cusps):
			meridian_intersection, longitude_intersection = 0, 0
			for corner_class in upper_triangulation.corner_classes:
				corner = corner_class[0]
				tetra, perm = fibre_immersion[corner.triangle]
				if tetra.cusp_indices[perm(corner.side)] == index:
					for corner in corner_class:
						tetra, perm = fibre_immersion[corner.triangle]
						side, other = perm(corner.side), perm(3)
						meridian_intersection += tetra.peripheral_curves[MERIDIANS][side][other]
						longitude_intersection += tetra.peripheral_curves[LONGITUDES][side][other]
					triangulation3.fibre_slopes[index] = (longitude_intersection, -meridian_intersection)
					break
			else:
				raise RuntimeError('No vertex was mapped to this cusp.')
		
		# Compute degeneracy slopes.
		cusp_pairing = triangulation3.cusp_identification_map()
		for index, cusp in enumerate(cusps):
			triangulation3.clear_temp_peripheral_structure()
			
			# Set the degeneracy curve into the TEMPS peripheral structure.
			# First find a good starting point:
			start_tetrahedron, start_side = cusp[0]
			edge_labels = [start_tetrahedron.get_edge_label(start_side, other) for other in VERTICES_MEETING[start_side]]
			for i in range(3):
				if edge_labels[(i+1) % 3] == VEERING_RIGHT and edge_labels[(i+2) % 3] == VEERING_LEFT:
					start_other = VERTICES_MEETING[start_side][i]
					break
			
			# Then walk around, never crossing through an edge where both ends veer the same way.
			current_tetrahedron, current_side, current_other = start_tetrahedron, start_side, start_other
			while True:
				current_tetrahedron.peripheral_curves[TEMPS][current_side][current_other] += 1
				if start_tetrahedron.get_edge_label(current_side, current_other) == VEERING_LEFT:
					leave = EXIT_CUSP_LEFT[(current_side, current_other)]
				else:
					leave = EXIT_CUSP_RIGHT[(current_side, current_other)]
				current_tetrahedron.peripheral_curves[TEMPS][current_side][leave] -= 1
				current_tetrahedron, current_side, current_other = cusp_pairing[(current_tetrahedron, current_side, leave)]
				if (current_tetrahedron, current_side, current_other) == (start_tetrahedron, start_side, start_other):
					break
			
			triangulation3.degeneracy_slopes[index] = triangulation3.slope()
		
		return triangulation3

