
import flipper

class SplittingSequence(object):
	''' This represents a sequence of flips of an AbstractTriangulation. '''
	def __init__(self, initial_lamination, preperiodic, periodic, laminations, flips):
		self.initial_lamination = initial_lamination
		self.preperiodic = preperiodic
		self.periodic = periodic
		self.laminations = laminations
		self.flips = flips
		self.closing_isometries = self.laminations[-1].all_projective_isometries(self.laminations[0])
		self.num_isometries = len(self.closing_isometries)
		self.closing_isometry = self.closing_isometries[0] if self.num_isometries == 1 else None
	
	def dilatation(self):
		return float(self.laminations[0].weight()) / float(self.laminations[-1].weight())
	
	def bundle(self, isometry_number=None):
		L = flipper.kernel.LayeredTriangulation(self.laminations[0].triangulation)
		L.flips(self.flips)
		if isometry_number is not None:
			closing_isometries = [isometry for isometry in L.upper_lower_isometries() if any(isometry.edge_map == isom.edge_map for isom in self.closing_isometries)]
			return L.close(closing_isometries[isometry_number])
		else:
			# We still need to adapt the closing isometry that we have.
			closing_isometries = [isom for isom in L.upper_lower_isometries() if isom.edge_map == self.closing_isometry.edge_map]
			# Problem: There may be more than one.
			return L.close(closing_isometries[0])
	
	def snappy_manifold(self, isometry_number=None, name='flipper triangulation'):
		import snappy
		B = self.bundle(isometry_number)
		M = snappy.Manifold(B.snappy_string(name))
		for index, (cusp_type, fibre_slope) in enumerate(zip(B.cusp_types, B.fibre_slopes)):
			if cusp_type == 1: M.dehn_fill(fibre_slope, index)
		
		return M
	
	def bundles(self):
		return [self.bundle(isometry_number) for isometry_number in range(len(self.closing_isometries))]
	
	def snappy_manifolds(self, name='flipper triangulation'):
		return [self.snappy_manifold(isometry_number, name) for isometry_number in range(len(self.closing_isometries))]

