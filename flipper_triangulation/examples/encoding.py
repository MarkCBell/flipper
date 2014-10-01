
from __future__ import print_function

import flipper

def main():
	S = flipper.load.equipped_triangulation('S_1_2')
	word = 'aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa'
	
	h = S.mapping_class(word)
	print('Built the mapping class h := \'%s\'.' % word)
	
	print('h has order %s (where 0 == infinite).' % h.order())
	
	# These computations can fails with a ComputationError in which case the map was almost certainly reducible.
	try:
		print('h is %s.' % h.nielsen_thurston_type())
	except flipper.ComputationError:
		print('The computation failed, h is probably reducible.')
	
	try:
		dilatation, lamination = h.invariant_lamination()
		print('h leaves L := %s projectively invariant.' % lamination.projective_string())
		print('and dilates it by a factor of %s.' % dilatation)
	except flipper.AssumptionError:
		print('We cannot find a projectively invariant lamination for h as it is not pseudo-Anosov.')
	except flipper.ComputationError:
		print('The computation failed, h is probably reducible.')
	

if __name__ == '__main__':
	main()

