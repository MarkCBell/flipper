import flipper

def main(verbose=False):
	if verbose: print('Running LLL tests.')
	
	M = flipper.kernel.Matrix([[1, 0, 0, 0, 0], [0, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 0], [5615, 3944, 8021, 2117, -7732]]).transpose()
	N = M.LLL().transpose()
	if verbose: print(N)
	if N != flipper.kernel.Matrix([[1, -1, -5, 3, -3],[0, -1, 0, -12, 4],[0, -1, 7, 1, -11],[1, 1, 5, -4, 2],[0, 1, -3, -2, -14]]):
		return False
	
	M = flipper.kernel.Matrix([[10, 11], [11, 12]]).transpose()
	N = M.LLL().transpose()
	if verbose: print(N)
	if N != flipper.kernel.Matrix([[-1, 0],[0, 1]]):
		return False
	
	M = flipper.kernel.Matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [15, 22, 13, -35]]).transpose()
	N = M.LLL().transpose()
	if verbose: print(N)
	if N != flipper.kernel.Matrix([[0, -1, 2, -1],[1, 0, -2, -2],[1, 1, 1, 2],[0, -2, -1, 2]]):
		return False
	
	M = flipper.kernel.Matrix([[1, 0, 0], [0, 1, 0], [15, 22, -22]]).transpose()
	N = M.LLL().transpose()
	if verbose: print(N)
	if N != flipper.kernel.Matrix([[0, 3, -1],[1, 0, 0],[0, 1, 7]]):
		return False
	
	M = flipper.kernel.Matrix([[1, -1, 3], [1, 0, 5], [1, 2, 6]]).transpose()
	N = M.LLL().transpose()
	if verbose: print(N)
	if N != flipper.kernel.Matrix([[0, 1, -1],[1, 0, 0],[0, 1, 2]]):
		return False
	
	M = flipper.kernel.Matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [22, 87, 45, -67]]).transpose()
	N = M.LLL().transpose()
	if verbose: print(N)
	if N != flipper.kernel.Matrix([[1, -2, 0, 1],[0, 0, 1, 8],[1, 1, 1, -1],[0, 1, -2, 3]]):
		return False
	
	M = flipper.kernel.Matrix([[1, -1], [-1, 2]]).transpose()
	N = M.LLL().transpose()
	if verbose: print(N)
	if N != flipper.kernel.Matrix([[1, 0],[0, -1]]):
		return False
	
	M = flipper.kernel.Matrix([[2, 3], [0, 1]]).transpose()
	N = M.LLL().transpose()
	if verbose: print(N)
	if N != flipper.kernel.Matrix([[-1, 1],[1, 1]]):
		return False
	
	M = flipper.kernel.Matrix([[1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0], [17, 8, 10, 14, 3, -30]]).transpose()
	N = M.LLL().transpose()
	if verbose: print(N)
	if N != flipper.kernel.Matrix([[-1, -1, 0, 1, 0, -1],[1, 0, -1, 0, -2, 0],[1, 0, 1, 0, 0, -1],[0, 1, 0, 1, -1, 0],[0, 1, -1, 0, 0, -1],[1, 0, -1, 1, 0, 0]]):
		return False
	
	M = flipper.kernel.Matrix([[263, -224, -3021], [289, -246, -3319], [850, -724, -9764]]).transpose()
	N = M.LLL().transpose()
	if verbose: print(N)
	if N != flipper.kernel.Matrix([[-1, 1, 0],[1, 1, 0],[0, 0, 2]]):
		return False
	
	return True

if __name__ == '__main__':
	main(verbose=True)

