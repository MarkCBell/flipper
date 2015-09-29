
from math import sqrt
from random import random
from colorsys import hls_to_rgb

PHI = (1 + sqrt(5)) / 2

DEFAULT_OBJECT_COLOUR = 'black'
DEFAULT_VERTEX_COLOUR = 'black'
DEFAULT_EDGE_COLOUR = 'black'
DEFAULT_TRIANGLE_COLOUR = 'gray80'
DEFAULT_CURVE_COLOUR = 'grey40'
DEFAULT_TRAIN_TRACK_BLOCK_COLOUR = 'grey40'

def dot(a, b):
	return a[0] * b[0] + a[1] * b[1]

def lines_intersect(s1, e1, s2, e2, float_error, equivalent_edge):
	dx1, dy1 = e1[0] - s1[0], e1[1] - s1[1]
	dx2, dy2 = e2[0] - s2[0], e2[1] - s2[1]
	D = dx2*dy1 - dx1*dy2
	if D == 0: return (-1, False)
	
	xx = s2[0] - s1[0]
	yy = s2[1] - s1[1]
	
	s = float(yy*dx1 - xx*dy1)/D
	t = float(yy*dx2 - xx*dy2)/D
	
	return (t if 0-float_error <= s <= 1+float_error and 0-float_error <= t <= 1+float_error else -1, equivalent_edge and 0+float_error <= s <= 1-float_error and 0+float_error <= t <= 1-float_error)

def interpolate(A, B, C, r, s):
	# Given points a, b, c and parameters R, S
	# Let X := rB + (1-r)A and
	# Y := sB + (1-s)C
	dx, dy = A[0] - B[0], A[1] - B[1]
	dx2, dy2 = C[0] - B[0], C[1] - B[1]
	
	X = (B[0] + r*dx, B[1] + r*dy)
	Y = (B[0] + s*dx2, B[1] + s*dy2)
	
	d = dy * dx2 - dy2 *dx
	t  = (dx2 * (r*dx - s*dx2) + dy2 * (r*dy - s*dy2)) / d
	t2 = (dx * (r*dx - s*dx2) + dy * (r*dy - s*dy2)) / d
	
	# Hmmm, this is a hack. !?!
	d = sqrt(dx*dx + dy*dy)
	d2 = sqrt(dx2*dx2 + dy2*dy2)
	t, t2 = 0.1, -0.1
	P = (X[0] - t/2 * dy, X[1] + t/2 * dx)
	Q = (Y[0] - t2/2 * dy2, Y[1] + t2/2 * dx2)
	
	return X, P, Q, Y

class ColourPalette(object):
	def __init__(self):
		self.state = 0
	
	def get_colour(self):
		self.state += 1
		hue = (self.state / PHI) % 1.
		lightness = (50 + random() * 10)/100.
		saturation = (90 + random() * 10)/100.
		r, g, b = hls_to_rgb(hue, lightness, saturation)
		return '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))
	
	def reset(self):
		self.state = 0

class DrawableObject(object):
	def __init__(self, canvas, vertices, options):
		self.options = options
		self.canvas = canvas
		self.vertices = vertices
		self.default_colour = DEFAULT_OBJECT_COLOUR
		self.colour = None
		self.drawn = None
	
	# Note that this means that CanvasTriangle will NOT have the same convention as AbstractTriangle,
	# there iterating and index accesses return edges.
	def __getitem__(self, index):
		return self.vertices[index % len(self)]
	
	def __iter__(self):
		return iter(self.vertices)
	
	def __len__(self):
		return len(self.vertices)
	
	def set_current_colour(self, colour=None):
		if colour is None: colour = self.colour
		self.canvas.itemconfig(self.drawn, fill=colour)
	
	def set_colour(self, colour=None):
		if colour is None: colour = self.default_colour
		self.colour = colour
		self.set_current_colour(self.colour)
	
	def centre(self):
		return (sum(x[0] for x in self.vertices) / len(self), sum(x[1] for x in self.vertices) / len(self))
	
	def update(self):
		self.canvas.coords(self.drawn, *[c for v in self for c in v])

class CanvasVertex(DrawableObject):
	def __init__(self, canvas, vertex, options):
		super(CanvasVertex, self).__init__(canvas, [vertex], options)
		self.default_colour = self.colour = DEFAULT_VERTEX_COLOUR
		self.vertex = list(vertex)
		self.drawn = self.canvas.create_oval(
			[p + scale*self.options.dot_size for scale in [-1, 1] for p in self],
			outline=self.default_colour, fill=self.default_colour, tag='oval'
			)
	
	def __repr__(self):
		return str(self.vertex)
	
	def __sub__(self, other):
		return (self[0] - other[0], self[1] - other[1])
	
	# We have to redo these manually.
	def __iter__(self):
		return iter(self.vertex)
	
	def __getitem__(self, key):
		return self.vertex[key]
	
	def __setitem__(self, key, value):
		self.vertex[key] = value
	
	def __contains__(self, point):
		return all(abs(c - v) < self.options.epsilon for c, v in zip(point, self))
	
	def update(self):
		self.canvas.coords(self.drawn, *[p + scale*self.options.dot_size for scale in [-1, 1] for p in self])

class CanvasEdge(DrawableObject):
	def __init__(self, canvas, vertices, options):
		super(CanvasEdge, self).__init__(canvas, vertices, options)
		self.default_colour = self.colour = DEFAULT_EDGE_COLOUR
		self.drawn = self.canvas.create_line(
			[c for v in self for c in v],
			width=self.options.line_size,
			fill=self.default_colour,
			tag='line'
			)
		self.equivalent_edge = None
		self.in_triangles = []
		self.index = -1
	
	def __contains__(self, point):
		if any(point in vertex for vertex in self):
			return False
		try:
			(x, y) = point
			Dx = x - self[0][0]
			Dy = y - self[0][1]
			dx = self[1][0] - self[0][0]
			dy = self[1][1] - self[0][1]
			length = sqrt(dx*dx + dy*dy)
			A = (Dx*dx + Dy*dy) / length
			B = (Dy*dx - Dx*dy) / length
			return -self.options.epsilon < A < length + self.options.epsilon and -self.options.epsilon < B < self.options.epsilon
		except ZeroDivisionError:
			return False
	
	def hide(self, hide=False):
		self.canvas.itemconfig(self.drawn, state='hidden' if hide else 'normal')
	
	def free_sides(self):
		return 2-len(self.in_triangles)-(1 if self.equivalent_edge is not None else 0)
	
	def is_internal(self):
		return len(self.in_triangles) == 2
	
	def flip_orientation(self):
		self.vertices = self.vertices[::-1]
		self.update()

class CanvasTriangle(DrawableObject):
	def __init__(self, canvas, edges, options):
		super(CanvasTriangle, self).__init__(canvas, list(set(v for e in edges for v in e)), options)
		self.default_colour = self.colour = DEFAULT_TRIANGLE_COLOUR
		self.edges = edges
		
		# We reorder the vertices to guarantee that the vertices are cyclically ordered anticlockwise in the plane.
		d10, d20 = self[1] - self[0], self[2] - self[0]
		if d10[0]*d20[1] - d10[1]*d20[0] > 0: self.vertices = [self[0], self[2], self[1]]
		# Now we reorder the edges such that edges[i] does not meet vertices[i].
		self.edges = [edge for vertex in self for edge in self.edges if vertex not in edge.vertices]
		
		# And check to make sure everyone made it through alive.
		assert(len(self.edges) == 3)
		assert(self[0] != self[1] and self[1] != self[2] and self[2] != self[0])
		assert(self.edges[0] != self.edges[1] and self.edges[1] != self.edges[2] and self.edges[2] != self.edges[0])
		
		self.drawn = self.canvas.create_polygon([c for v in self for c in v], fill=self.default_colour, tag='polygon')
		# Add this triangle to each edge involved.
		for edge in self.edges:
			edge.in_triangles.append(self)
	
	def __contains__(self, point):
		if any(point in vertex for vertex in self):
			return False
		if any(point in edge for edge in self.edges):
			return False
		
		v0 = self[2] - self[0]
		v1 = self[1] - self[0]
		v2 = (point[0] - self[0][0], point[1] - self[0][1])
		
		dot00 = dot(v0, v0)
		dot01 = dot(v0, v1)
		dot02 = dot(v0, v2)
		dot11 = dot(v1, v1)
		dot12 = dot(v1, v2)
		
		invDenom = 1.0 / (dot00 * dot11 - dot01 * dot01)
		u = (dot11 * dot02 - dot01 * dot12) * invDenom
		v = (dot00 * dot12 - dot01 * dot02) * invDenom
		
		return (u >= 0) and (v >= 0) and (u + v <= 1)

class CurveComponent(DrawableObject):
	def __init__(self, canvas, vertices, options, multiplicity=1, smooth=False):
		super(CurveComponent, self).__init__(canvas, vertices, options)
		self.default_colour = self.colour = DEFAULT_CURVE_COLOUR
		self.drawn = self.canvas.create_line(
			[c for v in self.vertices for c in v],
			width=self.options.line_size,
			fill=self.colour,
			tag='curve',
			smooth=smooth
			)
		self.multiplicity = multiplicity
	
	def append_point(self, point):
		self.vertices.append(point)
		self.update()
		return self
	
	def pop_point(self):
		if len(self.vertices) > 2:
			self.vertices.pop()
			self.update()
	
	def move_point(self, index, x, y):
		self.vertices[index] = (x, y)
		self.update()

class TrainTrackBlock(DrawableObject):
	def __init__(self, canvas, vertices, options, multiplicity=1, smooth=False):
		super(TrainTrackBlock, self).__init__(canvas, vertices, options)
		self.default_colour = self.colour = DEFAULT_TRAIN_TRACK_BLOCK_COLOUR
		self.drawn = self.canvas.create_polygon(
			[v[j] for v in self.vertices for j in range(2)],
			fill=self.default_colour,
			tag='train_track',
			outline=self.default_colour,
			smooth=smooth
			)
		self.multiplicity = multiplicity

