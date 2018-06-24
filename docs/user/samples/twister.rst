
Twister
=======

Some sample code to check that the mapping tori built by Twister and flipper agree::

    import snappy
    import flipper

    while True:
        surface = raw_input('Choose surface (leave blank to quit): ')
        if not surface: break
        try:
            S = flipper.load(surface)
        except KeyError:
            print('Not a valid surface name')
        else:
            while True:
                word = raw_input('Enter mapping class (leave blank to rechoose surface): ')
                if not word: break
                try:
                    M = snappy.twister.Surface(surface).bundle(word)
                    mapping_class = S.mapping_class(word)
                    match = M.is_isometric_to(snappy.Manifold(mapping_class.bundle().snappy_string()))
                    print('Match: %s' % match)
                except KeyError:
                    print('Not a valid mapping class.')
                except flipper.AssumptionError:
                    print('Mapping class is not pseudo-Anosov.')

