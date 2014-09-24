
from __future__ import print_function
from time import time

import flipper

def main():
	times = {}
	S = flipper.load.equipped_triangulations('S_1_2')
	
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
		('S_2_1', 'ACBBaF'),
		('S_2_1', 'ECdEEEaEce'),
		('S_2_1', 'DCDfCaEd'),
		('S_2_1', 'BaEcCCeAbC'),
		('S_3_1', 'abcdeGh')  # Takes ~12 iterations to converge!
		]
	
	for index, (surface, word) in enumerate(examples):
		print('%d/%d: %s %s' % (index+1, len(examples), surface, word), end='')
		S = flipper.load.equipped_triangulation(surface)
		mapping_class = S.mapping_class(word)
		t = time()
		try:
			mapping_class.invariant_lamination()
		except flipper.AssumptionError:
			pass  # mapping_class is not pseudo-Anosov.
		# This can also fail with a flipper.ComputationError if self.invariant_lamination()
		# fails to find an invariant lamination.
		times[word] = time() - t
		print(', Time: %0.3f' % times[word])
	print('Average time: %0.3f' % (sum(times.values()) / len(examples)))
	print('Slowest: %s, Time: %0.3f' % (max(times, key=lambda w: times[w]), max(times.values())))
	print('Total time: %0.3f' % sum(times.values()))

if __name__ == '__main__':
	main()

