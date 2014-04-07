
import sys
import Flipper.application

if __name__ == '__main__':
	Flipper.application.start(load_path=(None if len(sys.argv) == 1 else sys.argv[1]))

