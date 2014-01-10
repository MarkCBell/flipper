
from Flipper.Kernel.Lamination import invariant_lamination
from Flipper.Kernel.LayeredTriangulation import Layered_Triangulation
from Flipper.Examples.AbstractTriangulation import build_example_mapping_class

from Flipper.Examples.AbstractTriangulation import Example_S_1_1 as Example

def build_bundle(word, isometry_number):
	word, mapping_class = build_example_mapping_class(Example, word)
	lamination, dilatation = invariant_lamination(mapping_class, exact=True)  # !?! ImportError.
	preperiodic, periodic, new_dilatation, correct_lamination, isometries = lamination.splitting_sequence()
	
	L = Layered_Triangulation(correct_lamination.abstract_triangulation, word)
	L.flips(periodic)
	closing_isometries = [isometry for isometry in L.upper_lower_isometries() if any(isometry.edge_map == isom.edge_map for isom in isometries)]
	try:
		M, cusp_types, fibre_slopes, degeneracy_slopes = L.close(closing_isometries[isometry_number])
	except IndexError:
		return None
	
	return M.SnapPy_string()

def main():
	
	try:
		S = __import__('snappy')
	except ImportError:
		print('SnapPy unavailable, tests skipped.')
		return True
	
	tests = [
		('aB', 0, 'm003'),
		('aB', 1, 'm004')
		]
	
	for word, isometry_number, target_manifold in tests:
		M = build_bundle(word, isometry_number)
		if M is None or not S.Manifold(M).is_isometric_to(S.Manifold(target_manifold)):
			print(word, isometry_number, target_manifold)
			return False
	
	return True

if __name__ == '__main__':
	main()
