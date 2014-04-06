
from __future__ import print_function

import Flipper

def main():
	T, dic = Flipper.examples.abstracttriangulation.Example_S_2_1()
	for i in range(100):
		word = Flipper.examples.abstracttriangulation.random_word(dic, 20)
		word = 'AEeadfaCEeCdEBfbCDFC'  # !?! Negative eigenvalues (and minpoly!!!!)
		#word = 'aFcE'  # 2 Dim eigenspace 
		#word = 'aDefFecDBdFCcACDcCdF'  # 12 iterates.
		print('###############')
		print(i, word)
		print('###############')
		mapping_class = Flipper.examples.abstracttriangulation.build_mapping_class(T, dic, word)
		print(mapping_class.invariant_lamination())
		exit(0)
		#mapping_class.decompose(dic)
		print('###############')

if __name__ == '__main__':
	main()

