
''' A module for representing triangulations along with laminations and mapping classes on them.

Provides one class: EquippedTriangulation. '''

from random import choice
from itertools import product
import re

import flipper

def inverse(word):
	''' Return the inverse of a word by reversing and swapcasing it. '''
	
	return tuple([letter.swapcase() for letter in reversed(word)])

def generate_ordering(letters):
	''' Return a function which determines if v >= w (with respect to the short-lex ordering).
	
	If v or w contains any letter not in letters then returns False. '''
	
	positions = dict([(letter, index) for index, letter in enumerate(letters)])
	return lambda v, w: all(x in positions for x in v) and \
		all(y in positions for y in v) and \
		[len(v)] + [positions[x] for x in v] >= [len(w)] + [positions[y] for y in w]

class EquippedTriangulation(object):
	''' This represents a triangulation along with a collection of named laminations and mapping classes on it.
	
	Most importantly this object can construct a mapping class from a string descriptor.
	See self.mapping_class for additional information. '''
	def __init__(self, triangulation, laminations, mapping_classes):
		assert(isinstance(triangulation, flipper.kernel.Triangulation))
		assert(isinstance(laminations, (dict, list, tuple)))
		assert(isinstance(mapping_classes, (dict, list, tuple)))
		
		self.triangulation = triangulation
		if isinstance(laminations, dict):
			assert(all(isinstance(key, flipper.StringType) for key in laminations))
			assert(all(isinstance(laminations[key], flipper.kernel.Lamination) for key in laminations))
			assert(all(laminations[key].triangulation == self.triangulation for key in laminations))
			self.laminations = laminations
		else:
			assert(all(isinstance(lamination, flipper.kernel.Lamination) for lamination in laminations))
			assert(all(lamination.triangulation == self.triangulation for lamination in laminations))
			self.laminations = dict(list(flipper.kernel.utilities.name_objects(laminations)))
		
		if isinstance(mapping_classes, dict):
			assert(all(isinstance(key, flipper.StringType) for key in mapping_classes))
			assert(all(isinstance(mapping_classes[key], flipper.kernel.Encoding) for key in mapping_classes))
			assert(all(mapping_classes[key].source_triangulation == self.triangulation for key in mapping_classes))
			assert(all(mapping_classes[key].is_mapping_class() for key in mapping_classes))
			assert(all(key.swapcase() not in mapping_classes for key in mapping_classes))
			
			self.pos_mapping_classes = dict(mapping_classes)
			self.neg_mapping_classes = dict((name.swapcase(), self.pos_mapping_classes[name].inverse()) for name in self.pos_mapping_classes)
			self.mapping_classes = dict(list(self.pos_mapping_classes.items()) + list(self.neg_mapping_classes.items()))
		else:
			assert(all(isinstance(mapping_class, flipper.kernel.Encoding) for mapping_class in mapping_classes))
			assert(all(mapping_class.source_triangulation == self.triangulation for mapping_class in mapping_classes))
			assert(all(mapping_class.is_mapping_class() for mapping_class in mapping_classes))
			
			self.pos_mapping_classes = dict(list(flipper.kernel.utilities.name_objects(mapping_classes)))
			self.neg_mapping_classes = dict((name.swapcase(), self.pos_mapping_classes[name].inverse()) for name in self.pos_mapping_classes)
			self.mapping_classes = dict(list(self.pos_mapping_classes.items()) + list(self.neg_mapping_classes.items()))
		
		self.zeta = self.triangulation.zeta
	
	def __repr__(self):
		return str(self)
	def __str__(self):
		lam_keys = sorted(self.laminations.keys())
		pos_keys = sorted(self.pos_mapping_classes.keys())
		return 'Triangulation with laminations: %s and mapping classes: %s.' % (lam_keys, pos_keys)
	
	def random_word(self, length, positive=True, negative=True, letters=None):
		''' Return a random word of the required length.
		
		The letters to choose from can be specified or, alternatively, the set
		of positive, negative or all (default) mapping classes can be used by using the 
		flags postive and negative. '''
		
		assert(isinstance(length, flipper.IntegerType))
		
		if letters is None:
			pos_keys = sorted(self.pos_mapping_classes.keys())
			neg_keys = sorted(self.neg_mapping_classes.keys())
			
			if positive and negative:
				letters = pos_keys + neg_keys
			elif positive and not negative:
				letters = pos_keys
			elif not positive and negative:
				letters = neg_keys
			else:
				raise TypeError('At least one of positive and negative must be allowed.')
		
		return '.'.join(choice(letters) for _ in range(length))
	
	def generate_skip(self, length, letters=None):
		''' Return a dictionary whose keys are substrings that cannot appear in reduced words. '''
		
		letters = letters if letters is not None else sorted(self.mapping_classes, key=lambda x: (len(x), x.lower(), x.swapcase()))
		order = generate_ordering(letters)
		
		skip = dict()
		# Start by finding some common relations:
		# Trivial relations.
		for letter in letters:
			skip[(letter, letter.swapcase())] = tuple()
		# Commuting and braiding.
		for a, b in product(letters, repeat=2):
			A, B = a.swapcase(), b.swapcase()
			for relator in [(a, b, A, B), (a, b, a, B, A, B)]:
				if self.mapping_class('.'.join(relator)).is_identity():
					j = len(relator) // 2
					for k in range(len(relator)):  # Cycling.
						ww = relator[k:] + relator[:k]
						if order(ww[:j], inverse(ww[j:])) and ww[:j] != inverse(ww[j:]):
							if all(ww[l:m] not in skip for m in range(j+1) for l in range(m)):
								skip[ww[:j]] = inverse(ww[j:])
		
		# Then do the actual search to the given relator_len.
		temp_options = {
			'group': True,
			'conjugacy': True,
			'bundle': False,
			'exact': True,
			'letters': letters,
			'order': order,
			'skip': skip,
			'prefilter': None,
			'filter': None
			}
		for i in range(1, length+1):
			relators = [word for word in self.all_words_unjoined(i, **temp_options) if self.mapping_class('.'.join(word)).is_identity()]
			for j in range(i // 2, i+1):  # Slice length.
				for relator in relators:
					for k in range(i):  # Cycling.
						ww = relator[k:] + relator[:k]
						if order(ww[:j], inverse(ww[j:])) and ww[:j] != inverse(ww[j:]):
							if all(ww[l:m] not in skip for m in range(j+1) for l in range(m)):
								skip[ww[:j]] = inverse(ww[j:])
		
		return skip
	
	def all_words_unjoined(self, length, prefix=None, **options):
		''' Yield all words of given length.
		
		Users should not call directly but should use self.all_words(...) instead.
		Assumes that various options have been set. '''
		
		if prefix is None: prefix = tuple()
		order = options['order']
		letters = options['letters']
		skip = options['skip']
		lp = len(prefix)
		lp2 = lp + 1
		
		if not options['exact'] or length == 0:
			prefix_inv = inverse(prefix)
			
			good = True
			if good and options['conjugacy'] and prefix[-1:] == inverse(prefix[:1]): good = False
			if good and options['conjugacy'] and not all(order(prefix[i:] + prefix[:i], prefix) for i in range(lp)): good = False
			if good and options['bundle'] and all(x in letters for x in prefix_inv):
				if not all(order(prefix_inv[i:] + prefix_inv[:i], prefix) for i in range(lp)): good = False
			if good and options['filter'] is not None and not options['filter'](prefix): good = False
			if good:
				yield prefix
		
		if length > 0:
			for letter in letters:
				prefix2 = prefix + (letter,)
				
				good = True
				if good and options['group'] and prefix and any(prefix2[i:] in skip for i in range(lp2)): good = False
				if good and options['conjugacy'] and not all(order(prefix2[i:2*i], prefix2[:min(i, lp2-i)]) for i in range(lp2 // 2, lp)): good = False
				if good and options['prefilter'] is not None and not options['prefilter'](prefix): good = False
				if good:
					for word in self.all_words_unjoined(length-1, prefix2, **options):
						yield word
		
		return
	
	def all_words(self, length, prefix=None, **options):
		''' Yield all words of at most the specified length.
		
		There are several equivalence relations defined on these words.
		Words may represent the same:
			- mapping class group element (==),
			- conjugacy class (~~), or
			- fibre class (~?).
		
		Valid options and their defaults:
			group=True -- yield few words representing the same group element.
			conjugacy=True -- yield few words representing the same conjugacy class.
			bundle=True -- yield few words representing the same mapping torus.
			exact=False -- skip words that do not have exactly the required length.
			letters=self.mapping_classes - a list of available letters to use, in alphabetical order.
			skip=None -- an iterable containing substrings that cannot appear.
			relator_len=2 -- if skip is not given then search words of length at most this much looking for relations.
			prefilter=None -- fliter the prefixes of words by this function.
			filter=None -- fliter the words by this function.
		
		Notes:
			- By default letters are sorted by (length, lower case, swapcase).
			- bundle ==> conjugacy ==> group. '''
		
		prefix = tuple() if prefix is None else tuple(self.decompose_word(prefix))
		
		default_options = {
			'group': True,
			'conjugacy': True,
			'bundle': True,
			'letters': sorted(self.mapping_classes, key=lambda x: (len(x), x.lower(), x.swapcase())),
			'exact': False,
			'skip': None,
			'relator_len': 2,  # 6 is also a good default as it gets all commutators and braids.
			'prefilter': None,
			'filter': None
			}
		
		# Install any missing options with defaults.
		for option in default_options:
			if option not in options: options[option] = default_options[option]
		
		# Set implications. We use the contrapositive as these flags are set to True by default.
		if not options['group']: options['conjugacy'] = False
		if not options['conjugacy']: options['bundle'] = False
		
		# Build the ordering based on the letters given.
		letters = options['letters']
		options['order'] = generate_ordering(letters)
		
		# Build the list of substrings that must be avoided.
		if options['skip'] is not None:
			skip = set(options['skip'])
		elif options['group']:
			skip = self.generate_skip(options['relator_len'], letters)
		else:
			skip = set()
		options['skip'] = skip
		
		for word in self.all_words_unjoined(length - len(prefix), prefix, **options):
			yield '.'.join(word)
	
	def decompose_word(self, word):
		''' Return a list of mapping_classes keys whose concatenation is word and the keys are chosen greedly.
		
		Raises a KeyError if the greedy decomposition fails. '''
		
		assert(isinstance(word, flipper.StringType))
		
		# By sorting the available keys, longest first, we ensure that any time we
		# get a match it is as long as possible.
		available_letters = sorted(self.mapping_classes, key=len, reverse=True)
		decomposition = []
		for subword in word.split('.'):
			while subword:
				for letter in available_letters:
					if subword.startswith(letter):
						decomposition.append(letter)
						subword = subword[len(letter):]
						break
				else:
					raise KeyError('After extracting %s, the remaining %s cannot be greedly decomposed as a concatination of self.mapping_classes.' % ('.'.join(decomposition), word))
		
		return decomposition
	
	def mapping_class(self, word):
		''' Return the mapping class corresponding to the given word of a random one of given length if given an integer.
		
		The given word is decomposed using self.decompose_word and the composition
		of the mapping classes involved is returned.
		
		Raises a KeyError if the word does not correspond to a mapping class. '''
		
		assert(isinstance(word, flipper.StringType) or isinstance(word, flipper.IntegerType))
		
		if isinstance(word, flipper.IntegerType):
			word = self.random_word(word)
		
		# Expand out parenthesis powers.
		# This can fail with a KeyError.
		old_word = None
		while word != old_word:  # While a change was made.
			old_word = word
			for subword, power in re.findall(r'(\([\w_\.]*\))\^(-?\d+)', word):
				decompose = self.decompose_word(subword[1:-1])
				int_power = int(power)
				if int_power > 0:
					replacement = '.'.join(decompose) * int_power
				else:
					replacement = '.'.join(letter.swapcase() for letter in decompose[::-1]) * abs(int_power)
				word = word.replace(subword + '^' + power, replacement)
		
		# Expand out powers without parenthesis. Here we use a greedy algorithm and take the
		# longest mapping class occuring before the power. Note that we only do one pass and so
		# only all pure powers to be expanded once, that is 'aBBB^2^3' is not recognised.
		available_letters = sorted(self.mapping_classes, key=len, reverse=True)
		for letter in available_letters:
			for subword, power in re.findall(r'(%s)\^(-?\d+)' % letter, word):
				int_power = int(power)
				word = word.replace(subword + '^' + power, (letter if int_power > 0 else letter.swapcase()) * abs(int_power))
		
		# This can fail with a KeyError.
		decomposition = [self.mapping_classes[letter] for letter in self.decompose_word(word)]
		return flipper.kernel.product(decomposition, start=self.triangulation.id_encoding())


def create_equipped_triangulation(objects):
	
	''' Create an EquippedTriangulation from a list of triangulations, laminations and mapping classes.
	
	Objects must be a non-empty list where each item is:
		1) an triangulation (at most one may be given),
		2) a Lamination,
		3) an Encoding,
		4) a pair (String, Lamination),
		5) a pair (String, Encoding).
	
	All laminations / mapping classes must be defined on the same triangulation
	We will automatically name items of type 2) and 3) sequentially:
		a, b, ..., z, aa, ab, ... . '''
	
	triangulation = None
	laminations, mapping_classes = {}, {}
	unnamed_laminations, unnamed_mapping_classes = [], []
	for item in objects:
		if isinstance(item, flipper.kernel.Triangulation):
			if triangulation is None:
				triangulation = item
			else:
				if item != triangulation:
					raise ValueError('Only one triangulation may be given.')
		elif isinstance(item, flipper.kernel.Lamination):
			unnamed_laminations.append(item)
		elif isinstance(item, flipper.kernel.Encoding):
			unnamed_mapping_classes.append(item)
		elif isinstance(item, (list, tuple)) and len(item) == 2:
			name, item2 = item
			if isinstance(name, flipper.StringType):
				if isinstance(item2, flipper.kernel.Lamination):
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
			raise ValueError('Each item given must be: Triangulation, Lamination, Encoding, (String, Lamination) or (String, Encoding).')
	
	for name, lamination in flipper.kernel.utilities.name_objects(unnamed_laminations, laminations):
		laminations[name] = lamination
	
	for name, encoding in flipper.kernel.utilities.name_objects(unnamed_mapping_classes, mapping_classes):
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
	
	return flipper.kernel.EquippedTriangulation(triangulation, laminations, mapping_classes)

