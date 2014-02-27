
import os
from time import time

import snappy, Flipper

surfaces = {'S_1_1':Flipper.examples.abstracttriangulation.Example_S_1_1, 
			'S_1_2':Flipper.examples.abstracttriangulation.Example_S_1_2,
			'S_2_1':Flipper.examples.abstracttriangulation.Example_S_2_1,
			'S_3_1':Flipper.examples.abstracttriangulation.Example_S_3_1 
			}

def bundles(surface_name, word):
	splitting = surfaces[surface_name](word).splitting_sequence()
	bundles = [splitting.bundle(i, word) for i in range(len(splitting.closing_isometries))]
	manifolds = [snappy.Manifold(bundle.SnapPy_string()) for bundle in bundles]
	for bundle, manifold in zip(bundles, manifolds):
		for index, (cusp_type, fibre_slope) in enumerate(zip(bundle.cusp_types, bundle.fibre_slopes)):
			if cusp_type == 1: manifold.dehn_fill(fibre_slope, index)
	
	return manifolds

def with_bundle_structure(manifold_name, surface_name, word, *args):
	# M = snappy.Manifold(manifold_name)
	# This should be the same as:
	M = snappy.twister.Surface(surface_name).bundle(word)
	
	buns = bundles(surface_name, word)
	for B in buns:
		if B.is_isometric_to(M):
			return B
	else:
		print('Could not match %s on %s' % (manifold_name, surface_name))
		print(M.volume(), M.homology(), M.chern_simons())
		print('with any of:')
		for B in buns:
			print(B.volume(), B.homology(), B.chern_simons())
			print(B.identify())
		return None

def bundle_specs(surface_name=None):
	for line in open(os.path.join(os.path.dirname(__file__), 'census_mondromies')):
		datum = line.strip().split('\t')
		if not surface_name or datum[1] == surface_name:
			yield datum

def check_bundle_specs(surface_name=None):
	print('##################################')
	print('\tComputing over %s' % (surface_name if surface_name is not None else 'all'))
	print('##################################')
	for datum in bundle_specs(surface_name):
		start_time = time()
		print(datum[0], datum[2])
		with_bundle_structure(*datum)
		print('Computed in %f' % (time() - start_time))

if __name__ == '__main__':
	check_bundle_specs('S_1_1')
	check_bundle_specs('S_1_2')
	check_bundle_specs('S_2_1')
	check_bundle_specs('S_3_1')

