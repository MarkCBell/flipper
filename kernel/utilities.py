
''' This module provides a collection of useful generic functions. '''

from string import digits, ascii_letters, punctuation

VISIBLE_CHARACTERS = digits + ascii_letters + punctuation

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

