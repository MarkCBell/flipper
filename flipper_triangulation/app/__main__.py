
import sys
import flipper.app

if __name__ == '__main__':
	flipper.app.start(load_from=(None if len(sys.argv) == 1 else sys.argv[1]))

