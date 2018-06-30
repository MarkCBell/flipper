import flipper

length = 10
num_samples = 100

S = flipper.load('S_2_1')
for i in range(length):
    pA_samples = sum(1 if S.mapping_class(i).is_pseudo_anosov() else 0 if j for j in range(num_samples))
    print('Length %d: %0.1f%% pA' % (i, float(pA_samples) * 100 / num_samples))

