
from __future__ import print_function

import flipper

from time import time

# The purpose of this example is to demonstrate that:
#   even for atypical mapping classes, Encoding.invariant_lamination() does
#   not raise flipper.ComputationErrors.

def main():
	times = {}
	
	examples = [
		('S_2_1', 'AEeadfaCEeCdEBfbCDFC'),  # Cannot estimate!
		('S_2_1', 'abDeFaabDeFaabDeFaAEeadfaCEeCdEBfbCDFCAfEdBAAfEdBAAfEdBA'),  # Reducing curve [4, 12, 20, 44, 24, 40, 28, 44, 32] - slow!
		('S_2_1', 'aFcE'),  # Dim 2 eigenspace
		('S_2_1', 'AEeadfaCEeCdEBfbCDFC'),  # Word is reducible (reducing curve has weight ~ 6000).
		('S_2_1', 'aDefFecDBdFCcACDcCdF'),  # 12 iterates?
		('S_2_1', 'BcEC'),  # Is reducible but (unlike BC) mixes every edge just a little so growth is super slow.
		('S_2_1', 'ebbFaBDECFbBCFFbFeCa'),  # First iteration has no real roots.
		('S_2_1', 'daeaeFEdbEDaDf'),
		('S_2_1', 'fAAEffcedEafdDeFcDCe'),  # Dividing by total steps is bad for this one.
		('S_2_1', 'eeDcbeBbcdFfDBaDfDeF'),  # Really slow. 4 iterations needed.
		('S_2_1', 'fCbaAdDafeEdbcaabABb'),
		('S_2_1', 'baccabebededdccceeba'),
		('S_2_1', 'FacBcDBACfbDAbCAfEdb'),
		('S_2_1', 'bbdcecbcFA'),  # Reducible with 2 pseudo-Anosov components which are swapped.
		('S_2_1', 'FEFdFCBA'),
		('S_2_1', 'acdCccbBcf'),
		('S_2_1', 'ACBBaF'),  # !?!
		('S_2_1', 'ECdEEEaEce'),
		('S_2_1', 'DCDfCaEd'),
		('S_2_1', 'BaEcCCeAbC'),
		('S_3_1', 'abcdeGh'),  # Takes ~11 iterations to converge!
		('S_3_1', 'fAfdBh'),
		('S_3_1', 'FECC'),
		('S_3_1', 'FdbEBABaGa'),  # Reducible with 2 pA components.
		('S_3_1', 'FdbEABAaGa'),  # These have there invariant laminations in the same cell!
		('S_3_1', 'gEBGhCDHbdgF'),  # The invariant lamination does not have the top eigenvalue.
		('S_3_1', 'edbcAdgGhdHf'),  # Some of these cells only have complex eigenvalues.
		('S_1_2', 'axCxaCACABCcBXbxabCAACACxCCXXXacXCCCXcac'),  # Use to take a long time thanks to overestimated bounds.
		('S_3_1', 'fEbDGFAdagBhAdceCfeE'),  # This has 1 dim eigenspaces that don't lie in the cone.
		]
	
	for index, (surface, word) in enumerate(examples):
		print('%3d/%d: %s %s' % (index+1, len(examples), surface, word), end='')
		S = flipper.load(surface)
		mapping_class = S.mapping_class(word)
		start_time = time()
		try:
			mapping_class.invariant_lamination_uncached()
		except flipper.AssumptionError:
			print(', Claim: not pA', end='')
		# This can also fail with a flipper.ComputationError if self.invariant_lamination()
		# fails to find an invariant lamination. This is very bad so we wont try and catch
		# this exception.
		times[word] = time() - start_time
		print(', Time: %0.3f' % times[word])
	print('Average time: %0.3f' % (sum(times.values()) / len(examples)))
	print('Slowest: %s, Time: %0.3f' % (max(times, key=lambda w: times[w]), max(times.values())))
	print('Total time: %0.3f' % sum(times.values()))

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Some of the hardest examples to find invariant laminations for.')
	parser.add_argument('--show', action='store_true', default=False, help='show the source code of this example and exit')
	args = parser.parse_args()
	
	if args.show:
		print(open(__file__, 'r').read())
	else:
		main()

