
''' A module of useful, generic functions; including input and output formatting. '''

import flipper

import pickle
import itertools
from string import ascii_lowercase, digits, ascii_letters, punctuation

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
	''' This packages an abstract triangulation, some laminations and mapping classes
	into a format that can be writen to disk and loaded into an instance of the
	flipper application at a later date.
	
	Objects must be a non-empty list where each item is:
		1) an abstract triangulation (at most one may be given),
		2) a Lamination,
		3) an Encoding,
		4) a pair (String, Lamination),
		5) a pair (String, Encoding).
	Or an EquippedTriangulation.
	
	All laminations / mapping classes must be defined on the same triangulation
	We will automatically name items of type 2) and 3) sequentially:
		a, b, ..., z, aa, ab, ... . '''
	
	if isinstance(objects, flipper.kernel.EquippedTriangulation):
		objects = [objects.triangulation] + list(objects.laminations.items()) + list(objects.pos_mapping_classes.items())
	
	triangulation = None
	laminations, mapping_classes = {}, {}
	unnamed_laminations, unnamed_mapping_classes = [], []
	for item in objects:
		if isinstance(item, flipper.kernel.AbstractTriangulation):
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
				if isinstance(item2, flipper.kernel.AbstractTriangulation):
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
			raise ValueError('Each item given must be an AbstractTriangulation, Lamination, Encoding, (String, Lamination) or (String, Encoding).')
	
	for name, lamination in name_objects(unnamed_laminations, laminations):
		laminations[name] = lamination
	
	for name, encoding in name_objects(unnamed_mapping_classes, mapping_classes):
		mapping_classes[name] = encoding
	
	if triangulation is None:
		if len(laminations) > 0:
			triangulation = laminations[0][1].triangulation
		elif len(mapping_classes) > 0:
			triangulation = mapping_classes[0][1].source_triangulation
		else:
			raise ValueError('A triangulation, Lamination or Encoding must be given.')
	
	if any(laminations[name].triangulation != triangulation for name in laminations):
		raise ValueError('All laminations must be on the same abstract triangulations.')
	if any(mapping_classes[name].source_triangulation != triangulation for name in mapping_classes):
		raise ValueError('All mapping classes must go from the same abstract triangulations.')
	if any(mapping_classes[name].target_triangulation != triangulation for name in mapping_classes):
		raise ValueError('All mapping classes must go to the same abstract triangulations.')
	
	spec = 'A flipper kernel file.'
	version = flipper.version
	data = flipper.kernel.EquippedTriangulation(triangulation, laminations, mapping_classes)
	return pickle.dumps((spec, version, data))

###############################################################################

class memoized(object):
	''' Decorator. Caches a function's return value each time it is called.
	
	If called later with the same arguments, the cached value is returned
	(not reevaluated). This is stronger than the standard memoization as it
	caches exceptions that are thrown too. '''
	def __init__(self, func):
		self.func = func
		self.cache = {}
	def __call__(self, *args):
		try:
			if args not in self.cache:
				try:
					self.cache[args] = self.func(*args)
				except Exception as error:
					self.cache[args] = error
		except TypeError:
			# If we can't cache the results then it is better to not than blow up.
			return self.func(*args)
		
		if isinstance(self.cache[args], Exception):
			raise self.cache[args]
		else:
			return self.cache[args]
	def __repr__(self):
		return self.func.__repr__
	def __get__(self, obj, objtype):
		''' Support instance methods. '''
		
		def memoized_function(*args):
			''' Call the given instance with these arguements. '''
			
			return self.__call__(obj, *args)
		
		memoized_function.__doc__ = 'A memoized version of ' + self.func.__name__ + '.\n\n' + self.func.__doc__
		return memoized_function

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

def change_base(integer, base=64):
	''' Return the given number as a string in the given base.
	
	The given base must be less than 95. '''
	
	assert(base < len(VISIBLE_CHARACTERS))
	
	strn = ''
	while integer:
		strn = VISIBLE_CHARACTERS[integer % base] + strn
		integer = integer // base
	
	return strn

