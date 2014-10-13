
from __future__ import print_function

import flipper
try:
	import snappy
except ImportError:
	snappy = None

def main():
	surface, word = 'S_1_2', 'abC'
	# Get an example mapping class - this one we know is pseudo-Anosov.
	# This process will fail (with an AssumptionError or ComputationError) if our map is not pseudo-Anosov.
	h = flipper.load.equipped_triangulation(surface).mapping_class(word)
	print('Built the mapping class h := \'%s\' on %s.' % (word, surface))
	splittings = h.splitting_sequences()  # A list of splitting sequences.
	# There may be more than one isometry, for now let's just pick the first. We'll worry about this eventually.
	bundle = splittings[0].bundle()
	print('Built the bundle with monodromy h.')
	print('It is the first of %d sisters.' % len(splittings))
	print('It has %d cusp(s) with the following properties:' % bundle.num_cusps)
	for index, (real, fibre, degeneracy) in enumerate(zip(bundle.real_cusps, bundle.fibre_slopes, bundle.degeneracy_slopes)):
		print('\tCusp %s (%s): Fibre slope %s, degeneracy slope %s' % (index, 'Real' if real else 'Fake', fibre, degeneracy))
	
	M = snappy.Manifold(bundle.snappy_string())
	print('The manifold M: %s' % M)
	print('has these fake cusps filled along the fibre slopes.')
	print('Hence M is actually the mapping torus M_h.')
	
	N = snappy.Manifold(bundle.snappy_string(filled=False))
	print('The manifold N: %s' % N)
	print('has these cusps left unfilled.')

if __name__ == '__main__':
	if snappy is None:
		print('This example requires SnapPy.')
		print('Please install it and try again.')
	else:
		main()

