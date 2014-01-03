
# To run from within sage you might need to first update tkiner by doing:
# sudo apt-get install tk8.5-dev
# sage -f python
# Then run with:
# sage -python App.py


import re
import os
import sys
import pickle
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

from Flipper.App.Pieces import Colour_Palette, Vertex, Edge, Triangle, Curve_Component, lines_intersect
from Flipper.App.Options import Options, Options_App
from Flipper.App.Progress import Progress_App

from Flipper.Kernel.AbstractTriangulation import Abstract_Triangulation
from Flipper.Kernel.Encoding import Id_Encoding_Sequence, encode_twist, encode_halftwist, encode_isometry
from Flipper.Kernel.Isometry import extend_isometry
from Flipper.Kernel.Lamination import Lamination, invariant_lamination, empty_lamination
from Flipper.Kernel.LayeredTriangulation import Layered_Triangulation
from Flipper.Kernel.Error import AbortError, ComputationError, AssumptionError

# Modes.
TRIANGULATION_MODE = 0
GLUING_MODE = 1
CURVE_MODE = 2
CURVE_DRAWING_MODE = 3

COMMAND_MODIFIERS = {'darwin':'Command', 'win32':'Ctrl', 'linux2':'Ctrl', 'linux3':'Ctrl'}
COMMAND_MODIFIER = COMMAND_MODIFIERS[sys.platform] if sys.platform in COMMAND_MODIFIERS else 'Ctrl'
COMMAND_MODIFIER_BINDINGS = {'darwin':'Command', 'win32':'Control', 'linux2':'Control', 'linux3':'Control'}
COMMAND_MODIFIER_BINDING = COMMAND_MODIFIER_BINDINGS[sys.platform] if sys.platform in COMMAND_MODIFIER_BINDINGS else 'Control'

# A name is valid if it consists of letters, numbers, underscores and at least one letter.
def valid_name(name):
	if re.match('\w+', name) is not None and re.match('\w+', name).group() == name and re.search('[a-zA-Z]+', name) is not None:
		return True
	else:
		tkMessageBox.showwarning('Name', '%s is not a valid name.' % name)
		return False

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
		self.label_curves = TK.Label(self.frame_interface, text='Multicurves:', anchor='w', font=self.options.custom_font)
		self.label_curves.pack(fill='x')
		
		self.list_curves = TK.Listbox(self.frame_interface, font=self.options.custom_font)
		self.list_curves.pack(fill='both', expand=True)
		
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
		self.list_curves.bind('<Button-1>', self.list_curves_left_click)
		self.list_mapping_classes.bind('<Button-1>', self.list_mapping_classes_left_click)
		self.list_mapping_classes.bind('<Button-3>', self.list_mapping_classes_right_click)
		
		###
		
		# Create the menus.
		menubar = TK.Menu(self.parent)
		
		filemenu = TK.Menu(menubar, tearoff=0)
		filemenu.add_command(label='New', command=self.initialise, accelerator='%s+N' % COMMAND_MODIFIER)
		filemenu.add_command(label='Open', command=lambda : self.load(), accelerator='%s+O' % COMMAND_MODIFIER)
		filemenu.add_command(label='Save', command=lambda : self.save(), accelerator='%s+S' % COMMAND_MODIFIER)
		exportmenu = TK.Menu(menubar, tearoff=0)
		exportmenu.add_command(label='Export script', command=lambda : self.export_script())
		exportmenu.add_command(label='Export image', command=lambda : self.export_image())
		filemenu.add_cascade(label='Export', menu=exportmenu)
		filemenu.add_separator()
		filemenu.add_command(label='Exit', command=self.parent.quit, accelerator='%s+W' % COMMAND_MODIFIER)
		
		editmenu = TK.Menu(menubar, tearoff=0)
		editmenu.add_radiobutton(label='Triangulation', variable=self.mode_variable, value=TRIANGULATION_MODE, command=lambda : self.set_mode(TRIANGULATION_MODE), accelerator='F2')
		editmenu.add_radiobutton(label='Gluing', variable=self.mode_variable, value=GLUING_MODE, command=lambda : self.set_mode(GLUING_MODE), accelerator='F3')
		editmenu.add_radiobutton(label='Curve', variable=self.mode_variable, value=CURVE_MODE, command=lambda : self.set_mode(CURVE_MODE), accelerator='F4')
		editmenu.add_separator()
		editmenu.add_command(label='Erase Curve', command=self.destroy_curve, accelerator='F5')
		
		viewmenu = TK.Menu(menubar, tearoff=0)
		zoommenu = TK.Menu(menubar, tearoff=0)
		zoommenu.add_command(label='Zoom in', command=lambda : self.zoom_centre(1.05), accelerator='Pg Up')
		zoommenu.add_command(label='Zoom out', command=lambda : self.zoom_centre(0.95), accelerator='Pg Down')
		zoommenu.add_command(label='Auto zoom', command=lambda : self.auto_zoom())
		viewmenu.add_cascade(label='Zoom', menu=zoommenu)
		# viewmenu.add_command(label='Translate', command=self.show_options)
		
		settingsmenu = TK.Menu(menubar, tearoff=0)
		settingsmenu.add_command(label='Options', command=self.show_options)
		
		helpmenu = TK.Menu(menubar, tearoff=0)
		helpmenu.add_command(label='Help', command=self.show_help, accelerator='F1')
		helpmenu.add_separator()
		helpmenu.add_command(label='About', command=self.show_about)
		
		menubar.add_cascade(label='File', menu=filemenu)
		menubar.add_cascade(label='Edit', menu=editmenu)
		menubar.add_cascade(label='View', menu=viewmenu)
		menubar.add_cascade(label='Settings', menu=settingsmenu)
		menubar.add_cascade(label='Help', menu=helpmenu)
		self.parent.config(menu=menubar)
		
		parent.bind('<%s-n>' % COMMAND_MODIFIER_BINDING, lambda event: self.initialise())
		parent.bind('<%s-o>' % COMMAND_MODIFIER_BINDING, lambda event: self.load())
		parent.bind('<%s-s>' % COMMAND_MODIFIER_BINDING, lambda event: self.save())
		parent.bind('<%s-w>' % COMMAND_MODIFIER_BINDING, lambda event: self.quit())
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
		self.curves = {}
		self.mapping_classes = {}
		self.selected_object = None
		self.list_curves.delete(0, TK.END)
		self.list_mapping_classes.delete(0, TK.END)
		
		self.build_complete_structure()
		
		self.colour_picker = Colour_Palette()
		self.set_mode(TRIANGULATION_MODE)
		
		self.canvas.delete('all')
		self.entry_command.delete(0, TK.END)
		
		self.entry_command.focus()
	
	def save(self, path=''):
		if path == '': path = tkFileDialog.asksaveasfilename(defaultextension='.flp', filetypes=[('Flipper files', '.flp'), ('all files', '.*')], title='Save Flipper File')
		if path != '':
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
		if path != '':
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
					self.lamination_to_canvas(self.curves['_'])
					self.set_mode(CURVE_MODE)
			except IOError:
				tkMessageBox.showwarning('Load Error', 'Could not open: %s' % path)
	
	def export_image(self, path=''):
		if path == '': path = tkFileDialog.asksaveasfilename(defaultextension='.ps', filetypes=[('postscript files', '.ps'), ('all files', '.*')], title='Export Image')
		if path != '':
			try:
				self.canvas.postscript(file=path, colormode='color')
			except IOError:
				tkMessageBox.showwarning('Export Error', 'Could not open: %s' % path)
	
	def export_script(self, path=''):
		if self.is_complete():
			if path == '': path = tkFileDialog.asksaveasfilename(defaultextension='.py', filetypes=[('Python files', '.py'), ('all files', '.*')], title='Export Image')
			if path != '':
				try:
					file = open(path, 'w')
					
					twists = [(mapping_class,self.mapping_classes[mapping_class][1][1].vector) for mapping_class in self.mapping_classes if self.mapping_classes[mapping_class][1][0] == 'twist' and self.mapping_classes[mapping_class][1][2] == +1]
					halfs  = [(mapping_class,self.mapping_classes[mapping_class][1][1].vector) for mapping_class in self.mapping_classes if self.mapping_classes[mapping_class][1][0] == 'half'  and self.mapping_classes[mapping_class][1][2] == +1]
					isoms  = [(mapping_class,self.mapping_classes[mapping_class][1][1].edge_map) for mapping_class in self.mapping_classes if self.mapping_classes[mapping_class][1][0] == 'isometry' and self.mapping_classes[mapping_class][1][2] == +1]
					
					example = '\n' + \
					'from Flipper.Kernel.AbstractTriangulation import Abstract_Triangulation\n' + \
					'from Flipper.Kernel.Isometry import all_isometries\n' + \
					'from Flipper.Kernel.Encoding import encode_twist, encode_halftwist, encode_isometry, Id_Encoding_Sequence\n' + \
					'from Flipper.Kernel.Lamination import Lamination\n' + \
					'\n' + \
					'def Example():\n' + \
					'	T = Abstract_Triangulation(%s)\n' % [triangle.edge_indices for triangle in self.abstract_triangulation] + \
					'	\n' + \
					''.join('\t%s = encode_twist(Lamination(T, %s))\n' % (mapping_class, vector) for (mapping_class, vector) in twists) + \
					''.join('\t%s = encode_twist(Lamination(T, %s), k=-1)\n' % (mapping_class.swapcase(), vector) for (mapping_class, vector) in twists) + \
					''.join('\t%s = encode_halftwist(Lamination(T, %s))\n' % (mapping_class, vector) for (mapping_class, vector) in halfs) + \
					''.join('\t%s = encode_halftwist(Lamination(T, %s), k=-1)\n' % (mapping_class.swapcase(), vector) for (mapping_class, vector) in halfs) + \
					''.join('\t%s = encode_isometry(isometry_from_edge_map(T, T, %s))\n' % (mapping_class, edge_map) for (mapping_class, edge_map) in isoms) + \
					''.join('\t%s = encode_isometry(isometry_from_edge_map(T, T, %s).inverse())\n' % (mapping_class.swapcase(), edge_map) for (mapping_class, edge_map) in isoms) + \
					'	\n' + \
					'	return T, {%s}\n' % ', '.join('\'%s\':%s' % (mapping_class, mapping_class) for mapping_class in self.mapping_classes) + \
					'	\n' + \
					'def build_example_mapping_class(example, word=None, random_length=50):\n' + \
					'	from random import choice\n' + \
					'	\n' + \
					'	T, twists = example()\n' + \
					'	\n' + \
					'	if word is None: word = \'\'.join(choice(list(twists.keys())) for i in range(random_length))\n' + \
					'	h = Id_Encoding_Sequence(T)\n' + \
					'	for letter in word:\n' + \
					'		h = twists[letter] * h\n' + \
					'	return word, h\n' + \
					'\n'
					
					file.write(example)
				except IOError:
					tkMessageBox.showwarning('Export Error', 'Could not open: %s' % path)
				finally:
					file.close()
		else:
			tkMessageBox.showwarning('Export Error', 'Cannot export incomplete surface.')
			
	
	def quit(self):
		self.parent.quit()
	
	def show_options(self):
		self.options_app.parent.state('normal')
		self.options_app.parent.lift()
	
	def show_help(self):
		# !?! TO DO
		tkMessageBox.showwarning('Help', 'Not yet implemented. See "A users guide to Flipper" for more information.')
	
	def show_about(self):
		tkMessageBox.showinfo('About', 'Flipper (Version %s).\nCopyright (c) Mark Bell 2013.' % self.options.version)
	
	def debug(self):
		self.options.debugging = not self.options.debugging
		if self.options.debugging and self.is_complete():
			print([triangle.edge_indices for triangle in self.abstract_triangulation])
	
	def profile(self):
		self.options.profiling = not self.options.profiling
	
	def stats(self):
		self.options.statistics = not self.options.statistics
	
	def translate(self, dx, dy):
		for vertex in self.vertices:
			vertex.x += dx
			vertex.y += dy
		
		for curve_component in self.curve_components:
			for i in range(len(curve_component.vertices)):
				curve_component.vertices[i] = curve_component.vertices[i][0] + dx, curve_component.vertices[i][1] + dy
		
		self.canvas.move('all', dx, dy)
	
	def zoom(self, scale):
		for vertex in self.vertices:
			vertex.x, vertex.y = scale * vertex.x, scale * vertex.y
			vertex.update()
		for edge in self.edges:
			edge.update()
		for triangle in self.triangles:
			triangle.update()
		for curve_component in self.curve_components:
			for i in range(len(curve_component.vertices)):
				curve_component.vertices[i] = scale * curve_component.vertices[i][0], scale * curve_component.vertices[i][1]
			curve_component.update()
		self.create_edge_labels()
		self.redraw()
	
	def zoom_centre(self, scale):
		cw = int(self.canvas.winfo_width())
		ch = int(self.canvas.winfo_height())
		self.translate(-cw / 2, -ch / 2)
		self.zoom(scale)
		self.translate(cw / 2, ch / 2)
	
	def auto_zoom(self):
		box = self.canvas.bbox('all')
		if box is not None:
			x0, y0, x1, y1 = box
			cw = int(self.canvas.winfo_width())
			ch = int(self.canvas.winfo_height())
			cr = min(cw, ch)
			
			w, h = x1 - x0, y1 - y0
			r = max(w, h)
			
			self.translate(-x0 - w / 2, -y0 - h / 2)
			self.zoom(self.options.zoom_fraction * float(cr) / r)
			self.translate(cw / 2, ch / 2)
	
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
				elif task == 'new': self.initialise()
				elif task == 'save': self.save(combined)
				elif task == 'open': self.load(combined)
				elif task == 'export_image': self.export_image(combined)
				elif task == 'export_script': self.export_script(combined)
				elif task == 'triangulation_mode': self.set_mode(TRIANGULATION_MODE)
				elif task == 'gluing_mode': self.set_mode(GLUING_MODE)
				elif task == 'curve_mode': self.set_mode(CURVE_MODE)
				elif task == 'erase': self.destroy_curve()
				elif task == 'options': self.show_options()
				elif task == 'help': self.show_help()
				elif task == 'about': self.show_about()
				elif task == 'exit': self.quit()
				
				elif task == 'debug': self.debug()
				elif task == 'profile': self.profile()
				elif task == 'stats': self.stats()
				
				elif task == 'ngon': self.initialise_circular_n_gon(combined)
				elif task == 'rngon': self.initialise_radial_n_gon(combined)
				elif task == 'information': self.show_surface_information()
				
				elif task == 'zoom': self.auto_zoom()
				
				elif task == 'tighten': self.tighten_curve()
				elif task == 'show': self.show_composition(combined)
				elif task == 'render': self.show_render(combined)
				elif task == 'vectorise': self.vectorise()
				
				elif task == 'curve': self.store_curve(combined)
				elif task == 'twist': self.store_twist(combined)
				elif task == 'half': self.store_halftwist(combined)
				elif task == 'isometry': self.store_isometry(combined)
				elif task == 'apply': self.show_apply(combined)
				
				elif task == 'order': self.order(combined)
				elif task == 'periodic': self.is_periodic(combined)
				elif task == 'reducible': self.is_reducible(combined)
				elif task == 'pA': self.is_pseudo_Anosov(combined)
				elif task == 'lamination': self.invariant_lamination(combined)
				elif task == 'lamination_exact': self.invariant_lamination(combined, exact=True)
				elif task == 'split': self.splitting_sequence(combined)
				elif task == 'bundle': self.build_bundle(combined)
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
	
	def select_object(self, selected_object):
		self.selected_object = selected_object
		for x in self.vertices + self.edges + self.curve_components:
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
		# Don't create a new edge if one already exists.
		if any(set([edge.source_vertex, edge.target_vertex]) == set([v1, v2]) for edge in self.edges):
			return None
		
		# Don't create a new edge if it would intersect one that already exists.
		if any(lines_intersect(edge.source_vertex, edge.target_vertex, v1, v2, self.options.float_error, True)[1] for edge in self.edges):
			return None
		
		e0 = Edge(v1, v2, self.options)
		self.edges.append(e0)
		for e1, e2 in combinations(self.edges, r=2):
			if e1 != e0 and e2 != e0:
				if e1.free_sides() > 0 and e2.free_sides() > 0:
					if len(set([e.source_vertex for e in [e0,e1,e2]] + [e.target_vertex for e in [e0,e1,e2]])) == 3:
						self.create_triangle(e0, e1, e2)
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
		
		new_triangle = Triangle(e1,e2,e3, self.options)
		self.triangles.append(new_triangle)
		
		corner_vertices = [e.source_vertex for e in [e1,e2,e3]] + [e.target_vertex for e in [e1,e2,e3]]
		if any(vertex in new_triangle and vertex not in corner_vertices for vertex in self.vertices):
			self.destroy_triangle(new_triangle)
			return None
		
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
		r = min(w, h) * (1 + self.options.zoom_fraction) / 4
		
		self.create_vertex((w / 2, h / 2))
		for i in range(n):
			self.create_vertex((w / 2 + sin(2*pi*(i+0.5) / n) * r, h / 2 + cos(2*pi*(i+0.5) / n) * r))
		for i in range(1,n):
			self.create_edge(self.vertices[i], self.vertices[i+1])
		self.create_edge(self.vertices[n], self.vertices[1])
		for i in range(n):
			self.create_edge(self.vertices[0], self.vertices[i+1])
		if gluing != '':
			for i, j in combinations(range(n), r=2):
				if gluing[i] == gluing[j].swapcase():
					self.create_edge_identification(self.edges[i], self.edges[j])
			# self.store_isometry('p %d.%d.%d %d.%d.%d' % (0,n+1,n,1,n+2,n+1))  # !?! Add in a 1/n rotation by default.
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
		r = min(w, h) * (1 + self.options.zoom_fraction) / 4
		
		for i in range(n):
			self.create_vertex((w / 2 + sin(2*pi*(i+0.5) / n) * r, h / 2 + cos(2*pi*(i+0.5) / n) * r))
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
	
	def show_surface_information(self):
		if self.is_complete():
			num_marked_points = self.abstract_triangulation.num_vertices
			Euler_characteristic = self.abstract_triangulation.Euler_characteristic
			genus = (2 - Euler_characteristic - num_marked_points) // 2
			tkMessageBox.showinfo('Surface information', 'Underlying surface has genus %d and %d marked point(s). (Euler characteristic %d.)' % (genus ,num_marked_points, Euler_characteristic))
		else:
			tkMessageBox.showwarning('Surface information', 'Cannot compute information about an incomplete surface.')
	
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
		self.abstract_triangulation = Abstract_Triangulation([[triangle.edges[side].index for side in range(3)] for triangle in self.triangles])
		self.curves = {'_':empty_lamination(self.abstract_triangulation)}
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
	
	
	def set_current_curve(self, lamination=None):
		if lamination is None: lamination = self.canvas_to_lamination()
		self.curves['_'] = lamination
		self.create_edge_labels()
	
	def canvas_to_lamination(self):
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
		
		return Lamination(self.abstract_triangulation, [i / 2 for i in vector])
	
	def lamination_to_canvas(self, lamination):
		self.destroy_curve()
		for triangle in self.triangles:
			weights = [lamination[edge.index] for edge in triangle.edges]
			dual_weights = [(weights[1] + weights[2] - weights[0]) / 2, (weights[2] + weights[0] - weights[1]) / 2, (weights[0] + weights[1] - weights[2]) / 2]
			for i in range(3):
				a = triangle.vertices[i-1] - triangle.vertices[i]
				b = triangle.vertices[i-2] - triangle.vertices[i]
				if self.options.compress_curve:
					if dual_weights[i] > 0:
						scale = float(1) / 2
						start_point = triangle.vertices[i][0] + a[0] * scale, triangle.vertices[i][1] + a[1] * scale
						end_point = triangle.vertices[i][0] + b[0] * scale, triangle.vertices[i][1] + b[1] * scale
						self.create_curve_component(start_point, int(dual_weights[i])).append_point(end_point)
				else:  # This is the slowest bit when the weight of the image curve is 10000.
					for j in range(int(dual_weights[i])):
						scale_a = float(1) / 2 if weights[i-2] == 1 else self.options.vertex_buffer + (1 - 2*self.options.vertex_buffer) * j / (weights[i-2] - 1)
						scale_b = float(1) / 2 if weights[i-1] == 1 else self.options.vertex_buffer + (1 - 2*self.options.vertex_buffer) * j / (weights[i-1] - 1)
						start_point = triangle.vertices[i][0] + a[0] * scale_a, triangle.vertices[i][1] + a[1] * scale_a
						end_point = triangle.vertices[i][0] + b[0] * scale_b, triangle.vertices[i][1] + b[1] * scale_b
						self.create_curve_component(start_point).append_point(end_point)
		
		self.set_current_curve(lamination)
	
	def tighten_curve(self):
		if self.is_complete():
			curve = self.curves['_']
			if curve.is_multicurve():
				self.lamination_to_canvas(curve)
			else:
				tkMessageBox.showwarning('Curve', 'Not an essential multicurve.')
	
	def store_curve(self, name):
		if self.is_complete():
			if valid_name(name):
				lamination = self.curves['_']
				if lamination.is_multicurve():
					if name not in self.curves: self.list_curves.insert(TK.END, name)
					self.curves[name] = lamination
					self.destroy_curve()
				else:
					tkMessageBox.showwarning('Curve', 'Not an essential multicurve.')
	
	def store_twist(self, name):
		if self.is_complete():
			if valid_name(name):
				lamination = self.curves['_']
				if lamination.is_good_curve():
					if name not in self.curves: self.list_curves.insert(TK.END, name)
					self.curves[name] = lamination
					if name not in self.mapping_classes: self.list_mapping_classes.insert(TK.END, name)
					self.mapping_classes[name] = (encode_twist(lamination), ('twist', lamination, +1))
					self.mapping_classes[name.swapcase()] = (encode_twist(lamination, k=-1), ('twist', lamination, -1))
					self.destroy_curve()
				else:
					tkMessageBox.showwarning('Curve', 'Cannot twist about this, it is either a multicurve or a complementary region of it has no punctures.')
	
	def store_halftwist(self, name):
		if self.is_complete():
			if valid_name(name):
				lamination = self.curves['_']
				if lamination.is_pants_boundary():
					if name not in self.curves: self.list_curves.insert(TK.END, name)
					self.curves[name] = lamination
					if name not in self.mapping_classes: self.list_mapping_classes.insert(TK.END, name)
					self.mapping_classes[name] = (encode_halftwist(lamination), ('half', lamination, +1))
					self.mapping_classes[name.swapcase()] = (encode_halftwist(lamination, k=-1), ('half', lamination, -1))
					self.destroy_curve()
				else:
					tkMessageBox.showwarning('Curve', 'Not an essential curve bounding a pair of pants.')
	
	def store_isometry(self, specification):
		if self.is_complete():
			name, from_edges, to_edges = specification.split(' ')[:3]
			
			from_edges = [int(x) for x in from_edges.split('.')]
			to_edges = [int(x) for x in to_edges.split('.')]
			
			source_triangles = [triangle for triangle in self.abstract_triangulation if set(triangle.edge_indices) == set(from_edges)]
			target_triangles = [triangle for triangle in self.abstract_triangulation if set(triangle.edge_indices) == set(to_edges)]
			if len(source_triangles) != 1 or len(source_triangles) != 1:
				tkMessageBox.showwarning('Isometry', 'Information does not specify a triangle.')
				return
			
			source_triangle, target_triangle = source_triangles[0], target_triangles[0]
			
			cycle = [i for i in range(3) for j in range(3) if source_triangle[j] == from_edges[0] and target_triangle[j+i] == to_edges[0]][0]
			try:
				isometry = extend_isometry(self.abstract_triangulation, self.abstract_triangulation, source_triangle, target_triangle, cycle)
				mapping_class = encode_isometry(isometry)
				mapping_class_inverse = encode_isometry(isometry.inverse())
			except AssumptionError:
				tkMessageBox.showwarning('Isometry', 'Information does not specify an isometry.')
			else:
				if valid_name(name):
					if name not in self.mapping_classes: self.list_mapping_classes.insert(TK.END, name)
					self.mapping_classes[name] = (mapping_class, ('isometry', isometry, +1))
					self.mapping_classes[name.swapcase()] = (mapping_class_inverse, ('isometry', isometry, -1))
	
	def show_curve(self, name):
		if self.is_complete():
			if name in self.curves:
				self.destroy_curve()
				self.lamination_to_canvas(self.curves[name])
				self.set_current_curve(self.curves[name])
			else:
				tkMessageBox.showwarning('Curve', '%s is not a multicurve.' % name)
	
	def create_composition(self, twists):
		if self.is_complete():
			mapping_class = Id_Encoding_Sequence(self.abstract_triangulation)
			for twist in twists[::-1]:
				if twist in self.mapping_classes:
					mapping_class = self.mapping_classes[twist][0] * mapping_class
				else:
					tkMessageBox.showwarning('Mapping class', 'Unknown mapping class: %s' % twist)
					raise AbortError()
		
			if self.options.debugging: print('Mapping class size: %d' % mapping_class.size)
			return mapping_class
	
	def show_composition(self, composition):
		if self.is_complete():
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
				self.lamination_to_canvas(self.curves['_'])
	
	def show_render(self, composition):
		if self.is_complete():
			self.set_current_curve(Lamination(self.abstract_triangulation, [int(i) for i in composition.split('.')]))
			self.lamination_to_canvas(self.curves['_'])
	
	def vectorise(self):
		if self.is_complete():
			tkMessageBox.showinfo('Curve', 'Current curve is: %s' % self.curves['_'])
	
	def show_apply(self, composition):
		if self.is_complete():
			self.show_composition(composition + '._')
	
	
	######################################################################
	
	
	def order(self, composition):
		if self.is_complete():
			try:
				mapping_class = self.create_composition(composition.split('.'))
			except AbortError:
				pass
			else:
				order = mapping_class.order()
				if order == 0:
					tkMessageBox.showinfo('Order', '%s has infinite order.' % composition)
				else:
					tkMessageBox.showinfo('Order', '%s has order %s.' % (composition, order))
	
	def is_periodic(self, composition):
		if self.is_complete():
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
		if self.is_complete():
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
		if self.is_complete():
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
	
	
	def invariant_lamination(self, composition, exact=False):
		if self.is_complete():
			try:
				mapping_class = self.create_composition(composition.split('.'))
			except AbortError:
				pass
			else:
				try:
					lamination, dilatation = invariant_lamination(mapping_class, exact)
				except AssumptionError:
					tkMessageBox.showwarning('Lamination', 'Can not find any projectively invariant laminations of %s, it is periodic.' % composition)
				except ComputationError:
					tkMessageBox.showwarning('Lamination', 'Could not find any projectively invariant laminations of %s. It is probably reducible.' % composition)
				else:
					tkMessageBox.showinfo('Lamination', '%s has projectively invariant lamination: %s \nwith dilatation: %s' % (composition, lamination, dilatation))
	
	def splitting_sequence(self, composition):
		if self.is_complete():
			try:
				mapping_class = self.create_composition(composition.split('.'))
			except AbortError:
				pass
			else:
				try:
					lamination, dilatation = invariant_lamination(mapping_class, exact=True)
				except AssumptionError:
					tkMessageBox.showwarning('Lamination', 'Can not find any projectively invariant laminations of %s, it is periodic.' % composition)
				except ComputationError:
					tkMessageBox.showwarning('Lamination', 'Could not find any projectively invariant laminations of %s. It is probably reducible.' % composition)
				else:
					try:
						start_time = time()
						preperiodic, periodic, dilatation, correct_lamination, isometries = lamination.splitting_sequence()
					except AssumptionError:
						tkMessageBox.showwarning('Lamination', '%s is reducible.' % composition)
					else:
						if self.options.profiling: print('Computed splitting sequence of %s in %0.1fs.' % (composition, time() - start_time))
						tkMessageBox.showinfo('Splitting sequence', 'Preperiodic splits: %s \nPeriodic splits: %s' % (preperiodic, periodic))
	
	def build_bundle(self, composition):
		if self.is_complete():
			path = tkFileDialog.asksaveasfilename(defaultextension='.tri', filetypes=[('SnapPy Files', '.tri'), ('all files', '.*')], title='Export SnapPy Triangulation')
			if path != '':
				try:
					file = open(path, 'w')
					try:
						mapping_class = self.create_composition(composition.split('.'))
					except AbortError:
						pass
					else:
						try:
							lamination, dilatation = invariant_lamination(mapping_class, exact=True)
						except AssumptionError:
							tkMessageBox.showwarning('Lamination', 'Can not find any projectively invariant laminations of %s, it is periodic.' % composition)
						except ComputationError:
							tkMessageBox.showwarning('Lamination', 'Could not find any projectively invariant laminations of %s. It is probably reducible.' % composition)
						else:
							try:
								preperiodic, periodic, dilatation, correct_lamination, isometries = lamination.splitting_sequence()
							except AssumptionError:
								tkMessageBox.showwarning('Lamination', '%s is reducible.' % composition)
							else:
								L = Layered_Triangulation(correct_lamination.abstract_triangulation, composition)
								L.flips(periodic)
								closing_isometries = [isometry for isometry in L.upper_lower_isometries() if any(isometry.edge_map == isom.edge_map for isom in isometries)]
								# There may be more than one isometry, for now let's just pick the first. We'll worry about this eventually.
								M, cusp_types, fibre_slopes, degeneracy_slopes = L.close(closing_isometries[0])
								file.write(M.SnapPy_string())
								description = 'It was built using the first of %d isometries.\n' % len(closing_isometries) + \
								'It has %d cusp(s) with the following properties (in order):\n' % M.num_cusps + \
								'Cusp types: %s\n' % cusp_types + \
								'Fibre slopes: %s\n' % fibre_slopes + \
								'Degeneracy slopes: %s\n' % degeneracy_slopes + \
								'To build this bundle I had to create some artificial punctures,\n' + \
								'these are the ones with puncture type 1.\n' + \
								'You should fill them with their fibre slope to get\n' + \
								'the manifold you were expecting.'
								tkMessageBox.showinfo('Bundle', description)
				except IOError:
					tkMessageBox.showwarning('Save Error', 'Could not write to: %s' % path)
				finally:
					file.close()
	
	
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
			if possible_object.equivalent_edge is None:
				if possible_object.free_sides() == 1:
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
		elif key == 'Escape':
			self.canvas_right_click(None)
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
		elif key == 'F1':
			self.show_help()
		elif key == 'F2':
			self.set_mode(TRIANGULATION_MODE)
		elif key == 'F3':
			self.set_mode(GLUING_MODE)
		elif key == 'F4':
			self.set_mode(CURVE_MODE)
		elif key == 'F5':
			self.destroy_curve()
		elif key == 'Prior':
			self.zoom_centre(1.05)
		elif key == 'Next':
			self.zoom_centre(0.95)
	
	def list_curves_left_click(self, event):
		if self.list_curves.size() > 0:
			index = self.list_curves.nearest(event.y)
			xoffset, yoffset, width, height = self.list_curves.bbox(index)
			if yoffset <= event.y <= yoffset + height:
				self.show_curve(self.list_curves.get(index))
	
	def list_mapping_classes_left_click(self, event):
		if self.list_mapping_classes.size() > 0:
			index = self.list_mapping_classes.nearest(event.y)
			xoffset, yoffset, width, height = self.list_mapping_classes.bbox(index)
			if yoffset <= event.y <= yoffset + height:
				self.show_apply(self.list_mapping_classes.get(index))
	
	def list_mapping_classes_right_click(self, event):
		if self.list_mapping_classes.size() > 0:
			index = self.list_mapping_classes.nearest(event.y)
			xoffset, yoffset, width, height = self.list_mapping_classes.bbox(index)
			if yoffset <= event.y <= yoffset + height:
				self.show_apply(self.list_mapping_classes.get(index).swapcase())

def main(load_path=None):
	root = TK.Tk()
	root.title('Flipper')
	flipper = Flipper_App(root)
	if load_path is not None: flipper.load(load_path)
	# Set the icon.
	# Make sure to get the right path if we are in a cx_Freeze compiled executable.
	# See: http://cx-freeze.readthedocs.org/en/latest/faq.html#using-data-files
	datadir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
	icon_path = os.path.join(datadir, 'Icon', 'Icon.gif')
	img = TK.PhotoImage(file=icon_path)
	root.tk.call('wm', 'iconphoto', root._w, img)
	root.mainloop()

if __name__ == '__main__':
	main()
