
from __future__ import print_function

import Flipper

UNKNOWN, PERIODIC, REDUCIBLE, PSEUDO_ANOSOV = 0, 1, 2, 3

def determine_type(mapping_class):
	if mapping_class.is_periodic():
		return PERIODIC
	else:
		try:
			mapping_class.splitting_sequence()
			return PSEUDO_ANOSOV
		except Flipper.ComputationError:
			return UNKNOWN
		except Flipper.AssumptionError:
			return REDUCIBLE

def main():
	Example = Flipper.examples.abstracttriangulation.Example_S_1_2
	
	# Add more tests here.
	tests = [
		('c', REDUCIBLE),
		('aB', REDUCIBLE), 
		('bbaCBAaBabcABB', REDUCIBLE),
		('aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa', PSEUDO_ANOSOV)
		]
	
	for word, mapping_class_type in tests:
		mapping_class = Example(word)
		try:
			determined_type = determine_type(mapping_class)
			if determined_type != mapping_class_type:
				print(mapping_class.name)
				print(mapping_class_type)
				print(determined_type)
				return False
		except ImportError:
			print('SymbolicComputation library unavailable, tests skipped.')
			return True
	
	return True

if __name__ == '__main__':
	print(main())
