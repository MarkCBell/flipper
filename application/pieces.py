
from math import sqrt, pi
from random import random
from colorsys import hls_to_rgb
try:
	import Tkinter as TK
except ImportError: # Python 3
	import tkinter as TK

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

class ColourPalette:
	def __init__(self):
		self.state = 0
	
	def __call__(self):
		self.state += 1
		hue = (self.state * (pi * 20) / 360) % 1.
		lightness = (50 + random() * 10)/100.
		saturation = (90 + random() * 10)/100.
		r, g, b = hls_to_rgb(hue, lightness, saturation)
		return '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))

class Vertex:
	def __init__(self, canvas, p, options):
		self.options = options
		self.default_colour = self.options.default_vertex_colour
		self.x, self.y = p
		self.canvas = canvas
		self.drawn_self = self.canvas.create_oval(self.x-self.options.dot_size, self.y-self.options.dot_size, self.x+self.options.dot_size, self.y+self.options.dot_size, outline=self.default_colour, fill=self.default_colour, tag='oval')
	
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
		(x,y) = p
		return abs(x - self.x) < self.options.epsilon and abs(y - self.y) < self.options.epsilon
	
	def set_colour(self, colour=None):
		if colour is None: colour = self.default_colour
		self.canvas.itemconfig(self.drawn_self, fill=colour)
	
	def set_default_colour(self, colour):
		self.default_colour = colour
		self.set_colour(self.default_colour)
	
	def update(self):
		self.canvas.coords(self.drawn_self, self.x-self.options.dot_size, self.y-self.options.dot_size, self.x+self.options.dot_size, self.y+self.options.dot_size)

class Edge:
	def __init__(self, source_vertex, target_vertex, options):
		self.options = options
		self.default_colour = self.options.default_edge_colour
		self.source_vertex = source_vertex
		self.target_vertex = target_vertex
		self.vertices = [self.target_vertex, self.source_vertex]
		self.canvas = self.source_vertex.canvas
		self.drawn_self = self.canvas.create_line(self.source_vertex.x, self.source_vertex.y, self.target_vertex.x, self.target_vertex.y, width=self.options.line_size, fill=self.default_colour, tag='line')
		self.equivalent_edge = None
		self.in_triangles = []
		self.index = -1
	
	def __str__(self):
		return '%s -- %s' % (self.source_vertex, self.target_vertex)
	
	def set_colour(self, colour=None):
		if colour is None: colour = self.default_colour
		self.canvas.itemconfig(self.drawn_self, fill=colour)
	
	def set_default_colour(self, colour):
		self.default_colour = colour
		self.set_colour(self.default_colour)
	
	def __contains__(self, p):
		if p in self.source_vertex or p in self.target_vertex:
			return False
		try:
			(x,y) = p
			Dx = x - self.source_vertex.x
			Dy = y - self.source_vertex.y
			dx = self.target_vertex.x - self.source_vertex.x
			dy = self.target_vertex.y - self.source_vertex.y
			length = sqrt(dx**2 + dy**2)
			A = (Dx*dx + Dy*dy)/length
			B = (Dy*dx - Dx*dy)/length
			return -self.options.epsilon < A < length + self.options.epsilon and -self.options.epsilon < B < self.options.epsilon
		except ZeroDivisionError:
			return False
	
	def hide(self, hide=False):
		self.canvas.itemconfig(self.drawn_self, state=TK.HIDDEN if hide else TK.NORMAL)
	
	def free_sides(self):
		return 2-len(self.in_triangles)-(1 if self.equivalent_edge is not None else 0)
	
	def is_internal(self):
		return len(self.in_triangles) == 2
	
	def flip_orientation(self):
		self.source_vertex, self.target_vertex = self.target_vertex, self.source_vertex
	
	def update(self):
		self.canvas.coords(self.drawn_self, self.source_vertex.x, self.source_vertex.y, self.target_vertex.x, self.target_vertex.y)

class Triangle:
	def __init__(self, e1, e2, e3, options):
		self.options = options
		self.default_colour = self.options.default_triangle_colour
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
		self.drawn_self = self.canvas.create_polygon([self.vertices[0].x, self.vertices[0].y, self.vertices[1].x, self.vertices[1].y, self.vertices[2].x, self.vertices[2].y], fill=self.default_colour, tag='polygon')
		for edge in self.edges:
			edge.in_triangles.append(self)
	
	def __str__(self):
		return '%s %s %s' % (self.vertices[0], self.vertices[1], self.vertices[2])
	
	def set_colour(self, colour=None):
		if colour is None: colour = self.default_colour
		self.canvas.itemconfig(self.drawn_self, fill=colour)
	
	def set_default_colour(self, colour):
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
		self.canvas.coords(self.drawn_self, *[self.vertices[0].x, self.vertices[0].y, self.vertices[1].x, self.vertices[1].y, self.vertices[2].x, self.vertices[2].y])

class CurveComponent:
	def __init__(self, canvas, source_point, options, multiplicity=1):
		self.options = options
		self.default_colour = self.options.default_curve_colour
		self.colour = self.default_colour
		self.vertices = [source_point]
		self.drawn_segments = []
		self.canvas = canvas
		self.multiplicity = multiplicity
	
	def append_point(self, point):
		self.vertices.append(point)
		self.drawn_segments.append(self.canvas.create_line(self.vertices[-2][0], self.vertices[-2][1], self.vertices[-1][0], self.vertices[-1][1], width=self.options.line_size, fill=self.colour, tag='curve'))
		return self
	
	def pop_point(self):
		if len(self.vertices) > 1:
			self.vertices.pop()
			self.canvas.delete(self.drawn_segments[-1])
			self.drawn_segments.pop()
	
	def set_colour(self, colour=None):
		if colour is None: colour = self.default_colour
		self.colour = colour
		for segment in self.drawn_segments:
			self.canvas.itemconfig(segment, fill=colour)
	
	def set_default_colour(self, colour):
		self.default_colour = colour
		self.set_colour(self.default_colour)
	
	def move_last_point(self, new_point):
		if len(self.vertices) > 1:
			self.vertices[-1] = new_point
			self.canvas.coords(self.drawn_segments[-1], self.vertices[-2][0], self.vertices[-2][1], self.vertices[-1][0], self.vertices[-1][1])
	
	def update(self):
		for i in range(len(self.drawn_segments)):
			self.canvas.coords(self.drawn_segments[i], self.vertices[i][0], self.vertices[i][1], self.vertices[i+1][0], self.vertices[i+1][1])
