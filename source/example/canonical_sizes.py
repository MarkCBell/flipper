
# This example shows that there are hyperbolic bundles with a layered veering triangulation
# whose canonical triangulation has a different number of tetrahedra. In fact there are bundles
# where the inequality is < and >.

from __future__ import print_function

import flipper
try:
	import snappy
except ImportError:
	snappy = None

def test(mapping_class):
	try:
		splitting = mapping_class.splitting_sequence()
		M = snappy.Manifold(splitting.bundle().snappy_string(filled=False))
		M.canonize()
		print('Bundle size: %d' % len(splitting.periodic_flips))
		print('Canonical bundle size: %d' % M.num_tetrahedra())
	except flipper.AssumptionError:
		pass  # Mapping class is not pseudo-Anosov.

def main():
	S = flipper.load.equipped_triangulation('S_2_1')
	
	for _ in range(100):
		word = S.random_word(20)
		h = S.mapping_class(word)
		print('##############')
		print(word)
		test(h)

if __name__ == '__main__':
	if snappy is None:
		print('This example requires SnapPy.')
		print('Please install it and try again.')
	else:
		main()

