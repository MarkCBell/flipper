
''' A module of useful, generic functions; including input and output formatting. '''

import flipper

import pickle
import itertools
from string import ascii_lowercase, digits, ascii_letters, punctuation
from fractions import gcd as gcd2
from functools import reduce as freduce

VISIBLE_CHARACTERS = digits + ascii_letters + punctuation

def string_generator(n, skip=None):
	''' Return a list of n usable names, none of which are in skip. '''
	
	assert(isinstance(n, flipper.IntegerType))
	assert(skip is None or isinstance(skip, (list, tuple, dict, set)))
	
	skip = set() if skip is None else set(skip)
	if n < 1: return []
	
	alphabet = ascii_lowercase
	results = []
	i = 0
	while True:
		i += 1
		for letters in itertools.product(alphabet, repeat=i):
			word = ''.join(letters)
			if word not in skip:
				results.append(word)
			if len(results) >= n:
				return results

def name_objects(objects, skip=None):
	''' Return a list of pairs (name, object). '''
	
	assert(isinstance(objects, (list, tuple)))
	
	return zip(string_generator(len(objects), skip), objects)

def package(objects):
	''' This packages an triangulation, some laminations and mapping classes
	into a format that can be writen to disk and loaded into an instance of the
	flipper application at a later date.
	
	Objects must be a non-empty list where each item is:
		1) an triangulation (at most one may be given),
		2) a Lamination,
		3) an Encoding,
		4) a pair (String, Lamination),
		5) a pair (String, Encoding).
	Or an EquippedTriangulation.
	
	All laminations / mapping classes must be defined on the same triangulation
	We will automatically name items of type 2) and 3) sequentially:
		a, b, ..., z, aa, ab, ... . '''
	
	spec = 'A flipper kernel file.'
	version = flipper.__version__
	
	if isinstance(objects, flipper.kernel.EquippedTriangulation):
		data = objects
	else:
		triangulation = None
		laminations, mapping_classes = {}, {}
		unnamed_laminations, unnamed_mapping_classes = [], []
		for item in objects:
			if isinstance(item, flipper.kernel.Triangulation):
				if triangulation is not None:
					raise ValueError('Only one triangulation may be given.')
				triangulation = item
			elif isinstance(item, flipper.kernel.Lamination):
				unnamed_laminations.append(item)
			elif isinstance(item, flipper.kernel.Encoding):
				unnamed_mapping_classes.append(item)
			elif isinstance(item, (list, tuple)) and len(item) == 2:
				name, item2 = item
				if isinstance(name, flipper.StringType):
					if isinstance(item2, flipper.kernel.Triangulation):
						if triangulation is not None:
							raise ValueError('Only one triangulation may be given.')
						triangulation = item2
					elif isinstance(item2, flipper.kernel.Lamination):
						if name not in laminations:
							laminations[name] = item2
						else:
							raise ValueError('Laminations with identical names.')
					elif isinstance(item2, flipper.kernel.Encoding):
						if name not in mapping_classes:
							mapping_classes[name] = item2
						else:
							raise ValueError('Encodings with identical names.')
					else:
						raise ValueError('Each item given must be a Lamination, Encoding, (String, Lamination) or (String, Encoding).')
				else:
					raise ValueError('Item must be named by a string.')
			else:
				raise ValueError('Each item given must be an Triangulation, Lamination, Encoding, (String, Lamination) or (String, Encoding).')
		
		for name, lamination in name_objects(unnamed_laminations, laminations):
			laminations[name] = lamination
		
		for name, encoding in name_objects(unnamed_mapping_classes, mapping_classes):
			mapping_classes[name] = encoding
		
		if triangulation is None:
			if len(laminations) > 0:
				triangulation = list(laminations.values())[0].triangulation
			elif len(mapping_classes) > 0:
				triangulation = list(mapping_classes.values())[0].source_triangulation
			else:
				raise ValueError('A triangulation, Lamination or Encoding must be given.')
		
		if any(laminations[name].triangulation != triangulation for name in laminations):
			raise ValueError('All laminations must be on the same triangulation.')
		if any(mapping_classes[name].source_triangulation != triangulation for name in mapping_classes):
			raise ValueError('All mapping classes must go from the same triangulation.')
		if any(mapping_classes[name].target_triangulation != triangulation for name in mapping_classes):
			raise ValueError('All mapping classes must go to the same triangulation.')
		
		data = flipper.kernel.EquippedTriangulation(triangulation, laminations, mapping_classes)
	
	return pickle.dumps((spec, version, data))

###############################################################################

def product(iterable, start=1, left=True):
	''' Return the product of start (default 1) and an iterable of numbers. '''
	
	value = None
	for item in iterable:
		if value is None:
			value = item
		elif left:
			value = item * value
		else:
			value = value * item
	if value is None: value = start
	
	return value

def encode_binary(sequence):
	''' Return the given sequence of 0's and 1's as a string in base 64. '''
	
	step = 6  # 2**step <= len(VISABLE_CHARACTERS)
	return ''.join(VISIBLE_CHARACTERS[int(''.join(str(x) for x in sequence[i:i+step]), base=2)] for i in range(0, len(sequence), step))

def gcd(numbers):
	''' Return the gcd of a list of numbers. '''
	
	return freduce(gcd2, numbers)

