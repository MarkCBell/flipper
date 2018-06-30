import snappy
import flipper

# A pseudo-Anosov mapping class.
h = flipper.load('S_1_2').mapping_class('abC')

# Build Agol's veering triangulation of the bundle.
# This will fail with an AssumptionError if h is not pseudo-Anosov.
bundle = h.bundle()

print('It has %d cusp(s) with the following properties:' % bundle.triangulation3.num_cusps)
for index, (real, fibre, degeneracy) in enumerate(zip(bundle.cusp_types(), bundle.fibre_slopes(), bundle.degeneracy_slopes())):
    print('\tCusp %s (%s): Fibre slope %s, degeneracy slope %s' % (index, 'Real' if real else 'Fake', fibre, degeneracy))

# Fake cusps filled.
M = snappy.Manifold(bundle)
print(M.identify())

# Can also build a non-veering triangulation of the bundle.
# This works for all mapping classes.
M2 = snappy.Manifold(h.bundle(veering=False))
print(M2.identify())

# If we don't fill the fake cusps we may get a differnt manifold.
N = snappy.Manifold(bundle.snappy_string(filled=False))
print(N.identify())

