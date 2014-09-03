
import flipper

class SplittingSequence(object):
	''' This represents a sequence of flips of an AbstractTriangulation. '''
	def __init__(self, initial_lamination, preperiodic, periodic, isometries, periodic_flips):
		assert(isinstance(initial_lamination, flipper.kernel.Lamination))
		assert(preperiodic is None or isinstance(preperiodic, flipper.kernel.Encoding))
		assert(isinstance(periodic, flipper.kernel.Encoding))
		assert(all(isinstance(isom, flipper.kernel.Isometry) for isom in isometries))
		assert(all(isinstance(flip, flipper.Integer_Type) for flip in periodic_flips))
		
		self.initial_lamination = initial_lamination
		self.preperiodic = preperiodic
		self.periodic = periodic
		self.isometries = isometries
		self.periodic_flips = periodic_flips
		self.num_isometries = len(self.isometries)
		self.closing_isometry = self.isometries[0] if self.num_isometries == 1 else None
		self.L = flipper.kernel.LayeredTriangulation(self.periodic.source_triangulation)
		self.L.flips(self.periodic_flips)
		self.upper_lower = self.L.upper_lower_isometries()
		self.UL_isometries = [isometry for isometry in self.L.upper_lower_isometries() if any(isometry.equivalent(isom) for isom in self.isometries)]
		
		#print(self.initial_lamination.triangulation)
		#print(self.periodic_flips)
		#print(self.initial_lamination)
		#print(self.isometries)
		#print(len(self.isometries))
	
	def bundle(self, isometry_number=None):
		if isometry_number is None: isometry_number = 0
		
		return self.L.close(self.UL_isometries[isometry_number])
	
	def snappy_manifold(self, isometry_number=None, name='flipper triangulation'):
		import snappy
		B = self.bundle(isometry_number)
		#print(B.real_cusps, B.fibre_slopes)
		M = snappy.Manifold(B.snappy_string(name))
		for index, (real_cusp, fibre_slope) in enumerate(zip(B.real_cusps, B.fibre_slopes)):
			if not real_cusp: M.dehn_fill(fibre_slope, index)
		
		return M
	
	def bundles(self):
		return [self.bundle(isometry_number) for isometry_number in range(len(self.isometries))]
	
	def snappy_manifolds(self, name='flipper triangulation'):
		return [self.snappy_manifold(isometry_number, name) for isometry_number in range(len(self.isometries))]

