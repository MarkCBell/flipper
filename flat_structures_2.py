__author__ = 'shannonhorrigan'

import flipper

try:
	from Queue import Queue
except ImportError:
	from queue import Queue

def flat_structure(self):
	''' Return a dictionary taking each edge of self.canonical().source_triangulation to a vector in RR^2.
	
	These vectors describe the flat structure of self.canonical() and can be used to build a flat surface for self.canonical().
	This is based off of code supplied by Shannon Horrigan.
	
	Assumes that this mapping class is pseudo-Anosov.
	
	This encoding must be a mapping class. '''
	
	assert(self.is_mapping_class())
	
	stable_lamination = self.splitting_sequence().lamination
	unstable_lamination = self.splitting_sequence().mapping_class.inverse().invariant_lamination()
	periodic_triangulation = self.splitting_sequence().triangulation
	
	queue = Queue()  # The edges whose vectors are decided but whose triangles have not been inspected.
	edge_vectors = dict()  # A dictionary mapping edges to their corresponding vectors. 
	
	while len(edge_vectors) < self.zeta:
		# We fix an edge to start the procedure.
		e = [edge for edge in periodic_triangulation.edges if edge not in edge_vectors][0]
		
		# Fill in the basic information for this edge (and its inverse).
		edge_vectors[e] = flipper.kernel.Vector2(stable_lamination(e), unstable_lamination(e))
		edge_vectors[~e] = flipper.kernel.Vector2(-stable_lamination(e), -unstable_lamination(e))
		
		queue.put(e)
		queue.put(~e)
		
		while not queue.empty():
			edge_1 = queue.get()  # Get an unchecked edge.
			# Moving anticlockwise around the triangle from edge_1 brings you to edge_2 then edge_3
			#          /\
			#         /  \
			#        /    \
			#  e_3  v      ^  e_2
			#      /        \
			#     /          \
			#     ------>-----
			#         e_1
			current_triangle = periodic_triangulation.triangle_lookup[edge_1.label]
			edge_2 = current_triangle.edges[current_triangle.edges.index(edge_1) - 2]
			edge_3 = current_triangle.edges[current_triangle.edges.index(edge_1) - 1]
			
			# There is nothing to do if all edges are known.
			if edge_2 in edge_vectors and edge_3 not in edge_vectors:  # If two of the edges are known we can calculate the third using the formula: edge_1  + edge_2  + edge_3 == 0.
				edge_vectors[edge_3] = -(edge_vectors[edge_1] + edge_vectors[edge_2])
				edge_vectors[~edge_3] = -edge_vectors[edge_3]
				queue.put(~edge_3)
			elif edge_2 not in edge_vectors and edge_3 in edge_vectors:  # The other possibility if two edges are known.
				edge_vectors[edge_2] = -(edge_vectors[edge_1] + edge_vectors[edge_3])
				edge_vectors[~edge_2] = -edge_vectors[edge_2]
				queue.put(~edge_2)
			elif edge_2 not in edge_vectors and edge_3 not in edge_vectors:  # If edge_2 and edge_3 are both unknown:
				# Here we just choose positive signs in anticipation of changing them later if need be.
				s_1, u_1 = stable_lamination(edge_1), unstable_lamination(edge_1)
				s_2, u_2 = stable_lamination(edge_2), unstable_lamination(edge_2)
				s_3, u_3 = stable_lamination(edge_3), unstable_lamination(edge_3)
				
				edge_vectors[edge_2] = flipper.kernel.Vector2(
					-s_2 if (s_1 == s_2 + s_3 and edge_vectors[edge_1].x >= 0) or \
						(s_2 == s_1 + s_3 and edge_vectors[edge_1].x >= 0) or \
						(s_3 == s_1 + s_2 and edge_vectors[edge_1].x < 0) else s_2,
					-u_2 if (u_1 == u_2 + u_3 and edge_vectors[edge_1].y >= 0) or \
						(u_2 == u_1 + u_3 and edge_vectors[edge_1].y >= 0) or \
						(u_3 == u_1 + u_2 and edge_vectors[edge_1].y < 0) else u_2
					)
				
				edge_vectors[edge_3] = flipper.kernel.Vector2(
					-s_3 if (s_1 == s_2 + s_3 and edge_vectors[edge_1].x >= 0) or \
						(s_2 == s_1 + s_3 and edge_vectors[edge_1].x < 0) or \
						(s_3 == s_1 + s_2 and edge_vectors[edge_1].x >= 0) else s_3,
					-u_3 if (u_1 == u_2 + u_3 and edge_vectors[edge_1].y >= 0) or \
						(u_2 == u_1 + u_3 and edge_vectors[edge_1].y < 0) or \
						(u_3 == u_1 + u_2 and edge_vectors[edge_1].y >= 0) else u_3
					)
				
				# Put the inverses in too.
				edge_vectors[~edge_2] = -edge_vectors[edge_2]
				edge_vectors[~edge_3] = -edge_vectors[edge_3]
				queue.put(~edge_2)
				queue.put(~edge_3)
	
	# Check that we do indeed have triangles:
	
	return flipper.kernel.FlatStructure(periodic_triangulation, edge_vectors)

