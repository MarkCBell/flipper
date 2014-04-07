
import pickle

import Flipper

def package(abstract_triangulation, laminations=None, mapping_classes=None):
	''' Dumps some information into a format that can be loaded into an instance of 
	the Flipper application. 
	
	Let T = abstract_triangulation then laminations is a list of pairs (name, lamination)
	where name is a valid name and lamination is on T.
	Similarly mapping_classes is a list of pairs (name, mapping_class) where
	name is a valid name and mapping_class is on T. '''
	if laminations is None: laminations = []
	if mapping_classes is None: mapping_classes = []
	
	spec = 'A Flipper kernel file.'
	version = Flipper.version.Flipper_version
	
	data = (abstract_triangulation, laminations, mapping_classes)
	return pickle.dumps((spec, version, data))

def depackage(packaged_objects):
	''' Extracts the stuff from the contents of a Flipper kernel file. '''
	(spec, version, data) = pickle.loads(packaged_objects)
	if spec != 'A Flipper kernel file.':
		raise ValueError('Not a valid specification.')
	if Flipper.version.version_tuple(version) != Flipper.version.version_tuple(Flipper.version.Flipper_version):
		raise ValueError('Wrong version of Flipper.')
	
	[abstract_triangulation, laminations, mapping_classes] = data
	return abstract_triangulation, laminations, mapping_classes

