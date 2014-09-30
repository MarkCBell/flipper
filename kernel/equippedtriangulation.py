
''' A module for representing triangulations along with laminations and mapping classes on them.

Provides one class: EquippedTriangulation. '''

import flipper

from random import choice

class EquippedTriangulation(object):
	''' This represents a triangulation along with a collection of named laminations and mapping classes on it. '''
	def __init__(self, triangulation, laminations, mapping_classes):
		assert(isinstance(triangulation, flipper.kernel.AbstractTriangulation))
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
			self.mapping_classes = mapping_classes
		else:
			assert(all(isinstance(mapping_class, flipper.kernel.Encoding) for mapping_class in mapping_classes))
			assert(all(mapping_class.source_triangulation == self.triangulation for mapping_class in mapping_classes))
			assert(all(mapping_class.is_mapping_class() for mapping_class in mapping_classes))
			self.pos_mapping_classes = dict(list(flipper.kernel.utilities.name_objects(mapping_classes)))
			self.inverse_mapping_classes = dict((name.swapcase(), self.pos_mapping_classes[name].inverse()) for name in self.pos_mapping_classes)
			self.mapping_classes = dict(list(self.pos_mapping_classes.items()) + list(self.inverse_mapping_classes.items()))
	
	def random_word(self, length, positive=True, negative=True, other=True):
		''' Return a random word of the required length.
		
		Mapping classes with lower case names are used if and only if positive is True.
		Mapping classes with upper case names are used if and only if negative is True.
		Other mapping classes are used if and only if other is True. '''
		
		assert(isinstance(length, flipper.IntegerType))
		
		available_letters = [x for x in self.mapping_classes.keys() if (positive and x.islower()) or (negative and x.isupper()) or (other and not x.islower() and not x.isupper())]
		return '.'.join(choice(available_letters) for _ in range(length))
	
	def decompose_word(self, word):
		''' Return a list of mapping_class keys whose concatenation is word and the keys are chosen greedly.
		
		Raises a KeyError if the greedy decomposition fails. '''
		
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
		''' Return the mapping class corresponding to the given word of a random one of given length if word is an integer.
		
		Raises a KeyError if the word does not correspond to a mapping class. '''
		
		assert(isinstance(word, flipper.StringType) or isinstance(word, flipper.IntegerType))
		
		if isinstance(word, flipper.IntegerType):
			word = self.random_word(word)
		
		# This can fail with a KeyError.
		decomposition = [self.mapping_classes[letter] for subword in word.split('.') for letter in self.decompose_word(subword)]
		return flipper.kernel.product(decomposition, start=self.triangulation.id_encoding())
		
		h = self.triangulation.id_encoding()
		for letter in word:
			h = h * self.mapping_classes[letter]
		
		return h
	def objects(self):
		''' Return a list of all objects known on this triangulation.
		
		This can be passed directly into flipper.application.start(). '''
		
		return [self.triangulation] + list(self.laminations.items()) + list(self.pos_mapping_classes.items())

