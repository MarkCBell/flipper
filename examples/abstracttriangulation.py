
# Some standard example surfaces with mapping classes defined on them.
# Mainly used for running tests on.

from random import choice
from string import ascii_lowercase

import Flipper

def make_mapping_classes(twists, half_twists, isometries, names=None):
	mapping_classes = [C.encode_twist(k=1) for C in twists] + [C.encode_halftwist(k=1) for C in half_twists] + [isom.encode_isometry() for isom in isometries]
	mapping_classes_inverses = [C.encode_twist(k=-1) for C in twists] + [C.encode_halftwist(k=-1) for C in half_twists] + [isom.inverse().encode_isometry() for isom in isometries]
	
	if names is None: names = ascii_lowercase
	inverse_names = [name.swapcase() for name in names]
	
	return dict(list(zip(names, mapping_classes)) + list(zip(inverse_names, mapping_classes_inverses)))

def build_mapping_class(T, dic, word):
	if word is None:
		return T, dic
	
	if isinstance(word, Flipper.Integer_Type):
		word = ''.join(choice(list(dic.keys())) for _ in range(word))
	
	h = T.Id_EncodingSequence()
	for letter in word:
		h = dic[letter] * h
	h.name = word
	
	return h

def Example_S_1_1(word=None):
	# S_1_1 and its standard (Twister) curves:
	T = Flipper.AbstractTriangulation([[0,2,1], [0,2,1]])
	
	a = Flipper.Lamination(T, [1,0,1])
	b = Flipper.Lamination(T, [0,1,1])
	
	return build_mapping_class(T, make_mapping_classes([a, b], [], []), word)

def Example_S_1_1m(word=None):
	# Mirror image of S_1_1 and its standard (Twister) curves:
	T = Flipper.AbstractTriangulation([[0,1,2], [0,1,2]])
	
	a = Flipper.Lamination(T, [1,1,0]).encode_twist()
	b = Flipper.Lamination(T, [0,1,1]).encode_twist()
	
	return build_mapping_class(T, make_mapping_classes([a, b], [], []), word)

def Example_S_1_2(word=None):
	# S_1_2 and its standard (Twister) curves:
	T = Flipper.AbstractTriangulation([[1, 3, 2], [2, 0, 4], [1, 5, 0], [5, 4, 3]])
	
	a = Flipper.Lamination(T, [0,0,1,1,1,0])
	b = Flipper.Lamination(T, [1,0,0,0,1,1])
	c = Flipper.Lamination(T, [0,1,0,1,0,1])
	
	return build_mapping_class(T, make_mapping_classes([a, b, c], [], []), word)

def Example_S_2_1(word=None):
	# S_2_1 and its standard (Twister) curves:
	T = Flipper.AbstractTriangulation([[1, 2, 4], [5, 3, 0], [2, 6, 1], [3, 0, 7], [4, 5, 8], [7, 8, 6]])
	
	a = Flipper.Lamination(T, [0, 1, 1, 0, 0, 0, 0, 0, 0])
	b = Flipper.Lamination(T, [0, 0, 1, 0, 1, 0, 1, 0, 1])
	c = Flipper.Lamination(T, [1, 0, 0, 0, 0, 1, 0, 1, 1])
	d = Flipper.Lamination(T, [0, 1, 1, 1, 0, 1, 2, 1, 1])
	e = Flipper.Lamination(T, [0, 1, 1, 1, 2, 1, 0, 1, 1])
	f = Flipper.Lamination(T, [0, 1, 2, 1, 1, 1, 1, 1, 0])
	
	return build_mapping_class(T, make_mapping_classes([a, b, c, d, e, f], [], []), word)

def Example_S_3_1(word=None):
	T = Flipper.AbstractTriangulation([[1, 2, 5], [0, 6, 3], [4, 1, 7], [3, 8, 2], [9, 5, 6],
									   [10, 0, 9], [10, 7, 8], [11, 12, 4], [12, 14, 13], [13, 11, 14]])
	
	a = Flipper.Lamination(T, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1])
	b = Flipper.Lamination(T, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1])
	c = Flipper.Lamination(T, [0, 1, 1, 0, 2, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1])
	d = Flipper.Lamination(T, [0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0])
	e = Flipper.Lamination(T, [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0])
	f = Flipper.Lamination(T, [0, 1, 1, 1, 2, 0, 1, 1, 0, 1, 1, 2, 2, 2, 2])
	g = Flipper.Lamination(T, [0, 1, 1, 1, 0, 2, 1, 1, 2, 1, 1, 0, 0, 0, 0])
	h = Flipper.Lamination(T, [0, 1, 2, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0])
	
	return build_mapping_class(T, make_mapping_classes([a, b, c, d, e, f, g, h], [], []), word)


def Example_12(word=None):
	# A 12-gon:
	T = Flipper.AbstractTriangulation([[6, 7, 0], [8, 1, 7], [8, 9, 2], [9, 10, 3], [11, 4, 10], [12, 5, 11], [12, 13, 0], [14, 1, 13], 
		[14, 15, 2], [15, 16, 3], [16, 17, 4], [6, 5, 17]])
	
	a = Flipper.Lamination(T, [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0])
	b = Flipper.Lamination(T, [1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0])
	p = T.all_isometries(T)[1]  # This is a 1/12 click.
	
	return build_mapping_class(T, make_mapping_classes([a, b], [], [p]), word)

def Example_24(word=None):
	# A 24-gon.
	T = Flipper.AbstractTriangulation([[12, 13, 0], [14, 1, 13], [15, 2, 14], [15, 16, 3], [17, 4, 16], [17, 18, 5], 
		[18, 19, 6], [20, 7, 19], [21, 8, 20], [21, 22, 9], [22, 23, 10], [24, 11, 23], [25, 0, 24], [25, 26, 1], 
		[26, 27, 2], [28, 3, 27], [29, 4, 28], [29, 30, 5], [30, 31, 6], [32, 7, 31], [33, 8, 32], [33, 34, 9], 
		[34, 35, 10], [12, 11, 35]])
	
	a = Flipper.Lamination(T, [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
	b = Flipper.Lamination(T, [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0])
	p = T.all_isometries(T)[1]  # This is a 1/24 click.
	
	return build_mapping_class(T, make_mapping_classes([a, b], [], [p]), word)

def Example_36(word=None):
	# A 36-gon
	T = Flipper.AbstractTriangulation([[18, 19, 0], [20, 1, 19], [21, 2, 20], [21, 22, 3], [22, 23, 4], [24, 5, 23], [25, 6, 24], [25, 26, 7], 
		[27, 8, 26], [27, 28, 9], [28, 29, 10], [30, 11, 29], [31, 12, 30], [31, 32, 13], [32, 33, 14], [34, 15, 33], [35, 16, 34], 
		[35, 36, 17], [36, 37, 0], [38, 1, 37], [39, 2, 38], [39, 40, 3], [40, 41, 4], [42, 5, 41],	[43, 6, 42], [43, 44, 7], [44, 45, 8], 
		[46, 9, 45], [47, 10, 46], [47, 48, 11], [48, 49, 12], [50, 13, 49], [51, 14, 50], [51, 52, 15], [52, 53, 16], [18, 17,53]])
	
	a = Flipper.Lamination(T, [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
	b = Flipper.Lamination(T, [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
	p = T.all_isometries(T)[1]  # This is a 1/36 click.
	
	return build_mapping_class(T, make_mapping_classes([a, b], [], [p]), word)
