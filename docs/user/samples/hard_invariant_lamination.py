from time import time
import flipper

times = {}

examples = flipper.census('hard')

for index, row in examples.iterrows():
    h = flipper.load(row.surface).mapping_class(row.monodromy)
    start_time = time()
    try:
        h.invariant_lamination()
        times[row.monodromy] = time() - start_time
        print('%3d/%d: %s %s, Time: %0.3f' % (index+1, len(examples), row.surface, row.monodromy, times[row.monodromy]))
    except flipper.AssumptionError:
        times[row.monodromy] = time() - start_time
        print('%3d/%d: %s %s, not pA, Time: %0.3f' % (index+1, len(examples), row.surface, row.monodromy, times[row.monodromy]))

print('Average time: %0.3f' % (sum(times.values()) / len(examples)))
print('Slowest: %s, Time: %0.3f' % (max(times, key=lambda w: times[w]), max(times.values())))
print('Total time: %0.3f' % sum(times.values()))

