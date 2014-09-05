
# Some standard example surfaces with mapping classes defined on them.
# Mainly used for running tests on.

from string import ascii_lowercase, ascii_uppercase  # !?! Possible concern: ascii_lower/uppercase is too short.
from time import time
from random import randint

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
	
	E1 = T.encode_flips([4])
	[isom1] = [isom for isom in E1.target_triangulation.all_isometries(T) if isom.label_map[3] == 3]
	a = isom1.encode() * E1
	
	E2 = T.encode_flips([4, 6, 8])
	[isom2] = [isom for isom in E2.target_triangulation.all_isometries(T) if isom.label_map[1] == 2]
	b = isom2.encode() * E2
	
	E3 = T.encode_flips([6, 8, 1, 2])
	[isom3] = [isom for isom in E3.target_triangulation.all_isometries(T) if isom.label_map[0] == 0]
	c = isom3.encode() * E3
	
	#E1 = T.encode_flips([4])
	#[isom1] = [isom for isom in E1.target_triangulation.all_isometries(T) if isom.label_map[3] == 3]
	#d = isom1.encode() * E1
	
	return flipper.examples.ExampleSurface(T, [], [a, b, c])

possible_examples = [
	'a',
	'b',
	'c',
	'ab',
	'ac',
	'aab',
	'aac',
	'aaab',
	'bc',
	'aaac',
	'abb',
	'aaaab',
	'abc',
	'acb',
	'aaaac',
	'aabb',
	'aaaaab',
	'acc',
	'aabc',
	'aacb',
	'abac',
	'aaaaac',
	'aaabb',
	'aabab',
	'aaaaaab',
	'aacc',
	'bbc',
	'aaabc',
	'aaacb',
	'aabac',
	'aacab',
	'aaaaaac',
	'abbb',
	'aaaabb',
	'aaabab',
	'aaaaaaab',
	'bcc',
	'aaacc',
	'aacac',
	'abbc',
	'abcb',
	'acbb',
	'aaaabc',
	'aaaacb',
	'aaabac',
	'aaacab',
	'aabaac',
	'aaaaaaac',
	'aabbb',
	'ababb',
	'aaaaabb',
	'aaaabab',
	'aaabaab',
	'aaaaaaaab',
	'abcc',
	'acbc',
	'accb',
	'aaaacc',
	'aaacac',
	'aabbc',
	'aabcb',
	'aacbb',
	'ababc',
	'abacb',
	'abbac',
	'aaaaabc',
	'aaaaacb',
	'aaaabac',
	'aaaacab',
	'aaabaac',
	'aaacaab',
	'aaaaaaaac',
	'aaabbb',
	'aababb',
	'aabbab',
	'aaaaaabb',
	'aaaaabab',
	'aaaabaab',
	'aaaaaaaaab'
	]

def main(h):
	try:
		dilatation, invariant_lamination = h.invariant_lamination()
		
		print(dilatation)
		print(dilatation.number_field)
		
		splittings = invariant_lamination.splitting_sequence(dilatation)
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
	for word in possible_words:
		start_time = time()
		word = word.strip()
		length = randint(3, 10)
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
		#word = 'BbBccacb'  # !?!?
		#word = 'CbCA'  # 6 tetra, m160
		h = S.mapping_class(word)
		if not main(h):
			print('##############################')
			print(word)
			print('##############################')
		print('Time %0.3f' % (time() - start_time))

def test3():
	S = Example_H2()
	h = S.mapping_class('CbCA')
	splittings = h.splitting_sequence()
	for index, splitting in enumerate(splittings):
		snappy.Manifold(splitting.bundle().snappy_string()).save('test%d.tri' % index)

if __name__ == '__main__':
	#test1()
	#test2()
	test3()

