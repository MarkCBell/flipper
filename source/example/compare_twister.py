
from __future__ import print_function

import flipper
try:
	import snappy
except ImportError:
	snappy = None

def main():
	while True:
		surface = raw_input('Choose surface (leave blank to quit): ')
		if surface == '': break
		try:
			S = flipper.load(surface)
		except KeyError:
			print('Not a valid surface name')
		else:
			while True:
				word = raw_input('Enter mapping class (leave blank to rechoose surface): ')
				if word == '': break
				try:
					M = snappy.twister.Surface(surface).bundle(word)
					mapping_class = S.mapping_class(word)
					match = M.is_isometric_to(snappy.Manifold(mapping_class.bundle().snappy_string()))
					print('Match: %s' % match)
				except KeyError:
					print('Not a valid mapping class.')
				except flipper.AssumptionError:
					print('Mapping class is not pseudo-Anosov.')

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Compare bundles built with flipper and Twister')
	parser.add_argument('--show', action='store_true', default=False, help='show the source code of this example and exit')
	args = parser.parse_args()
	
	if args.show:
		print(open(__file__, 'r').read())
	else:
		if snappy is None:
			print('This example requires SnapPy.')
			print('Please install it and try again.')
		else:
			main()

