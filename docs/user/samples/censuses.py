from time import time
import snappy
import flipper

def compare(surface, monodromy, manifold):
    M = snappy.Manifold(manifold)  # = snappy.twister.Surface(surface).bundle(monodromy)
    N = snappy.Manifold(flipper.load(surface).mapping_class(monodromy).bundle())
    for _ in range(100):
        try:
            if M.is_isometric_to(N):
                return True
        except RuntimeError:
            pass  # SnapPy couldn't decide if these are isometric or not.
        M.randomize()
        N.randomize()

    return False

database = 'CHW'  # We could also load 'knots'.
df = flipper.census(database)  # A pandas DataFrame.
print('Building mapping tori for each monodromy in:')
print('\t%s' % database)

for manifold, row in df.iterrows():
    print('Buiding: %s over %s (target %s).' % (row.monodromy, row.surface, manifold))
    start_time = time()
    if not compare(row.surface, row.monodromy, manifold):
        print('Could not match %s on %s' % (row.monodromy, row.surface))
    print('\tComputed in %0.3fs' % (time() - start_time))

