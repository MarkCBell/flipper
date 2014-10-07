
import sys
import flipper.application

if __name__ == '__main__':
	flipper.application.start(load_from=(None if len(sys.argv) == 1 else sys.argv[1]))

