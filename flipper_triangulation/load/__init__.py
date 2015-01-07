
''' Provides an interface for loading premade examples and censuses. '''

from . import databases
from . import equippedtriangulation

database = databases.load
equipped_triangulation = equippedtriangulation.load

