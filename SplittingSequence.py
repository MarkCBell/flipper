from AbstractTriangulation import Abstract_Triangulation
from Error import ComputationError, AssumptionError
from Symbolic_Computation import simplify, compute_powers

def puncture_trigons(abstract_triangulation, vector):
	# We label real punctures with a 0 and fake ones created by this process with a 1.
	new_labels = []
	new_corner_labels = []
	new_vector = list(vector)
	zeta = abstract_triangulation.zeta
	for triangle in abstract_triangulation.triangles:
		a, b, c = triangle.edge_indices
		if new_vector[a] + new_vector[b] > new_vector[c] and new_vector[b] + new_vector[c] > new_vector[a] and new_vector[c] + new_vector[a] > new_vector[b]:
			x, y, z = zeta, zeta+1, zeta+2
			new_labels.append([a,z,y])
			new_labels.append([b,x,z])
			new_labels.append([c,y,x])
			new_corner_labels.append([1,0,0])
			new_corner_labels.append([1,0,0])
			new_corner_labels.append([1,0,0])
			new_vector.append((new_vector[b] + new_vector[c] - new_vector[a]) / 2)
			new_vector.append((new_vector[c] + new_vector[a] - new_vector[b]) / 2)
			new_vector.append((new_vector[a] + new_vector[b] - new_vector[c]) / 2)
			zeta = zeta + 3
		else:
			new_labels.append([a,b,c])
			new_corner_labels.append([0,0,0])
	
	return Abstract_Triangulation(new_labels, new_corner_labels), new_vector

def collapse_trivial_weight(abstract_triangulation, lamination, edge_index):
	# Assumes that the given edge does not connect between two real vertices, that is vertices
	# with label 0. If not an AssumptionError is thrown.
	
	# !?! TO DO: Still an error in here when a == d, see 'cbccbaAbbccACaCccAbaacCaccBCca'.
	
	assert(lamination[edge_index] == 0)
	
	# We'll first compute the new corner labels. This way we can check if our assumption is False
	# early and so save some work.
	
	base_triangle, base_side = abstract_triangulation.find_edge(edge_index)[0]
	corner_A_label = base_triangle.corner_labels[(base_side + 1) % 3]
	corner_B_label = base_triangle.corner_labels[(base_side + 2) % 3]
	if corner_A_label == 0 and corner_B_label == 0:
		raise AssumptionError('Edge connects between two vertices labelled 0.')
	elif corner_A_label == 0 and corner_B_label == 1:
		good_corner_label = corner_A_label
		bad_corner_class = abstract_triangulation.find_corner_class(base_triangle, (base_side+2) % 3)
	elif corner_A_label == 1 and corner_B_label == 0:
		good_corner_label = corner_B_label
		bad_corner_class = abstract_triangulation.find_corner_class(base_triangle, (base_side+1) % 3)
	elif corner_A_label == 1 and corner_B_label == 1:
		good_corner_label = corner_A_label
		bad_corner_class = abstract_triangulation.find_corner_class(base_triangle, (base_side+2) % 3)
	
	new_corner_labels = [[triangle.corner_labels[side] if (triangle, side) not in bad_corner_class else good_corner_label for side in range(3)] for triangle in abstract_triangulation if edge_index not in triangle]
	
	a, b, c, d = abstract_triangulation.find_indicies_of_square_about_edge(edge_index)  # Get the square about it.
	
	# WLOG: a < b and c < d.
	if b < a: a, b = b, a
	if d < c: c, d = d, c
	
	# replacement is a map sending 0,...,abstract_triangulation.zeta to 0,...,abstract_triangulation.zeta-3. It skips mapping edge_index anywhere
	# and maps b to where a is sent and d to where c is sent.
	replacement = dict(zip([i for i in range(abstract_triangulation.zeta) if i not in [edge_index, b, d]], range(abstract_triangulation.zeta)))
	replacement[b] = replacement[a]
	replacement[d] = replacement[c]
	
	new_labels = [[replacement[i] for i in triangle] for triangle in abstract_triangulation if edge_index not in triangle]
	new_vector = [[lamination[j] for j in range(abstract_triangulation.zeta) if j != edge_index and replacement[j] == i][0] for i in range(abstract_triangulation.zeta - 3)]
	
	return Abstract_Triangulation(new_labels, new_corner_labels), new_vector

def compute_splitting_sequence(abstract_triangulation, lamination):
	# Assumes that lamination is a filling lamination. If not, it will discover this along the way and throw an 
	# AssumptionError
	# We assume that lamination is given as a list of algebraic numbers. 
	# We continually use Symbolic_Computation.simplify() just to be safe.
	# This assumes that the edges are labelled 0, ..., abstract_triangulation.zeta-1, this is a very sane labelling system.
	
	# We use this function to hash the number down. It MUST be (projectively) invariant under isometries of the triangulation.
	# We take the coefficients of the minimal polynomial of each entry and sort them.
	def hash_vector(vector):
		return tuple(sorted(([tuple(v.minpoly().coefficients()) for v in projectivise_vector(vector)])))
	
	def projectivise_vector(vector):
		s = simplify(sum(vector))
		return tuple([simplify(v / s) for v in vector])
	
	# Check if vector is obviously reducible.
	if any(v == 0 for v in lamination):
		raise AssumptionError('Lamination is not filling.')
	
	working_copy, lamination_copy = puncture_trigons(abstract_triangulation, lamination)  # Puncture out all trigon regions.
	flipped = []
	seen = {hash_vector(lamination_copy):[[0, list(lamination_copy), projectivise_vector(lamination_copy), working_copy]]}
	while True:
		i = max(range(working_copy.zeta), key=lambda i: lamination_copy[i])  # Find the index of the largest entry
		a, b, c, d = working_copy.find_indicies_of_square_about_edge(i)  # Get the square about it.
		working_copy = working_copy.flip_edge(i)  # Flip the square.
		lamination_copy[i] = simplify(max(lamination_copy[a] + lamination_copy[c], lamination_copy[b] + lamination_copy[d]) - lamination_copy[i])  # Update the weights.
		
		if lamination_copy[i] == 0:
			try:
				# Here collapse_trivial_weight uses the assumption that lamination is filling.
				working_copy, lamination_copy = collapse_trivial_weight(working_copy, lamination_copy, i)
			except AssumptionError:
				raise AssumptionError('Lamination is not filling.')
		
		flipped.append(i)
		
		projective_lamination = projectivise_vector(lamination_copy)
		# if len(flipped) % 20 == 0: print(flipped[-20:])  # Every once in a while show how we're progressing.
		
		# Check if it (projectively) matches a lamination we've already seen.
		target = hash_vector(lamination_copy)
		if target in seen:
			for index, old_lamination, old_projective_vector, old_triangulation in seen[target]:
				for isometry in working_copy.all_isometries(old_triangulation):
					permuted_old_projective_vector = tuple([old_projective_vector[isometry.edge_map[i]] for i in range(working_copy.zeta)])
					if projective_lamination == permuted_old_projective_vector:
						# Return: the pre-periodic part, the periodic part, the dilatation.
						return flipped[:index], flipped[index:], simplify(old_lamination[isometry.edge_map[0]] / lamination_copy[0])
			seen[target].append([len(flipped), list(lamination_copy), list(projective_lamination), working_copy])
		else:
			seen[target] = [[len(flipped), list(lamination_copy), list(projective_lamination), working_copy]]

def splitting_sequence_to_encoding(abstract_triangulation, sequence):
	encoding = Id_Encoding_Sequence(abstract_triangulation)
	for edge_index in sequence:
		forwards, backwards = encoding.target_triangulation.encode_flip()
		encoding = forwards * encoding
	
	return encoding

if __name__ == '__main__':
	from random import choice
	from time import time
	from Encoding import Id_Encoding_Sequence
	from Error import ComputationError
	
	# This is a 36--gon with one vertex at the centre and opposite sides identified.
	# T = Abstract_Triangulation([[18, 19, 0], [20, 1, 19], [21, 2, 20], [21, 22, 3], [22, 23, 4], [24, 5, 23], [25, 6, 24], [25, 26, 7], [27, 8, 26], [27, 28, 9], [28, 29, 10], [30, 11, 29], 
	# [31, 12, 30], [31, 32, 13], [32, 33, 14], [34, 15, 33], [35, 16, 34], [35, 36, 17], [36, 37, 0], [38, 1, 37], [39, 2, 38], [39, 40, 3], [40, 41, 4], [42, 5, 41],
	# [43, 6, 42], [43, 44, 7], [44, 45, 8], [46, 9, 45], [47, 10, 46], [47, 48, 11], [48, 49, 12], [50, 13, 49], [51, 14, 50], [51, 52, 15], [52, 53, 16], [18, 17,53]])
	# a = T.encode_twist([1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
	# A = T.encode_twist([1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], k=-1)
	# b = T.encode_twist([0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
	# B = T.encode_twist([0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], k=-1)
	
	# p = T.all_isometries(T, as_Encodings=True)[1]  # This is a click of some sort.
	# print('Start')
	# h = (a*B*B*a*p)**3
	# print('Lamination')
	# V, dilatation = h.stable_lamination(exact=True)
	# print('Splitting')
	# x, y, z = compute_splitting_sequence(T, V)
	# print(len(x), len(y), compute_powers(dilatation, z))
	
	# T = Abstract_Triangulation([[6, 7, 0], [8, 1, 7], [8, 9, 2], [9, 10, 3], [11, 4, 10], [12, 5, 11], 
	# [12, 13, 0], [14, 1, 13], [14, 15, 2], [15, 16, 3], [16, 17, 4], [6, 5, 17]])  # This a 12--gon with one vertex at the centre and opposite sides identified.
	# a = T.encode_twist([1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0])
	# A = T.encode_twist([1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], k=-1)
	# b = T.encode_twist([1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0])
	# B = T.encode_twist([1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0], k = -1)
	
	# p = T.all_isometries(T, as_Encodings=True)[1]  # I've checked, this is a 1/12 click of a 12--gon.
	
	# print('Start')
	# h = (b*A*A*b*p)**6
	# print('Lamination')
	# V, dilatation = h.stable_lamination(exact=True)
	# print('Splitting')
	# x, y, z = compute_splitting_sequence(T, V)
	# print(len(x), len(y), compute_powers(dilatation, z))
	
	
	# T = Abstract_Triangulation([[12, 13, 0], [14, 1, 13], [15, 2, 14], [15, 16, 3], [17, 4, 16], [17, 18, 5], 
		# [18, 19, 6], [20, 7, 19], [21, 8, 20], [21, 22, 9], [22, 23, 10], [24, 11, 23], [25, 0, 24], [25, 26, 1], 
		# [26, 27, 2], [28, 3, 27], [29, 4, 28], [29, 30, 5], [30, 31, 6], [32, 7, 31], [33, 8, 32], [33, 34, 9], 
		# [34, 35, 10], [12, 11, 35]])  # Another n--gon. (n==24)
	
	# a = T.encode_twist([0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
	# A = T.encode_twist([0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], k=-1)
	# b = T.encode_twist([0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0])
	# B = T.encode_twist([0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], k=-1)
	
	# p = T.all_isometries(T, as_Encodings=True)[1]  # I've checked, this is a 1/24 click of a 24--gon.
	# print('Start')
	# h = (a*B*B*a*p)**3
	# print('Lamination')
	# V, dilatation = h.stable_lamination(exact=True)
	# print('Splitting')
	# x, y, z = compute_splitting_sequence(T, V)
	# print(len(x), len(y), compute_powers(dilatation, z))
	
	# S_1_2: We'll do some random twists.
	T = Abstract_Triangulation([[2, 1, 3], [2, 0, 4], [1, 5, 0], [4, 3, 5]])
	a = T.encode_twist([0,0,1,1,1,0])
	b = T.encode_twist([0,1,0,1,0,1])
	c = T.encode_twist([1,0,0,0,1,1])
	A = T.encode_twist([0,0,1,1,1,0], k=-1)
	B = T.encode_twist([0,1,0,1,0,1], k=-1)
	C = T.encode_twist([1,0,0,0,1,1], k=-1)
	
	def expand_class(string):
		print(string)
		h = Id_Encoding_Sequence(T)
		for letter in string:
			h = {'a':a, 'b':b, 'c':c, 'A':A, 'B':B, 'C':C}[letter] * h
		return h
	
	def random_mapping_class(n):
		return ''.join(choice('abcABC') for i in range(n))
	
	print('Start')
	random_length = 50
	num_trials = 50
	total_time = 0
	for k in range(num_trials):
		# h = (a*b*C*b)**k * (a*b*C) * (B*c*B*A)**k
		# h = expand_class(random_mapping_class(10))
		# h = expand_class('cbccbaAbbccACaCccAbaacCaccBCca')
		# h = expand_class('aBc')
		h = expand_class(random_mapping_class(random_length))
		
		start_time = time()
		
		if h.is_periodic():
			print(' -- Periodic.')
		else:
			try:
				V, dilatation = h.stable_lamination(exact=True)
				x, y, z = compute_splitting_sequence(T, V)
				print(' -- Pseudo-Anosov.')
			except ComputationError:
				print(' ~~ Probably reducible.')
			except AssumptionError:
				print(' -- Reducible.')
		t1 = time() - start_time
		print('      (Time: %0.4f)' % t1)
		total_time += t1
	
	print('Average decision time for %d trials: %0.4fs' % (num_trials, total_time / num_trials))
