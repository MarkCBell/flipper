
from __future__ import print_function
import Flipper

def main(word):
	# Get an example mapping class - this one we know is pseudo-Anosov.
	# This process will fail (with an AssumptionError or ComputationError) if our map is not pseudo-Anosov.
	example = Flipper.examples.abstracttriangulation.Example_S_1_2
	mapping_class = example(word)
	splitting = mapping_class.splitting_sequence()  # Requires the SymbolicComputation library.
	# There may be more than one isometry, for now let's just pick the first. We'll worry about this eventually.
	M = splitting.bundle(0, word)
	with open('test.tri', 'w') as file:
		file.write(M.SnapPy_string())  # Write the manifold to a file.
	print('I stored the bundle with monodromy \'%s\' in \'test.tri\'.' % word)
	print('It was built using the first of %d isometries.' % len(splitting.closing_isometries))
	print('It has %d cusp(s) with the following properties (in order):' % M.num_cusps)
	print('Cusp types: %s' % M.cusp_types)
	print('Fibre slopes: %s' % M.fibre_slopes)
	print('Degeneracy slopes: %s' % M.degeneracy_slopes)
	print('To build this bundle I may have had to create some artificial cusps,')
	print('these are the ones of type 1.')
	print('You should fill them with their fibre slope to get')
	print('the manifold you were expecting.')

if __name__ == '__main__':
	main('abC')
	# import cProfile
	# cProfile.run("main('aBBBBaBB')", sort='time')
