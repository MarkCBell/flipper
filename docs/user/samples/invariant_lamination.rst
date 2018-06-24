
Invariant laminations
=====================

This sample highlights just how good flipper is at finding invariant laminations::

    from __future__ import print_function
    from time import time
    import flipper

    times = {}
    surface = 'S_3_1'
    length = 20
    num_samples = 100

    S = flipper.load(surface)
    for index in range(num_samples):
        word = S.random_word(length)
        print('%3d/%d: %s %s' % (index+1, num_samples, surface, word.replace('.', '')), end='')
        h = S.mapping_class(word)
        start_time = time()
        try:
            L = h.invariant_lamination()
        except flipper.AssumptionError:
            print(', Claim: not pA', end='')
        times[word] = time() - start_time
        print(', Time: %0.3f' % times[word])

    print('Average time: %0.3f' % (sum(times.values()) / num_samples))
    print('Slowest: %s, Time: %0.3f' % (max(times, key=lambda w: times[w]).replace('.', ''), max(times.values())))
    print('Total time: %0.3f' % sum(times.values()))

