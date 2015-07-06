
import sys
import flipper.application

start = flipper.application.start

if __name__ == '__main__':
	start(load_from=(None if len(sys.argv) == 1 else sys.argv[1]))

