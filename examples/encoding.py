
from __future__ import print_function

import Flipper

def main():
	T, dic = Flipper.examples.abstracttriangulation.Example_S_2_1()
	word = Flipper.examples.abstracttriangulation.random_word(dic, 100)
	print('###############')
	print(word)
	print('###############')
	mapping_class = Flipper.examples.abstracttriangulation.build_mapping_class(T, dic, word)
	mapping_class.decompose(dic)
	print('###############')

if __name__ == '__main__':
	main()

