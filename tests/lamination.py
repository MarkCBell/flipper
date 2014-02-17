
from __future__ import print_function

import Flipper

UNKNOWN, PERIODIC, REDUCIBLE, PSEUDO_ANOSOV = 0, 1, 2, 3

def determine_type(mapping_class):
	if mapping_class.is_periodic():
		return PERIODIC
	else:
		try:
			preperiodic, periodic, new_dilatation, correct_lamination, isometries = mapping_class.invariant_lamination().splitting_sequence()
			return PSEUDO_ANOSOV
		except ImportError:
			pass  # !?!
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
		word, mapping_class = Flipper.examples.abstracttriangulation.build_example_mapping_class(Example, word)
		try:
			determined_type = determine_type(mapping_class)
			if determined_type != mapping_class_type:
				print(word)
				print(mapping_class_type)
				print(determined_type)
				return False
		except ImportError:
			print('SymbolicComputation library unavailable, tests skipped.')
			return True
	
	return True

if __name__ == '__main__':
	print(main())
