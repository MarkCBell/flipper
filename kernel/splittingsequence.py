
import Flipper

class SplittingSequence(object):
	def __init__(self, initial_lamination, prepreiodic_encoding, laminations, flips, encodings, prefered_isometry=None):
		self.initial_lamination = initial_lamination
		self.prepreiodic_encoding = prepreiodic_encoding
		self.laminations = laminations
		self.flips = flips
		self.encodings = encodings
		self.closing_isometries = self.laminations[-1].all_projective_isometries(self.laminations[0])  # !?! Check this. and in fact all indices!
		self.prefered_isometry = prefered_isometry
	
	def dilatation(self):
		return self.laminations[0].weight() / self.laminations[-1].weight()
	
	def bundle(self, isometry_number=None, name='', power=1):
		L = Flipper.LayeredTriangulation(self.laminations[0].abstract_triangulation, name)
		L.flips(self.flips)
		closing_isometries = [isometry for isometry in L.upper_lower_isometries() if any(isometry.edge_map == isom.edge_map for isom in self.closing_isometries)]
		
		return L.close(closing_isometries[isometry_number])
