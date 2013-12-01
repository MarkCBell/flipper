
# To run from within sage you might need to first update tkiner by doing:
# sudo apt-get install tk8.5-dev
# sage -f python
# Then run with:
# sage -python App.py

from math import sin, cos, pi
from itertools import combinations
from time import time
import pickle
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

try:
	from Source.Pieces import Colour_Palette, Vertex, Edge, Triangle, Curve_Component, lines_intersect
	from Source.AbstractTriangulation import Abstract_Triangulation
	from Source.Isometry import extend_isometry
	from Source.Lamination import Lamination, stable_lamination
	from Source.SplittingSequence import compute_splitting_sequence
	from Source.Progress import Progress_App
	from Source.Encoding import Id_Encoding_Sequence, Encoding, encode_twist, encode_isometry
	from Source.Matrix import Permutation_Matrix, Empty_Matrix
	from Source.Options import Options, Options_App
	from Source.Error import AbortError, ComputationError, AssumptionError
except ImportError:
	from Pieces import Colour_Palette, Vertex, Edge, Triangle, Curve_Component, lines_intersect
	from AbstractTriangulation import Abstract_Triangulation
	from Isometry import extend_isometry
	from Lamination import Lamination
	from SplittingSequence import compute_splitting_sequence
	from Progress import Progress_App
	from Encoding import Id_Encoding_Sequence, Encoding, encode_isometry
	from Matrix import Permutation_Matrix, Empty_Matrix
	from Options import Options, Options_App
	from Error import AbortError, ComputationError, AssumptionError

# Modes.
TRIANGULATION_MODE = 0
GLUING_MODE = 1
CURVE_MODE = 2
CURVE_DRAWING_MODE = 3

class Flipper_App:
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
		self.label_mapping_classes = TK.Label(self.frame_interface, text='Mapping Classes:', anchor='w', font=self.options.custom_font)
		self.label_mapping_classes.pack(fill='x')
		
		self.list_mapping_classes = TK.Listbox(self.frame_interface, font=self.options.custom_font)
		self.list_mapping_classes.pack(fill='both', expand=True)
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
		self.canvas = TK.Canvas(self.frame_draw, width=500, height=500, bg='#dcecff')
		self.canvas.pack(fill='both', expand=True)
		self.canvas.bind('<Button-1>', self.canvas_left_click)
		self.canvas.bind('<Double-Button-1>', self.canvas_double_click)
		self.canvas.bind('<Button-3>', self.canvas_right_click)
		self.canvas.bind('<Motion>', self.canvas_move)
		self.list_mapping_classes.bind('<Button-1>', self.list_left_click)
		self.list_mapping_classes.bind('<Button-3>', self.list_right_click)
		self.list_mapping_classes.bind('<Shift-Button-1>', self.list_shift_click)
		
		###
		
		# Create the menus.
		menubar = TK.Menu(self.parent)
		
		filemenu = TK.Menu(menubar, tearoff=0)
		filemenu.add_command(label='New', command=self.initialise)
		filemenu.add_command(label='Open', command=lambda : self.load())
		filemenu.add_command(label='Save', command=lambda : self.save())
		filemenu.add_command(label='Export', command=lambda : self.export_image())
		filemenu.add_separator()
		filemenu.add_command(label='Exit', command=self.parent.quit)
		
		toolmenu = TK.Menu(menubar, tearoff=0)
		toolmenu.add_radiobutton(label='Triangulation', variable=self.mode_variable, value=TRIANGULATION_MODE, command=lambda : self.set_mode(TRIANGULATION_MODE))
		toolmenu.add_radiobutton(label='Gluing', variable=self.mode_variable, value=GLUING_MODE, command=lambda : self.set_mode(GLUING_MODE))
		toolmenu.add_radiobutton(label='Curve', variable=self.mode_variable, value=CURVE_MODE, command=lambda : self.set_mode(CURVE_MODE))
		
		helpmenu = TK.Menu(menubar, tearoff=0)
		helpmenu.add_command(label='Help')  # !?!
		helpmenu.add_separator()
		helpmenu.add_command(label='About', command=self.show_about)
		
		menubar.add_cascade(label='File', menu=filemenu)
		menubar.add_cascade(label='Tools', menu=toolmenu)
		menubar.add_command(label='Options', command=self.show_options)
		menubar.add_cascade(label='Help', menu=helpmenu)
		self.parent.config(menu=menubar)
		
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
		self.abstract_triangulation = None
		self.curve_components = []
		self.mapping_classes = {}
		self.selected_object = None
		self.list_mapping_classes.delete(0, TK.END)
		
		self.build_complete_structure()
		
		self.colour_picker = Colour_Palette()
		self.set_mode(TRIANGULATION_MODE)
		
		self.canvas.delete('all')
		self.entry_command.delete(0, TK.END)
		
		self.entry_command.focus()
	
	def save(self, path=''):
		if path == '': path = tkFileDialog.asksaveasfilename(defaultextension='.flp', filetypes=[('Flipper files', '.flp'), ('all files', '.*')], title='Save Flipper File')
		if path is None: return
		try:
			spec = 'A Flipper file.'
			vertices = [(vertex.x, vertex.y) for vertex in self.vertices]
			edges = [(self.vertices.index(edge.source_vertex), self.vertices.index(edge.target_vertex), self.edges.index(edge.equivalent_edge) if edge.equivalent_edge is not None else -1) for edge in self.edges]
			abstract_triangulation = self.abstract_triangulation
			curves = self.curves
			mapping_classes = self.mapping_classes
			list_names = self.list_mapping_classes.get(0, TK.END)
			
			pickle.dump([spec, vertices, edges, abstract_triangulation, curves, mapping_classes, list_names], open(path, 'wb'))
		except IOError:
			tkMessageBox.showwarning('Save Error', 'Could not open: %s' % path)
	
	def load(self, path=''):
		if path == '': path = tkFileDialog.askopenfilename(defaultextension='.flp', filetypes=[('Flipper files', '.flp'), ('all files', '.*')], title='Open Flipper File')
		if path is None: return
		
		try:
			spec, vertices, edges, abstract_triangulation, curves, mapping_classes, list_names = pickle.load(open(path, 'rb'))
			# Might throw value error.
			# !?! Add more error checking.
			assert(spec == 'A Flipper file.')
			
			self.initialise()
			for vertex in vertices:
				self.create_vertex(vertex)
			
			for edge in edges:
				start_index, end_index, glued_to_index = edge
				self.create_edge(self.vertices[start_index], self.vertices[end_index])
			
			for index, edge in enumerate(edges):
				start_index, end_index, glued_to_index = edge
				if glued_to_index > index:
					self.create_edge_identification(self.edges[index], self.edges[glued_to_index])
			
			self.abstract_triangulation = abstract_triangulation
			
			self.curves = curves
			self.mapping_classes = mapping_classes
			
			for name in list_names:
				self.list_mapping_classes.insert(TK.END, name)
			
			if self.is_complete():
				self.lamination_to_curve(self.curves['_'])
				self.set_mode(CURVE_MODE)
			
		except IOError:
			tkMessageBox.showwarning('Load Error', 'Could not open: %s' % path)
	
	def export_image(self, path):
		if path == '': path = tkFileDialog.asksaveasfilename(defaultextension='.ps', filetypes=[('postscript files', '.ps'), ('all files', '.*')], title='Export Image')
		if path is None: return
		
		try:
			self.canvas.postscript(file=path, colormode='color')
		except IOError:
			tkMessageBox.showwarning('Export Error', 'Could not open: %s' % path)
	
	def show_about(self):
		tkMessageBox.showinfo('About', 'Flipper (Version %s).\nCopyright (c) Mark Bell 2013.' % self.options.version)
	
	def translate(self, dx, dy):
		for vertex in self.vertices:
			vertex.x += dx
			vertex.y += dy
		
		self.canvas.move('all', dx, dy)
	
	def is_complete(self):
		return len(self.triangles) > 0 and all(edge.free_sides() == 0 for edge in self.edges)
	
	def set_mode(self, mode):
		self.select_object(None)
		if mode == TRIANGULATION_MODE:
			self.destroy_curve()
			self.mode_variable.set(mode)
		elif mode == GLUING_MODE:
			self.destroy_curve()
			self.mode_variable.set(mode)
		elif mode == CURVE_MODE:
			if not self.is_complete():
				self.set_mode(GLUING_MODE)
			else:
				self.mode_variable.set(mode)
		else:
			raise ValueError()
	
	def command_return(self, event):
		command = self.entry_command.get()
		if command != '':
			self.command_history.insert(-1, command)
			self.history_position = len(self.command_history) - 1
			
			sections = command.split(' ')
			task, arguements = sections[0], sections[1:]
			combined = ' '.join(arguements)
			try:
				if task == '': pass
				
				elif task == 'save': self.save(combined)
				elif task == 'load': self.load(combined)
				elif task == 'open': self.load(combined)
				elif task == 'export': self.export_image(combined)
				elif task == 'options': self.show_options()
				elif task == 'about': self.show_about()
				elif task == 'exit': self.parent.quit()
				
				elif task == 'debug': self.debug()
				elif task == 'profile': self.profile()
				elif task == 'stats': self.stats()
				
				elif task == 'clear': self.initialise()
				elif task == 'erase': self.destroy_curve()
				elif task == 'ngon': self.initialise_circular_n_gon(combined)
				elif task == 'rngon': self.initialise_radial_n_gon(combined)
				
				elif task == 'tighten': self.tighten_curve()
				elif task == 'show': self.show_composition(combined)
				elif task == 'render': self.show_render(combined)
				elif task == 'vectorise': self.vectorise()
				
				elif task == 'twist': self.store_curve(combined)
				elif task == 'isometry': self.store_isometry(combined)
				elif task == 'apply': self.show_apply(combined)
				
				elif task == 'order': self.order(combined)
				elif task == 'periodic': self.is_periodic(combined)
				elif task == 'reducible': self.is_reducible(combined)
				elif task == 'pA': self.is_pseudo_Anosov(combined)
				elif task == 'lamination': self.stable_lamination(combined)
				elif task == 'lamination_exact': self.stable_lamination(combined, exact=True)
				elif task == 'split': self.splitting_sequence(combined)
				# elif task == '':
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
		self.canvas.tag_raise('edge_label')
	
	def show_options(self):
		self.options_app.parent.state('normal')
		self.options_app.parent.lift()
	
	def debug(self):
		self.options.debugging = not self.options.debugging
		if self.options.debugging and self.is_complete():
			print([triangle.edge_indices for triangle in self.abstract_triangulation])
	
	def profile(self):
		self.options.profiling = not self.options.profiling
	
	def stats(self):
		self.options.statistics = not self.options.statistics
	
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
	
	def destroy_curve(self):
		if self.is_complete():
			while self.curve_components != []:
				self.destroy_curve_component(self.curve_components[-1])
			
			self.set_current_curve()
			self.select_object(None)
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
			# self.store_isometry('p %d,%d,%d %d,%d,%d' % (0,n+1,n,1,n+2,n+1))  # !?! Add in a 1/n rotation by default.
			self.set_mode(CURVE_MODE)
		else:
			self.set_mode(GLUING_MODE)
	
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
	
	def create_edge_labels(self):
		self.destroy_edge_labels()
		if self.options.label_edges == 'Index':
			for edge in self.edges:
				self.canvas.create_text((edge.source_vertex[0] + edge.target_vertex[0]) / 2, (edge.source_vertex[1] + edge.target_vertex[1]) / 2, text=str(edge.index), tag='edge_label', font=self.options.custom_font, fill=self.options.default_edge_label_colour)
		elif self.options.label_edges == 'Geometric':
			vector = self.curves['_']
			for edge in self.edges:
				self.canvas.create_text((edge.source_vertex[0] + edge.target_vertex[0]) / 2, (edge.source_vertex[1] + edge.target_vertex[1]) / 2, text=str(vector[edge.index]), tag='edge_label', font=self.options.custom_font, fill=self.options.default_edge_label_colour)
		elif self.options.label_edges == 'Algebraic':
			vector = self.abstract_triangulation.geometric_to_algebraic(self.curves['_'])
			for edge in self.edges:
				self.canvas.create_text((edge.source_vertex[0] + edge.target_vertex[0]) / 2, (edge.source_vertex[1] + edge.target_vertex[1]) / 2, text=str(vector[edge.index]), tag='edge_label', font=self.options.custom_font, fill=self.options.default_edge_label_colour)
		elif self.options.label_edges == 'None':
			self.canvas.delete('edge_label')
		else:
			raise ValueError()
	
	def destroy_edge_labels(self):
		self.canvas.delete('edge_label')
	
	def create_abstract_triangulation(self):
		# Must start by calling self.set_edge_indices() so that self.zeta is correctly set.
		self.set_edge_indices()
		self.curves = {'_':[0] * self.zeta}
		self.abstract_triangulation = Abstract_Triangulation([[triangle.edges[side].index for side in range(3)] for triangle in self.triangles])
		self.create_edge_labels()
	
	def destroy_abstract_triangulation(self):
		self.clear_edge_indices()
		self.destroy_edge_labels()
		self.abstract_triangulation = None
		self.curves = {}
		self.mapping_classes = {}
		self.list_mapping_classes.delete(0, TK.END)
	
	def build_complete_structure(self):
		if self.is_complete() and self.abstract_triangulation is None:
			self.create_abstract_triangulation()
		elif not self.is_complete() and self.abstract_triangulation is not None:
			self.destroy_abstract_triangulation()
	
	
	######################################################################
	
	
	def set_current_curve(self, vector=None):
		if vector is None: vector = self.curve_to_lamination()
		self.curves['_'] = vector
		self.create_edge_labels()
	
	def curve_to_lamination(self):
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
		
		return Lamination(self.abstract_triangulation, [i // 2 for i in vector])
		
		# for edge in self.edges:  # We'll double count everything!
			# for curve in self.curve_components:
				# for i in range(len(curve.vertices)-1):
					# if lines_intersect(edge.source_vertex, edge.target_vertex, curve.vertices[i], curve.vertices[i+1], self.options.float_error):
						# if lines_intersect(edge.source_vertex, edge.target_vertex, curve.vertices[i], curve.vertices[i+1], self.options.float_error, properly=True) and edge.equivalent_edge is None:
							# vector[edge.index] += 2 * (1 if curve.multiplicity is None else curve.multiplicity)
						# else:
							# vector[edge.index] += 1 * (1 if curve.multiplicity is None else curve.multiplicity)
		
		# return [i // 2 for i in vector]
	
	def lamination_to_curve(self, lamination):
		self.destroy_curve()
		for triangle in self.triangles:
			weights = [lamination.vector[edge.index] for edge in triangle.edges]
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
		
		self.set_current_curve(lamination)
	
	def tighten_curve(self):
		curve = self.curve_to_lamination()
		if self.abstract_triangulation is not None:
			if self.abstract_triangulation.is_multicurve(curve):
				self.lamination_to_curve(curve)
			else:
				tkMessageBox.showwarning('Curve', 'Not an essential curve.')
	
	def store_curve(self, name):
		if name != '' and name != '_':
			lamination = self.curve_to_lamination()
			if lamination.is_curve():
				if name not in self.mapping_classes: self.list_mapping_classes.insert(TK.END, name)
				self.curves[name] = lamination
				self.mapping_classes[name] = encode_twist(lamination)
				self.mapping_classes[name.swapcase()] = encode_twist(lamination, k=-1)
				self.destroy_curve()
			else:
				tkMessageBox.showwarning('Curve', 'Not an essential curve.')
	
	def show_curve(self, name):
		if name in self.curves:
			self.destroy_curve()
			self.lamination_to_curve(self.curves[name])
			self.set_current_curve(self.curves[name])
		else:
			tkMessageBox.showwarning('Curve', '%s is not a curve.' % name)
	
	def create_composition(self, twists):
		mapping_class = Id_Encoding_Sequence(self.abstract_triangulation)
		for twist in twists[::-1]:
			if twist in self.mapping_classes:
				mapping_class = self.mapping_classes[twist] * mapping_class
			else:
				tkMessageBox.showwarning('Curve', 'Unknown curve: %s' % twist)
				raise AbortError()
		
		# mapping_class = mapping_class.compactify()  # !?! Broken.
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
			self.set_current_curve(mapping_class * curve)
			self.lamination_to_curve(self.curves['_'])
	
	def show_render(self, composition):
		self.set_current_curve([int(i) for i in composition.split(',')])
		self.lamination_to_curve(self.curves['_'])
	
	def vectorise(self):
		tkMessageBox.showinfo('Curve', '%s' % self.curve_to_lamination().vector)
	
	def show_apply(self, composition):
		self.show_composition(composition + '._')
	
	def store_isometry(self, specification):
		name, from_edges, to_edges = specification.split(' ')[:3]
		
		from_edges = [int(x) for x in from_edges.split(',')]
		to_edges = [int(x) for x in to_edges.split(',')]
		
		source_triangles = [triangle for triangle in self.abstract_triangulation if set(triangle.edge_indices) == set(from_edges)]
		target_triangles = [triangle for triangle in self.abstract_triangulation if set(triangle.edge_indices) == set(to_edges)]
		if len(source_triangles) != 1 or len(source_triangles) != 1:
			tkMessageBox.showwarning('Isometry', 'Information does not specify a triangle.')
			return
		
		source_triangle, target_triangle = source_triangles[0], target_triangles[0]
		
		cycle = [i for i in range(3) for j in range(3) if source_triangle[j] == from_edges[0] and target_triangle[j+i] == to_edges[0]][0]
		try:
			isometry = encode_isometry(extend_isometry(self.abstract_triangulation, self.abstract_triangulation, source_triangle, target_triangle, cycle))
			isometry_inverse = encode_isometry(extend_isometry(self.abstract_triangulation, self.abstract_triangulation, target_triangle, source_triangle, (cycle * 2) % 3))
		except AssumptionError:
			tkMessageBox.showwarning('Isometry', 'Information does not specify an isometry.')
		else:
			if name != '' and name != '_':
				if name not in self.mapping_classes: self.list_mapping_classes.insert(TK.END, name)
				self.mapping_classes[name] = isometry
				self.mapping_classes[name.swapcase()] = isometry_inverse
	
	
	######################################################################
	
	
	def order(self, composition):
		try:
			mapping_class = self.create_composition(composition.split('.'))
		except AbortError:
			pass
		else:
			order = mapping_class.order()
			tkMessageBox.showinfo('Order', '%s has order %s.' % (composition, ('infinite' if order == 0 else str(order))))
	
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
					tkMessageBox.showinfo('pseudo-Anosov', '%s is not pseudo-Anosov because it is periodic.' % composition)
				elif mapping_class.is_reducible(certify=False, show_progress=Progress_App(self), options=self.options):
					tkMessageBox.showinfo('pseudo-Anosov', '%s is not pseudo-Anosov because it is reducible.' % composition)
				else:
					tkMessageBox.showinfo('pseudo-Anosov', '%s is pseudo-Anosov.' % composition)
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
				lamination, dilatation = stable_lamination(mapping_class, exact)
			except ComputationError:
				tkMessageBox.showwarning('Lamination', 'Could not estimate the stable lamination of %s.  It is probably reducible.' % composition)
			else:
				tkMessageBox.showinfo('Lamination', '%s has lamination: %s \nand dilatation: %s' % (composition, lamination, dilatation))
	
	def splitting_sequence(self, composition):
		try:
			mapping_class = self.create_composition(composition.split('.'))
		except AbortError:
			pass
		else:
			try:
				start_time = time()
				lamination, dilatation = stable_lamination(mapping_class, exact=True)
			except ComputationError:
				tkMessageBox.showwarning('Lamination', 'Could not estimate the stable lamination of %s. It is probably reducible.' % composition)
			else:
				if self.options.profiling: print('Computed initial data of %s in %0.1fs.' % (composition, time() - start_time))
				try:
					start_time = time()
					preperiodic, periodic, dilatation = compute_splitting_sequence(lamination)
				except AssumptionError:
					tkMessageBox.showwarning('Lamination', '%s is reducible.' % composition)
				else:
					if self.options.profiling: print('Computed splitting sequence of %s in %0.1fs.' % (composition, time() - start_time))
					tkMessageBox.showinfo('Splitting sequence', 'Preperiodic splits: %s \nPeriodic splits: %s' % (preperiodic, periodic))
	
	
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
			self.select_object(self.create_curve_component((x,y)))
			self.selected_object.append_point((x,y))
		else:
			self.selected_object.append_point((x,y))
			self.set_current_curve()
	
	
	######################################################################
	
	
	def canvas_left_click(self, event):
		x, y = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))
		if self.mode_variable.get() == TRIANGULATION_MODE:
			self.triangulation_click(x, y)
		if self.mode_variable.get() == GLUING_MODE:
			self.gluing_click(x, y)
		if self.mode_variable.get() == CURVE_MODE:
			self.curve_click(x, y)
	
	def canvas_move(self, event):
		x, y = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))
		if self.mode_variable.get() == CURVE_MODE:
			if self.selected_object is not None:
				self.selected_object.move_last_point((x,y))
	
	def canvas_right_click(self, event):
		if self.selected_object is not None:
			if self.mode_variable.get() == CURVE_MODE:
				self.selected_object.pop_point()
			self.select_object(None)
	
	def canvas_double_click(self, event):
		self.canvas_right_click(event)
	
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
			if self.mode_variable.get() == GLUING_MODE:
				pass
			if self.mode_variable.get() == CURVE_MODE:
				if self.selected_object is not None:
					if len(self.selected_object.vertices) > 2:
						(x,y) = self.selected_object.vertices[-1]
						self.selected_object.pop_point()
						self.selected_object.pop_point()
						self.selected_object.append_point((x,y))
						self.set_current_curve()
					else:
						self.destroy_curve_component(self.selected_object)
						self.select_object(None)
						self.set_current_curve()
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
		if self.list_mapping_classes.size() > 0:
			self.show_apply(self.list_mapping_classes.get(self.list_mapping_classes.nearest(event.y)))
	
	def list_right_click(self, event):
		if self.list_mapping_classes.size() > 0:
			self.show_apply(self.list_mapping_classes.get(self.list_mapping_classes.nearest(event.y)).swapcase())
	
	def list_shift_click(self, event):
		if self.list_mapping_classes.size() > 0:
			self.show_curve(self.list_mapping_classes.get(self.list_mapping_classes.nearest(event.y)))

def main():
	root = TK.Tk()
	root.title('Flipper')
	Flipper_App(root)
	root.mainloop()

if __name__ == '__main__':
	main()
