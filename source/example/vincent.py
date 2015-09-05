
import flipper
T = flipper.create_triangulation([(~8, ~2, 7), (~7, ~1, 4), (~6, 1, 5), (~5, ~4, 0), (~3, 8, ~0), (2, 6, 3)])

h = T.encode([{0: -6, 1: -1, 2: -2, 3: 6, 4: 2, 5: -8, 6: -9, 7: -4, 8: 4, -1: 5}, 5, 6, 1, 3, 0, 2, 4, 5, 6, 0, 1, 4, 3, 4, 7, 5, 1, 6, 7, 4, 0, 8, 7, 4, None])
# x^4 - 8*x^3 + 12*x^2 - 8*x + 1
f = flipper.kernel.Polynomial([1, -8, 12, -8, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: -6, 1: 8, 2: 0, 3: -4, 4: -2, 5: 6, 6: 7, 7: 2, 8: 4, -1: 5}, 6, 1, 2, 5, 0, 4, 6, 1, 0, 2, 4, 3, 5, 6, 1, 2, 3, 4, 7, 5, 1, 6, 7, 4, 0, 8, 7, 4, None])
# x^4 - 8*x^3 + 16*x^2 - 8*x + 1
f = flipper.kernel.Polynomial([1, -8, 16, -8, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: -5, 1: -1, 2: 2, 3: -9, 4: 5, 5: 6, 6: 7, 7: -2, 8: -4, -1: 4}, 6, 3, 1, 5, 4, 7, 2, 7, 6, 3, 4, 1, 5, 7, 6, 1, 3, 7, 0, 4, 5, 6, 3, 4, 0, 8, 7, 4, None])
# x^4 - 10*x^3 + 22*x^2 - 10*x + 1
f = flipper.kernel.Polynomial([1, -10, 22, -10, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: -5, 1: -1, 2: -2, 3: -9, 4: 5, 5: 6, 6: 7, 7: 2, 8: -4, -1: 4}, 6, 3, 1, 5, 4, 2, 7, 6, 3, 4, 1, 5, 7, 6, 1, 3, 7, 0, 4, 5, 6, 3, 4, 0, 8, 7, 4, None])
# x^4 - 9*x^3 + 18*x^2 - 9*x + 1
f = flipper.kernel.Polynomial([1, -9, 18, -9, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 3, 1: -1, 2: -2, 3: 7, 4: 4, 5: -6, 6: -7, 7: 2, 8: 8, -2: 0}, 3, 8, 1, 6, 5, 2, 7, 3, 8, 5, 1, 6, 7, 3, 1, 8, 7, 4, 5, 6, 3, 8, 0, 4, 5, 6, 3, 4, 0, 8, 7, 4, None])
# x^4 - 11*x^3 + 24*x^2 - 11*x + 1
f = flipper.kernel.Polynomial([1, -11, 24, -11, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: -2, 1: -1, 2: -8, 3: -3, 4: -7, 5: 4, 6: -6, 7: -9, 8: -4, -1: 1}, 2, 7, 1, 4, 6, 0, 2, 7, 6, 1, 4, 0, 2, 1, 7, 0, 4, 0, 5, 6, 2, 3, 8, 0, 5, 6, 0, 8, 7, 4, None])
# x^4 - 9*x^3 + 18*x^2 - 9*x + 1
f = flipper.kernel.Polynomial([1, -9, 18, -9, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: -2, 1: -1, 2: 6, 3: -9, 4: 5, 5: -4, 6: -5, 7: 7, 8: 2, -2: 0}, 7, 3, 1, 2, 4, 0, 7, 3, 4, 1, 2, 0, 7, 1, 3, 0, 6, 4, 2, 7, 3, 4, 0, 5, 6, 2, 8, 0, 5, 6, 0, 8, 7, 4, None])
# x^4 - 11*x^3 + 18*x^2 - 11*x + 1
f = flipper.kernel.Polynomial([1, -11, 18, -11, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: -1, 2: 2, 3: 1, 4: -6, 5: -8, 6: -9, 7: -4, 8: -7, -2: 0}, 5, 6, 1, 8, 4, 3, 2, 3, 5, 6, 4, 1, 3, 8, 7, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 9*x^3 + 12*x^2 - 9*x + 1
f = flipper.kernel.Polynomial([1, -9, 12, -9, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: -1, 2: -2, 3: -3, 4: -6, 5: -8, 6: -9, 7: -4, 8: -7, -2: 0}, 5, 6, 1, 8, 4, 2, 3, 5, 6, 4, 1, 3, 8, 7, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 8*x^3 + 12*x^2 - 8*x + 1
f = flipper.kernel.Polynomial([1, -8, 12, -8, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: 8, 2: 0, 3: -3, 4: -6, 5: 6, 6: 7, 7: -2, 8: 3, -2: -9}, 6, 1, 2, 5, 4, 7, 3, 6, 1, 4, 2, 3, 8, 5, 6, 1, 2, 8, 7, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 11*x^3 + 19*x^2 - 11*x + 1
f = flipper.kernel.Polynomial([1, -11, 19, -11, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: 8, 2: 0, 3: 1, 4: -6, 5: 6, 6: 7, 7: 2, 8: 3, -2: -9}, 6, 1, 2, 5, 4, 3, 6, 1, 4, 2, 3, 8, 5, 6, 1, 2, 8, 7, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 9*x^3 + 18*x^2 - 9*x + 1
f = flipper.kernel.Polynomial([1, -9, 18, -9, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: -8, 2: -9, 3: 1, 4: -6, 5: -4, 6: -7, 7: 0, 8: -3, -1: -5}, 1, 2, 7, 6, 4, 3, 1, 2, 4, 7, 3, 5, 6, 1, 2, 7, 8, 5, 6, 1, 2, 8, 7, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 11*x^3 + 24*x^2 - 11*x + 1
f = flipper.kernel.Polynomial([1, -11, 24, -11, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: -1, 2: -2, 3: 6, 4: -6, 5: -8, 6: -9, 7: 2, 8: -4, -1: -5}, 5, 6, 1, 3, 4, 2, 7, 2, 7, 5, 6, 4, 1, 7, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 9*x^3 + 13*x^2 - 9*x + 1
f = flipper.kernel.Polynomial([1, -9, 13, -9, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: -1, 2: 2, 3: 6, 4: -6, 5: -8, 6: -9, 7: -2, 8: -4, -1: -5}, 5, 6, 1, 3, 4, 7, 2, 7, 5, 6, 4, 1, 7, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 8*x^3 + 12*x^2 - 8*x + 1
f = flipper.kernel.Polynomial([1, -8, 12, -8, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 7, 1: -5, 2: -2, 3: 6, 4: -6, 5: -9, 6: -1, 7: 2, 8: -4, -2: 4}, 6, 5, 0, 5, 6, 1, 3, 4, 2, 7, 5, 6, 4, 1, 7, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 8*x^3 + 12*x^2 - 8*x + 1
f = flipper.kernel.Polynomial([1, -8, 12, -8, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: 1, 2: 0, 3: -9, 4: 7, 5: 5, 6: 6, 7: 2, 8: -4, -2: -2}, 4, 3, 2, 6, 5, 1, 4, 3, 5, 2, 6, 1, 4, 2, 3, 5, 6, 1, 3, 4, 2, 7, 5, 6, 4, 1, 7, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 14*x^3 + 24*x^2 - 14*x + 1
f = flipper.kernel.Polynomial([1, -14, 24, -14, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: -3, 2: -2, 3: -9, 4: 7, 5: 5, 6: 6, 7: 0, 8: -4, -2: 2}, 4, 3, 7, 6, 5, 2, 1, 4, 3, 5, 7, 6, 1, 4, 7, 3, 5, 6, 1, 3, 4, 7, 5, 6, 4, 1, 7, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 11*x^3 + 18*x^2 - 11*x + 1
f = flipper.kernel.Polynomial([1, -11, 18, -11, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: 8, 2: 0, 3: -7, 4: -6, 5: 1, 6: 7, 7: -4, 8: 2, -2: -9}, 6, 1, 2, 3, 4, 5, 6, 1, 4, 2, 5, 3, 7, 3, 5, 6, 1, 2, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 10*x^3 + 20*x^2 - 10*x + 1
f = flipper.kernel.Polynomial([1, -10, 20, -10, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: -8, 2: -9, 3: 3, 4: -6, 5: 1, 6: -7, 7: 2, 8: 0, -2: 7}, 1, 2, 8, 6, 4, 5, 1, 2, 4, 8, 5, 3, 6, 1, 2, 8, 3, 7, 3, 5, 6, 1, 2, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 13*x^3 + 29*x^2 - 13*x + 1
f = flipper.kernel.Polynomial([1, -13, 29, -13, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: 8, 2: 0, 3: -4, 4: -6, 5: 6, 6: 7, 7: 2, 8: -2, -2: -9}, 6, 1, 2, 5, 4, 8, 7, 8, 7, 6, 1, 4, 2, 7, 3, 5, 6, 1, 2, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 13*x^3 + 22*x^2 - 13*x + 1
f = flipper.kernel.Polynomial([1, -13, 22, -13, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: 8, 2: 0, 3: -4, 4: -6, 5: 6, 6: 7, 7: -2, 8: 2, -2: -9}, 6, 1, 2, 5, 4, 7, 8, 7, 6, 1, 4, 2, 7, 3, 5, 6, 1, 2, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 11*x^3 + 19*x^2 - 11*x + 1
f = flipper.kernel.Polynomial([1, -11, 19, -11, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: 8, 2: 0, 3: -4, 4: -6, 5: 6, 6: 7, 7: -2, 8: 2, -2: -9}, 6, 1, 2, 5, 4, 7, 6, 1, 4, 2, 7, 3, 5, 6, 1, 2, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 7*x^3 + 13*x^2 - 7*x + 1
f = flipper.kernel.Polynomial([1, -7, 13, -7, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 7, 1: 0, 2: 4, 3: -4, 4: -6, 5: 6, 6: 8, 7: -2, 8: 2, -1: -8}, 1, 6, 0, 6, 1, 2, 5, 4, 7, 6, 1, 4, 2, 7, 3, 5, 6, 1, 2, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 8*x^3 + 16*x^2 - 8*x + 1
f = flipper.kernel.Polynomial([1, -8, 16, -8, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: -7, 2: -2, 3: -4, 4: 7, 5: -9, 6: -6, 7: 0, 8: 2, -1: -5}, 4, 5, 7, 1, 6, 2, 4, 5, 6, 7, 1, 2, 4, 7, 5, 6, 1, 2, 5, 4, 7, 6, 1, 4, 2, 7, 3, 5, 6, 1, 2, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 10*x^3 + 20*x^2 - 10*x + 1
f = flipper.kernel.Polynomial([1, -10, 20, -10, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: -8, 2: -9, 3: 2, 4: -6, 5: -7, 6: -2, 7: -4, 8: 0, -2: 7}, 1, 2, 8, 5, 4, 6, 1, 2, 4, 8, 6, 5, 7, 5, 6, 1, 2, 8, 3, 5, 6, 1, 2, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 13*x^3 + 28*x^2 - 13*x + 1
f = flipper.kernel.Polynomial([1, -13, 28, -13, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: -8, 2: -9, 3: -2, 4: -6, 5: -4, 6: -7, 7: 2, 8: 0, -2: 7}, 1, 2, 8, 6, 4, 3, 7, 1, 2, 4, 8, 7, 5, 6, 1, 2, 8, 3, 5, 6, 1, 2, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 11*x^3 + 21*x^2 - 11*x + 1
f = flipper.kernel.Polynomial([1, -11, 21, -11, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: -8, 2: -9, 3: 2, 4: -6, 5: -4, 6: -7, 7: -2, 8: 0, -2: 7}, 1, 2, 8, 6, 4, 7, 3, 7, 1, 2, 4, 8, 7, 5, 6, 1, 2, 8, 3, 5, 6, 1, 2, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# (x - 1)^2 * (x^2 - 12*x + 1)
f = flipper.kernel.Polynomial([1, -12, 1])
print(h.dilatation().minimal_polynomial() == f)
#############

h = T.encode([{0: 4, 1: -8, 2: -9, 3: 2, 4: -6, 5: -4, 6: -7, 7: -2, 8: 0, -2: 7}, 1, 2, 8, 6, 4, 7, 1, 2, 4, 8, 7, 5, 6, 1, 2, 8, 3, 5, 6, 1, 2, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 8*x^3 + 16*x^2 - 8*x + 1
f = flipper.kernel.Polynomial([1, -8, 16, -8, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: 6, 2: 7, 3: 0, 4: -6, 5: -2, 6: 3, 7: 2, 8: -9, -2: -7}, 2, 8, 3, 1, 4, 5, 7, 2, 8, 4, 3, 7, 6, 1, 2, 8, 3, 5, 6, 1, 2, 8, 3, 5, 6, 1, 2, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 13*x^3 + 26*x^2 - 13*x + 1
f = flipper.kernel.Polynomial([1, -13, 26, -13, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: 6, 2: 7, 3: 0, 4: -6, 5: 2, 6: 3, 7: -2, 8: -9, -2: -7}, 2, 8, 3, 1, 4, 7, 2, 8, 4, 3, 7, 6, 1, 2, 8, 3, 5, 6, 1, 2, 8, 3, 5, 6, 1, 2, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 9*x^3 + 19*x^2 - 9*x + 1
f = flipper.kernel.Polynomial([1, -9, 19, -9, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: -4, 2: -7, 3: -9, 4: -6, 5: 0, 6: -3, 7: -2, 8: 7, -1: -5}, 8, 3, 5, 2, 4, 7, 8, 3, 4, 5, 7, 1, 2, 8, 3, 5, 6, 1, 2, 8, 3, 5, 6, 1, 2, 8, 3, 5, 6, 1, 2, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 10*x^3 + 22*x^2 - 10*x + 1
f = flipper.kernel.Polynomial([1, -10, 22, -10, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: -5, 1: 3, 2: 2, 3: 6, 4: 8, 5: 7, 6: -1, 7: 5, 8: -2, -2: -4}, 6, 0, 5, 4, 7, 3, 5, 0, 5, 6, 1, 7, 4, 8, 2, 8, 5, 6, 4, 1, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 11*x^3 + 24*x^2 - 11*x + 1
f = flipper.kernel.Polynomial([1, -11, 24, -11, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: -5, 1: 3, 2: -2, 3: 6, 4: 8, 5: 7, 6: -1, 7: 5, 8: 2, -2: -4}, 6, 0, 5, 4, 7, 3, 5, 0, 5, 6, 1, 7, 4, 2, 8, 5, 6, 4, 1, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 10*x^3 + 20*x^2 - 10*x + 1
f = flipper.kernel.Polynomial([1, -10, 20, -10, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 3, 1: 6, 2: -2, 3: -6, 4: -8, 5: -5, 6: -1, 7: -9, 8: 2, -1: -4}, 6, 5, 4, 7, 3, 1, 0, 5, 4, 7, 3, 5, 0, 5, 6, 1, 7, 4, 2, 8, 5, 6, 4, 1, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 13*x^3 + 28*x^2 - 13*x + 1
f = flipper.kernel.Polynomial([1, -13, 28, -13, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: 3, 2: 0, 3: 6, 4: 7, 5: 5, 6: 1, 7: 8, 8: 2, -2: -4}, 4, 7, 2, 3, 5, 6, 4, 7, 5, 2, 6, 3, 6, 1, 4, 2, 7, 5, 6, 1, 7, 4, 2, 8, 5, 6, 4, 1, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 11*x^3 + 18*x^2 - 11*x + 1
f = flipper.kernel.Polynomial([1, -11, 18, -11, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 0, 1: 3, 2: 5, 3: -3, 4: -5, 5: -9, 6: -7, 7: -8, 8: -2, -2: -4}, 0, 5, 0, 4, 7, 2, 3, 1, 0, 4, 7, 0, 5, 6, 1, 7, 4, 8, 5, 6, 4, 1, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 10*x^3 + 20*x^2 - 10*x + 1
f = flipper.kernel.Polynomial([1, -10, 20, -10, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 0, 1: -3, 2: -9, 3: 6, 4: 3, 5: 7, 6: 5, 7: 4, 8: -2, -2: 2}, 0, 7, 5, 2, 6, 3, 5, 0, 4, 7, 2, 1, 0, 4, 7, 0, 5, 6, 1, 7, 4, 8, 5, 6, 4, 1, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 14*x^3 + 24*x^2 - 14*x + 1
f = flipper.kernel.Polynomial([1, -14, 24, -14, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: 3, 2: -2, 3: 6, 4: 7, 5: 5, 6: -3, 7: 8, 8: 0, -2: -4}, 4, 7, 8, 3, 5, 2, 6, 4, 7, 5, 8, 6, 3, 6, 1, 4, 8, 7, 5, 6, 1, 7, 4, 8, 5, 6, 4, 1, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 11*x^3 + 18*x^2 - 11*x + 1
f = flipper.kernel.Polynomial([1, -11, 18, -11, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 4, 1: -3, 2: 0, 3: -4, 4: -7, 5: 5, 6: 1, 7: -8, 8: -9, -2: 2}, 7, 8, 2, 4, 5, 6, 7, 8, 5, 2, 6, 3, 4, 7, 8, 2, 3, 6, 1, 4, 8, 7, 5, 6, 1, 7, 4, 8, 5, 6, 4, 1, 7, 8, 5, 1, 6, 8, 7, 4, None])
# x^4 - 9*x^3 + 18*x^2 - 9*x + 1
f = flipper.kernel.Polynomial([1, -9, 18, -9, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: -4, 1: -1, 2: 2, 3: -9, 4: 5, 5: 1, 6: 7, 7: 6, 8: 4, -2: 0}, 6, 3, 1, 7, 4, 5, 2, 5, 6, 3, 4, 1, 7, 5, 6, 1, 3, 5, 7, 4, 8, 4, 7, 5, 6, 3, 7, 4, None])
# x^4 - 11*x^3 + 24*x^2 - 11*x + 1
f = flipper.kernel.Polynomial([1, -11, 24, -11, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: -4, 1: -1, 2: -2, 3: -9, 4: 5, 5: -3, 6: 7, 7: 6, 8: 4, -2: 0}, 6, 3, 1, 7, 4, 2, 5, 6, 3, 4, 1, 7, 5, 6, 1, 3, 5, 7, 4, 8, 4, 7, 5, 6, 3, 7, 4, None])
# x^4 - 10*x^3 + 20*x^2 - 10*x + 1
f = flipper.kernel.Polynomial([1, -10, 20, -10, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 8, 1: -1, 2: -2, 3: 7, 4: 4, 5: -3, 6: -7, 7: -6, 8: -4, -2: 0}, 3, 0, 1, 6, 7, 2, 5, 3, 0, 7, 1, 6, 5, 3, 1, 0, 5, 4, 7, 6, 3, 0, 7, 4, 8, 4, 7, 5, 6, 3, 7, 4, None])
# x^4 - 13*x^3 + 29*x^2 - 13*x + 1
f = flipper.kernel.Polynomial([1, -13, 29, -13, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: -4, 1: -1, 2: -8, 3: -6, 4: 1, 5: 8, 6: -5, 7: 6, 8: 2, -2: 0}, 2, 5, 1, 7, 3, 4, 2, 5, 3, 1, 7, 4, 2, 1, 5, 4, 7, 4, 6, 3, 2, 8, 4, 6, 3, 4, 8, 4, 7, 5, 6, 3, 7, 4, None])
# x^4 - 11*x^3 + 18*x^2 - 11*x + 1
f = flipper.kernel.Polynomial([1, -11, 18, -11, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 2, 1: -1, 2: -2, 3: -9, 4: -5, 5: 3, 6: 7, 7: 5, 8: -7, -1: -3}, 6, 3, 1, 8, 7, 2, 0, 6, 3, 7, 1, 0, 8, 5, 0, 5, 8, 6, 1, 3, 8, 4, 7, 5, 6, 3, 7, 4, None])
# x^4 - 11*x^3 + 19*x^2 - 11*x + 1
f = flipper.kernel.Polynomial([1, -11, 19, -11, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: -2, 1: 8, 2: 0, 3: 7, 4: -5, 5: -3, 6: -7, 7: 5, 8: 3, -2: -9}, 3, 1, 2, 6, 7, 0, 3, 1, 7, 2, 0, 8, 6, 3, 1, 2, 8, 5, 0, 5, 8, 6, 1, 3, 8, 4, 7, 5, 6, 3, 7, 4, None])
# x^4 - 13*x^3 + 25*x^2 - 13*x + 1
f = flipper.kernel.Polynomial([1, -13, 25, -13, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: -7, 1: -1, 2: -2, 3: -9, 4: -5, 5: -3, 6: 7, 7: 5, 8: -4, -1: 6}, 6, 3, 1, 0, 7, 2, 5, 2, 5, 6, 3, 7, 1, 5, 0, 5, 8, 6, 1, 3, 8, 4, 7, 5, 6, 3, 7, 4, None])
# (x - 1)^2 * (x^2 - 9*x + 1)
f = flipper.kernel.Polynomial([1, -9, 1])
print(h.dilatation().minimal_polynomial() == f)
#####################

h = T.encode([{0: -7, 1: -1, 2: 2, 3: -9, 4: -5, 5: 1, 6: 7, 7: 5, 8: -4, -1: 6}, 6, 3, 1, 0, 7, 5, 2, 5, 6, 3, 7, 1, 5, 0, 5, 8, 6, 1, 3, 8, 4, 7, 5, 6, 3, 7, 4, None])
# (x - 1)^2 * (x^2 - 8*x + 1)
f = flipper.kernel.Polynomial([1, -8, 1])
print(h.dilatation().minimal_polynomial() == f)
#####################

h = T.encode([{0: -7, 1: -1, 2: -2, 3: -9, 4: -5, 5: -3, 6: 7, 7: 5, 8: -4, -1: 6}, 6, 3, 1, 0, 7, 2, 5, 6, 3, 7, 1, 5, 0, 5, 8, 6, 1, 3, 8, 4, 7, 5, 6, 3, 7, 4, None])
# (x - 1)^2 * (x^2 - 7*x + 1)
f = flipper.kernel.Polynomial([1, -7, 1])
print(h.dilatation().minimal_polynomial() == f)
#####################

h = T.encode([{0: 4, 1: 8, 2: 0, 3: -4, 4: -6, 5: 6, 6: 7, 7: 2, 8: -2, -2: -9}, 6, 1, 2, 5, 4, 8, 7, 6, 1, 4, 2, 7, 3, 5, 6, 1, 2, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# (x - 1)^2 * (x^2 - 7*x + 1)
f = flipper.kernel.Polynomial([1, -7, 1])
print(h.dilatation().minimal_polynomial() == f)
#####################

h = T.encode([{0: 4, 1: 8, 2: 0, 3: -7, 4: -6, 5: -3, 6: 7, 7: -4, 8: -2, -2: -9}, 6, 1, 2, 3, 4, 8, 5, 6, 1, 4, 2, 5, 3, 7, 3, 5, 6, 1, 2, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# (x - 1)^2 * (x^2 - 11*x + 1)
f = flipper.kernel.Polynomial([1, -11, 1])
print(h.dilatation().minimal_polynomial() == f)
#####################

h = T.encode([{0: 4, 1: -1, 2: 2, 3: 6, 4: -6, 5: -8, 6: -9, 7: -2, 8: -4, -2: 0, -9: 3, -8: 1, -7: 8, -6: 7, -5: 5, -4: -7, -3: -3, -1: -5}, 5, 6, 1, 3, 4, 7, 2, 7, 2, 7, 5, 6, 4, 1, 7, 3, 7, 8, 5, 1, 6, 8, 7, 4, None])
# 1 - 10*x + 14*x^2 - 10*x^3 + x^4
f = flipper.kernel.Polynomial([1, -10, 14, -10, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: -4, 1: -1, 2: -8, 3: -6, 4: 1, 5: 8, 6: -5, 7: 6, 8: 2, -1: 3, -9: -3, -8: -7, -7: 4, -6: -9, -5: -2, -4: 5, -3: 7, -2: 0}, 2, 5, 1, 7, 3, 4, 2, 5, 3, 1, 7, 4, 2, 1, 5, 4, 7, 4, 6, 3, 2, 8, 4, 6, 3, 4, 8, 4, 7, 5, 6, 3, 7, 4, None])
# x^4 - 11*x^3 + 18*x^2 - 11*x + 1
f = flipper.kernel.Polynomial([1, -11, 18, -11, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: 2, 1: -1, 2: -6, 3: 7, 4: -2, 5: 8, 6: 3, 7: 4, 8: -7, -2: 0, -9: 6, -8: -5, -7: -4, -6: -9, -5: 1, -4: -8, -3: 5, -1: -3}, 3, 5, 1, 8, 2, 4, 0, 4, 3, 5, 2, 1, 8, 4, 3, 1, 5, 4, 7, 2, 8, 3, 5, 6, 7, 2, 8, 3, 7, 4, 5, 6, 2, 0, 4, 5, 6, 4, None])
# x^4 - 12*x^3 + 24*x^2 - 12*x + 1
f = flipper.kernel.Polynomial([1, -12, 24, -12, 1])
print(h.dilatation().minimal_polynomial() == f)


h = T.encode([{0: 2, 1: -1, 2: 3, 3: 5, 4: -2, 5: 6, 6: 7, 7: 8, 8: 4, -1: -3, -9: -5, -8: -9, -7: -8, -6: -7, -5: 1, -4: -6, -3: -4, -2: 0}, 6, 7, 1, 5, 3, 4, 6, 7, 3, 1, 5, 4, 6, 1, 7, 4, 8, 3, 5, 6, 7, 2, 8, 3, 5, 6, 7, 2, 8, 3, 5, 6, 7, 2, 8, 3, 7, 4, 5, 6, 2, 0, 4, 5, 6, 4, None])
# x^4 - 10*x^3 + 14*x^2 - 10*x + 1
f = flipper.kernel.Polynomial([1, -10, 14, -10, 1])
print(h.dilatation().minimal_polynomial() == f)

h = T.encode([{0: -4, 1: -5, 2: 0, 3: -9, 4: -6, 5: 6, 6: 1, 7: 7, 8: 2, -2: 4, -9: -3, -8: -8, -7: -2, -6: -7, -5: 5, -4: 8, -3: -1, -1: 3}, 7, 3, 2, 5, 4, 6, 7, 3, 4, 2, 5, 6, 7, 2, 3, 6, 5, 4, 5, 6, 1, 3, 7, 2, 8, 5, 6, 7, 1, 8, 3, 8, 0, 5, 1, 6, None])
# x^4 - 11*x^3 + 18*x^2 - 11*x + 1
f = flipper.kernel.Polynomial([1, -11, 18, -11, 1])
print(h.dilatation().minimal_polynomial() == f)

