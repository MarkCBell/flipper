
# This example shows that there are hyperbolic bundles with a layered veering triangulation
# whose canonical triangulation has a different number of tetrahedra. In fact there are bundles
# where the inequality is < and >.

import flipper
import snappy

def test():
	S = flipper.examples.template('S_2_1')
	
	for _ in range(100):
		word = S.random_word(50)
		h = S.mapping_class(word)
		ss = h.splitting_sequences()
		print('##############')
		print(word)
		for s in ss:
			M = snappy.Manifold(s.bundle().snappy_string(filled=False))
			M.canonize()
			print(M.num_tetrahedra(), len(s.periodic_flips))

if __name__ == '__main__':
	test()
