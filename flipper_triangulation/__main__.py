
import flipper

def main():
	print('flipper %s' % flipper.__version__)
	print('To open the flipper documentation use:')
	print('  > python -m flipper.help')
	print('To test your installation of flipper use:')
	print('  > python -m flipper.test')
	print('To start the flipper GUI use:')
	print('  > python -m flipper.app')
	print('Or start Python and import flipper directly.')

if __name__ == '__main__':
	main()

