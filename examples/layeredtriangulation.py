
from __future__ import print_function

import flipper

def main():
	word = 'abC'
	# Get an example mapping class - this one we know is pseudo-Anosov.
	# This process will fail (with an AssumptionError or ComputationError) if our map is not pseudo-Anosov.
	S = flipper.load.equipped_triangulation('S_1_2')
	mapping_class = S.mapping_class(word)
	splittings = mapping_class.splitting_sequences()  # Requires the SymbolicComputation library.
	# There may be more than one isometry, for now let's just pick the first. We'll worry about this eventually.
	bundle = splittings[0].bundle()
	with open('test.tri', 'w') as disk_file:
		disk_file.write(bundle.snappy_string(name='flipper abC layered triangulation'))  # Write the manifold to a file.
	print('I stored the bundle with monodromy \'%s\' in \'test.tri\'.' % word)
	print('It was built using the first of %d isometries.' % len(splittings))
	print('It has %d cusp(s) with the following properties (in order):' % bundle.num_cusps)
	print('Cusp types: %s' % bundle.cusp_types)
	print('Fibre slopes: %s' % bundle.fibre_slopes)
	print('Degeneracy slopes: %s' % bundle.degeneracy_slopes)
	print('To build this bundle I may have had to create some artificial cusps,')
	print('these are the ones of type 1.')

if __name__ == '__main__':
	main()

