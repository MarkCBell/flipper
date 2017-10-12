
Censuses
========

Flipper includes large censuses of monodromies for fibred knots and manifolds::

    from time import time
    import snappy
    import flipper

    def compare(surface, word, target):
        M = snappy.Manifold(target)  # = snappy.twister.Surface(surface).bundle(word)
        N = snappy.Manifold(flipper.load(surface).mapping_class(word).bundle().snappy_string())
        for _ in range(100):
            try:
                if M.is_isometric_to(N):
                    return True
            except RuntimeError:
                pass  # SnapPy couldn't decide if these are isometric or not.
            M.randomize()
            N.randomize()

        return False

    database = 'census_monodromies'  # We could also load('knot_monodromies').
    print('Building mapping tori for each monodromy in:')
    print('\t%s' % database)

    for surface, word, target in flipper.census(database):
        print('Buiding: %s over %s (target %s).' % (word, surface, target))
        start_time = time()
        if not compare(surface, word, target):
            print('Could not match %s on %s' % (word, surface))
        print('\tComputed in %0.3fs' % (time() - start_time))

