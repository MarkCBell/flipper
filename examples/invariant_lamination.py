
from __future__ import print_function
from time import time

import flipper

def main(n=100):
	times = {}
	S = flipper.examples.abstracttriangulation.Example_S_2_1()
	for i in range(n):
		word = S.random_word(30)  # , negative=False)
		#word = 'AEeadfaCEeCdEBfbCDFC'  # Word is reducible (reducing curve has weight ~ 6000).
		#word = 'aFcE'  # 2 Dim eigenspace.
		#word = 'aDefFecDBdFCcACDcCdF'  # 12 iterates.
		#word = 'BcEC'  # Is reducible but (unlike BC) mixes every edge just a little so growth is super slow.
		#word = 'ebbFaBDECFbBCFFbFeCa'
		#word = 'daeaeFEdbEDaDf'  # First iteration has no real roots.
		#word = 'fAAEffcedEafdDeFcDCe'  # Dividing by total steps is bad for this one.
		#word = 'eeDcbeBbcdFfDBaDfDeF'  # Really slow. 4 iterations needed.
		#word = 'fCbaAdDafeEdbcaabABb'
		#word = 'baccabebededdccceeba'
		#word = 'FacBcDBACfbDAbCAfEdb'
		#word = 'bbdcecbcFA'  # Reducible with 2 pseudo-Anosov components which are swapped.
		#word = 'FEFdFCBA'
		#word = 'acdCccbBcf'
		#word = 'ACBBaF'
		#word = 'ECdEEEaEce'
		#word = 'DCDfCaEd'
		#word = 'BaEcCCeAbC'
		print('%d: %s' % (i, word), end='')
		mapping_class = S.mapping_class(word)
		t = time()
		if not mapping_class.is_periodic():
			mapping_class.invariant_lamination()  # This assumes that the mapping class is not periodic.
		times[word] = time() - t
		print(', Time: %0.3f' % times[word])
	print('Average time: %0.3f' % (sum(times.values()) / n))
	print('Slowest: %s, Time: %0.3f' % (max(times, key=lambda w: times[w]), max(times.values())))

if __name__ == '__main__':
	main()

