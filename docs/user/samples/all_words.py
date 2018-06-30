from time import time
import flipper

length = 7
S = flipper.load('S_1_2')  # Get an EquippedTriangulation.

start_time = time()
all_words = list(S.all_words(length))
print('Built %d words in %0.3fs.' % (len(all_words), time() - start_time))

# In parallel:
start_time = time()
all_words2 = list(S.all_words(length, cores=2))
print('Built %d words in %0.3fs.' % (len(all_words2), time() - start_time))

assert len(all_words) == len(set(all_words)) and set(all_words) == set(all_words2)

