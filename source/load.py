
''' Some standard example surfaces with mapping classes defined on them.
Mainly used for running tests on. These can be accessed through
the load(SURFACE) function. '''

import re

import flipper

REGEX_IS_SPHERE_BRAID = re.compile(r'SB_(?P<num_strands>\d+)$')

def example_0_4():
	T = flipper.create_triangulation([[0, 3, ~0], [1, 4, ~3], [~1, ~4, 5], [~2, ~5, 2]])
	
	a = T.lamination([0, 1, 0, 0, 1, 0])
	b = T.lamination([1, 0, 1, 2, 2, 2])
	
	return flipper.kernel.EquippedTriangulation(T, [a, b], {
		'a': a.encode_twist(), 'b': b.encode_twist(),
		'w': a.encode_halftwist(), 'x': b.encode_halftwist(),
		'y': a.encode_halftwist(), 'z': b.encode_halftwist()
		})

def example_1_1():
	T = flipper.create_triangulation([[0, 2, 1], [~0, ~2, ~1]])
	
	a = T.lamination([1, 0, 1])
	b = T.lamination([0, 1, 1])
	
	return flipper.kernel.EquippedTriangulation(T, [a, b], [a.encode_twist(), b.encode_twist()])

def example_1_1m():
	# Mirror image of S_1_1 and its standard (Twister) curves:
	T = flipper.create_triangulation([[0, 1, 2], [~0, ~1, ~2]])
	
	a = T.lamination([1, 1, 0])
	b = T.lamination([0, 1, 1])
	
	return flipper.kernel.EquippedTriangulation(T, [a, b], [a.encode_twist(), b.encode_twist()])

def example_1_2():
	# S_1_2 and its standard (Twister) curves:
	T = flipper.create_triangulation([[1, 3, 2], [~2, 0, 4], [~1, 5, ~0], [~5, ~4, ~3]])
	
	a = T.lamination([0, 0, 1, 1, 1, 0])
	b = T.lamination([1, 0, 0, 0, 1, 1])
	c = T.lamination([0, 1, 0, 1, 0, 1])
	x = T.lamination([2, 0, 2, 2, 2, 2])
	
	return flipper.kernel.EquippedTriangulation(T, {
		'a': a, 'b': b, 'c': c, 'x': x
		}, {
		'a': a.encode_twist(), 'b': b.encode_twist(), 'c': c.encode_twist(),
		'x': T.encode([{0: ~2}, 4, 5, 2, 3, 0, 4, 2])
		})

def example_1_2b():
	# S_1_2 without the half twist
	T = flipper.create_triangulation([[1, 3, 2], [~2, 0, 4], [~1, 5, ~0], [~5, ~4, ~3]])
	
	a = T.lamination([0, 0, 1, 1, 1, 0])
	b = T.lamination([1, 0, 0, 0, 1, 1])
	c = T.lamination([0, 1, 0, 1, 0, 1])
	
	return flipper.kernel.EquippedTriangulation(T, {
		'a': a, 'b': b, 'c': c
		}, {
		'a': a.encode_twist(), 'b': b.encode_twist(), 'c': c.encode_twist(),
		})

def example_2_1():
	# S_2_1 and its standard (Twister) curves:
	T = flipper.create_triangulation([[0, 4, 1], [5, ~4, ~3], [2, ~5, 6], [7, ~6, ~2], [3, ~7, 8], [~0, ~8, ~1]])
	
	a = T.lamination([0, 1, 1, 0, 1, 1, 2, 1, 1])
	b = T.lamination([0, 1, 0, 1, 1, 0, 0, 0, 1])
	c = T.lamination([1, 0, 0, 1, 1, 0, 0, 0, 1])
	d = T.lamination([0, 1, 1, 1, 1, 0, 1, 2, 1])
	e = T.lamination([0, 1, 1, 1, 1, 2, 1, 0, 1])
	f = T.lamination([0, 0, 1, 0, 0, 0, 1, 0, 0])
	
	return flipper.kernel.EquippedTriangulation(T, [a, b, c, d, e, f],
		[a.encode_twist(), b.encode_twist(), c.encode_twist(),
		d.encode_twist(), e.encode_twist(), f.encode_twist()])

def example_2_1b():
	''' Nathans origional version. '''
	T = flipper.create_triangulation([[1, 2, 4], [5, 3, 0], [~2, 6, ~1], [~3, ~0, 7], [~4, ~5, 8], [~7, ~8, ~6]])
	
	a = T.lamination([0, 1, 1, 0, 0, 0, 0, 0, 0])
	b = T.lamination([0, 0, 1, 0, 1, 0, 1, 0, 1])
	c = T.lamination([1, 0, 0, 0, 0, 1, 0, 1, 1])
	d = T.lamination([0, 1, 1, 1, 0, 1, 2, 1, 1])
	e = T.lamination([0, 1, 1, 1, 2, 1, 0, 1, 1])
	f = T.lamination([0, 1, 2, 1, 1, 1, 1, 1, 0])
	
	return flipper.kernel.EquippedTriangulation(T, [a, b, c, d, e, f],
		[a.encode_twist(), b.encode_twist(), c.encode_twist(),
		d.encode_twist(), e.encode_twist(), f.encode_twist()])

def example_3_1():
	T = flipper.create_triangulation([[0, 6, 1], [7, ~6, ~5], [8, 2, ~7], [9, ~8, ~4], [10, 3, ~9], [11, ~10, ~3],
		[12, 4, ~11], [13, ~12, ~2], [14, 5, ~13], [~0, ~14, ~1]])
	
	a = T.lamination([0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1])
	b = T.lamination([0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0])
	c = T.lamination([0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0])
	d = T.lamination([0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0])
	e = T.lamination([0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0])
	f = T.lamination([1, 1, 1, 0, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0])
	g = T.lamination([1, 1, 1, 0, 1, 1, 0, 1, 2, 1, 1, 1, 0, 1, 2])
	h = T.lamination([1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 2])
	
	return flipper.kernel.EquippedTriangulation(T, [a, b, c, d, e, f, g, h],
		[a.encode_twist(), b.encode_twist(), c.encode_twist(),
		d.encode_twist(), e.encode_twist(), f.encode_twist(),
		g.encode_twist(), h.encode_twist()])

def example_3_1b():
	''' Nathans origional version. '''
	T = flipper.create_triangulation([[1, 2, 5], [0, 6, 3], [4, ~1, 7], [~3, 8, ~2], [9, ~5, ~6],
									[10, ~0, ~9], [~10, ~7, ~8], [11, 12, ~4], [~12, 14, 13], [~13, ~11, ~14]])
	
	a = T.lamination([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1])
	b = T.lamination([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1])
	c = T.lamination([0, 1, 1, 0, 2, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1])
	d = T.lamination([0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0])
	e = T.lamination([1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0])
	f = T.lamination([0, 1, 1, 1, 2, 0, 1, 1, 0, 1, 1, 2, 2, 2, 2])
	g = T.lamination([0, 1, 1, 1, 0, 2, 1, 1, 2, 1, 1, 0, 0, 0, 0])
	h = T.lamination([0, 1, 2, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0])
	
	return flipper.kernel.EquippedTriangulation(T, [a, b, c, d, e, f, g, h],
		[a.encode_twist(), b.encode_twist(), c.encode_twist(),
		d.encode_twist(), e.encode_twist(), f.encode_twist(),
		g.encode_twist(), h.encode_twist()])

def example_4_1():
	T = flipper.create_triangulation([[~8, 1, 2], [3, 4, ~9], [6, ~10, 5], [~0, ~11, 7], [~12, ~1, ~2],
									[~13, ~3, ~4], [~14, ~5, ~6], [~15, ~7, 0], [8, 9, ~16], [11, ~17, 10],
									[13, ~18, 12], [~19, 14, 15], [~20, 16, 17], [18, 19, 20]])
	
	a = T.lamination([0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 2])
	b = T.lamination([0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 2])
	c = T.lamination([0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 2])
	d = T.lamination([0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 2])
	e = T.lamination([0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 2])
	f = T.lamination([0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1])
	g = T.lamination([0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1])
	h = T.lamination([1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 2, 2, 2, 1, 0, 0, 1, 2, 1, 0, 1])
	i = T.lamination([1, 1, 1, 1, 0, 1, 1, 1, 2, 1, 0, 0, 0, 1, 2, 2, 1, 0, 1, 2, 1])
	j = T.lamination([1, 1, 1, 1, 0, 0, 1, 1, 2, 1, 1, 0, 0, 1, 1, 2, 1, 1, 1, 1, 2])
	
	return flipper.kernel.EquippedTriangulation(T, [a, b, c, d, e, f, g, h, i, j],
		[a.encode_twist(), b.encode_twist(), c.encode_twist(),
		d.encode_twist(), e.encode_twist(), f.encode_twist(),
		g.encode_twist(), h.encode_twist(), i.encode_twist(),
		j.encode_twist()])

def example_5_1():
	T = flipper.create_triangulation([[~10, 1, 2], [~11, 3, 4], [6, ~12, 5], [7, 8, ~13], [~0, ~14, 9],
									[~2, ~15, ~1], [~4, ~16, ~3], [~6, ~17, ~5], [~8, ~18, ~7], [0, ~19, ~9],
									[11, ~20, 10], [12, 13, ~21], [15, ~22, 14], [~23, 16, 17], [19, ~24, 18],
									[20, 21, ~25], [~26, 22, 23], [24, 25, 26]])
	
	a = T.lamination([0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0])
	b = T.lamination([0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0])
	c = T.lamination([0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 2, 1])
	d = T.lamination([0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 2, 1])
	e = T.lamination([0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 2, 1])
	f = T.lamination([0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 2, 1])
	g = T.lamination([0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 2, 0, 2, 2])
	h = T.lamination([0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1])
	i = T.lamination([0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1])
	j = T.lamination([1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 2, 2, 2, 2, 1, 0, 0, 0, 1, 2, 1, 0, 1, 1])
	k = T.lamination([1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 2, 2, 1, 0, 0, 0, 0, 1, 2, 2, 2, 1, 0, 1, 2, 1, 1])
	l = T.lamination([1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 2, 2, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 0, 0, 2, 2, 0])
	
	return flipper.kernel.EquippedTriangulation(T, [a, b, c, d, e, f, g, h, i, j, k, l],
		[a.encode_twist(), b.encode_twist(), c.encode_twist(),
		d.encode_twist(), e.encode_twist(), f.encode_twist(),
		g.encode_twist(), h.encode_twist(), i.encode_twist(),
		j.encode_twist(), k.encode_twist(), l.encode_twist()])

def example_12():
	# A 12-gon:
	T = flipper.create_triangulation([[6, 7, 0], [8, 1, ~7], [~8, 9, 2], [~9, 10, 3], [11, 4, ~10], [12, 5, ~11], [~12, 13, ~0],
		[14, ~1, ~13], [~14, 15, ~2], [~15, 16, ~3], [~16, 17, ~4], [~6, ~5, ~17]])
	
	a = T.lamination([1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0])
	b = T.lamination([1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0])
	p = T.find_isometry(T, {7: ~6})  # This is a 1/12 click.
	
	return flipper.kernel.EquippedTriangulation(T, [a, b], {
		'a': a.encode_twist(), 'b': b.encode_twist(), 'p': p.encode()
		})

def example_24():
	# A 24-gon.
	T = flipper.create_triangulation([[12, 13, 0], [14, 1, ~13], [15, 2, ~14], [~15, 16, 3], [17, 4, ~16],
		[~17, 18, 5], [~18, 19, 6], [20, 7, ~19], [21, 8, ~20], [~21, 22, 9], [~22, 23, 10], [24, 11, ~23],
		[25, ~0, ~24], [~25, 26, ~1], [~26, 27, ~2], [28, ~3, ~27], [29, ~4, ~28], [~29, 30, ~5], [~30, 31, ~6],
		[32, ~7, ~31], [33, ~8, ~32], [~33, 34, ~9], [~34, 35, ~10], [~12, ~11, ~35]])
	
	a = T.lamination([0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
	b = T.lamination([0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0])
	p = T.find_isometry(T, {13: ~12})  # This is a 1/24 click.
	
	return flipper.kernel.EquippedTriangulation(T, [a, b], {
		'a': a.encode_twist(), 'b': b.encode_twist(), 'p': p.encode()
		})

def example_36():
	# A 36-gon
	T = flipper.create_triangulation([[18, 19, 0], [20, 1, ~19], [21, 2, ~20], [~21, 22, 3], [~22, 23, 4],
		[24, 5, ~23], [25, 6, ~24], [~25, 26, 7], [27, 8, ~26], [~27, 28, 9], [~28, 29, 10], [30, 11, ~29],
		[31, 12, ~30], [~31, 32, 13], [~32, 33, 14], [34, 15, ~33], [35, 16, ~34], [~35, 36, 17], [~36, 37, ~0],
		[38, ~1, ~37], [39, ~2, ~38], [~39, 40, ~3], [~40, 41, ~4], [42, ~5, ~41], [43, ~6, ~42], [~43, 44, ~7],
		[~44, 45, ~8], [46, ~9, ~45], [47, ~10, ~46], [~47, 48, ~11], [~48, 49, ~12], [50, ~13, ~49],
		[51, ~14, ~50], [~51, 52, ~15], [~52, 53, ~16], [~18, ~17, ~53]])
	
	a = T.lamination([1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
	b = T.lamination([0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
	p = T.find_isometry(T, {19: ~18})  # This is a 1/36 click.
	
	return flipper.kernel.EquippedTriangulation(T, [a, b], {
		'a': a.encode_twist(), 'b': b.encode_twist(), 'p': p.encode()
		})

def example_braid_sphere(n):
	# A triangulation of S_{0,n}.
	assert(isinstance(n, flipper.IntegerType))
	assert(n >= 3)
	
	# We'll build the following triangulation of S_{0,n}:
	#
	# |      |      |      |       |
	# |0     |1     |2     |3      |n-3
	# |      |      |      |       |
	# | 2n-4 | 2n-3 | 2n-2 |       | 3n-7
	# X------X------X------X- ... -X------X
	#        |      |      |       |      |
	#        |      |      |       |      |
	#        |n-2   |n-1   |n      |2n-6  |2n-5
	#        |      |      |       |      |
	#
	# Note that there puncture 1 is not shown here and is on the "boundary" of the disk.
	# There are two families of triangles on the top and the bottom and two exceptional cases:
	#  1) Top triangles are given by [i, i+2n-4, ~(i+1)] for i in range(0, n-3)],
	#  2) Bottom triangles are given by [i, ~(i+1), ~(i+n-1)] for i in range(n-2, 2n-5),
	#  3) Left triangle given by [~0, ~(n-2), ~(2n-4)], and
	#  4) Right triangle given by [n-3, 3n-7, 2n-5].
	T = flipper.create_triangulation(
		[[i, i + 2 * n - 4, ~(i + 1)] for i in range(0, n - 3)] + \
		[[i, ~(i + 1), ~(i + n - 1)] for i in range(n-2, 2*n - 5)] + \
		[[~0, ~(n - 2), ~(2 * n - 4)], [n - 3, 3 * n - 7, 2 * n - 5]]
		)
	
	# We'll then create a curve isolating the ith and (i+1)st punctures from the others.
	# There are four special cases and a generic case:
	#  0) A curve isolating punctures 1 & 2, meeting edges 1, 2, ..., n-3, n-2, n-1, ..., 2n-5, 2n-4,
	#  1) A curve isolating punctures 2 & 3, meeting edges 0, 1, n-2 and 2n-3,
	#  2) A curve isolating punctures i & i+1, meeting edges i, i+1, i+n-3, i+n-2, i+2n-5 and i+2n-3,
	#  3) A curve isolating punctures n-1 & n, meeting edges n-3, 2n-6, 2n-5 and 3n-7, and
	#  4) A curve isolating punctures n & 1, meeting edges 0, 1, ..., n-3, n-2, n-1, ..., 2n-6, 3n-7.
	
	laminations = \
		[T.lamination([1 if 1 <= j <= 2 * n - 4 else 0 for j in range(T.zeta)])] + \
		[T.lamination([1 if j in [0, 1, n-2, 2*n - 3] else 0 for j in range(T.zeta)])] + \
		[T.lamination([1 if j in [i, i+1, i+n-3, i+n-2, i+2*n-5, i+2*n-3] else 0 for j in range(T.zeta)]) for i in range(1, n-3)] + \
		[T.lamination([1 if j in [n-3, 2*n - 6, 2*n - 5, 3*n - 8] else 0 for j in range(T.zeta)])] + \
		[T.lamination([1 if 0 <= j <= 2 * n - 6 or j == 3*n - 7 else 0 for j in range(T.zeta)])]
	
	# We take the half-twist about each of these curves as the generator \sigma_i of SB_n.
	mapping_classes = dict(('s_%d' % index, lamination.encode_halftwist()) for index, lamination in enumerate(laminations))
	
	return flipper.kernel.EquippedTriangulation(T, laminations, mapping_classes)

def load(surface):
	''' Return the requested example EquippedTriangulation.
	
	Available surfaces:
		'S_0_4', 'S_1_1', 'S_1_1m', 'S_1_2',
		'S_2_1', 'S_2_1b', 'S_3_1', 'S_3_1b',
		'E_12', 'E_24', 'E_36', and
		'SB_n' where n is an integer >= 3. '''
	assert(isinstance(surface, flipper.StringType))
	
	surfaces = {
		'S_0_4': example_0_4,
		'S_1_1': example_1_1,
		'S_1_1m': example_1_1m,
		'S_1_2': example_1_2,
		'S_1_2b': example_1_2b,
		'S_2_1': example_2_1,
		'S_2_1b': example_2_1b,
		'S_3_1': example_3_1,
		'S_4_1': example_4_1,
		'S_5_1': example_5_1,
		'S_3_1b': example_3_1b,
		'E_12': example_12,
		'E_24': example_24,
		'E_36': example_36
		}
	
	if surface in surfaces:
		return surfaces[surface]()
	elif REGEX_IS_SPHERE_BRAID.match(surface):
		return example_braid_sphere(int(REGEX_IS_SPHERE_BRAID.match(surface).groupdict()['num_strands']))
	
	raise KeyError('Unknown surface: %s' % surface)

