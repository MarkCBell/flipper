
''' A module for representing triangulations along with laminations and mapping classes on them.

Provides one class: EquippedTriangulation. '''

import flipper

from random import choice

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
		lam_keys = sorted(self.laminations.keys())
		pos_keys = sorted(self.pos_mapping_classes.keys())
		return 'Triangulation with laminations: %s and mapping classes: %s.' % (lam_keys, pos_keys)
	
	def random_word(self, length, positive=True, negative=True):
		''' Return a random word of the required length.
		
		Positive (respectively negative) mapping classes are used if and only if
		positve (resp. negative) is True. At least one of them must be. '''
		
		assert(isinstance(length, flipper.IntegerType))
		
		pos_keys = sorted(self.pos_mapping_classes.keys())
		neg_keys = sorted(self.neg_mapping_classes.keys())
		
		if positive and negative:
			available_letters = pos_keys + neg_keys
		elif positive and not negative:
			available_letters = pos_keys
		elif not positive and negative:
			available_letters = neg_keys
		else:
			raise TypeError('At least one of positive and negative must be allowed.')
		
		return '.'.join(choice(available_letters) for _ in range(length))
	
	def all_words(self, length, reduced=True, conjugate=True, inverse=True, prefix=None, letters=None, _first=True):
		''' Yield all words of given length.
		
		If reduced is set then obviously freely reducible words are skipped.
		If conjugate is set then obviously cyclically reducible words are skipped.
		If inverse is set then words that can be made earlier by inverting are skipped.
		Inverse implies conjugate. '''
		
		if prefix is None: prefix = []
		if inverse: conjugate = True
		letters = set(self.mapping_classes) if letters is None else set(letters)
		
		if _first:
			for word in self.all_words(length, reduced, conjugate, inverse, prefix, letters, False):
				yield '.'.join(word)
		else:
			if length > 0:
				for letter in letters:
					if not reduced or not prefix or letter != prefix[-1].swapcase():
						prefix2 = prefix + [letter]
						lp = len(prefix2)
						if not conjugate or all(prefix2[i:2*i] >= prefix2[:min(i, len(prefix2)-i)] for i in range(lp // 2, lp)):
							for word in self.all_words(length-1, reduced, conjugate, inverse, prefix2, letters, False):
								yield word
			else:
				lp = len(prefix)
				prefix_inv = [x.swapcase() for x in prefix[::-1]]
				if not conjugate or not prefix or prefix[0] != prefix[-1].swapcase():
					if not conjugate or all(prefix[i:] + prefix[:i] >= prefix for i in range(lp)):
						if not inverse or any(x not in letters for x in prefix_inv) or all(prefix_inv[i:] + prefix_inv[:i] >= prefix for i in range(lp)):
							yield prefix
		
		return
	
	def decompose_word(self, word):
		''' Return a list of mapping_classes keys whose concatenation is word and the keys are chosen greedly.
		
		Raises a KeyError if the greedy decomposition fails. '''
		
		assert(isinstance(word, flipper.StringType))
		
		# By sorting the available keys, longest first, we ensure that any time we
		# get a match it is as long as possible.
		available_letters = sorted(self.mapping_classes, key=len, reverse=True)
		decomposition = []
		while word:
			for letter in available_letters:
				if word.startswith(letter):
					decomposition.append(letter)
					word = word[len(letter):]
					break
			else:
				raise KeyError('After extracting %s, the remaining %s cannot be greedly decomposed as a concatination of self.mapping_classes.' % (decomposition, word))
		
		return decomposition
	
	def mapping_class(self, word):
		''' Return the mapping class corresponding to the given word of a random one of given length if given an integer.
		
		The given word is decomposed using self.decompose_word and the composition
		of the mapping classes involved is returned.
		
		Raises a KeyError if the word does not correspond to a mapping class. '''
		
		assert(isinstance(word, flipper.StringType) or isinstance(word, flipper.IntegerType))
		
		if isinstance(word, flipper.IntegerType):
			word = self.random_word(word)
		
		# This can fail with a KeyError.
		decomposition = [self.mapping_classes[letter] for subword in word.split('.') for letter in self.decompose_word(subword)]
		return flipper.kernel.product(decomposition, start=self.triangulation.id_encoding())

