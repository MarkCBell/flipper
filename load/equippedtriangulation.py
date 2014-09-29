
# Some standard example surfaces with mapping classes defined on them.
# Mainly used for running tests on. These can be accessed through
# the load(SURFACE) function.

import flipper

def Example_S_1_1():
	T = flipper.abstract_triangulation([[0, 2, 1], [~0, ~2, ~1]])
	
	a = T.lamination([1, 0, 1])
	b = T.lamination([0, 1, 1])
	
	return flipper.kernel.EquippedTriangulation(T, [a, b], [a.encode_twist(), b.encode_twist()])

def Example_S_1_1m():
	# Mirror image of S_1_1 and its standard (Twister) curves:
	T = flipper.abstract_triangulation([[0, 1, 2], [~0, ~1, ~2]])
	
	a = T.lamination([1, 1, 0]).encode_twist()
	b = T.lamination([0, 1, 1]).encode_twist()
	
	return flipper.kernel.EquippedTriangulation(T, [a, b], [a.encode_twist(), b.encode_twist()])

def Example_S_1_2():
	# S_1_2 and its standard (Twister) curves:
	T = flipper.abstract_triangulation([[1, 3, 2], [~2, 0, 4], [~1, 5, ~0], [~5, ~4, ~3]])
	
	a = T.lamination([0, 0, 1, 1, 1, 0])
	b = T.lamination([1, 0, 0, 0, 1, 1])
	c = T.lamination([0, 1, 0, 1, 0, 1])
	
	return flipper.kernel.EquippedTriangulation(T, [a, b, c], [a.encode_twist(), b.encode_twist(), c.encode_twist()])

def Example_S_2_1():
	# S_2_1 and its standard (Twister) curves:
	T = flipper.abstract_triangulation([[0, 4, 1], [5, ~4, ~3], [2, ~5, 6], [7, ~6, ~2], [3, ~7, 8], [~0, ~8, ~1]])
	
	a = T.lamination([0, 1, 1, 0, 1, 1, 2, 1, 1])
	b = T.lamination([0, 1, 0, 1, 1, 0, 0, 0, 1])
	c = T.lamination([1, 0, 0, 1, 1, 0, 0, 0, 1])
	d = T.lamination([0, 1, 1, 1, 1, 0, 1, 2, 1])
	e = T.lamination([0, 1, 1, 1, 1, 2, 1, 0, 1])
	f = T.lamination([0, 0, 1, 0, 0, 0, 1, 0, 0])
	
	return flipper.kernel.EquippedTriangulation(T, [a, b, c, d, e, f],
		[a.encode_twist(), b.encode_twist(), c.encode_twist(),
		d.encode_twist(), e.encode_twist(), f.encode_twist()])

def Example_S_2_1b():
	''' Nathans origional version. '''
	T = flipper.abstract_triangulation([[1, 2, 4], [5, 3, 0], [~2, 6, ~1], [~3, ~0, 7], [~4, ~5, 8], [~7, ~8, ~6]])
	
	a = T.lamination([0, 1, 1, 0, 0, 0, 0, 0, 0])
	b = T.lamination([0, 0, 1, 0, 1, 0, 1, 0, 1])
	c = T.lamination([1, 0, 0, 0, 0, 1, 0, 1, 1])
	d = T.lamination([0, 1, 1, 1, 0, 1, 2, 1, 1])
	e = T.lamination([0, 1, 1, 1, 2, 1, 0, 1, 1])
	f = T.lamination([0, 1, 2, 1, 1, 1, 1, 1, 0])
	
	#print(flipper.kernel.Matrix([[x.geometric_intersection(y) for y in [a,b,c,d,e,f]] for x in [a,b,c,d,e,f]]))
	
	return flipper.kernel.EquippedTriangulation(T, [a, b, c, d, e, f],
		[a.encode_twist(), b.encode_twist(), c.encode_twist(),
		d.encode_twist(), e.encode_twist(), f.encode_twist()])

def Example_S_3_1():
	T = flipper.abstract_triangulation([[0, 6, 1], [7, ~6, ~5], [8, 2, ~7], [9, ~8, ~4], [10, 3, ~9], [11, ~10, ~3],
		[12, 4, ~11], [13, ~12, ~2], [14, 5, ~13], [~0, ~14, ~1]])
	
	a = T.lamination([0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1])
	b = T.lamination([0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0])
	c = T.lamination([0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0])
	d = T.lamination([0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0])
	e = T.lamination([0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0])
	f = T.lamination([1, 1, 1, 0, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0])
	g = T.lamination([1, 1, 1, 0, 1, 1, 0, 1, 2, 1, 1, 1, 0, 1, 2])
	h = T.lamination([1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 2])
	
	#print(flipper.kernel.Matrix([[x.geometric_intersection(y) for y in [a,b,c,d,e,f,g,h]] for x in [a,b,c,d,e,f,g,h]]))
	
	return flipper.kernel.EquippedTriangulation(T, [a, b, c, d, e, f, g, h],
		[a.encode_twist(), b.encode_twist(), c.encode_twist(),
		d.encode_twist(), e.encode_twist(), f.encode_twist(),
		g.encode_twist(), h.encode_twist()])

def Example_S_3_1b():
	''' Nathans origional version. '''
	T = flipper.abstract_triangulation([[1, 2, 5], [0, 6, 3], [4, ~1, 7], [~3, 8, ~2], [9, ~5, ~6],
									[10, ~0, ~9], [~10, ~7, ~8], [11, 12, ~4], [~12, 14, 13], [~13, ~11, ~14]])
	
	a = T.lamination([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1])
	b = T.lamination([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1])
	c = T.lamination([0, 1, 1, 0, 2, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1])
	d = T.lamination([0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0])
	e = T.lamination([1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0])
	f = T.lamination([0, 1, 1, 1, 2, 0, 1, 1, 0, 1, 1, 2, 2, 2, 2])
	g = T.lamination([0, 1, 1, 1, 0, 2, 1, 1, 2, 1, 1, 0, 0, 0, 0])
	h = T.lamination([0, 1, 2, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0])
	
	#print(flipper.kernel.Matrix([[x.geometric_intersection(y) for y in [a,b,c,d,e,f,g,h]] for x in [a,b,c,d,e,f,g,h]]))
	
	return flipper.kernel.EquippedTriangulation(T, [a, b, c, d, e, f, g, h],
		[a.encode_twist(), b.encode_twist(), c.encode_twist(),
		d.encode_twist(), e.encode_twist(), f.encode_twist(),
		g.encode_twist(), h.encode_twist()])

def Example_12():
	# A 12-gon:
	T = flipper.abstract_triangulation([[6, 7, 0], [8, 1, ~7], [~8, 9, 2], [~9, 10, 3], [11, 4, ~10], [12, 5, ~11], [~12, 13, ~0],
		[14, ~1, ~13], [~14, 15, ~2], [~15, 16, ~3], [~16, 17, ~4], [~6, ~5, ~17]])
	
	a = T.lamination([1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0])
	b = T.lamination([1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0])
	p = T.self_isometries()[1] # This is a 1/12 click.
	
	return flipper.kernel.EquippedTriangulation(T, [a, b], [a.encode_twist(), b.encode_twist(), p.encode()])

def Example_24():
	# A 24-gon.
	T = flipper.abstract_triangulation([[12, 13, 0], [14, 1, ~13], [15, 2, ~14], [~15, 16, 3], [17, 4, ~16],
		[~17, 18, 5], [~18, 19, 6], [20, 7, ~19], [21, 8, ~20], [~21, 22, 9], [~22, 23, 10], [24, 11, ~23],
		[25, ~0, ~24], [~25, 26, ~1], [~26, 27, ~2], [28, ~3, ~27], [29, ~4, ~28], [~29, 30, ~5], [~30, 31, ~6],
		[32, ~7, ~31], [33, ~8, ~32], [~33, 34, ~9], [~34, 35, ~10], [~12, ~11, ~35]])
	
	a = T.lamination([0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
	b = T.lamination([0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0])
	p = T.self_isometries()[1] # This is a 1/24 click.
	
	return flipper.kernel.EquippedTriangulation(T, [a, b], [a.encode_twist(), b.encode_twist(), p.encode()])

def Example_36():
	# A 36-gon
	T = flipper.abstract_triangulation([[18, 19, 0], [20, 1, ~19], [21, 2, ~20], [~21, 22, 3], [~22, 23, 4],
		[24, 5, ~23], [25, 6, ~24], [~25, 26, 7], [27, 8, ~26], [~27, 28, 9], [~28, 29, 10], [30, 11, ~29],
		[31, 12, ~30], [~31, 32, 13], [~32, 33, 14], [34, 15, ~33], [35, 16, ~34], [~35, 36, 17], [~36, 37, ~0],
		[38, ~1, ~37], [39, ~2, ~38], [~39, 40, ~3], [~40, 41, ~4], [42, ~5, ~41], [43, ~6, ~42], [~43, 44, ~7],
		[~44, 45, ~8], [46, ~9, ~45], [47, ~10, ~46], [~47, 48, ~11], [~48, 49, ~12], [50, ~13, ~49],
		[51, ~14, ~50], [~51, 52, ~15], [~52, 53, ~16], [~18, ~17, ~53]])
	
	a = T.lamination([1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
	b = T.lamination([0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
	p = T.self_isometries()[1] # This is a 1/36 click.
	
	return flipper.kernel.EquippedTriangulation(T, [a, b], [a.encode_twist(), b.encode_twist(), p.encode()])

def load(surface):
	surfaces = {
		'S_1_1': Example_S_1_1,
		'S_1_1m': Example_S_1_1m,
		'S_1_2': Example_S_1_2,
		'S_2_1': Example_S_2_1,
		'S_2_1b': Example_S_2_1b,
		'S_3_1': Example_S_3_1,
		'S_3_1b': Example_S_3_1b,
		'E_12': Example_12,
		'E_24': Example_24,
		'E_36': Example_36
		}
	return surfaces[surface]()
