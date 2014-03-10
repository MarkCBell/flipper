
from __future__ import print_function

import Flipper

NT_TYPE_PERIODIC = Flipper.kernel.encoding.NT_TYPE_PERIODIC
NT_TYPE_REDUCIBLE = Flipper.kernel.encoding.NT_TYPE_REDUCIBLE
NT_TYPE_PSEUDO_ANOSOV = Flipper.kernel.encoding.NT_TYPE_PSEUDO_ANOSOV

def main():
	example = Flipper.examples.abstracttriangulation.Example_S_1_2
	
	# Add more tests here.
	tests = [
		('a', NT_TYPE_REDUCIBLE),
		('b', NT_TYPE_REDUCIBLE),
		('c', NT_TYPE_REDUCIBLE),
		('aB', NT_TYPE_REDUCIBLE), 
		('bbaCBAaBabcABB', NT_TYPE_REDUCIBLE),
		('aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa', NT_TYPE_PSEUDO_ANOSOV)
		]
	
	try:
		for word, mapping_class_type in tests:
			mapping_class = example(word)
			# assert(mapping_class.NT_type() == mapping_class_type)
			assert(mapping_class.NT_type_alternate() == mapping_class_type)
	except ImportError:
		print('Symbolic computation library required but unavailable, test skipped.')
	except AssertionError:
		return False
	
	return True

if __name__ == '__main__':
	print(main())
