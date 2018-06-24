
Mapping classes
===============

Computing some basic properties of a mapping class::

    import flipper

    S = flipper.load('S_1_2')
    word = 'aCBACBacbaccbAaAcAaBBcCcBBcCaBaaaABBabBcaBbCBCbaaa'

    h = S.mapping_class(word)
    print('Built the mapping class h := \'%s\'.' % word)

    print('h has order %s (where 0 == infinite).' % h.order())
    print('h is %s.' % h.nielsen_thurston_type())

    try:
        print('h leaves L := %s projectively invariant.' % h.invariant_lamination().projective_string())
        print('and dilates it by a factor of %s.' % h.dilatation())
    except flipper.AssumptionError:
        print('We cannot find a projectively invariant lamination for h as it is not pseudo-Anosov.')

