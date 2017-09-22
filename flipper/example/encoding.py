
from __future__ import print_function

import flipper

def main():
	S = flipper.load('S_1_2')
	word = 'aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa'
	
	h = S.mapping_class(word)
	print('Built the mapping class h := \'%s\'.' % word)
	
	print('h has order %s (where 0 == infinite).' % h.order())
	print('h is %s.' % h.nielsen_thurston_type())
	
	try:
		lamination = h.invariant_lamination()
		dilatation = h.dilatation()
		print('h leaves L := %s projectively invariant.' % lamination.projective_string())
		print('and dilates it by a factor of %s.' % dilatation)
	except flipper.AssumptionError:
		print('We cannot find a projectively invariant lamination for h as it is not pseudo-Anosov.')

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Compute some properties of a mapping class.')
	parser.add_argument('--show', action='store_true', default=False, help='show the source code of this example and exit')
	args = parser.parse_args()
	
	if args.show:
		print(open(__file__, 'r').read())
	else:
		main()

