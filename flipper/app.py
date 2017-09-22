
import sys
import argparse
import flipper.application

start = flipper.application.start

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Flipper GUI')
	parser.add_argument('load', nargs='?', help='path to load from when starting')
	args = parser.parse_args()
	
	start(load_from=args.load)

