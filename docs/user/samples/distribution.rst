from __future__ import print_function
import sys
import flipper

surface = 'S_2_1'
length = 10
num_samples = 100

S = flipper.load(surface)
for i in range(length):
    count = 0
    for j in range(num_samples):
        if S.mapping_class(i).is_pseudo_anosov(): count += 1
        print('\rLength: %d, Computed %d/%d - %0.1f%% pA' % (i, (j+1), num_samples, float(count) * 100 / (j+1)), end='')
        sys.stdout.flush()
    print('')

