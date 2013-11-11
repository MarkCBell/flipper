
from math import sin, cos, pi
from itertools import combinations
from time import time
try:
	import Tkinter as TK
	import tkFont as TK_FONT
	import tkFileDialog
	import tkMessageBox
	import tkSimpleDialog
except ImportError: # Python 3
	import tkinter as TK
	import tkinter.font as TK_FONT
	import tkinter.filedialog as tkFileDialog
	import tkinter.messagebox as tkMessageBox
	import tkinter.simpledialog as tkSimpleDialog

from Pieces import Colour_Palette, Vertex, Edge, Triangle, Curve_Component
from AbstractTriangulation import Abstract_Triangulation
from Progress import Progress_App
from Encoding import Id_Encoding_Sequence, Encoding
from Matrix import Permutation_Matrix, Empty_Matrix
from Options import Options, Options_App
from Error import AbortError

# Modes.
TRIANGULATION_MODE = 0
GLUING_MODE = 1
CURVE_MODE = 2
CURVE_DRAWING_MODE = 3

def lines_intersect(s1, e1, s2, e2, float_error, equivalent_edge):
	dx1, dy1 = e1[0] - s1[0], e1[1] - s1[1]
	dx2, dy2 = e2[0] - s2[0], e2[1] - s2[1]
	D = dx2*dy1 - dx1*dy2
	if D == 0: return (-1, False)
	
	xx = s2[0] - s1[0]
	yy = s2[1] - s1[1]
	
	s = (yy*dx1 - xx*dy1)/D
	t = (yy*dx2 - xx*dy2)/D
	
	return (t if 0-float_error <= s <= 1+float_error and 0-float_error <= t <= 1+float_error else -1, equivalent_edge and 0+float_error <= s <= 1-float_error and 0+float_error <= t <= 1-float_error)

class App:
	def __init__(self, parent):
		self.parent = parent
		self.mode_variable = TK.IntVar()
		self.mode_variable.set(TRIANGULATION_MODE)
		
		self.options = Options()
		self.options_app = Options_App(self)
		self.options_app.parent.state('withdrawn')
		
		self.frame_interface = TK.Frame(self.parent, width=50, height=2)
		self.frame_interface.grid(column=1, sticky='nse')
		###
		
		self.frame_mode = TK.Frame(self.frame_interface, pady=2)
		self.frame_mode.pack(padx=1, pady=1, side='top', fill='x')
		###
		###
		self.label_tools = TK.Label(self.frame_mode, text='Tools:', anchor='w', font=self.options.custom_font)
		self.radio_mode_triangulation = TK.Radiobutton(self.frame_mode, text="Triangulation", variable=self.mode_variable, value=TRIANGULATION_MODE, command=lambda : self.set_mode(TRIANGULATION_MODE), indicatoron=False, font=self.options.custom_font)
		self.radio_mode_gluing = TK.Radiobutton(self.frame_mode, text="Gluing", variable=self.mode_variable, value=GLUING_MODE, command=lambda : self.set_mode(GLUING_MODE), indicatoron=False, font=self.options.custom_font)
		self.radio_mode_curve = TK.Radiobutton(self.frame_mode, text="Curve", variable=self.mode_variable, value=CURVE_MODE, command=lambda : self.set_mode(CURVE_MODE), indicatoron=False, font=self.options.custom_font)
		self.label_tools.pack(fill='x') 
		self.radio_mode_triangulation.pack(fill='x', expand=True)
		self.radio_mode_gluing.pack(fill='x', expand=True)
		self.radio_mode_curve.pack(fill='x', expand=True)
		###
		###
		
		self.label_curves = TK.Label(self.frame_interface, text='Curves:', anchor='w', font=self.options.custom_font)
		self.label_curves.pack(fill='x')
		
		self.list_curves = TK.Listbox(self.frame_interface, font=self.options.custom_font)
		self.list_curves.pack(fill='both', expand=True)
		
		###
		
		self.frame_command = TK.Frame(self.parent)
		self.frame_command.grid(row=1, column=0, sticky='wes')
		###
		self.label_command = TK.Label(self.frame_command, text='Command:', font=self.options.custom_font)
		self.label_command.pack(side='left')
		
		self.entry_command = TK.Entry(self.frame_command, text='', font=self.options.custom_font)
		self.entry_command.pack(padx=15, pady=1, side='top', fill='x', expand=True)
		self.entry_command.bind('<Return>', self.command_return)
		###
		
		self.frame_draw = TK.Frame(self.parent)
		self.frame_draw.grid(row=0, column=0, sticky='nesw')
		###
		self.canvas = TK.Canvas(self.frame_draw, bg='#dcecff')
		self.canvas.pack(fill='both', expand=True)
		self.canvas.bind('<Button-1>', self.canvas_left_click)
		self.canvas.bind('<Button-3>', self.canvas_right_click)
		self.canvas.bind('<B1-Motion>', self.canvas_mouse_moved)
		self.canvas.bind('<ButtonRelease-1>', self.canvas_left_release)
		self.list_curves.bind("<Button-1>", self.list_left_click)
		self.list_curves.bind("<Button-3>", self.list_right_click)
		self.list_curves.bind('<Shift-Button-1>', self.list_shift_click)
		
		###
		parent.bind('<Key>', self.parent_key_press)
		
		self.parent.columnconfigure(0, weight=1)
		self.parent.rowconfigure(0, weight=1)
		
		self.command_history = ['']
		self.history_position = 0
		self.initialise()
	
	def initialise(self):
		self.vertices = []
		self.edges = []
		self.triangles = []
		self.curve_components = []
		self.selected_object = None
		
		self.build_complete_structure()
		
		self.colour_picker = Colour_Palette()
		self.set_mode(TRIANGULATION_MODE)
		
		self.canvas.delete('all')
		self.list_curves.delete(0, TK.END)
		self.entry_command.delete(0, TK.END)
		
		self.entry_command.focus()
	
	def save(self, path):
		pass
	
	def load(self, path):
		pass
	
	def export_image(self, path):
		self.canvas.postscript(file=path, colormode='color')
	
	def is_complete(self):
		return len(self.triangles) > 0 and all(edge.free_sides() == 0 for edge in self.edges)
	
	def set_mode(self, mode):
		self.select_object(None)
		if mode == TRIANGULATION_MODE:
			self.canvas.delete('curve')
			self.mode_variable.set(mode)
		elif mode == GLUING_MODE:
			self.canvas.delete('curve')
			self.curve_components = []
			self.mode_variable.set(mode)
		elif mode == CURVE_MODE:
			if not self.is_complete():
				self.set_mode(GLUING_MODE)
			else:
				self.mode_variable.set(mode)
		elif mode == CURVE_DRAWING_MODE:
			if not self.is_complete():
				self.set_mode(GLUING_MODE)
			else:
				self.mode_variable.set(mode)
	
	def command_return(self, event):
		command = self.entry_command.get()
		if command != '':
			self.command_history.insert(-1, command)
			self.history_position = len(self.command_history) - 1
			
			sections = command.split(' ')
			try:
				if sections[0] == 'clear': self.initialise()
				elif sections[0] == 'erase': self.destroy_curve()
				elif sections[0] == 'options': self.show_options()
				elif sections[0] == 'debug': self.debug()
				elif sections[0] == 'profile': self.profile()
				elif sections[0] == 'stats': self.stats()
				elif sections[0] == 'exit': self.parent.quit()
				
				elif sections[0] == 'ngon': self.initialise_circular_n_gon(sections[1])
				elif sections[0] == 'rngon': self.initialise_radial_n_gon(sections[1])
				
				elif sections[0] == 'tighten': self.tighten_curve()
				elif sections[0] == 'store': self.store_curve(sections[1])
				elif sections[0] == 'show': self.show_composition(sections[1])
				elif sections[0] == 'render': self.show_render(sections[1])
				elif sections[0] == 'vectorise': self.vectorise()
				elif sections[0] == 'apply': self.show_apply(sections[1])
				
				elif sections[0] == 'periodic': self.is_periodic(sections[1])
				elif sections[0] == 'reducible': self.is_reducible(sections[1])
				elif sections[0] == 'pA': self.is_pseudo_Anosov(sections[1])
				elif sections[0] == 'lamination': print(self.stable_lamination(sections[1]))
				elif sections[0] == 'lamination_exact': print(self.stable_lamination(sections[1], exact=True))
				elif sections[0] == 'applied': self.show_applied(sections[1])
				
				elif sections[0] == 'split': self.splitting_sequence(sections[1])
				
				elif sections[0] == 'save': self.save(sections[1])
				elif sections[0] == 'load': self.load(sections[1])
				elif sections[0] == 'export': self.export_image(sections[1])
				elif sections[0] == 'test': 
					self.initialise_circular_n_gon('abcACB')
					self.profile()
					self.stats()
					self.curves['a'] = [0,0,1,1,1,0]
					self.curves['b'] = [0,1,0,1,0,1]
					self.curves['c'] = [1,0,0,0,1,1]
					self.curves['_'] = self.curves['a']
					print([triangle.edge_indices for triangle in self.abstract_triangulation.triangles])
					print('Estimating stable_lamination of a.b.C:')
					print(self.stable_lamination('a.b.C'))
					# print('and now exactly:')
					# print(self.stable_lamination('a.b.C', exact=True))
					test = 'abCCbaCCaBBB'
					for i in range(3,len(test)):
						print('Computing splitting sequence of: %s' % '.'.join(test[:i]))
						self.splitting_sequence('.'.join(test[:i]))
					# self.is_reducible('c.A.B.C')  # Reducible
					# self.is_reducible('c.c.A.B.C.C')  # Reducible
					# self.is_reducible('a.a.B.C')  # ??
					# self.is_reducible('a.a.b.C')  # Irreducible.
				
				elif sections[0] == 'test2':
					# Test using 'rngon abcdefABCDEF'
					T = self.abstract_triangulation
					a = T.encode_twist([1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0])
					A = T.encode_twist([1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], k=-1)
					b = T.encode_twist([1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0])
					B = T.encode_twist([1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0], k = -1)
					
					perms = T.find_isometries(T)
					print(perms[1])
					
					p = Encoding([Permutation_Matrix(perms[1])], [Empty_Matrix(T.zeta)], T, T)
					
					h = (b*A*A*A*p)
					self.curves['_'] = h * self.curves['_']
					self.show_curve('_')
				# elif sections[0] == '':
				else:
					tkMessageBox.showwarning('Command', 'Unknown command: %s' % command)
				self.entry_command.delete(0, TK.END)
			except IndexError:
				tkMessageBox.showwarning('Command', 'Command requires more arguments.')
	
	def object_here(self, p):
		for object in self.vertices + self.edges + self.triangles:
			if p in object:
				return object
		return None
	
	def redraw(self):
		for edge in self.edges:
			edge.hide(not self.options.show_internals and edge.is_internal())
		self.canvas.tag_raise('polygon')
		self.canvas.tag_raise('line')
		self.canvas.tag_raise('oval')
		self.canvas.tag_raise('curve')
		self.canvas.tag_raise('label')
	
	def show_options(self):
		self.options_app.parent.state('normal')
		self.options_app.parent.lift()
	
	def debug(self):
		self.options.debugging = True
		if self.is_complete():
			for edge in self.edges:
				self.canvas.create_text((edge.source_vertex[0] + edge.target_vertex[0]) / 2, (edge.source_vertex[1] + edge.target_vertex[1]) / 2, text=str(edge.index), tag='edge_label')
			print([triangle.edge_indices for triangle in self.abstract_triangulation])
	
	def profile(self):
		self.options.profiling = True
	
	def stats(self):
		self.options.statistics = True
	
	def select_object(self, selected_object):
		self.selected_object = selected_object
		for x in self.vertices + self.edges:
			x.set_colour()
		if self.selected_object is not None:
			self.selected_object.set_colour(self.options.default_selected_colour)
	
	
	######################################################################
	
	
	def create_vertex(self, point):
		self.vertices.append(Vertex(self.canvas, point, self.options))
		self.redraw()
		self.build_complete_structure()
		return self.vertices[-1]
	
	def destroy_vertex(self, vertex):
		while True:
			for edge in self.edges:
				if edge.source_vertex == vertex or edge.target_vertex == vertex:
					self.destroy_edge(edge)
					break
			else:
				break
		self.canvas.delete(vertex.drawn_self)
		self.vertices.remove(vertex)
		self.redraw()
		self.build_complete_structure()
	
	def create_edge(self, v1, v2):
		if any(set([edge.source_vertex, edge.target_vertex]) == set([v1, v2]) for edge in self.edges):
			return None
		
		e0 = Edge(v1, v2, self.options)
		for e1, e2 in combinations(self.edges, r=2):
			if e1.free_sides() > 0 and e2.free_sides() > 0:
				if len(set([e.source_vertex for e in [e0,e1,e2]] + [e.target_vertex for e in [e0,e1,e2]])) == 3:
					self.create_triangle(e0, e1, e2)
		self.edges.append(e0)
		self.redraw()
		self.build_complete_structure()
		return self.edges[-1]
	
	def destroy_edge(self, edge):
		self.canvas.delete(edge.drawn_self)
		for triangle in edge.in_triangles:
			self.destroy_triangle(triangle)
		self.destroy_edge_identification(edge)
		self.edges.remove(edge)
		self.redraw()
		self.build_complete_structure()
	
	def create_triangle(self, e1, e2, e3):
		assert(True)  # Check distinct or something? Check each edge is in at most 2 triangles and is not equivalent.
		assert(e1 != e2 and e1 != e3 and e2 != e3)
		
		if any([set(triangle.edges) == set([e1, e2, e3]) for triangle in self.triangles]):
			return None
		
		self.triangles.append(Triangle(e1,e2,e3, self.options))
		self.redraw()
		self.build_complete_structure()
		return self.triangles[-1]
	
	def destroy_triangle(self, triangle):
		self.canvas.delete(triangle.drawn_self)
		for edge in self.edges:
			if triangle in edge.in_triangles:
				edge.in_triangles.remove(triangle)
		self.triangles.remove(triangle)
		self.redraw()
		self.build_complete_structure()
	
	def create_edge_identification(self, e1, e2):
		assert(e1.equivalent_edge is None and e2.equivalent_edge is None)
		assert(e1.free_sides() == 1 and e2.free_sides() == 1)
		e1.equivalent_edge = e2
		e2.equivalent_edge = e1
		
		# Change colour.
		new_colour = self.colour_picker()
		e1.set_default_colour(new_colour)
		e2.set_default_colour(new_colour)
		self.build_complete_structure()
	
	def destroy_edge_identification(self, edge):
		if edge.equivalent_edge is not None:
			other_edge = edge.equivalent_edge
			other_edge.default_colour = self.options.default_edge_colour
			edge.default_colour = self.options.default_edge_colour
			self.canvas.itemconfig(other_edge.drawn_self, fill=other_edge.default_colour)
			self.canvas.itemconfig(edge.drawn_self, fill=edge.default_colour)
			
			edge.equivalent_edge.equivalent_edge = None
			edge.equivalent_edge = None
		self.build_complete_structure()
	
	def create_curve_component(self, point, multiplicity=None):
		self.curve_components.append(Curve_Component(self.canvas, point, self.options, multiplicity))
		self.redraw()
		return self.curve_components[-1]
	
	def destroy_curve_component(self, curve_component):
		for i in range(len(curve_component.vertices)):
			curve_component.pop_point()
		self.curve_components.remove(curve_component)
		self.redraw()
	
	def destroy_curve(self):
		while True:
			for curve_component in self.curve_components:
				self.destroy_curve_component(curve_component)
				break
			else:
				break
		self.redraw()
	
	
	######################################################################
	
	
	def initialise_radial_n_gon(self, specification):
		self.initialise()
		if specification.isdigit():
			n, gluing = int(specification), ''
		else:
			n, gluing = len(specification), specification
		w = int(self.canvas.winfo_width())
		h = int(self.canvas.winfo_height())
		
		self.create_vertex((w / 2, h / 2))
		for i in range(n):
			self.create_vertex((w / 2 + sin(2*pi*(i+0.5) / n) * w * self.options.n_gon_fraction, h / 2 + cos(2*pi*(i+0.5) / n) * h * self.options.n_gon_fraction))
		for i in range(1,n):
			self.create_edge(self.vertices[i], self.vertices[i+1])
		self.create_edge(self.vertices[n], self.vertices[1])
		for i in range(n):
			self.create_edge(self.vertices[0], self.vertices[i+1])
		if gluing != '':
			for i, j in combinations(range(n), r=2):
				if gluing[i] == gluing[j].swapcase():
					self.create_edge_identification(self.edges[i], self.edges[j])
			self.set_mode(CURVE_MODE)
	
	def initialise_circular_n_gon(self, specification):
		self.initialise()
		if specification.isdigit():
			n, gluing = int(specification), ''
		else:
			n, gluing = len(specification), specification
		
		w = int(self.canvas.winfo_width())
		h = int(self.canvas.winfo_height())
		for i in range(n):
			self.create_vertex((w / 2 + sin(2*pi*(i+0.5) / n) * w * self.options.n_gon_fraction, h / 2 + cos(2*pi*(i+0.5) / n) * h * self.options.n_gon_fraction))
		for i in range(n):
			self.create_edge(self.vertices[i], self.vertices[i-1])
		
		all_vertices = list(range(n))
		while len(all_vertices) > 3:
			for i in range(0, len(all_vertices)-1, 2):
				self.create_edge(self.vertices[all_vertices[i]], self.vertices[all_vertices[(i+2) % len(all_vertices)]])
			all_vertices = all_vertices[::2]
		
		if gluing != '':
			for i, j in combinations(range(n), r=2):
				if gluing[i] == gluing[j].swapcase():
					self.create_edge_identification(self.edges[i], self.edges[j])
			self.set_mode(CURVE_MODE)
	
	
	######################################################################
	
	
	def set_edge_indices(self):
		# Assigns each edge an index in range(self.zeta).
		
		self.clear_edge_indices()
		self.zeta = 0
		for edge in self.edges:
			if edge.index == -1:
				self.zeta += 1
				edge.index = self.zeta-1
				if edge.equivalent_edge is not None:
					edge.equivalent_edge.index = edge.index
	
	def clear_edge_indices(self):
		self.zeta = 0
		for edge in self.edges:
			edge.index = -1
	
	def create_abstract_triangulation(self):
		self.set_edge_indices()
		self.curves = {'_':[0] * self.zeta}
		self.abstract_triangulation = Abstract_Triangulation([[triangle.edges[side].index for side in range(3)] for triangle in self.triangles])
	
	def destroy_abstract_triangulation(self):
		self.clear_edge_indices()
		self.curves = {}
		self.abstract_triangulation = None
	
	def build_complete_structure(self):
		if self.is_complete():
			self.create_abstract_triangulation()
		else:
			self.destroy_abstract_triangulation()
	
	######################################################################
	
	
	def curve_to_vector(self):
		vector = [0] * self.zeta
		
		# This version takes into account bigons between interior edges.
		for curve in self.curve_components:
			meets = []  # We store (index of edge intersection, should we double count).
			for i in range(len(curve.vertices)-1):
				this_segment_meets = [(lines_intersect(curve.vertices[i], curve.vertices[i+1], edge.source_vertex, edge.target_vertex, self.options.float_error, edge.equivalent_edge is None), edge.index) for edge in self.edges]
				for (d, double), index in sorted(this_segment_meets):
					if d >= -self.options.float_error:
						if len(meets) > 0 and meets[-1][0] == index:
							meets.pop()
						else:
							meets.append((index, double))
			
			for index, double in meets:
				vector[index] += (2 if double else 1) * (1 if curve.multiplicity is None else curve.multiplicity)
		
		return [i // 2 for i in vector]
		
		# for edge in self.edges:  # We'll double count everything!
			# for curve in self.curve_components:
				# for i in range(len(curve.vertices)-1):
					# if lines_intersect(edge.source_vertex, edge.target_vertex, curve.vertices[i], curve.vertices[i+1], self.options.float_error):
						# if lines_intersect(edge.source_vertex, edge.target_vertex, curve.vertices[i], curve.vertices[i+1], self.options.float_error, properly=True) and edge.equivalent_edge is None:
							# vector[edge.index] += 2 * (1 if curve.multiplicity is None else curve.multiplicity)
						# else:
							# vector[edge.index] += 1 * (1 if curve.multiplicity is None else curve.multiplicity)
		
		# return [i // 2 for i in vector]
	
	def vector_to_curve(self, vector):
		self.destroy_curve()
		for triangle in self.triangles:
			weights = [vector[edge.index] for edge in triangle.edges]
			dual_weights = [(weights[1] + weights[2] - weights[0]) // 2, (weights[2] + weights[0] - weights[1]) // 2, (weights[0] + weights[1] - weights[2]) // 2]
			for i in range(3):
				a = triangle.vertices[i-1] - triangle.vertices[i]
				b = triangle.vertices[i-2] - triangle.vertices[i]
				if self.options.compress_curve:
					if dual_weights[i] > 0:
						scale = float(1) / 2
						start_point = triangle.vertices[i][0] + a[0] * scale, triangle.vertices[i][1] + a[1] * scale
						end_point = triangle.vertices[i][0] + b[0] * scale, triangle.vertices[i][1] + b[1] * scale
						self.create_curve_component(start_point, dual_weights[i]).append_point(end_point)
				else:  # This is the slowest bit when the weight of the image curve is 10000.
					for j in range(dual_weights[i]):
						scale_a = float(1) / 2 if weights[i-2] == 1 else self.options.vertex_buffer + (1 - 2*self.options.vertex_buffer) * j / (weights[i-2] - 1)
						scale_b = float(1) / 2 if weights[i-1] == 1 else self.options.vertex_buffer + (1 - 2*self.options.vertex_buffer) * j / (weights[i-1] - 1)
						start_point = triangle.vertices[i][0] + a[0] * scale_a, triangle.vertices[i][1] + a[1] * scale_a
						end_point = triangle.vertices[i][0] + b[0] * scale_b, triangle.vertices[i][1] + b[1] * scale_b
						self.create_curve_component(start_point).append_point(end_point)
	
	def tighten_curve(self):
		curve = self.curve_to_vector()
		if self.abstract_triangulation is not None:
			if self.abstract_triangulation.is_multicurve(curve):
				self.vector_to_curve(curve)
			else:
				tkMessageBox.showwarning('Curve', 'Not a curve.')
	
	def store_curve(self, name):
		if name != '' and name != '_':
			if self.abstract_triangulation.is_multicurve(self.curve_to_vector()):
				if name not in self.curves: self.list_curves.insert(TK.END, name)
				self.curves[name] = self.curve_to_vector()
				self.destroy_curve()
				self.curves['_'] = [0] * self.zeta
			else:
				tkMessageBox.showwarning('Curve', 'Not a curve.')
	
	def show_curve(self, name):
		self.destroy_curve()
		self.vector_to_curve(self.curves[name])
		self.curves['_'] = self.curves[name]
	
	def create_composition(self, twists):
		mapping_class = Id_Encoding_Sequence(self.abstract_triangulation)
		for twist in twists[::-1]:
			if twist in self.curves:
				mapping_class = self.abstract_triangulation.encode_twist(self.curves[twist]) * mapping_class
			elif twist.swapcase() in self.curves:
				mapping_class = self.abstract_triangulation.encode_twist(self.curves[twist.swapcase()], k=-1) * mapping_class
			else:
				tkMessageBox.showwarning('Curve', 'Unknown curve: %s' % twist)
				raise AbortError()
		
		mapping_class = mapping_class.compactify()
		if self.options.debugging: print('Mapping class size: %d' % mapping_class.size)
		return mapping_class
	
	def show_composition(self, composition):
		curves = composition.split('.')
		twists, name = curves[:-1], curves[-1]
		if name in self.curves:
			curve = self.curves[name]
		elif name.swapcase() in self.curves:
			curve = self.curves[name.swapcase()]
		else:
			tkMessageBox.showwarning('Curve', 'Unknown curve: %s' % name)
			return
		
		try:
			mapping_class = self.create_composition(twists)
		except AbortError:
			pass
		else:
			self.curves['_'] = mapping_class * curve
			self.show_curve('_')
	
	def show_render(self, composition):
		self.curves['_'] = [int(i) for i in composition.split(',')]
		self.show_curve('_')
	
	def vectorise(self):
		print(self.curve_to_vector())
		tkMessageBox.showinfo('Curve', '%s' % self.curve_to_vector())
	
	def show_apply(self, composition):
		self.show_composition(composition + '._')
	
	def show_applied(self, composition):
		try:
			mapping_class = self.create_composition(composition.split('.'))
		except AbortError:
			pass
		else:
			print(mapping_class.applied_matrix(self.curves['_'])[0])
	
	
	######################################################################
	
	
	def is_periodic(self, composition):
		try:
			mapping_class = self.create_composition(composition.split('.'))
		except AbortError:
			pass
		else:
			if mapping_class.is_periodic():
				tkMessageBox.showinfo('Periodic', '%s is periodic.' % composition)
			else:
				tkMessageBox.showinfo('Periodic', '%s is not periodic.' % composition)
	
	def is_reducible(self, composition):
		try:
			mapping_class = self.create_composition(composition.split('.'))
		except AbortError:
			pass
		else:
			try:
				start_time = time()
				result = mapping_class.is_reducible(certify=True, show_progress=Progress_App(self), options=self.options)
				if self.options.profiling: print('Determined reducibility of %s in %0.1fs.' % (composition, time() - start_time))
				if result[0]:
					tkMessageBox.showinfo('Reducible', '%s is reducible, it fixes %s.' % (composition, result[1]))
				else:
					tkMessageBox.showinfo('Reducible', '%s is irreducible.' % composition)
			except AbortError:
				pass
	
	def is_pseudo_Anosov(self, composition):
		try:
			mapping_class = self.create_composition(composition.split('.'))
		except AbortError:
			pass
		else:
			try:
				if mapping_class.is_periodic():
					tkMessageBox.showinfo('pseudo Anosov', '%s is not pseudo-Anosov because it is periodic.' % composition)
				elif mapping_class.is_reducible(certify=False, show_progress=Progress_App(self), options=self.options):
					tkMessageBox.showinfo('pseudo Anosov', '%s is not pseudo-Anosov because it is reducible.' % composition)
				else:
					tkMessageBox.showinfo('pseudo Anosov', '%s is pseudo-Anosov.' % composition)
			except AbortError:
				pass
	
	
	######################################################################
	
	
	def stable_lamination(self, composition, exact=False):
		try:
			mapping_class = self.create_composition(composition.split('.'))
		except AbortError:
			pass
		else:
			try:
				return mapping_class.stable_lamination(exact)    # Get any old curve.
			except AbortError:
				tkMessageBox.showinfo('Dilatation', 'Could not estimate the stable lamination of %s.' % composition)
	
	def splitting_sequence(self, composition):
		try:
			start_time = time()
			V, dilatation = self.stable_lamination(composition, exact=True)
			if self.options.profiling: print('Computed initial data of %s in %0.1fs.' % (composition, time() - start_time))
		except AbortError:
			tkMessageBox.showinfo('Dilatation', 'Could not estimate the stable lamination of %s.' % composition)
		else:
			start_time = time()
			print(self.abstract_triangulation.splitting_sequence(V))
			if self.options.profiling: print('Computed splitting sequence of %s in %0.1fs.' % (composition, time() - start_time))
	
	
	######################################################################
	
	
	def triangulation_click(self, x, y):
		possible_object = self.object_here((x,y))
		if self.selected_object is None:
			if possible_object is None:
				self.select_object(self.create_vertex((x,y)))
			else:
				if isinstance(possible_object, Edge):
					self.destroy_edge_identification(possible_object)
				if isinstance(possible_object, Edge):
					if possible_object.free_sides() > 0:
						self.select_object(possible_object)
				if isinstance(possible_object, Vertex):
					self.select_object(possible_object)
		elif isinstance(self.selected_object, Vertex):
			if possible_object is None:
				new_vertex = self.create_vertex((x,y))
				self.create_edge(self.selected_object, new_vertex)
				self.select_object(new_vertex)
			elif isinstance(possible_object, Vertex):
				if possible_object != self.selected_object:
					self.create_edge(self.selected_object, possible_object)
					self.select_object(possible_object)
			elif isinstance(possible_object, Edge):
				if possible_object.free_sides() > 0:
					self.select_object(possible_object)
		elif isinstance(self.selected_object, Edge):
			if possible_object is None:
				new_vertex = self.create_vertex((x,y))
				self.create_edge(self.selected_object.source_vertex, new_vertex)
				self.create_edge(self.selected_object.target_vertex, new_vertex)
				self.select_object(None)
			elif isinstance(possible_object, Vertex):
				if possible_object != self.selected_object.source_vertex and possible_object != self.selected_object.target_vertex:
					self.create_edge(self.selected_object.source_vertex, possible_object)
					self.create_edge(self.selected_object.target_vertex, possible_object)
					self.select_object(None)
				else:
					self.select_object(possible_object)
			elif isinstance(possible_object, Edge):
				if possible_object.free_sides() > 0:
					self.select_object(possible_object)
	
	def gluing_click(self, x, y):
		possible_object = self.object_here((x,y))
		if isinstance(possible_object, Edge):
			if possible_object.free_sides() == 1:
				if possible_object.equivalent_edge is None:
					if isinstance(self.selected_object, Edge):
						if possible_object != self.selected_object:
							self.create_edge_identification(self.selected_object, possible_object)
							self.select_object(None)
					elif self.selected_object is None:
						self.select_object(possible_object)
				else:
					self.destroy_edge_identification(possible_object)
					self.select_object(possible_object)
	
	def curve_click(self, x, y):
		if self.selected_object is None:
			self.set_mode(CURVE_DRAWING_MODE)
			self.select_object(self.create_curve_component((x,y)))
	
	
	######################################################################
	
	
	def canvas_left_click(self, event):
		x, y = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))
		if self.mode_variable.get() == TRIANGULATION_MODE:
			self.triangulation_click(x, y)
		if self.mode_variable.get() == GLUING_MODE:
			self.gluing_click(x, y)
		if self.mode_variable.get() == CURVE_MODE:
			self.curve_click(x, y)
	
	def canvas_right_click(self, event):
		self.select_object(None)
	
	def canvas_mouse_moved(self, event):
		x, y = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))
		if self.mode_variable.get() == CURVE_DRAWING_MODE:
			x0, y0 = self.selected_object.vertices[-1]
			if (x - x0)**2 + (y - y0)**2 > self.options.spacing**2:
				self.selected_object.append_point((x,y))
	
	def canvas_left_release(self, event):
		if self.mode_variable.get() == CURVE_DRAWING_MODE:
			self.curves['_'] = self.curve_to_vector()
			self.set_mode(CURVE_MODE)
	
	def parent_key_press(self, event):
		key = event.keysym
		if key in ('Delete','BackSpace'):
			if self.mode_variable.get() == TRIANGULATION_MODE:
				if isinstance(self.selected_object, Vertex):
					self.destroy_vertex(self.selected_object)
					self.select_object(None)
				elif isinstance(self.selected_object, Edge):
					self.destroy_edge(self.selected_object)
					self.select_object(None)
		elif key == 'Up':
			if self.history_position > 0:
				self.history_position -= 1
				self.entry_command.delete(0, TK.END)
				self.entry_command.insert(0, self.command_history[self.history_position])
		elif key == 'Down':
			if self.history_position < len(self.command_history) - 1:
				self.history_position += 1
				self.entry_command.delete(0, TK.END)
				self.entry_command.insert(0, self.command_history[self.history_position])
	
	def list_left_click(self, event):
		self.show_apply(self.list_curves.get(self.list_curves.nearest(event.y)))
	
	def list_right_click(self, event):
		self.show_apply(self.list_curves.get(self.list_curves.nearest(event.y)).swapcase())
	
	def list_shift_click(self, event):
		if self.list_curves.size() > 0:
			self.show_curve(self.list_curves.get(self.list_curves.nearest(event.y)))

if __name__ == '__main__':
	root = TK.Tk()
	root.title('Twist Images')
	app = App(root)
	root.mainloop()
