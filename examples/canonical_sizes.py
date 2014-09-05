
import flipper
import snappy

def test():
	S = flipper.examples.template('S_2_1')
	
	for i in range(100):
		word = S.random_word(50)
		h = S.mapping_class(word)
		ss = h.splitting_sequence()
		print('##############')
		print(word)
		for s in ss:
			M = snappy.Manifold(s.bundle().snappy_string(filled=False))
			M.canonize()
			print(M.num_tetrahedra(), len(s.periodic_flips))

if __name__ == '__main__':
	test()
