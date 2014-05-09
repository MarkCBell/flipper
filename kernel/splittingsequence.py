
import flipper

class SplittingSequence(object):
	''' This represents a sequence of flips of an AbstractTriangulation. '''
	def __init__(self, initial_lamination, preperiodic, periodic, isometries, periodic_flips):
		self.initial_lamination = initial_lamination
		self.preperiodic = preperiodic
		self.periodic = periodic
		self.isometries = isometries
		self.periodic_flips = periodic_flips
		self.num_isometries = len(self.isometries)
		self.closing_isometry = self.isometries[0] if self.num_isometries == 1 else None
	
	def dilatation(self):
		return float(self.laminations[0].weight()) / float(self.laminations[-1].weight())
	
	def bundle(self, isometry_number=None):
		L = flipper.kernel.LayeredTriangulation(self.periodic.source_triangulation)
		L.flips(self.periodic_flips)
		if isometry_number is not None:
			isometries = [isometry for isometry in L.upper_lower_isometries() if any(isometry.edge_map == isom.edge_map for isom in self.isometries)]
			return L.close(isometries[isometry_number])
		else:
			# We still need to adapt the closing isometry that we have.
			isometries = [isom for isom in L.upper_lower_isometries() if isom.edge_map == self.closing_isometry.edge_map]
			# Problem: There may be more than one.
			return L.close(isometries[0])
	
	def snappy_manifold(self, isometry_number=None, name='flipper triangulation'):
		import snappy
		B = self.bundle(isometry_number)
		M = snappy.Manifold(B.snappy_string(name))
		for index, (real_cusp, fibre_slope) in enumerate(zip(B.real_cusps, B.fibre_slopes)):
			if not real_cusp: M.dehn_fill(fibre_slope, index)
		
		return M
	
	def bundles(self):
		return [self.bundle(isometry_number) for isometry_number in range(len(self.isometries))]
	
	def snappy_manifolds(self, name='flipper triangulation'):
		return [self.snappy_manifold(isometry_number, name) for isometry_number in range(len(self.isometries))]

