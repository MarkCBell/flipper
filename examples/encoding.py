
from __future__ import print_function
from time import time

import Flipper

def main():
	S = Flipper.examples.abstracttriangulation.Example_S_2_1()
	for i in range(100):
		word = S.random_word(20)
		#word = 'AEeadfaCEeCdEBfbCDFC'  # Word is reducible (reducing curve has weight ~ 6000).
		#word = 'CdEBfbCDFCAEeadfaCEe'  # Rotation of above. 
		#word = 'aFcE'  # 2 Dim eigenspace 
		#word = 'aDefFecDBdFCcACDcCdF'  # 12 iterates.
		#word = 'fedCFadBbBEfBBAdCDbb'
		#word = 'fDCFEdbafdaEbaDDcdCF'
		#word = 'EeEaadebAABDCEDCCfad'
		#word = 'EbbccbBcFcAbdcFCBFff'
		#word = 'acCCceedDCFdABdbFAcE'
		#word = 'aeedDCFdABdbFAcE'
		word = 'BcEC'  # Is reducible but (unlike BC) mixes every edge just a little so growth is super slow.
		print('###############')
		print(i, word)
		print('###############')
		mapping_class = S.mapping_class(word)
		t = time()
		mapping_class.invariant_lamination()
		print('TIME TAKEN: %f' % (time() - t))
		#print(mapping_class.invariant_lamination())
		#mapping_class.decompose(dic)
		print('###############')

if __name__ == '__main__':
	main()

