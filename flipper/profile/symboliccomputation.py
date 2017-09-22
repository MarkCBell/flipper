
from __future__ import print_function
from time import time
import cProfile
import pstats

import flipper

NT_TYPE_PERIODIC = flipper.kernel.encoding.NT_TYPE_PERIODIC
NT_TYPE_REDUCIBLE = flipper.kernel.encoding.NT_TYPE_REDUCIBLE
NT_TYPE_PSEUDO_ANOSOV = flipper.kernel.encoding.NT_TYPE_PSEUDO_ANOSOV

def main(verbose=False):
	if verbose: print('Running symbolic computation profile.')
	
	start_time = time()
	# Add more tests here.
	tests = [
		(flipper.kernel.Matrix([
		[1, 0, 0, 0, 1, -1],
		[0, 1, 0, 0, 0, 0],
		[0, 0, 0, 0, 2, -1],
		[0, 0, -1, 1, 2, -1],
		[0, 0, -1, 0, 4, -2],
		[0, 0, 0, 0, 1, 0]
		]), flipper.kernel.id_matrix(6)),
		(flipper.kernel.Matrix([
		[-3, 3, -3, 4, -4, 4],
		[-2, 2, -1, 2, -2, 2],
		[-3, 2, -1, 3, -3, 3],
		[-5, 3, -3, 6, -5, 5],
		[-5, 3, -3, 5, -4, 5],
		[-6, 4, -4, 6, -6, 7]
		]), flipper.kernel.id_matrix(6)),
		(flipper.kernel.Matrix([
		[-843, 194, -2990, 844, 2990, -194],
		[-982, 228, -3478, 982, 3478, -227],
		[-1222, 280, -4334, 1222, 4335, -280],
		[-2204, 507, -7813, 2205, 7813, -507],
		[-2066, 474, -7325, 2066, 7326, -474],
		[-138, 33, -488, 138, 488, -32]
		]), flipper.kernel.id_matrix(6)),
		(flipper.kernel.Matrix([
		[0, 2, -1, 2, 0, 0, -1, -1, 0],
		[-1, 6, -2, 2, 0, 0, -3, -1, 0],
		[0, 3, -1, 2, 0, 0, -2, -1, 0],
		[0, 0, 0, 1, 1, 0, 0, -1, 0],
		[0, 3, -1, 1, 0, 0, -1, -1, 0],
		[0, 1, 0, 1, 0, 0, -1, 0, 0],
		[-1, 3, -1, 2, 0, 0, -2, -1, 1],
		[1, 2, -1, 2, 1, -1, -1, -2, 0],
		[0, 5, -2, 2, 0, 0, -3, -1, 0]
		]), flipper.kernel.id_matrix(9)),
		(flipper.kernel.Matrix([
		[0, 0, 0, 1, 0, 0, 0, -1, 1],
		[0, 3, -1, 1, 0, 0, -1, -1, 0],
		[0, 1, 0, 1, 0, 0, 0, -1, 0],
		[0, 0, 0, 0, 0, 1, 0, 0, 0],
		[0, 1, 0, 0, 0, 0, 0, 0, 0],
		[0, 0, 0, 1, 1, 0, 0, -1, 0],
		[1, 2, -1, 1, 0, 0, -1, -1, 0],
		[0, 0, 0, -1, 0, 1, 1, 0, 0],
		[0, 2, -1, 1, 0, 0, 0, -1, 0]
		]), flipper.kernel.id_matrix(9))
		]
	
	for action_matrix, condition_matrix in tests:
		try:
			flipper.kernel.symboliccomputation.directed_eigenvector(action_matrix, condition_matrix)
		except flipper.AssumptionError:
			print('bad test %s' % vector)
	
	return time() - start_time

if __name__ == '__main__':
	# print(main(verbose=True))
	# pstats.Stats(cProfile.Profile().run('main()')).strip_dirs().sort_stats('time').print_callers(20)
	# pstats.Stats(cProfile.Profile().run('main()')).strip_dirs().sort_stats('time').print_callees(20)
	pstats.Stats(cProfile.Profile().run('main()')).strip_dirs().sort_stats('cumtime').print_stats(20)

