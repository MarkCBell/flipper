from time import time
import flipper

times = {}
surface = 'S_3_1'
length = 20
num_samples = 100

S = flipper.load(surface)
for index in range(num_samples):
    monodromy = S.random_word(length)
    h = S.mapping_class(monodromy)
    start_time = time()
    try:
        h.invariant_lamination()
        times[monodromy] = time() - start_time
        print('%3d/%d: %s %s, Time: %0.3f' % (index+1, num_samples, surface, monodromy, times[monodromy]))
    except flipper.AssumptionError:
        times[monodromy] = time() - start_time
        print('%3d/%d: %s %s, not pA, Time: %0.3f' % (index+1, num_samples, surface, monodromy, times[monodromy]))

print('Average time: %0.3f' % (sum(times.values()) / num_samples))
print('Slowest: %s, Time: %0.3f' % (max(times, key=lambda w: times[w]).replace('.', ''), max(times.values())))
print('Total time: %0.3f' % sum(times.values()))

