
from string import digits, ascii_letters, punctuation

def product(iterable, start=1, left=True):
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
	master_string = digits + ascii_letters + punctuation
	
	strn = ''
	while integer:
		strn = master_string[integer % base] + strn
		integer = integer // base
	
	return strn

