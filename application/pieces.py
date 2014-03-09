
from math import sqrt, pi
from random import random
from colorsys import hls_to_rgb

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

class ColourPalette(object):
	def __init__(self):
		self.state = 0
	
	def get_colour(self):
		self.state += 1
		hue = (self.state * (pi * 20) / 360) % 1.
		lightness = (50 + random() * 10)/100.
		saturation = (90 + random() * 10)/100.
		r, g, b = hls_to_rgb(hue, lightness, saturation)
		return '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))
	
	def reset(self):
		self.state = 0

class DrawableObject(object):
	def __init__(self, default_colour, canvas, options):
		self.default_colour = default_colour
		self.options = options
		self.canvas = canvas
		self.drawn = None
	
	def set_colour(self, colour=None):
		if colour is None: colour = self.default_colour
		self.canvas.itemconfig(self.drawn, fill=colour)
	
	def set_default_colour(self, colour):
		self.default_colour = colour
		self.set_colour(self.default_colour)

class Vertex(object):
	def __init__(self, canvas, p, options):
		self.options = options
		self.default_colour = DEFAULT_VERTEX_COLOUR
		self.x, self.y = p
		self.canvas = canvas
		self.drawn = self.canvas.create_oval(self.x-self.options.dot_size, self.y-self.options.dot_size, self.x+self.options.dot_size, self.y+self.options.dot_size, outline=self.default_colour, fill=self.default_colour, tag='oval')
	
	def __str__(self):
		return str((self.x, self.y))
	
	def __sub__(self, other):
		return (self.x - other.x, self.y - other.y)
	
	def __getitem__(self, key):
		if key == 0:
			return self.x
		elif key == 1:
			return self.y
		else:
			raise KeyError('%s' % key)
	
	def __contains__(self, p):
		(x, y) = p
		return abs(x - self.x) < self.options.epsilon and abs(y - self.y) < self.options.epsilon
	
	def set_colour(self, colour=None):
		if colour is None: colour = self.default_colour
		self.canvas.itemconfig(self.drawn, fill=colour)
	
	def set_default_colour(self, colour=None):
		if colour is None: colour = DEFAULT_VERTEX_COLOUR
		self.default_colour = colour
		self.set_colour(self.default_colour)
	
	def update(self):
		self.canvas.coords(self.drawn, self.x-self.options.dot_size, self.y-self.options.dot_size, self.x+self.options.dot_size, self.y+self.options.dot_size)

class Edge(object):
	def __init__(self, source_vertex, target_vertex, options):
		self.options = options
		self.default_colour = DEFAULT_EDGE_COLOUR
		self.source_vertex = source_vertex
		self.target_vertex = target_vertex
		self.vertices = [self.target_vertex, self.source_vertex]
		self.canvas = self.source_vertex.canvas
		self.drawn = self.canvas.create_line(self.source_vertex.x, self.source_vertex.y, self.target_vertex.x, self.target_vertex.y, width=self.options.line_size, fill=self.default_colour, tag='line')
		self.equivalent_edge = None
		self.in_triangles = []
		self.index = -1
	
	def __str__(self):
		return '%s -- %s' % (self.source_vertex, self.target_vertex)
	
	def set_colour(self, colour=None):
		if colour is None: colour = self.default_colour
		self.canvas.itemconfig(self.drawn, fill=colour)
	
	def set_default_colour(self, colour=None):
		if colour is None: colour = DEFAULT_EDGE_COLOUR
		self.default_colour = colour
		self.set_colour(self.default_colour)
	
	def length(self):
		v = self.target_vertex - self.source_vertex
		return sqrt(dot(v, v))
	
	def __contains__(self, p):
		if p in self.source_vertex or p in self.target_vertex:
			return False
		try:
			(x, y) = p
			Dx = x - self.source_vertex.x
			Dy = y - self.source_vertex.y
			dx = self.target_vertex.x - self.source_vertex.x
			dy = self.target_vertex.y - self.source_vertex.y
			length = self.length()
			A = (Dx*dx + Dy*dy)/length
			B = (Dy*dx - Dx*dy)/length
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
		self.source_vertex, self.target_vertex = self.target_vertex, self.source_vertex
	
	def update(self):
		self.canvas.coords(self.drawn, self.source_vertex.x, self.source_vertex.y, self.target_vertex.x, self.target_vertex.y)

class Triangle(object):
	def __init__(self, e1, e2, e3, options):
		self.options = options
		self.default_colour = DEFAULT_TRIANGLE_COLOUR
		self.edges = (e1, e2, e3)
		self.vertices = list(set([e.source_vertex for e in self.edges] + [e.target_vertex for e in self.edges]))
		assert(self.vertices[0] != self.vertices[1] and self.vertices[1] != self.vertices[2] and self.vertices[2] != self.vertices[0])
		
		# We reorder the vertices to guarantee that the vertices are cyclically ordered anticlockwise in the plane. 
		d10, d20 = self.vertices[1] - self.vertices[0], self.vertices[2] - self.vertices[0]
		if d10[0]*d20[1] - d10[1]*d20[0] > 0: self.vertices = [self.vertices[0], self.vertices[2], self.vertices[1]]
		# Now we reorder the edges such that edges[i] does not meet vertices[i].
		self.edges = [edge for vertex in self.vertices for edge in self.edges if edge.source_vertex != vertex and edge.target_vertex != vertex]
		# And reorient any edges so that they point anti-clockwise. This wont hold for internal edges as they will be overwritten later
		# but boundary edges will retain theirs. We probably wont actually need this and can remove it later.
		for i in range(3):
			if self.edges[i].source_vertex != self.vertices[(i+1) % 3]: self.edges[i].flip_orientation()
		
		# And check to make sure everyone made it through alive.
		assert(len(self.edges) == 3)
		assert(self.vertices[0] != self.vertices[1] and self.vertices[1] != self.vertices[2] and self.vertices[2] != self.vertices[0])
		assert(self.edges[0] != self.edges[1] and self.edges[1] != self.edges[2] and self.edges[2] != self.edges[0])
		
		self.canvas = self.edges[0].source_vertex.canvas
		self.drawn = self.canvas.create_polygon([self.vertices[i][j] for i in range(3) for j in range(2)], fill=self.default_colour, tag='polygon')
		for edge in self.edges:
			edge.in_triangles.append(self)
	
	def __str__(self):
		return '%s %s %s' % (self.vertices[0], self.vertices[1], self.vertices[2])
	
	def __getitem__(self, index):
		return self.edges[index]
	
	def __iter__(self):
		return iter(self.edges)
	
	def set_colour(self, colour=None):
		if colour is None: colour = self.default_colour
		self.canvas.itemconfig(self.drawn, fill=colour)
	
	def set_default_colour(self, colour=None):
		if colour is None: colour = DEFAULT_TRIANGLE_COLOUR
		self.default_colour = colour
		self.set_colour(self.default_colour)
	
	def __contains__(self, point):
		v0 = self.vertices[2] - self.vertices[0]
		v1 = self.vertices[1] - self.vertices[0]
		v2 = (point[0] - self.vertices[0].x, point[1] - self.vertices[0].y)
		
		dot00 = dot(v0, v0)
		dot01 = dot(v0, v1)
		dot02 = dot(v0, v2)
		dot11 = dot(v1, v1)
		dot12 = dot(v1, v2)
		
		invDenom = 1.0 / (dot00 * dot11 - dot01 * dot01)
		u = (dot11 * dot02 - dot01 * dot12) * invDenom
		v = (dot00 * dot12 - dot01 * dot02) * invDenom
		
		return (u >= 0) and (v >= 0) and (u + v <= 1)
	
	def update(self):
		self.canvas.coords(self.drawn, *[self.vertices[i][j] for i in range(3) for j in range(2)])

class CurveComponent(object):
	def __init__(self, canvas, source_point, options, multiplicity=1, counted=False):
		self.options = options
		self.default_colour = DEFAULT_CURVE_COLOUR
		self.colour = self.default_colour
		self.vertices = [source_point, source_point]
		self.canvas = canvas
		self.drawn = self.canvas.create_line([v[c] for v in self.vertices for c in [0, 1]], width=self.options.line_size, fill=self.colour, tag='curve')
		self.multiplicity = multiplicity
		self.counted = counted
	
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
	
	def set_colour(self, colour=None):
		if colour is None: colour = self.default_colour
		self.colour = colour
		self.canvas.itemconfig(self.drawn, fill=colour)
	
	def set_default_colour(self, colour=None):
		if colour is None: colour = DEFAULT_CURVE_COLOUR
		self.default_colour = colour
		self.set_colour(self.default_colour)
	
	def move_last_point(self, new_point):
		if len(self.vertices) > 1:
			self.vertices[-1] = new_point
			self.canvas.coords(self.drawn, *[v[c] for v in self.vertices for c in [0, 1]])
	
	def update(self):
		self.canvas.coords(self.drawn, *[v[c] for v in self.vertices for c in [0, 1]])

class TrainTrackBlock(object):
	def __init__(self, canvas, vertices, options, multiplicity=1, counted=False):
		self.options = options
		self.default_colour = DEFAULT_TRAIN_TRACK_BLOCK_COLOUR
		self.colour = self.default_colour
		self.vertices = vertices
		self.canvas = canvas
		self.drawn = self.canvas.create_polygon([v[j] for v in self.vertices for j in range(2)], fill=self.default_colour, tag='train_track', outline=self.default_colour)
		self.multiplicity = multiplicity
		self.counted = counted
	
	def set_colour(self, colour=None):
		if colour is None: colour = self.default_colour
		self.colour = colour
		self.canvas.itemconfig(self.drawn, fill=colour)
	
	def set_default_colour(self, colour=None):
		if colour is None: colour = DEFAULT_TRAIN_TRACK_BLOCK_COLOUR
		self.default_colour = colour
		self.set_colour(self.default_colour)
	
	def update(self):
		self.canvas.coords(self.drawn, *[v[j] for v in self.vertices for j in range(2)])
