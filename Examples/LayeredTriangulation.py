
from __future__ import print_function
import Flipper

def main(word):
	# Get an example mapping class - this one we know is pseudo-Anosov.
	# This process will fail (with an AssumptionError or ComputationError) if our map is not pseudo-Anosov.
	Example = Flipper.Examples.AbstractTriangulation.Example_S_1_1m
	word, mapping_class = Flipper.Examples.AbstractTriangulation.build_example_mapping_class(Example, word)
	preperiodic, periodic, new_dilatation, lamination, isometries = mapping_class.invariant_lamination().splitting_sequence()  # Requires the SymbolicComputation library.
	
	L = Flipper.Kernel.LayeredTriangulation.Layered_Triangulation(lamination.abstract_triangulation, word)
	L.flips(periodic)
	closing_isometries = [isometry for isometry in L.upper_lower_isometries() if any(isometry.edge_map == isom.edge_map for isom in isometries)]
	# There may be more than one isometry, for now let's just pick the first. We'll worry about this eventually.
	M = L.close(closing_isometries[0])
	with open('test.tri', 'w') as file:
		file.write(M.SnapPy_string())  # Write the manifold to a file.
	print('I stored the bundle with monodromy \'%s\' in \'test.tri\'.' % word)
	print('It was built using the first of %d isometries.' % len(closing_isometries))
	print('It has %d cusp(s) with the following properties (in order):' % M.num_cusps)
	print('Cusp types: %s' % M.cusp_types)
	print('Fibre slopes: %s' % M.fibre_slopes)
	print('Degeneracy slopes: %s' % M.degeneracy_slopes)
	print('To build this bundle I may have had to create some artificial cusps,')
	print('these are the ones of type 1.')
	print('You should fill them with their fibre slope to get')
	print('the manifold you were expecting.')

if __name__ == '__main__':
	main('aB')
	# import cProfile
	# cProfile.run("main('aBBBBaBB')", sort='time')
