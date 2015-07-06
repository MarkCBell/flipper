
from __future__ import print_function

import flipper

def main(n=6, verbose=False):
	S = flipper.load.equipped_triangulation('S_1_1')
	buckets = []  # All the different conjugacy classes that we have found.
	for word in S.all_words(n):
		h = S.mapping_class(word)
		# Currently, we can only determine conjugacy classes for
		# pseudo-Anosovs, so we had better filter by them.
		if h.nielsen_thurston_type() == 'Pseudo-Anosov':
			# Check if this is conjugate to a mapping class we have seen.
			for bucket in buckets:
				# Conjugacy is transitive, so we only have to bother checking
				# if h is conjugate to the first entry in the bucket.
				if bucket[0].is_conjugate_to(h):
					bucket.append(h)
					break
			else:  # We have found a new conjugacy class.
				buckets.append([h])
		if verbose: print('%d buckets with distribution:\n %s' % (len(buckets), [len(bucket) for bucket in buckets]))
	
	if verbose:
		print(len(buckets))
		for bucket in buckets:
			print(bucket)
	
	return buckets

if __name__ == '__main__':
	main(4, verbose=True)

