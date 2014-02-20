
from __future__ import print_function

import Flipper

def build_bundle(word, isometry_number):
	Example = Flipper.examples.abstracttriangulation.Example_S_1_1
	word, mapping_class = Flipper.examples.abstracttriangulation.build_example_mapping_class(Example, word)
	# !?! Could throw an ImportError if no SymbolicComputation library is present.
	splitting = mapping_class.splitting_sequence()
	return splitting.build_bundle(isometry_number, word)

def main():
	try:
		import snappy
	except ImportError:
		print('SnapPy unavailable, tests skipped.')
		return True
	
	tests = [
		('aB', 0, 'm004'),
		('aB', 1, 'm003'),
		('Ba', 0, 'm004'),
		('Ba', 1, 'm003'),
		('Ab', 0, 'm004'),
		('Ab', 1, 'm003'),
		('bA', 0, 'm004'),
		('bA', 1, 'm003')
		]
	
	for word, isometry_number, target_manifold in tests:
		try:
			M = build_bundle(word, isometry_number)
		except IndexError:
			print('Invalid index.')
		else:
			Ma = snappy.Manifold(M.SnapPy_string())
			Mb = snappy.Manifold(target_manifold)
			if Ma.is_isometric_to(Mb):
				print(word, isometry_number, target_manifold)
				print(Ma.volume(), Mb.volume())
				print(Ma.homology(), Mb.homology())
				return False
		
	
	# for _ in range(50):
		# word, mapping_class = build_example_mapping_class(Example, random_length=10)
		
		# print(word)
		# try:
			# M = snappy.twister.Surface('S_1_1').bundle(word)
			# N0 = snappy.Manifold(build_bundle(word, 0))
			# N1 = snappy.Manifold(build_bundle(word, 1))
			# if not M.is_isometric_to(N0) and not M.is_isometric_to(N1):
				# print(M.volume())
				# print(word)
				# return False
		# except (Flipper.AssumptionError, Flipper.ComputationError):
			# print('Not pA.')
	
	return True

if __name__ == '__main__':
	print(main())
