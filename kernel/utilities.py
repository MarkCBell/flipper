
def product(iterable, start=1, left=True):
	iterable = list(iterable)  # Shouldn't really do this.
	if iterable:
		value = iterable[0]
		for item in iterable[1:]:
			value = item * value if left else value * item
	else:
		value = start
	
	return value

