
from __future__ import print_function

import os
from time import time

import Flipper

import snappy

def with_bundle_structure(manifold_name, surface_name, word):
	# M = snappy.Manifold(manifold_name)
	# This should be the same as:
	M = snappy.twister.Surface(surface_name).bundle(word)
	Bs = Flipper.examples.abstracttriangulation.SURFACES[surface_name](word).splitting_sequence().snappy_manifolds()
	for B in Bs:
		if B.is_isometric_to(M):
			return B
	
	print('Could not match %s on %s' % (manifold_name, surface_name))
	print(M.volume(), M.homology(), M.chern_simons())
	print('with any of:')
	for B in Bs:
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
		manifold_name, surface_name, word = datum[:3]
		with_bundle_structure(manifold_name, surface_name, word)
		print('Computed in %f' % (time() - start_time))

if __name__ == '__main__':
	check_bundle_specs('S_1_1')
	check_bundle_specs('S_1_2')
	check_bundle_specs('S_2_1')
	check_bundle_specs('S_3_1')

