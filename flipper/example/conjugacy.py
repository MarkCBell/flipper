
from __future__ import print_function

import flipper
import sys

def main(length):
	S = flipper.load('S_1_1')
	buckets = []  # All the different conjugacy classes that we have found.
	# We could order the buckets by something, say dilatation.
	for index, word in enumerate(S.all_words(length)):
		h = S.mapping_class(word)
		# Currently, we can only determine conjugacy classes for
		# pseudo-Anosovs, so we had better filter by them.
		if h.is_pseudo_anosov():
			# Check if this is conjugate to a mapping class we have seen.
			for bucket in buckets:
				# Conjugacy is transitive, so we only have to bother checking
				# if h is conjugate to the first entry in the bucket.
				if bucket[0].is_conjugate_to(h):
					bucket.append(h)
					break
			else:  # We have found a new conjugacy class.
				buckets.append([h])
		print('\r%d words in %d conjugacy classes.' % (index, len(buckets)), end='')
		sys.stdout.flush()
	
	return buckets

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Group mapping classes into conjugacy classes.')
	parser.add_argument('--length', type=int, default=6, help='length of words to generate')
	parser.add_argument('--show', action='store_true', default=False, help='show the source code of this example and exit')
	args = parser.parse_args()
	
	if args.show:
		print(open(__file__, 'r').read())
	else:
		main(args.length)

