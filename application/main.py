
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
except ImportError:  # Python 3.
	try:
		import tkinter as TK
		import tkinter.font as TK_FONT
		import tkinter.filedialog as tkFileDialog
		import tkinter.messagebox as tkMessageBox
		import tkinter.simpledialog as tkSimpleDialog
	except ImportError:
		raise ImportError('Tkinter not available.')

try:
	import ttk as TTK
except ImportError:  # Python 3.
	try:
		from tkinter import ttk as TTK
	except ImportError:
		raise ImportError('Ttk not available.')

import Flipper

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


render_lamination_FULL = 'Full'
render_lamination_W_TRAIN_TRACK = 'Weighted train track'
render_lamination_C_TRAIN_TRACK = 'Compressed train track'
label_edges_NONE = 'None'
label_edges_INDEX = 'Index'
label_edges_GEOMETRIC = 'Geometric'
size_SMALL = 10
size_MEDIUM = 12
size_LARGE = 14
#size_XLARGE = 16
#label_edges_ALGEBRAIC = 'Algebraic'

class Options(object):
	def __init__(self, parent):
		self.parent = parent
		self.custom_font = TK_FONT.Font(family='TkDefaultFont', size=10)
		
		self.render_lamination_var = TK.StringVar(value=render_lamination_FULL)
		self.show_internals_var = TK.BooleanVar(value=False)
		self.label_edges_var = TK.StringVar(value=label_edges_NONE)
		self.size_var = TK.IntVar(value=size_SMALL)
		
		self.render_lamination = render_lamination_FULL
		self.show_internals = False
		self.label_edges = label_edges_NONE
		self.line_size = 2
		self.dot_size = 3
		
		self.render_lamination_var.trace('w', self.update)
		self.show_internals_var.trace('w', self.update)
		self.label_edges_var.trace('w', self.update)
		self.size_var.trace('w', self.update)
		
		# Drawing parameters.
		self.epsilon = 10
		self.float_error = 0.001
		self.dilatation_error = 0.001
		self.spacing = 10
		
		self.vertex_buffer = 0.2  # Must be in (0,0.5)
		self.zoom_fraction = 0.9 # Must be in (0,1)
		
		self.default_vertex_colour = 'black'
		self.default_edge_colour = 'black'
		self.default_triangle_colour = 'gray80'
		self.default_curve_colour = 'grey40'
		self.default_selected_colour = 'red'
		self.default_edge_label_colour = 'red'
		self.default_curve_label_colour = 'black'
		
		self.version = Flipper.kernel.version.Flipper_version
	
	def update(self, *args):
		self.render_lamination = str(self.render_lamination_var.get())
		self.show_internals = bool(self.show_internals_var.get())
		self.label_edges = str(self.label_edges_var.get())
		self.line_size = int(self.size_var.get()) - 8
		self.dot_size = int(self.size_var.get()) - 7
		self.custom_font.configure(size=int(self.size_var.get()))
		self.parent.treeview_objects.tag_configure('txt', font=self.custom_font)

		self.parent.redraw()


class FlipperApp(object):
	def __init__(self, parent):
		self.parent = parent
		self.options = Options(self)
		
		self.panels = TK.PanedWindow(self.parent, orient='horizontal', relief='raised')

		self.frame_interface = TK.Frame(self.parent, width=50)
		###
		self.treeview_objects = TTK.Treeview(self.frame_interface, selectmode='browse')
		self.treeview_objects.pack(fill='both', expand=True)
		self.treeview_objects.bind('<Button-1>', self.treeview_objects_left_click)
		self.treeview_objects.bind('<Double-Button-1>', self.treeview_objects_double_left_click)
		###
		
		self.frame_draw = TK.Frame(self.parent)
		###
		# Now for some reason which I can't explain, we need this height=1 to prevent the command
		# bar below from collapsing when the application is small.
		self.canvas = TK.Canvas(self.frame_draw, height=1, bg='#dcecff')
		self.canvas.pack(fill='both', expand=True)
		self.canvas.bind('<Button-1>', self.canvas_left_click)
		self.canvas.bind('<Double-Button-1>', self.canvas_double_left_click)
		self.canvas.bind('<Button-3>', self.canvas_right_click)
		self.canvas.bind('<Motion>', self.canvas_move)
		
		self.frame_command = TK.Frame(self.parent)
		###
		self.label_command = TK.Label(self.frame_command, text='Command:', font=self.options.custom_font)
		self.label_command.pack(side='left')
		
		self.entry_command = TK.Entry(self.frame_command, text='', font=self.options.custom_font)
		self.entry_command.pack(side='left', fill='x', expand=True, padx=10, pady=2)
		self.entry_command.bind('<Return>', self.command_return)
		###
		
		self.panels.add(self.frame_interface)
		self.panels.add(self.frame_draw)
		self.panels.pack(fill='both', expand=True)
		self.frame_command.pack(fill='x', expand=False)
		
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
		
		settingsmenu = TK.Menu(menubar, tearoff=0)

		sizemenu = TK.Menu(menubar, tearoff=0)
		sizemenu.add_radiobutton(label='Small', var=self.options.size_var, value=size_SMALL)
		sizemenu.add_radiobutton(label='Medium', var=self.options.size_var, value=size_MEDIUM)
		sizemenu.add_radiobutton(label='Large', var=self.options.size_var, value=size_LARGE)
		# sizemenu.add_radiobutton(label='Extra large', var=self.options.size_var, value=size_XLARGE)

		edgelabelmenu = TK.Menu(menubar, tearoff=0)
		edgelabelmenu.add_radiobutton(label=label_edges_NONE, var=self.options.label_edges_var)
		edgelabelmenu.add_radiobutton(label=label_edges_INDEX, var=self.options.label_edges_var)
		edgelabelmenu.add_radiobutton(label=label_edges_GEOMETRIC, var=self.options.label_edges_var)
		# edgelabelmenu.add_radiobutton(label=label_edges_ALGEBRAIC, var=self.options.edge_labels_var)
		
		laminationdrawmenu = TK.Menu(menubar, tearoff=0)
		laminationdrawmenu.add_radiobutton(label=render_lamination_FULL, var=self.options.render_lamination_var)
		laminationdrawmenu.add_radiobutton(label=render_lamination_C_TRAIN_TRACK, var=self.options.render_lamination_var)
		# laminationdrawmenu.add_radiobutton(label=render_lamination_W_TRAIN_TRACK, var=self.options.render_lamination_var)

		settingsmenu.add_cascade(label='Sizes', menu=sizemenu)
		settingsmenu.add_cascade(label='Edge label', menu=edgelabelmenu)
		settingsmenu.add_cascade(label='Draw lamination', menu=laminationdrawmenu)
		settingsmenu.add_checkbutton(label='Show internal edges', var=self.options.show_internals_var)
		
		helpmenu = TK.Menu(menubar, tearoff=0)
		helpmenu.add_command(label='Help', command=self.show_help, accelerator='F1')
		helpmenu.add_separator()
		helpmenu.add_command(label='About', command=self.show_about)
		
		menubar.add_cascade(label='File', menu=filemenu)
		menubar.add_cascade(label='Settings', menu=settingsmenu)
		menubar.add_cascade(label='Help', menu=helpmenu)
		self.parent.config(menu=menubar)
		
		parent.bind('<%s-n>' % COMMAND_MODIFIER_BINDING, lambda event: self.initialise())
		parent.bind('<%s-o>' % COMMAND_MODIFIER_BINDING, lambda event: self.load())
		parent.bind('<%s-s>' % COMMAND_MODIFIER_BINDING, lambda event: self.save())
		parent.bind('<%s-w>' % COMMAND_MODIFIER_BINDING, lambda event: self.quit())
		parent.bind('<Key>', self.parent_key_press) 
		
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
		for child in self.treeview_objects.get_children(''):
			self.treeview_objects.delete(child)
		self.treeview_objects.insert('', 'end', 'curve', text='Curves:', open=True, tags=['txt', 'menu'])
		self.treeview_objects.insert('', 'end', 'mapping_class', text='Mapping Classes:', open=True, tags=['txt', 'menu'])
		self.treeview_objects.tag_configure('txt', font=self.options.custom_font)
		
		self.build_complete_structure()
		
		self.colour_picker = Flipper.application.pieces.ColourPalette()
		
		self.canvas.delete('all')
		self.entry_command.delete(0, TK.END)
		
		self.entry_command.focus()
	
	def add_curve(self, name):
		self.treeview_objects.insert('curve', 'end', text=name, tags=['txt', 'curve'])
	
	def add_mapping_class(self, name):
		iid = self.treeview_objects.insert('mapping_class', 'end', text=name, tags=['txt', 'mapping_class'])
		self.treeview_objects.insert(iid, 'end', text='Apply', tags=['txt', 'apply_mapping_class'])
		self.treeview_objects.insert(iid, 'end', text='Apply inverse', tags=['txt', 'apply_mapping_class_inverse'])
		self.treeview_objects.insert(iid, 'end', text='Order: ?', tags=['txt', 'mapping_class_order'])
		self.treeview_objects.insert(iid, 'end', text='Type: ??', tags=['txt', 'mapping_class_type'])
		# self.treeview_objects.insert(iid, 'end', text='Invariant lamination: ??', tags=['txt', 'mapping_class_invariant_lamination'])
	
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
				list_curves = [self.treeview_objects.item(child)['text'] for child in self.treeview_objects.get_children('curve')]
				list_mapping_classes = [self.treeview_objects.item(child)['text'] for child in self.treeview_objects.get_children('mapping_class')]
				
				pickle.dump([spec, vertices, edges, abstract_triangulation, curves, mapping_classes, list_curves, list_mapping_classes], open(path, 'wb'))
			except IOError:
				tkMessageBox.showwarning('Save Error', 'Could not open: %s' % path)
	
	def load(self, path=''):
		if path == '': path = tkFileDialog.askopenfilename(defaultextension='.flp', filetypes=[('Flipper files', '.flp'), ('all files', '.*')], title='Open Flipper File')
		if path != '':
			try:
				spec, vertices, edges, abstract_triangulation, curves, mapping_classes, list_curves, list_mapping_classes = pickle.load(open(path, 'rb'))
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

				for name in list_curves:
					self.add_curve(name)
				
				for name in list_mapping_classes:
					self.add_mapping_class(name)
				
				if self.is_complete():
					self.lamination_to_canvas(self.curves['_'])
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
					
					twist_names = [mapping_class for mapping_class, _ in twists]
					half_names = [mapping_class for mapping_class, _ in halfs]
					isom_names = [mapping_class for mapping_class, _ in isoms]
					
					example = '\n' + \
					'import Flipper\n' + \
					'\n' + \
					'def Example(word=None):\n' + \
					'	T = Flipper.AbstractTriangulation(%s)\n' % [triangle.edge_indices for triangle in self.abstract_triangulation] + \
					'	\n' + \
					''.join('\t%s = T.lamination(%s)\n' % (mapping_class, vector) for (mapping_class, vector) in twists) + \
					''.join('\t%s = T.lamination(%s)\n' % (mapping_class, vector) for (mapping_class, vector) in halfs) + \
					''.join('\t%s = Flipper.isometry_from_edge_map(T, T, %s).encode_isometry()\n' % (mapping_class, edge_map) for (mapping_class, edge_map) in isoms) + \
					'	\n' + \
					'	return build_mapping_class(T, Flipper.examples.abstracttriangulation.make_mapping_classes(%s, %s, %s), word)\n' % (twist_names, half_names, isom_names)
					
					example = example.replace("'", '')
					
					file.write(example)
				except IOError:
					tkMessageBox.showwarning('Export Error', 'Could not open: %s' % path)
				finally:
					file.close()
		else:
			tkMessageBox.showwarning('Export Error', 'Cannot export incomplete surface.')
			
	
	def quit(self):
		self.parent.quit()
	
	def show_help(self):
		datadir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
		file = os.path.join(datadir, 'docs', 'Flipper.pdf')
		if sys.platform.startswith('darwin'):
			command = 'open'
		elif sys.platform.startswith('win'):
			command = 'start'
		else:
			command = 'xdg-open'
		os.system(command + ' ' + file)
	
	def show_about(self):
		tkMessageBox.showinfo('About', 'Flipper (Version %s).\nCopyright (c) Mark Bell 2013.' % self.options.version)
	
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
		self.build_edge_labels()
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
				elif task == 'erase': self.destroy_curve()
				elif task == 'help': self.show_help()
				elif task == 'about': self.show_about()
				elif task == 'exit': self.quit()
				
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
				elif task == 'compose': self.store_composition(combined)
				elif task == 'apply': self.show_apply(combined)
				
				elif task == 'order': self.order(combined)
				elif task == 'type': self.NT_type(combined)
				elif task == 'lamination': self.invariant_lamination(combined)
				elif task == 'lamination_estimate': self.invariant_lamination(combined, exact=False)
				elif task == 'split': self.splitting_sequence(combined)
				elif task == 'bundle': self.build_bundle(combined)
				elif task == 'latex': self.latex(combined)
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
		self.build_edge_labels()
		# if self.is_complete(): self.lamination_to_canvas(self.curves['_'])

		for vertex in self.vertices:
			self.canvas.coords(vertex.drawn_self, vertex.x-self.options.dot_size, vertex.y-self.options.dot_size, vertex.x+self.options.dot_size, vertex.y+self.options.dot_size)
		self.canvas.itemconfig('line', width=self.options.line_size)
		self.canvas.itemconfig('curve', width=self.options.line_size)
		
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
		self.vertices.append(Flipper.application.pieces.Vertex(self.canvas, point, self.options))
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
		if any(Flipper.application.pieces.lines_intersect(edge.source_vertex, edge.target_vertex, v1, v2, self.options.float_error, True)[1] for edge in self.edges):
			return None
		
		e0 = Flipper.application.pieces.Edge(v1, v2, self.options)
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
		
		new_triangle = Flipper.application.pieces.Triangle(e1,e2,e3, self.options)
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
				self.destroy_edge_identification(edge)
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
	
	def create_curve_component(self, point, multiplicity=1):
		self.curve_components.append(Flipper.application.pieces.CurveComponent(self.canvas, point, self.options, multiplicity))
		return self.curve_components[-1]
	
	def destroy_curve_component(self, curve_component):
		for i in range(len(curve_component.vertices)):
			curve_component.pop_point()
		self.curve_components.remove(curve_component)
	
	def destroy_curve(self):
		while self.curve_components != []:
			self.destroy_curve_component(self.curve_components[-1])
		
		if self.is_complete():
			self.set_current_curve()
			self.select_object(None)
	
	
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
				if gluing[i] == gluing[j].swapcase():  # !?! Get rid of the swapcase()?
					self.create_edge_identification(self.edges[i], self.edges[j])
	
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
			lamination = self.curves['_']
			for edge in self.edges:
				self.canvas.create_text((edge.source_vertex[0] + edge.target_vertex[0]) / 2, (edge.source_vertex[1] + edge.target_vertex[1]) / 2, text=str(lamination[edge.index]), tag='edge_label', font=self.options.custom_font, fill=self.options.default_edge_label_colour)
		elif self.options.label_edges == 'Algebraic':
			pass  # !?! To do.
		elif self.options.label_edges == 'None':
			pass  # This is correct.
		else:
			raise ValueError()
	
	def destroy_edge_labels(self):
		self.canvas.delete('edge_label')

	def build_edge_labels(self):
		if self.is_complete():
			self.create_edge_labels()
		else:
			self.destroy_edge_labels()
	
	def create_abstract_triangulation(self):
		# Must start by calling self.set_edge_indices() so that self.zeta is correctly set.
		self.set_edge_indices()
		self.abstract_triangulation = Flipper.AbstractTriangulation([[triangle.edges[side].index for side in range(3)] for triangle in self.triangles])
		self.curves = {'_':self.abstract_triangulation.empty_lamination()}
		self.create_edge_labels()
	
	def destroy_abstract_triangulation(self):
		self.clear_edge_indices()
		self.destroy_edge_labels()
		self.destroy_curve()
		self.abstract_triangulation = None
		self.curves = {}
		self.mapping_classes = {}
		for child in self.treeview_objects.get_children('curves') + self.treeview_objects.get_children('mapping_class'):
			self.treeview_objects.delete(child)
	
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
				this_segment_meets = [(Flipper.application.pieces.lines_intersect(curve.vertices[i], curve.vertices[i+1], edge.source_vertex, edge.target_vertex, self.options.float_error, edge.equivalent_edge is None), edge.index) for edge in self.edges]
				for (d, double), index in sorted(this_segment_meets):
					if d >= -self.options.float_error:
						if len(meets) > 0 and meets[-1][0] == index:
							meets.pop()
						else:
							meets.append((index, double))
			
			for index, double in meets:
				vector[index] += (2 if double else 1) * curve.multiplicity
		
		return self.abstract_triangulation.lamination([i // 2 for i in vector])
	
	def lamination_to_canvas(self, lamination):
		self.destroy_curve()
		for triangle in self.triangles:
			weights = [lamination[edge.index] for edge in triangle.edges]
			dual_weights = [(weights[1] + weights[2] - weights[0]) / 2, (weights[2] + weights[0] - weights[1]) / 2, (weights[0] + weights[1] - weights[2]) / 2]
			for i in range(3):
				a = triangle.vertices[i-1] - triangle.vertices[i]
				b = triangle.vertices[i-2] - triangle.vertices[i]
				if self.options.render_lamination == render_lamination_C_TRAIN_TRACK:
					if dual_weights[i] > 0:
						scale = float(1) / 2
						start_point = triangle.vertices[i][0] + a[0] * scale, triangle.vertices[i][1] + a[1] * scale
						end_point = triangle.vertices[i][0] + b[0] * scale, triangle.vertices[i][1] + b[1] * scale
						self.create_curve_component(start_point).append_point(end_point)
				elif self.options.render_lamination == render_lamination_FULL:  # This is the slowest bit when the weight of the image curve is 10000.
					for j in range(int(dual_weights[i])):
						scale_a = float(1) / 2 if weights[i-2] == 1 else self.options.vertex_buffer + (1 - 2*self.options.vertex_buffer) * j / (weights[i-2] - 1)
						scale_b = float(1) / 2 if weights[i-1] == 1 else self.options.vertex_buffer + (1 - 2*self.options.vertex_buffer) * j / (weights[i-1] - 1)
						start_point = triangle.vertices[i][0] + a[0] * scale_a, triangle.vertices[i][1] + a[1] * scale_a
						end_point = triangle.vertices[i][0] + b[0] * scale_b, triangle.vertices[i][1] + b[1] * scale_b
						self.create_curve_component(start_point).append_point(end_point)
				elif self.options.render_lamination == render_lamination_W_TRAIN_TRACK:  # !?! To Do.
					pass
		
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
					self.add_curve(name)
					self.curves[name] = lamination
					self.destroy_curve()
				else:
					tkMessageBox.showwarning('Curve', 'Not an essential multicurve.')
	
	def store_twist(self, name):
		if self.is_complete():
			if valid_name(name):
				lamination = self.curves['_']
				if lamination.is_good_curve():
					self.add_curve(name)
					self.curves[name] = lamination
					self.add_mapping_class(name)
					self.mapping_classes[name] = (lamination.encode_twist(), ('twist', lamination, +1))
					self.mapping_classes[name.swapcase()] = (lamination.encode_twist(k=-1), ('twist', lamination, -1))
					self.destroy_curve()
				else:
					tkMessageBox.showwarning('Curve', 'Cannot twist about this, it is either a multicurve or a complementary region of it has no punctures.')
	
	def store_halftwist(self, name):
		if self.is_complete():
			if valid_name(name):
				lamination = self.curves['_']
				if lamination.is_pants_boundary():
					self.add_curve(name)
					self.curves[name] = lamination
					self.add_mapping_class(name)
					self.mapping_classes[name] = (lamination.encode_halftwist(), ('half', lamination, +1))
					self.mapping_classes[name.swapcase()] = (lamination.encode_halftwist(k=-1), ('half', lamination, -1))
					self.destroy_curve()
				else:
					tkMessageBox.showwarning('Curve', 'Not an essential curve bounding a pair of pants.')
	
	def store_isometry(self, specification):
		if self.is_complete():
			name, from_edges, to_edges = specification.split(' ')[:3]
			
			from_edges = [int(x) for x in from_edges.split('.')]
			to_edges = [int(x) for x in to_edges.split('.')]
			
			try:
				possible_isometry = [isom for isom in self.abstract_triangulation.all_isometries(self.abstract_triangulation) if all(isom.edge_map[from_edge] == to_edge for from_edge, to_edge in zip(from_edges, to_edges))]
				isometry = possible_isometry[0]
				mapping_class = isometry.encode_isometry()
				mapping_class_inverse = isometry.inverse().encode_isometry()
			except IndexError:
				tkMessageBox.showwarning('Isometry', 'Information does not specify an isometry.')
			else:
				if valid_name(name):
					self.add_mapping_class(name)
					self.mapping_classes[name] = (mapping_class, ('isometry', isometry, +1))
					self.mapping_classes[name.swapcase()] = (mapping_class_inverse, ('isometry', isometry, -1))

	def store_composition(self, composition):
		if self.is_complete():
			name, twists = composition.split(' ')
			if valid_name(name):
				self.add_mapping_class(name)
				self.mapping_classes[name] = (self.create_composition(twists.split('.')), ('composition', twists, +1))
				self.mapping_classes[name.swapcase()] = (self.create_composition(twists.swapcase().split('.')[::-1]), ('composition', twists, -1))
	
	def show_curve(self, name):
		if self.is_complete():
			if name in self.curves:
				self.destroy_curve()
				self.lamination_to_canvas(self.curves[name])
				self.set_current_curve(self.curves[name])
			else:
				tkMessageBox.showwarning('Curve', '%s is not a multicurve.' % name)
	
	def create_composition(self, twists):
		# Assumes that each of the named mapping classes exist. If not an
		# AssumptionError is thrown.
		if self.is_complete():
			mapping_class = self.abstract_triangulation.Id_EncodingSequence()
			for twist in twists[::-1]:
				if twist in self.mapping_classes:
					mapping_class = self.mapping_classes[twist][0] * mapping_class
				else:
					tkMessageBox.showwarning('Mapping class', 'Unknown mapping class: %s' % twist)
					raise Flipper.AssumptionError()
		
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
			except Flipper.AssumptionError:
				pass
			else:
				self.set_current_curve(mapping_class * curve)
				self.lamination_to_canvas(self.curves['_'])
	
	def show_render(self, composition):
		if self.is_complete():
			self.set_current_curve(self.abstract_triangulation.lamination([int(i) for i in composition.split('.')]))
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
			except Flipper.AssumptionError:
				pass
			else:
				order = mapping_class.order()
				if order == 0:
					tkMessageBox.showinfo('Order', '%s has infinite order.' % composition)
				else:
					tkMessageBox.showinfo('Order', '%s has order %s.' % (composition, order))
	
	def NT_type(self, composition):
		if self.is_complete():
			try:
				mapping_class = self.create_composition(composition.split('.'))
				progress_app=Flipper.application.progress.ProgressApp(self)
				NT_type = mapping_class.NT_type(progression=progress_app.update_bar)
				progress_app.cancel()
				
				if NT_type == Flipper.kernel.encoding.NT_TYPE_PERIODIC:
					tkMessageBox.showinfo('Periodic', '%s is periodic.' % composition)
				elif NT_type == Flipper.kernel.encoding.NT_TYPE_REDUCIBLE:
					tkMessageBox.showinfo('Periodic', '%s is reducible.' % composition)
				elif NT_type == Flipper.kernel.encoding.NT_TYPE_PSEUDO_ANOSOV:
					tkMessageBox.showinfo('Periodic', '%s is pseudo-Anosov.' % composition)
			except Flipper.AssumptionError:
				pass
			except Flipper.AbortError:
				pass
	
	
	######################################################################
	
	
	def invariant_lamination(self, composition, exact=True):
		if self.is_complete():
			try:
				mapping_class = self.create_composition(composition.split('.'))
			except Flipper.AssumptionError:
				pass
			else:
				try:
					lamination = mapping_class.invariant_lamination(exact)
					dilatation = mapping_class.dilatation(lamination)
				except Flipper.AssumptionError:
					tkMessageBox.showwarning('Lamination', 'Can not find any projectively invariant laminations of %s, it is periodic.' % composition)
				except Flipper.ComputationError:
					tkMessageBox.showwarning('Lamination', 'Could not find any projectively invariant laminations of %s. It is probably reducible.' % composition)
				except ImportError:
					tkMessageBox.showerror('Lamination', 'Can not compute projectively invariant laminations without a symbolic computation library.')
				else:
					tkMessageBox.showinfo('Lamination', '%s has projectively invariant lamination: %s \nwith dilatation: %s' % (composition, lamination, dilatation))
	
	def splitting_sequence(self, composition):
		if self.is_complete():
			try:
				mapping_class = self.create_composition(composition.split('.'))
			except Flipper.AssumptionError:
				pass
			else:
				try:
					lamination = mapping_class.invariant_lamination()
				except Flipper.AssumptionError:
					tkMessageBox.showinfo('Lamination', 'Can not find any projectively invariant laminations of %s, it is periodic.' % composition)
				except Flipper.ComputationError:
					tkMessageBox.showwarning('Lamination', 'Could not find any projectively invariant laminations of %s. It is probably reducible.' % composition)
				except ImportError:
					tkMessageBox.showerror('Lamination', 'Can not compute projectively invariant laminations without a symbolic computation library.')
				else:
					try:
						start_time = time()
						splitting = lamination.splitting_sequence()
					except Flipper.AssumptionError:
						tkMessageBox.showwarning('Lamination', '%s is reducible.' % composition)
					else:
						tkMessageBox.showinfo('Splitting sequence', 'Periodic splits: %s' % (len(splitting.flips)))
	
	def build_bundle(self, composition):
		if self.is_complete():
			path = tkFileDialog.asksaveasfilename(defaultextension='.tri', filetypes=[('SnapPy Files', '.tri'), ('all files', '.*')], title='Export SnapPy Triangulation')
			if path != '':
				try:
					file = open(path, 'w')
					try:
						mapping_class = self.create_composition(composition.split('.'))
					except Flipper.AssumptionError:
						pass
					else:
						try:
							lamination = mapping_class.invariant_lamination()
						except Flipper.AssumptionError:
							tkMessageBox.showwarning('Lamination', 'Can not find any projectively invariant laminations of %s, it is periodic.' % composition)
						except Flipper.ComputationError:
							tkMessageBox.showwarning('Lamination', 'Could not find any projectively invariant laminations of %s. It is probably reducible.' % composition)
						except ImportError:
							tkMessageBox.showerror('Lamination', 'Can not compute projectively invariant laminations without a symbolic computation library.')
						else:
							try:
								splitting = lamination.splitting_sequence()
							except Flipper.AssumptionError:
								tkMessageBox.showwarning('Lamination', '%s is reducible.' % composition)
							else:
								# There may be more than one isometry, for now let's just pick the first. We'll worry about this eventually.
								M = splitting.bundle(0, composition)
								file.write(M.SnapPy_string())
								description = 'It was built using the first of %d isometries.\n' % len(splitting.closing_isometries) + \
								'It has %d cusp(s) with the following properties (in order):\n' % M.num_cusps + \
								'Cusp types: %s\n' % M.cusp_types + \
								'Fibre slopes: %s\n' % M.fibre_slopes + \
								'Degeneracy slopes: %s\n' % M.degeneracy_slopes + \
								'To build this bundle I had to create some artificial punctures,\n' + \
								'these are the ones with puncture type 1.\n' + \
								'You should fill them with their fibre slope to get\n' + \
								'the manifold you were expecting.'
								tkMessageBox.showinfo('Bundle', description)
				except IOError:
					tkMessageBox.showwarning('Save Error', 'Could not write to: %s' % path)
				finally:
					file.close()
	
	def latex(self, composition):
		path = tkFileDialog.asksaveasfilename(defaultextension='.tex', filetypes=[('Tex / Latex document', '.tex'), ('all files', '.*')], title='Export Latex code')
		if path != '':
			try:
				file = open(path, 'w')
				try:
					mapping_class = self.create_composition(composition.split('.'))
				except Flipper.AssumptionError:
					pass
				else:
					s = '\\documentclass[a4paper]{article}\n'
					s += '\\usepackage{fullpage}\n'
					s += '\\usepackage{amsmath}\n'
					s += '\\allowdisplaybreaks\n'
					s += '\\begin{document}\n'
					s += 'The mapping class \\texttt{%s} on the triangulation\n' % composition
					s += '\\[ %s \\]\n' % ','.join(str(triangle.edge_indices) for triangle in self.abstract_triangulation)
					s += 'induces the PL--function\n'
					s += mapping_class.latex_string()
					s += '\\end{document}\n'
					
					with open('test.tex', 'w') as file:
						file.write(s)
			except IOError:
				tkMessageBox.showwarning('Save Error', 'Could not write to: %s' % path)
			finally:
				file.close()
	
	
	######################################################################
	
	
	def canvas_left_click(self, event):
		# Modifier keys. Originate from: http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
		BIT_SHIFT = 0x001; BIT_CAPSLOCK = 0x002; BIT_CONTROL = 0x004; BIT_LEFT_ALT = 0x008;
		BIT_NUMLOCK = 0x010; BIT_RIGHT_ALT = 0x080; BIT_MB_1 = 0x100; BIT_MB_2 = 0x200; BIT_MB_3 = 0x400;
		shift_pressed = (event.state & BIT_SHIFT) == BIT_SHIFT
		
		x, y = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))
		possible_object = self.object_here((x,y))
		
		if self.is_complete() and not shift_pressed:
			if self.selected_object is None:
				self.select_object(self.create_curve_component((x,y)))
				self.selected_object.append_point((x,y))
			elif isinstance(self.selected_object, Flipper.application.pieces.CurveComponent):
				self.selected_object.append_point((x,y))
				self.set_current_curve()
		else:
			if self.selected_object is None:
				if possible_object is None:
					self.select_object(self.create_vertex((x,y)))
				elif isinstance(possible_object, Flipper.application.pieces.Edge):
					self.destroy_edge_identification(possible_object)
					if possible_object.free_sides() > 0:
						self.select_object(possible_object)
				elif isinstance(possible_object, Flipper.application.pieces.Vertex):
					self.select_object(possible_object)
			elif isinstance(self.selected_object, Flipper.application.pieces.Vertex):
				if possible_object == self.selected_object:
					self.select_object(None)
				elif possible_object is None:
					new_vertex = self.create_vertex((x,y))
					self.create_edge(self.selected_object, new_vertex)
					self.select_object(new_vertex)
				elif isinstance(possible_object, Flipper.application.pieces.Vertex):
					self.create_edge(self.selected_object, possible_object)
					self.select_object(possible_object)
				elif isinstance(possible_object, Flipper.application.pieces.Edge):
					if possible_object.free_sides() > 0:
						self.select_object(possible_object)
			elif isinstance(self.selected_object, Flipper.application.pieces.Edge):
				if possible_object == self.selected_object:
					self.select_object(None)
				elif possible_object is None:
					new_vertex = self.create_vertex((x,y))
					self.create_edge(self.selected_object.source_vertex, new_vertex)
					self.create_edge(self.selected_object.target_vertex, new_vertex)
					self.select_object(None)
				elif isinstance(possible_object, Flipper.application.pieces.Vertex):
					if possible_object != self.selected_object.source_vertex and possible_object != self.selected_object.target_vertex:
						self.create_edge(self.selected_object.source_vertex, possible_object)
						self.create_edge(self.selected_object.target_vertex, possible_object)
						self.select_object(None)
					else:
						self.select_object(possible_object)
				elif isinstance(possible_object, Flipper.application.pieces.Edge):
					if (self.selected_object.free_sides() == 1 or self.selected_object.equivalent_edge is not None) and (possible_object.free_sides() == 1 or possible_object.equivalent_edge is not None):
						self.destroy_edge_identification(self.selected_object)
						self.destroy_edge_identification(possible_object)
						self.create_edge_identification(self.selected_object, possible_object)
						self.select_object(None)
					else:
						self.select_object(possible_object)
	
	def canvas_right_click(self, event):
		if self.selected_object is not None:
			if isinstance(self.selected_object, Flipper.application.pieces.CurveComponent):
				self.selected_object.pop_point()
			self.select_object(None)
	
	def canvas_double_left_click(self, event):
		return self.canvas_right_click(event)
	
	def canvas_move(self, event):
		x, y = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))
		if isinstance(self.selected_object, Flipper.application.pieces.CurveComponent):
			self.selected_object.move_last_point((x,y))
	
	def parent_key_press(self, event):
		key = event.keysym
		if key in ('Delete', 'BackSpace'):
			if isinstance(self.selected_object, Flipper.application.pieces.Vertex):
				self.destroy_vertex(self.selected_object)
				self.select_object(None)
			elif isinstance(self.selected_object, Flipper.application.pieces.Edge):
				self.destroy_edge(self.selected_object)
				self.select_object(None)
			elif isinstance(self.selected_object, Flipper.application.pieces.CurveComponent):
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
			self.canvas_right_click(event)
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
		elif key == 'F5':
			self.destroy_curve()
		elif key == 'Prior':
			self.zoom_centre(1.05)
		elif key == 'Next':
			self.zoom_centre(0.95)
	
	def treeview_objects_left_click(self, event):
		iid = self.treeview_objects.identify('row', event.x, event.y)
		tags = self.treeview_objects.item(iid, 'tags')

		name = self.treeview_objects.item(iid, 'text')
		parent_name = self.treeview_objects.item(self.treeview_objects.parent(iid), 'text')
		if 'curve' in tags:
			self.show_curve(name)
		elif 'apply_mapping_class' in tags:
			self.show_apply(parent_name)
		elif 'apply_mapping_class_inverse' in tags:
			self.show_apply(parent_name.swapcase())
		else:
			pass  # !?! To do.
	
	def treeview_objects_double_left_click(self, event):
		self.treeview_objects_left_click(event)
		iid = self.treeview_objects.identify('row', event.x, event.y)
		tags = self.treeview_objects.item(iid, 'tags')

		name = self.treeview_objects.item(iid, 'text')
		parent_name = self.treeview_objects.item(self.treeview_objects.parent(iid), 'text')
		if 'mapping_class_order' in tags:
			mapping_class = self.mapping_classes[parent_name][0]
			order = mapping_class.order()
			self.treeview_objects.item(iid, text='Order: %s' % ('Infinite' if order == 0 else str(order)))
		if 'mapping_class_type' in tags:
			mapping_class = self.mapping_classes[parent_name][0]
			try:
				progress_app = Flipper.application.progress.ProgressApp(self)
				self.treeview_objects.item(iid, text='Type: %s' % mapping_class.NT_type(progression=progress_app.update_bar))
				progress_app.cancel()
			except Flipper.AbortError:
				pass
		if 'mapping_class_invariant_lamination' in tags:
			try:
				mapping_class = self.mapping_classes[parent_name][0]
				lamination = mapping_class.invariant_lamination()
				self.treeview_objects.item(iid, text='Invariant lamination')
				self.lamination_to_canvas(lamination)
			except Flipper.ComputationError:
				pass
			except Flipper.AssumptionError:
				pass
		else:
			pass  # !?! To do.


def main(load_path=None):
	root = TK.Tk()
	root.title('Flipper')
	flipper = FlipperApp(root)
	root.minsize(300, 300)
	root.geometry('700x500')
	if load_path is not None: flipper.load(load_path)
	# Set the icon.
	# Make sure to get the right path if we are in a cx_Freeze compiled executable.
	# See: http://cx-freeze.readthedocs.org/en/latest/faq.html#using-data-files
	datadir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
	icon_path = os.path.join(datadir, 'icon', 'icon.gif')
	img = TK.PhotoImage(file=icon_path)
	root.tk.call('wm', 'iconphoto', root._w, img)
	root.mainloop()

if __name__ == '__main__':
	main()
