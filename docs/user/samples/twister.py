import snappy
import flipper

def match(surface, monodromy):
    M = snappy.twister.Surface(surface).bundle(monodromy)
    N = snappy.Manifold(flipper.load(surface).mapping_class(monodromy).bundle())
    return M.is_isometric_to(N)

assert match('S_1_1', 'aB')
assert match('S_1_2', 'abC')
assert match('S_2_1', 'abbbCddEdaa')
