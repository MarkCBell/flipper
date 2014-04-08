
from __future__ import print_function

import Flipper

def main():
	S = Flipper.examples.abstracttriangulation.Example_S_1_1()
	T = S.abstract_triangulation
	if len(T.all_isometries(T)) != 6:
		return False
	
	return True

if __name__ == '__main__':
	print(main())

