
from __future__ import print_function

import Flipper

def main():
	T, dic = Flipper.examples.abstracttriangulation.Example_S_1_1()
	if len(T.all_isometries(T)) != 6:
		return False
	
	return True

if __name__ == '__main__':
	print(main())

