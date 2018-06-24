
Knot cusp orders
================

Flipper can find fibred knots where the stable lamination has two (6_2) or even one (8_20) prong coming out of the knot::

    import flipper

    for surface, word, target in flipper.census('knot_monodromies'):
        print('Buiding: %s over %s (target %s).' % (word, surface, target))
        stratum = flipper.load(surface).mapping_class(word).stratum()
        vertex_orders = [stratum[singularity] for singularity in stratum]
        real_vertex_orders = [stratum[singularity] for singularity in stratum if not singularity.filled]
        print('\tAll: %s, Real: %s' % (vertex_orders, real_vertex_orders))

