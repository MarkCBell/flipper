import sys
from Flipper.App.Main import main

if __name__ == '__main__':
	main(None if len(sys.argv) == 1 else sys.argv[1])
