from __future__ import print_function
import sys
import flipper

S = flipper.load('S_1_1')
length = 6

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

print(buckets)

