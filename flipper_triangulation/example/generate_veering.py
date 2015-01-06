
from __future__ import print_function

import flipper
from itertools import product
from flipper.example.non_geometric_bundles import is_degenerate
from snappy import Manifold

S = flipper.load.equipped_triangulation('S_0_4')
T = S.triangulation
zeta = T.zeta
X = range(zeta)
L = T.empty_lamination()

# 6(g-1) + 3n <= 12
# g \ n  1  2  3  4  5  6  7
# 0               6  9 12 15
# 1      3  6  9 12 15
# 2      9  12 15
# 3     15

# Checked:
# S_0_4 -> __
# S_0_5 -> __
# S_0_6 -> __
# S_1_1 -> 12
# S_1_2 -> 10
# S_1_3 -> __
# S_1_4 -> __
# S_2_1 ->  9
# S_2_2 -> __

def no_repeat(X, i, prefix=None):
	if prefix is None: prefix = []
	for x in X:
		if not prefix or x != prefix[-1]:
			if i > 1:
				for pattern in no_repeat(X, i-1, prefix + [x]):
					yield pattern
			else:
				yield prefix + [x]

def valid_prefix(X, pattern, n):
	#if len(set(X).difference(pattern)) > n - len(pattern):
	#	return False
	
	try:
		E = T.encode_flips(pattern)
		B = flipper.kernel.SplittingSequence(L, pattern, None).bundle()
		return True
	except IOError: #(AssertionError, IndexError):
		return False

def backtrack(pattern):
	while pattern and pattern[-1] == zeta-1:
		pattern.pop()
	
	if pattern:
		pattern[-1] += 1
	
	return pattern


def test(n):
	c, d = 0, 0
	
	pattern = [0]
	while pattern[0] == 0:
		print('\n%s' % pattern, end='')
		if len(set(pattern)) == T.zeta and pattern[1] <= T.zeta // 2:
			try:
				E = T.encode_flips(pattern)
			except AssertionError:
				pass  # Not a flip sequence.
			else:
				isoms = E.target_triangulation.isometries_to(E.source_triangulation)
				print('*  %d' % len(isoms), end='')
				for isom in isoms:
					try:
						B = flipper.kernel.SplittingSequence(L, pattern, isom).bundle()
					except (AssertionError, IndexError):
						pass  # Not veering.
					else:
						c += 1
						M = Manifold(B.snappy_string(filled=False))
						if M.volume() < 1:
							if is_degenerate(M):
								print('!!!!!!!!!!!', pattern, isom)
								d += 1
								assert(False)
		
		if len(pattern) < n and valid_prefix(X, pattern, n):
			pattern = pattern + [0]
		else:
			pattern = backtrack(pattern)
	
	print('VEERING BUNDLES: %d' % c)
	print('DEGENERAGE BUNDLES: %d' % d)
	assert(d == 0)

print('test')
test(9)

