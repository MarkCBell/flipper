
import flipper
from random import seed

def main(verbose=False):
	seed(1)  # To make this test deterministic.
	
	S = flipper.load.equipped_triangulation('S_1_2')
	
	all_words = set(S.all_words(5, reduced=False, conjugate=False, inverse=False, exact=False))
	# There should be 8^5 + 8^4 + ... + 8^0 = 37449 words.
	if verbose: print('Constructed %d words.' % len(all_words))
	for _ in range(10):
		word = S.random_word(5)
		if word not in all_words:
			return False
	
	return True

if __name__ == '__main__':
	print(main(verbose=True))
