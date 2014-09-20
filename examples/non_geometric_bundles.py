
from random import randint
from time import time

import flipper
import snappy

def tetrahedra_shapes(manifold):
	# Return the exact shapes of the tetrahedra using snap.
	T = snappy.snap.tetrahedra_field_gens(manifold)
	_, generator, shapes = T.find_field(prec=100, degree=20, optimize=True)
	generator_approximation = generator.f(100)
	return [shape(generator_approximation).imag() for shape in shapes]

def is_geometric(manifold):
	return all([shape > 0 for shape in tetrahedra_shapes(manifold)])

def is_degenerate(manifold):
	return any([shape == 0 for shape in tetrahedra_shapes(manifold)])

###########################################################################

def Example_H2():
	T = flipper.abstract_triangulation([[3, 0, ~4], [4, ~5, ~0], [5, 2, ~6], [6, ~7, ~1], [7, 1, ~8], [8, ~3, ~2]])
	
	a = T.encode_flips_and_close([4], 3, 3)
	b = T.encode_flips_and_close([4, 6, 8], 1, 2)
	c = T.encode_flips_and_close([6, 8, 1, 2], 0, 0)
	# d = ???  # Ask Vincent for the 4th generator.
	
	return flipper.examples.ExampleSurface(T, [], [a, b, c])

# To try and find smaller non-geometric bundles we know that if we use positive words then the number of
# tetrahedra in the bundle is #a + 3#b + 4#c. So the following is a list of all Lyndon words (cyclically
# first) that will produce bundles with <13 tetrahedra.
possible_examples = [
	'a', 'b', 'c', 'ab', 'ac', 'aab', 'aac', 'aaab', 'bc', 'aaac', 'abb', 'aaaab', 'abc', 'acb',
	'aaaac', 'aabb', 'aaaaab', 'acc', 'aabc', 'aacb', 'abac', 'aaaaac', 'aaabb', 'aabab', 'aaaaaab',
	'aacc', 'bbc', 'aaabc', 'aaacb', 'aabac', 'aacab', 'aaaaaac', 'abbb', 'aaaabb', 'aaabab', 'aaaaaaab',
	'bcc', 'aaacc', 'aacac', 'abbc', 'abcb', 'acbb', 'aaaabc', 'aaaacb', 'aaabac', 'aaacab', 'aabaac',
	'aaaaaaac', 'aabbb', 'ababb', 'aaaaabb', 'aaaabab', 'aaabaab', 'aaaaaaaab', 'abcc', 'acbc', 'accb',
	'aaaacc', 'aaacac', 'aabbc', 'aabcb', 'aacbb', 'ababc', 'abacb', 'abbac', 'aaaaabc', 'aaaaacb',
	'aaaabac', 'aaaacab', 'aaabaac', 'aaacaab', 'aaaaaaaac', 'aaabbb', 'aababb', 'aabbab', 'aaaaaabb',
	'aaaaabab', 'aaaabaab', 'aaaaaaaaab'
]

def test1():
	S = Example_H2()
	for word in possible_examples:
		start_time = time()
		word = word.strip()
		print('Testing: %s' % word)
		h = S.mapping_class(word)
		try:
			splittings = h.splitting_sequences()
			for M in [snappy.Manifold(splitting.bundle().snappy_string()) for splitting in splittings]:
				if M.solution_type() != 'all tetrahedra positively oriented':
					print('##############################')
					print('(POSSIBLY) NON GEOMETRIC')
					print(word, M.num_tetrahedra())
					print('##############################')
		except flipper.AssumptionError:
			pass  # Mapping class is not pseudo-Anosov.
		
		print('Time %0.3f' % (time() - start_time))

def test2():
	S = Example_H2()
	# S = flipper.examples.template('S_2_1')
	# S = flipper.examples.template('S_1_2')
	while True:
		word = S.random_word(randint(2, 5))  # , negative=False)
		print('Testing: %s' % word)
		h = S.mapping_class(word)
		try:
			splittings = h.splitting_sequences()
			for M in [snappy.Manifold(splitting.bundle().snappy_string(filled=False)) for splitting in splittings]:
				if M.solution_type() != 'all tetrahedra positively oriented':
					print('##############################')
					print('(POSSIBLY) NON GEOMETRIC')
					print(word, M.num_tetrahedra())
					print('##############################')
		except flipper.AssumptionError:
			pass  # Mapping class is not pseudo-Anosov.

def test3():
	S = Example_H2()
	h = S.mapping_class('CbCA')  # 6 tetrahedra.
	# h = S.mapping_class('Bcc')  # 10 tetrahedra.
	# h = S.mapping_class('abbbb')  # 13 tetrahedra.  HIS example.
	# h = S.mapping_class('aabAb')  # 13 tetrahedra (not HIS example?).
	# h = flipper.examples.template('S_2_1').mapping_class('abbcccDeffD')
	
	splittings = h.splitting_sequences()
	print('Saving %d bundles.' % len(splittings))
	for index, splitting in enumerate(splittings):
		print(snappy.Manifold(splitting.bundle().snappy_string(filled=False)).solution_type())
		# open('test%d.tri' % index, 'w').write(splitting.bundle().snappy_string(filled=False))

if __name__ == '__main__':
	# test1()
	# test2()
	test3()

# On S_1_2 length 6:
# BAbAc == bcBA == abCB
# cbA == aBC
# On S_2_1 length ??:
# 
