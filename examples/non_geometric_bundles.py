
from random import randint
from time import time

import flipper
import snappy

def Example_H2():
	T = flipper.abstract_triangulation([
		[3, 0, ~4],
		[4, ~5, ~0],
		[5, 2, ~6],
		[6, ~7, ~1],
		[7, 1, ~8],
		[8, ~3, ~2]
		])
	
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

def main(h):
	try:
		dilatation, invariant_lamination = h.invariant_lamination()
		
		print(dilatation)
		print(dilatation.number_field)
		
		splittings = invariant_lamination.splitting_sequences(dilatation)
		for splitting in splittings:
			M = snappy.Manifold(splitting.bundle().snappy_string())
			print(len(splitting.periodic_flips), M.num_tetrahedra())
			print(splitting.initial_lamination.stratum_orders())
			print(M.solution_type())
			print('Volume %f' % M.volume())
			print(M.identify())
			return M.solution_type() == 'all tetrahedra positively oriented'
	except flipper.AssumptionError:
		print('Not pA.')
	
	return True

def test1():
	S = Example_H2()
	for word in possible_examples:
		start_time = time()
		word = word.strip()
		print('Testing: %s' % word)
		h = S.mapping_class(word)
		if not main(h):
			print('##############################')
			print(word)
			print('##############################')
		print('Time %0.3f' % (time() - start_time))

def test2():
	S = Example_H2()
	while True:
		start_time = time()
		length = randint(3, 10)
		word = S.random_word(length)  # , negative=False)
		h = S.mapping_class(word)
		if not main(h):
			print('##############################')
			print(word)
			print('##############################')
		print('Time %0.3f' % (time() - start_time))

def test3():
	S = Example_H2()
	h = S.mapping_class('CbCA')  # 6 tetrahedra.
	#h = S.mapping_class('Bcc')  # 10 tetrahedra.
	splittings = h.splitting_sequences()
	print('Saving %d bundles.' % len(splittings))
	for index, splitting in enumerate(splittings):
		snappy.Manifold(splitting.bundle().snappy_string()).save('test%d.tri' % index)

if __name__ == '__main__':
	#test1()
	test2()
	#test3()

