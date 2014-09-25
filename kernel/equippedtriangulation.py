
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
		
		# !?! Add more error checking here.
		
		self.triangulation = triangulation
		if isinstance(laminations, dict):
			self.laminations = laminations
		else:
			self.laminations = dict(list(flipper.kernel.utilities.name_objects(laminations)))
		if isinstance(mapping_classes, dict):
			self.mapping_classes = mapping_classes
		else:
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
		return ''.join(choice(available_letters) for _ in range(length))
	def mapping_class(self, word):
		''' Return the mapping class corresponding to the given word of a random one of given length if word is an integer. '''
		
		assert(isinstance(word, flipper.StringType) or isinstance(word, flipper.IntegerType))
		
		if isinstance(word, flipper.IntegerType):
			word = self.random_word(word)
		
		h = self.triangulation.id_encoding()
		for letter in word:
			h = h * self.mapping_classes[letter]
		
		return h
	def objects(self):
		''' Return a list of all objects known on this triangulation.
		
		This can be passed directly into flipper.application.start(). '''
		
		return [self.triangulation] + list(self.laminations.items()) + list(self.pos_mapping_classes.items())

