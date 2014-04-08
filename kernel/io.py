
import pickle

import Flipper

def package(objects, names=None):
	''' Dumps packages an abstract triangulation, some laminations and mapping classes 
	into a format that can be loaded into an instance of the Flipper application. 
	
	The list must contain at most one abstract triangulation and all laminations and 
	mapping classes must be defined on the same triangulation (which must be the given 
	one if provided). '''
	
	abstract_triangulations = [item for item in objects if isinstance(item, Flipper.kernel.AbstractTriangulation)]
	laminations = [item for item in objects if isinstance(item, Flipper.kernel.Lamination)]
	mapping_classes = [item for item in objects if isinstance(item, Flipper.kernel.EncodingSequence)]
	if len(abstract_triangulations) > 0:
		raise ValueError('At most one abstract triangulation must be provided')
	[abstract_triangulation] = abstract_triangulations
	if any(lamination.abstract_triangulation != abstract_triangulation for lamination in laminations):
		raise ValueError('All laminations must be on the same abstract triangulations.')
	if any(mapping_class.source_triangulation != abstract_triangulation for mapping_class in mapping_classes):
		raise ValueError('All mapping classes must go from the same abstract triangulations.')
	if any(mapping_class.target_triangulation != abstract_triangulation for mapping_class in mapping_classes):
		raise ValueError('All mapping classes must go to the same abstract triangulations.')
	
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

