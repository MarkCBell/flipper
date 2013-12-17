import sys
from App.App import main

main(None if len(sys.argv) == 1 else sys.argv[1])
