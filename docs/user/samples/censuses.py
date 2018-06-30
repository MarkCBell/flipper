from time import time
import snappy
import flipper

for _, row in flipper.census('CHW').iterrows():
    start_time = time()
    M = snappy.Manifold(row.manifold)
    N = snappy.Manifold(flipper.load(row.surface).mapping_class(row.monodromy).bundle())
    assert M.is_isometric_to(N)  # Never fails for these examples.
    print('Matched %s over %s with %s in %0.3fs.' % (row.monodromy, row.surface, row.manifold, time() - start_time))

