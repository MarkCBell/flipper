
from __future__ import print_function
from time import time
import cProfile
import pstats

import flipper

def main(verbose=False):
	if verbose: print('Running encoding profile.')
	
	start_time = time()
	# Add more tests here.
	# These need to be changed if the standard example triangulations ever change.
	
	for i in range(10, 30, 3):
		if verbose: print('Building B_%d' % i)
		S = flipper.load('B_%d' % i)
	
	return time() - start_time

if __name__ == '__main__':
	#print(main(verbose=True))
	#pstats.Stats(cProfile.Profile().run('main()')).strip_dirs().sort_stats('time').print_callers(20)
	#pstats.Stats(cProfile.Profile().run('main()')).strip_dirs().sort_stats('cumtime').print_callees(20)
	pstats.Stats(cProfile.Profile().run('main()')).strip_dirs().sort_stats('time').print_stats(30)

