
import flipper

def main():
	print('flipper %s' % flipper.__version__)
	print('To start the flipper GUI use:')
	print('  > python -m flipper.app')
	print('To open the flipper documentation use:')
	print('  > python -m flipper.doc')
	print('To test your installation of flipper use:')
	print('  > python -m flipper.tests')
	print('To see a list of included examples use:')
	print('  > python -m flipper.example')
	print('Or start Python and import flipper directly.')

if __name__ == '__main__':
	main()

