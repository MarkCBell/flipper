
import flipper
import snappy

def main():
	while True:
		surface = raw_input('Choose surface (leave blank to quit): ')
		if surface == '': break
		try:
			S = flipper.load.equipped_triangulation(surface)
		except KeyError:
			print('Not a valid surface name')
		else:
			while True:
				word = raw_input('Enter mapping class (leave blank to rechoose surface): ')
				if word == '': break
				try:
					M = snappy.twister.Surface(surface).bundle(word)
					mapping_class = S.mapping_class(word)
					splittings = mapping_class.splitting_sequences()
					match = any(M.is_isometric_to(snappy.Manifold(splitting.bundle().snappy_string())) for splitting in splittings)
					print('Match: %s' % match)
				except KeyError:
					print('Not a valid mapping class.')
				except flipper.AssumptionError:
					print('Mapping class is not pseudo-Anosov.')

if __name__ == '__main__':
	main()

