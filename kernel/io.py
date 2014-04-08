
import pickle
from string import ascii_lowercase
# !?! Possible concern: ascii_lowercase is too short.

import Flipper

def package(objects, names=None):
	''' This packages an abstract triangulation, some laminations and mapping classes 
	into a format that can be writen to disk and loaded into an instance of the 
	Flipper application at a later date. 
	
	Objects must be either:
		1) an abstract triangulation,
		2) ({names -> laminations}, {name -> mapping classes}), or
		2) ([laminations], [mapping classes]) (or some combination of the pair).
	
	All laminations / mapping classes must be defined on the same triangulation and
	in the last two cases at least one of the pair must be non-empty. In the third
	case we will name the laminations and mapping classes sequentially:
		a, b, ..., z. '''
	
	if isinstance(objects, Flipper.AbstractTriangulation):
		abstract_triangulation = objects
		laminations = {}
		mapping_classes = {}
	elif isinstance(objects, (list, tuple)) and len(objects) == 2:
		laminations, mapping_classes = objects
		if isinstance(laminations, (list, tuple)): laminations = dict(list(zip(ascii_lowercase, laminations)))
		if isinstance(mapping_classes, (list, tuple)): mapping_classes = dict(list(zip(ascii_lowercase, mapping_classes)))
		if len(laminations) > 0:
			abstract_triangulation = list(laminations.values())[0].abstract_triangulation
		elif len(mapping_classes) > 0:
			abstract_triangulation = list(mapping_classes.values())[0].source_triangulation
		else:
			raise ValueError('Must be a pair of laminations and mapping classes.')
		
		if any(lamination.abstract_triangulation != abstract_triangulation for lamination in laminations.values()):
			raise ValueError('All laminations must be on the same abstract triangulations.')
		if any(mapping_class.source_triangulation != abstract_triangulation for mapping_class in mapping_classes.values()):
			raise ValueError('All mapping classes must go from the same abstract triangulations.')
		if any(mapping_class.target_triangulation != abstract_triangulation for mapping_class in mapping_classes.values()):
			raise ValueError('All mapping classes must go to the same abstract triangulations.')
	else:
		raise ValueError('Must be an abstract triangulation or a pair.')
	
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

