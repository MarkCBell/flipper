
try:
	from Source.AbstractTriangulation import Abstract_Triangulation
	from Source.Encoding import encode_flip
	from Source.Lamination import Lamination, stable_lamination
	from Source.Error import AssumptionError
	from Source.Symbolic_Computation import simplify, compute_powers, minimal_polynomial_coefficients
except ImportError:
	from AbstractTriangulation import Abstract_Triangulation
	from Encoding import encode_flip
	from Lamination import Lamination, key_curves, stable_lamination
	from Error import AssumptionError
	from Symbolic_Computation import simplify, compute_powers, minimal_polynomial_coefficients

def puncture_trigons(lamination):
	# We label real punctures with a 0 and fake ones created by this process with a 1.
	new_labels = []
	new_corner_labels = []
	new_vector = list(lamination.vector)
	zeta = lamination.zeta
	for triangle in lamination.abstract_triangulation:
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
	
	return Lamination(Abstract_Triangulation(new_labels, new_corner_labels), new_vector)

def collapse_trivial_weight(lamination, edge_index):
	# Assumes that abstract_triangulation is not S_{0,3}. Assumes that the given 
	# edge does not connect between two real vertices, that is vertices with 
	# label 0. Assumes that edge_index is the only edge of weight 0.
	# If any of these assumptions are not met an AssumptionError is thrown.
	
	assert(lamination[edge_index] == 0)
	
	a, b, c, d = lamination.abstract_triangulation.find_indicies_of_square_about_edge(edge_index)  # Get the square about it.
	
	# We'll first deal with some bad cases that con occur when some of the sides of the square are in fact the same.
	if a == b or c == d:
		# This means that lamination[a] (respectively lamination[c] == 0).
		raise AssumptionError('Additional weightless edge.')
	
	# There is at most one duplicated pair.
	if a == d and b == c:
		# We're on S_{0,3}.
		raise AssumptionError('Underlying surface is S_{0,3}.')
	
	if a == c and a == d:
		# We're on the square torus, there's only one vertex so both endpoints of this edge must be labelled 0.
		raise AssumptionError('Edge connects between two vertices labelled 0.')
	
	# We'll first compute the new corner labels. This way we can check if our assumption is False early and so save some work.
	base_triangle, base_side = lamination.abstract_triangulation.find_edge(edge_index)[0]
	corner_A_label = base_triangle.corner_labels[(base_side + 1) % 3]
	corner_B_label = base_triangle.corner_labels[(base_side + 2) % 3]
	if corner_A_label == 0 and corner_B_label == 0:
		raise AssumptionError('Edge connects between two vertices labelled 0.')
	
	# We'll replace the labels on the corner class with higher labels with the label from the lower
	good_corner_label = min(corner_A_label, corner_B_label)
	if corner_A_label < corner_B_label:
		bad_corner_class = lamination.abstract_triangulation.find_corner_class(base_triangle, (base_side+2) % 3)
	else:
		bad_corner_class = lamination.abstract_triangulation.find_corner_class(base_triangle, (base_side+1) % 3)
	
	# replacement is a map sending the old edge_indices to the new edge indices. We already know what it does on edges far away from edge_index.
	replacement = dict(zip([i for i in range(lamination.zeta) if i not in [edge_index, a, b, c, d]], range(lamination.zeta)))
	zeta = len(replacement)
	if a == c:
		replacement[a] = replacement[b] = replacement[c] = replacement[d] = zeta
		zeta += 1
	elif a == d:
		# Must make sure to update the vertex which is not in the interior of the bigon.
		bad_corner_class = lamination.abstract_triangulation.find_corner_class(base_triangle, (base_side+1) % 3)
		
		replacement[a] = replacement[b] = replacement[c] = replacement[d] = zeta
		zeta += 1
	elif b == c:
		# Must make sure to update the vertex which is not in the interior of the bigon.
		bad_corner_class = lamination.abstract_triangulation.find_corner_class(base_triangle, (base_side+2) % 3)
		
		replacement[a] = replacement[b] = replacement[c] = replacement[d] = zeta
		zeta += 1
	elif b == d:
		replacement[a] = replacement[b] = replacement[c] = replacement[d] = zeta
		zeta += 1
	else:
		replacement[a] = replacement[b] = zeta
		replacement[c] = replacement[d] = zeta + 1
		zeta += 2
	
	new_edge_labels = [[replacement[i] for i in triangle] for triangle in lamination.abstract_triangulation if edge_index not in triangle]
	new_vector = [[lamination[j] for j in range(lamination.zeta) if j != edge_index and replacement[j] == i][0] for i in range(zeta)]
	new_corner_labels = [[triangle.corner_labels[side] if (triangle, side) not in bad_corner_class else good_corner_label for side in range(3)] for triangle in lamination.abstract_triangulation if edge_index not in triangle]
	
	return Lamination(Abstract_Triangulation(new_edge_labels, new_corner_labels), new_vector)

def compute_splitting_sequence(lamination):
	# Assumes that lamination is a filling lamination. If not, it will discover this along the way and throw an 
	# AssumptionError
	# We assume that lamination is given as a list of algebraic numbers. 
	# We continually use Symbolic_Computation.simplify() just to be safe.
	# This assumes that the edges are labelled 0, ..., abstract_triangulation.zeta-1, this is a very sane labelling system.
	
	def projective_weights(x):
		s = simplify(1 / sum(x))
		return tuple([simplify(v * s) for v in x])
	
	# We use this function to hash the number down. It MUST be (projectively) invariant under isometries of the triangulation.
	# We take the coefficients of the minimal polynomial of each entry and sort them. This has the nice property that there is a
	# uniform bound on the number of collisions.
	def hash_lamination(x):
		return tuple(sorted(([minimal_polynomial_coefficients(v) for v in projective_weights(x)])))
	
	# Check if vector is obviously reducible.
	if any(v == 0 for v in lamination.vector):
		raise AssumptionError('Lamination is not filling.')
	
	lamination = puncture_trigons(lamination)  # Puncture out all trigon regions.
	flipped = []
	seen = {hash_lamination(lamination):[[0, lamination, projective_weights(lamination)]]}
	while True:
		edge_index = max(range(lamination.zeta), key=lambda i: lamination[i])  # Find the index of the largest entry
		lamination = lamination.flip_edge(edge_index)
		
		if lamination[edge_index] == 0:
			try:
				# If this fails it's because the lamination isn't filling.
				lamination = collapse_trivial_weight(lamination, edge_index)
			except AssumptionError:
				raise AssumptionError('Lamination is not filling.')
		
		flipped.append(edge_index)
		
		# if len(flipped) % 20 == 0: print(flipped[-20:])  # Every once in a while show how we're progressing.
		
		# Check if it (projectively) matches a lamination we've already seen.
		target = hash_lamination(lamination)
		current_triangulation = lamination.abstract_triangulation
		current_projective_weights = projective_weights(lamination)
		if target in seen:
			for index, old_lamination, old_projective_weights in seen[target]:
				old_triangulation = old_lamination.abstract_triangulation
				for isometry in current_triangulation.all_isometries(old_triangulation):
					permuted_old_projective_weights = tuple([old_projective_weights[isometry.edge_map[i]] for i in range(lamination.zeta)])
					if current_projective_weights == permuted_old_projective_weights:
						# Return: the pre-periodic part, the periodic part, the dilatation.
						return flipped[:index], flipped[index:], simplify(old_lamination[isometry.edge_map[0]] / lamination[0])
			seen[target].append([len(flipped), lamination, current_projective_weights])
		else:
			seen[target] = [[len(flipped), lamination, current_projective_weights]]

# class MaximalSplittingSequence:
	# def __init__(self, encodings, period_target, isometry):
		# self.encodings = encodings
		# self.isometry = isometry
		# self.isometry_target = isometry_target
	
def splitting_sequence_to_encoding(abstract_triangulation, sequence):
	encoding = None
	triangulation = abstract_triangulation.copy()
	for edge_index in sequence:
		triangulation = forwards, backwards = triangulation.flip_edge(edge_index, encoding=True)
		encoding = forwards * encoding
	
	return encoding

def determine_type(mapping_class):
	from Error import ComputationError, AssumptionError
	from time import time
	
	start_time = time()
	if mapping_class.is_periodic():
		print(' -- Periodic.')
	else:
		try:
			# We know the map cannot be periodic.
			# If this computation fails it will throw a ComputationError - the map was probably reducible.
			lamination, dilatation = stable_lamination(mapping_class, exact=True)
			# If this computation fails it will throw an AssumptionError - the map _is_ reducible.
			preperiodic, periodic, new_dilatation = compute_splitting_sequence(lamination)
			print(' -- Pseudo-Anosov.')
		except ComputationError:
			print(' ~~ Probably reducible.')
		except AssumptionError:
			print(' -- Reducible.')
	print('      (Time: %0.4fs)' % (time() - start_time))
	return time() - start_time

if __name__ == '__main__':
	from random import choice
	from time import time
	from Encoding import Id_Encoding_Sequence
	
	print('Start')
	
	# from Examples import Example_24
	# T, twists = Example_24()
	# h = (twists['a']*twists['B']*twists['B']*twists['a']*twists['p'])**3
	# print('Lamination')
	# lamination, dilatation = h.stable_lamination(exact=True)
	# print('Splitting')
	# preperiodic, periodic, new_dilatation = compute_splitting_sequence(lamination)
	# print(len(preperiodic), len(periodic), compute_powers(dilatation, new_dilatation))
	
	from Examples import Example_S_1_2
	T, twists = Example_S_1_2()
	
	def expand_class(string):
		print(string)
		h = Id_Encoding_Sequence(T)
		for letter in string:
			h = twists[letter] * h
		return h
	
	def random_mapping_class(n):
		return ''.join(choice('abcABC') for i in range(n))
	
	# h = expand_class('aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa')
	# determine_type(h)
	# exit(1)
	import cProfile
	h = expand_class('aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa')
	cProfile.run('determine_type(h)', sort='cumtime')
	exit(1)
	
	random_length = 50
	num_trials = 50
	times = []
	for k in range(num_trials):
		times.append(determine_type(expand_class(random_mapping_class(random_length))))
	
	print('Times over %d trials: Average %0.4fs, Max %0.4fs' % (num_trials, sum(times) / len(times), max(times)))
