
import Flipper

class SplittingSequence(object):
	''' This represents a sequence of flips of an AbstractTriangulation. '''
	def __init__(self, initial_lamination, prepreiodic_encoding, laminations, flips, encodings, prefered_isometry=None, name=''):
		self.initial_lamination = initial_lamination
		self.prepreiodic_encoding = prepreiodic_encoding
		self.laminations = laminations
		self.flips = flips
		self.encodings = encodings
		self.closing_isometries = self.laminations[-1].all_projective_isometries(self.laminations[0])
		self.prefered_isometry = prefered_isometry
		self.name = name
	
	def dilatation(self):
		return self.laminations[0].weight() / self.laminations[-1].weight()
	
	def bundle(self, isometry_number=0):
		L = Flipper.kernel.LayeredTriangulation(self.laminations[0].abstract_triangulation, self.name)
		L.flips(self.flips)
		closing_isometries = [isometry for isometry in L.upper_lower_isometries() if any(isometry.edge_map == isom.edge_map for isom in self.closing_isometries)]
		
		return L.close(closing_isometries[isometry_number])
	
	def snappy_manifold(self, isometry_number=0):
		import snappy
		B = self.bundle(isometry_number)
		M = snappy.Manifold(B.snappy_string())
		for index, (cusp_type, fibre_slope) in enumerate(zip(B.cusp_types, B.fibre_slopes)):
			if cusp_type == 1: M.dehn_fill(fibre_slope, index)
		
		return M
	
	def bundles(self):
		return [self.bundle(isometry_number) for isometry_number in range(len(self.closing_isometries))]
	
	def snappy_manifolds(self):
		return [self.snappy_manifold(isometry_number) for isometry_number in range(len(self.closing_isometries))]
