import sys
import Flipper

if __name__ == '__main__':
	Flipper.application.main.main(None if len(sys.argv) == 1 else sys.argv[1])
