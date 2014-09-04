
import flipper

class SplittingSequence(object):
	''' This represents a sequence of flips of an AbstractTriangulation. '''
	def __init__(self, initial_lamination, preperiodic, periodic, isometry, periodic_flips):
		assert(isinstance(initial_lamination, flipper.kernel.Lamination))
		assert(preperiodic is None or isinstance(preperiodic, flipper.kernel.Encoding))
		assert(isinstance(periodic, flipper.kernel.Encoding))
		assert(isinstance(isometry, flipper.kernel.Isometry))
		assert(all(isinstance(flip, flipper.Integer_Type) for flip in periodic_flips))
		
		self.initial_lamination = initial_lamination
		self.preperiodic = preperiodic  # Unused.
		self.periodic = periodic  # Sort of unused.
		self.isometry = isometry
		self.periodic_flips = periodic_flips
		self.source_triangulation = self.periodic.source_triangulation
		self.target_triangulation = self.periodic.target_triangulation
	
	def bundle(self):
		return flipper.kernel.LayeredTriangulation(self.source_triangulation, self.periodic_flips, self.isometry).closed_triangulation
	
	def snappy_manifold(self, name='flipper triangulation'):
		import snappy
		B = self.bundle()
		#print(B.real_cusps, B.fibre_slopes)
		M = snappy.Manifold(B.snappy_string(name))
		for index, (real_cusp, fibre_slope) in enumerate(zip(B.real_cusps, B.fibre_slopes)):
			if not real_cusp: M.dehn_fill(fibre_slope, index)
		
		return M

