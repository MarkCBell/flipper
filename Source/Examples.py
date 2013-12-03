
# Some standard example surfaces with mapping classes defined on them.
# Mainly used for running tests on.

try:
	from Source.AbstractTriangulation import Abstract_Triangulation
	from Source.Isometry import all_isometries
	from Source.Encoding import encode_twist, encode_isometry
	from Source.Lamination import Lamination
except ImportError:
	from AbstractTriangulation import Abstract_Triangulation
	from Isometry import all_isometries
	from Encoding import encode_twist, encode_isometry
	from Lamination import Lamination

def Example_12():
	# A 12-gon:
	T = Abstract_Triangulation([[6, 7, 0], [8, 1, 7], [8, 9, 2], [9, 10, 3], [11, 4, 10], [12, 5, 11], [12, 13, 0], [14, 1, 13], 
		[14, 15, 2], [15, 16, 3], [16, 17, 4], [6, 5, 17]])
	
	a = encode_twist(Lamination(T, [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]))
	A = encode_twist(Lamination(T, [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]), k=-1)
	b = encode_twist(Lamination(T, [1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]))
	B = encode_twist(Lamination(T, [1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]), k =-1)
	p = encode_isometry(all_isometries(T, T)[1])  # This is a 1/12 click.
	return T, {'a':a, 'b':b, 'A':A, 'B':B, 'p':p}

def Example_24():
	# A 24-gon.
	T = Abstract_Triangulation([[12, 13, 0], [14, 1, 13], [15, 2, 14], [15, 16, 3], [17, 4, 16], [17, 18, 5], 
		[18, 19, 6], [20, 7, 19], [21, 8, 20], [21, 22, 9], [22, 23, 10], [24, 11, 23], [25, 0, 24], [25, 26, 1], 
		[26, 27, 2], [28, 3, 27], [29, 4, 28], [29, 30, 5], [30, 31, 6], [32, 7, 31], [33, 8, 32], [33, 34, 9], 
		[34, 35, 10], [12, 11, 35]])
	
	a = encode_twist(Lamination(T, [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]))
	A = encode_twist(Lamination(T, [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]), k=-1)
	b = encode_twist(Lamination(T, [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]))
	B = encode_twist(Lamination(T, [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]), k=-1)
	p = encode_isometry(all_isometries(T, T)[1])  # This is a 1/24 click.
	return T, {'a':a, 'b':b, 'A':A, 'B':B, 'p':p}

def Example_36():
	# A 36-gon
	T = Abstract_Triangulation([[18, 19, 0], [20, 1, 19], [21, 2, 20], [21, 22, 3], [22, 23, 4], [24, 5, 23], [25, 6, 24], [25, 26, 7], 
		[27, 8, 26], [27, 28, 9], [28, 29, 10], [30, 11, 29], [31, 12, 30], [31, 32, 13], [32, 33, 14], [34, 15, 33], [35, 16, 34], 
		[35, 36, 17], [36, 37, 0], [38, 1, 37], [39, 2, 38], [39, 40, 3], [40, 41, 4], [42, 5, 41],	[43, 6, 42], [43, 44, 7], [44, 45, 8], 
		[46, 9, 45], [47, 10, 46], [47, 48, 11], [48, 49, 12], [50, 13, 49], [51, 14, 50], [51, 52, 15], [52, 53, 16], [18, 17,53]])
	
	a = encode_twist(Lamination(T, [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))
	A = encode_twist(Lamination(T, [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), k=-1)
	b = encode_twist(Lamination(T, [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))
	B = encode_twist(Lamination(T, [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]), k=-1)
	p = encode_isometry(all_isometries(T, T)[1])  # This is a 1/36 click.
	return T, {'a':a, 'b':b, 'A':A, 'B':B, 'p':p}

def Example_S_1_2():
	# S_1_2 and its standard (Twister) curves:
	T = Abstract_Triangulation([[2, 1, 3], [2, 0, 4], [1, 5, 0], [4, 3, 5]])
	
	a = encode_twist(Lamination(T, [0,0,1,1,1,0]))
	b = encode_twist(Lamination(T, [0,1,0,1,0,1]))
	c = encode_twist(Lamination(T, [1,0,0,0,1,1]))
	A = encode_twist(Lamination(T, [0,0,1,1,1,0]), k=-1)
	B = encode_twist(Lamination(T, [0,1,0,1,0,1]), k=-1)
	C = encode_twist(Lamination(T, [1,0,0,0,1,1]), k=-1)
	return T, {'a':a, 'b':b, 'c':c, 'A':A, 'B':B, 'C':C}

def Example_S_1_1():
	# S_1_1 and its standard (Twister) curves:
	T = Abstract_Triangulation([[0,2,1], [0,2,1]])
	
	a = encode_twist(Lamination(T, [1,0,1]))
	b = encode_twist(Lamination(T, [0,1,1]))
	A = encode_twist(Lamination(T, [1,0,1]), k=-1)
	B = encode_twist(Lamination(T, [0,1,1]), k=-1)
	return T, {'a':a, 'b':b, 'A':A, 'B':B}

def build_example_mapping_class(Example, word=None, random_length=50):
	from random import choice
	from Encoding import Id_Encoding_Sequence
	
	T, twists = Example()
	
	if word is None: word = ''.join(choice(list(twists.keys())) for i in range(random_length))
	h = Id_Encoding_Sequence(T)
	for letter in word:
		h = twists[letter] * h
	return word, h
