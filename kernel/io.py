
import pickle
from string import ascii_lowercase
from itertools import product
from math import log

import flipper

def string_generator(n, skip=None):
	if skip is None: skip = []
	
	alphabet = ascii_lowercase
	k = n + len(skip)
	p = int(log(k), len(alphabet)) + 1
	results = []
	for i in range(1, p+1):
		for letters in product(alphabet, repeat=i):
			word = ''.join(letters)
			if word not in skip:
				results.append(word)
			if len(results) >= n:
				return results

def package(objects):
	''' This packages an abstract triangulation, some laminations and mapping classes
	into a format that can be writen to disk and loaded into an instance of the
	flipper application at a later date.
	
	Objects must be a non-empty list where each item is:
		1) an abstract triangulation (at most one may be given),
		2) a Lamination,
		3) an Encoding,
		4) a pair (String, Lamination),
		5) a pair (String, Encoding).
	
	All laminations / mapping classes must be defined on the same triangulation
	We will automatically name items of type 2) and 3) sequentially:
		a, b, ..., z. '''
	
	triangulation = None
	laminations, mapping_classes = [], []
	unnamed_laminations, unnamed_mapping_classes = [], []
	lamination_names, mapping_class_names = set(), set()
	for item in objects:
		if isinstance(item, flipper.kernel.AbstractTriangulation):
			if triangulation is not None:
				raise ValueError('Only one triangulation may be given.')
			triangulation = item
		if isinstance(item, flipper.kernel.Lamination):
			unnamed_laminations.append(item)
		elif isinstance(item, flipper.kernel.Encoding):
			unnamed_mapping_classes.append(item)
		elif isinstance(item, (list, tuple)) and len(item) == 2:
			name, item2 = item
			if isinstance(name, flipper.String_Type):
				if isinstance(item2, flipper.kernel.AbstractTriangulation):
					if triangulation is not None:
						raise ValueError('Only one triangulation may be given.')
					triangulation = item2
				elif isinstance(item2, flipper.kernel.Lamination):
					if name not in lamination_names:
						laminations.append(item)
						lamination_names.add(name)
					else:
						raise ValueError('Laminations with identical names.')
				elif isinstance(item2, flipper.kernel.Encoding):
					if name not in mapping_class_names:
						mapping_classes.append(item)
						mapping_class_names.add(name)
					else:
						raise ValueError('Encodings with identical names.')
				else:
					raise ValueError('Each item given must be a Lamination, Encoding, (String, Lamination) or (String, Encoding).')
			else:
				raise ValueError('Item must be named by a string.')
		else:
			raise ValueError('Each item given must be a Lamination, Encoding, (String, Lamination) or (String, Encoding).')
	
	for name, lamination in zip(string_generator(len(unnamed_laminations), lamination_names), unnamed_laminations):
		laminations.append((name, lamination))
	
	for name, encoding in zip(string_generator(len(unnamed_mapping_classes), mapping_class_names), unnamed_mapping_classes):
		mapping_classes.append((name, encoding))
	
	if triangulation is None:
		if len(laminations) > 0:
			triangulation = laminations[0][1].triangulation
		elif len(mapping_classes) > 0:
			triangulation = mapping_classes[0][1].source_triangulation
		else:
			raise ValueError('A triangulation, Lamination or Encoding must be given.')
	
	if any(lamination.triangulation != triangulation for name, lamination in laminations):
		raise ValueError('All laminations must be on the same abstract triangulations.')
	if any(mapping_class.source_triangulation != triangulation for name, mapping_class in mapping_classes):
		raise ValueError('All mapping classes must go from the same abstract triangulations.')
	if any(mapping_class.target_triangulation != triangulation for name, mapping_class in mapping_classes):
		raise ValueError('All mapping classes must go to the same abstract triangulations.')
	else:
		raise ValueError('Must be an abstract triangulation or a pair.')
	
	spec = 'A flipper kernel file.'
	version = flipper.version
	
	data = (triangulation, laminations, mapping_classes)
	return pickle.dumps((spec, version, data))

def depackage(packaged_objects):
	''' Extracts the stuff from the contents of a flipper kernel file. '''
	(spec, version, data) = pickle.loads(packaged_objects)
	if spec != 'A flipper kernel file.':
		raise ValueError('Not a valid specification.')
	if version != flipper.version:
		raise ValueError('Wrong version of flipper.')
	
	[triangulation, laminations, mapping_classes] = data
	return triangulation, laminations, mapping_classes

