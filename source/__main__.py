
''' A simple starting point for flipper. '''

import flipper

def main():
	''' Describe how to start flipper. '''
	
	print('flipper %s' % flipper.__version__)
	print('Some basic commands:')
	print('  > python -m flipper.app      # To start the flipper GUI.')
	print('  > python -m flipper.doc      # To open the flipper documentation.')
	print('  > python -m flipper.example  # To see a list of included examples.')
	print('  > python -m flipper.test     # To test your installation of flipper.')
	print('  > python -m flipper.profile  # To see profile your installation of flipper.')
	print('Or start Python and import flipper directly.')

if __name__ == '__main__':
	main()

