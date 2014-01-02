
from Flipper.Kernel.Lamination import invariant_lamination
from Flipper.Kernel.Error import ComputationError, AssumptionError
from Flipper.Examples.AbstractTriangulation import build_example_mapping_class

UNKNOWN, PERIODIC, REDUCIBLE, PSEUDO_ANOSOV = 0, 1, 2, 3

def determine_type(mapping_class):
	if mapping_class.is_periodic():
		return PERIODIC
	else:
		try:
			lamination, dilatation = invariant_lamination(mapping_class, exact=True)
			preperiodic, periodic, new_dilatation, correct_lamination, isometries = lamination.splitting_sequence()
			return PSEUDO_ANOSOV
		except ComputationError:
			return UNKNOWN
		except AssumptionError:
			return REDUCIBLE

def main():
	from Flipper.Examples.AbstractTriangulation import Example_S_1_2 as Example
	
	# Add more tests here.
	tests = [
		('c', REDUCIBLE),
		('aB', REDUCIBLE), 
		('bbaCBAaBabcABB', REDUCIBLE),
		('aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa', PSEUDO_ANOSOV)
		]
	
	for word, mapping_class_type in tests:
		word, mapping_class = build_example_mapping_class(Example, word)
		determined_type = determine_type(mapping_class)
		if determined_type != mapping_class_type:
			print(word)
			print(mapping_class_type)
			print(determined_type)
			return False
	
	return True

if __name__ == '__main__':
	print(main())
