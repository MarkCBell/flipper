
import re
import os
import sys
import pickle
import string
from math import sin, cos, pi
from itertools import combinations
try:
	import Tkinter as TK
	import tkFont as TK_FONT
	import tkFileDialog
	import tkMessageBox
	# import tkSimpleDialog
except ImportError:  # Python 3.
	try:
		import tkinter as TK
		import tkinter.font as TK_FONT
		import tkinter.filedialog as tkFileDialog
		import tkinter.messagebox as tkMessageBox
		# import tkinter.simpledialog as tkSimpleDialog
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
import Flipper.application

# Some constants.
COMMAND_MODIFIERS = {'darwin':'Command', 'win32':'Ctrl', 'linux2':'Ctrl', 'linux3':'Ctrl'}
COMMAND_MODIFIER = COMMAND_MODIFIERS[sys.platform] if sys.platform in COMMAND_MODIFIERS else 'Ctrl'
COMMAND_MODIFIER_BINDINGS = {'darwin':'Command', 'win32':'Control', 'linux2':'Control', 'linux3':'Control'}
COMMAND_MODIFIER_BINDING = COMMAND_MODIFIER_BINDINGS[sys.platform] if sys.platform in COMMAND_MODIFIER_BINDINGS else 'Control'

# Event modifier keys. Originate from: http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
BIT_SHIFT = 0x001
# BIT_CAPSLOCK = 0x002
# BIT_CONTROL = 0x004
# BIT_LEFT_ALT = 0x008
# BIT_NUMLOCK = 0x010
# BIT_RIGHT_ALT = 0x080
# BIT_MB_1 = 0x100
# BIT_MB_2 = 0x200
# BIT_MB_3 = 0x400

DEFAULT_EDGE_LABEL_COLOUR = 'red'
DEFAULT_SELECTED_COLOUR = 'red'
MAX_DRAWABLE = 1000  # Maximum weight of a multicurve to draw fully.

class FlipperApp(object):
	def __init__(self, parent):
		self.parent = parent
		self.options = Flipper.application.Options(self)
		self.colour_picker = Flipper.application.ColourPalette()
		
		self.panels = TK.PanedWindow(self.parent, orient='horizontal', relief='raised')
		
		self.frame_interface = TK.Frame(self.parent)
		###
		TTK.Style().configure('Treeview', font=self.options.application_font)
		self.treeview_objects = TTK.Treeview(self.frame_interface, selectmode='browse')
		self.treeview_objects.heading('#0', text='Objects:', anchor='w')
		self.scrollbar_treeview = TK.Scrollbar(self.frame_interface, orient='vertical', command=self.treeview_objects.yview)
		self.treeview_objects.configure(yscroll=self.scrollbar_treeview.set)
		self.treeview_objects.bind('<Button-1>', self.treeview_objects_left_click)
		self.treeview_objects.bind('<Double-Button-1>', self.treeview_objects_double_left_click)
		self.treeview_objects.tag_configure('txt', font=self.options.application_font)
		self.treeview_objects.tag_configure('Heading', font=self.options.application_font)
		
		self.treeview_objects.grid(row=0, column=0, sticky='nesw')
		self.scrollbar_treeview.grid(row=0, column=1, sticky='nws')
		self.frame_interface.grid_rowconfigure(0, weight=1)
		self.frame_interface.grid_columnconfigure(0, weight=1)
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
		
		self.panels.add(self.frame_interface, width=260)  # Make sure to set an inital width.
		self.panels.add(self.frame_draw)
		self.panels.pack(fill='both', expand=True)
		self.frame_command.pack(fill='x', expand=False)
		
		###
		
		# Create the menus.
		# Make sure to start the Lamination and Mapping class menus disabled.
		self.menubar = TK.Menu(self.parent)
		app_font = self.options.application_font  # Get a shorter name.
		
		self.filemenu = TK.Menu(self.menubar, tearoff=0)
		self.filemenu.add_command(label='New', command=self.initialise, accelerator='%s+N' % COMMAND_MODIFIER, font=app_font)
		self.filemenu.add_command(label='Open', command=self.load, accelerator='%s+O' % COMMAND_MODIFIER, font=app_font)
		self.filemenu.add_command(label='Save', command=self.save, accelerator='%s+S' % COMMAND_MODIFIER, font=app_font)
		self.exportmenu = TK.Menu(self.menubar, tearoff=0)
		self.exportmenu.add_command(label='Export script', command=self.export_script, font=app_font)
		self.exportmenu.add_command(label='Export image', command=self.export_image, font=app_font)
		self.filemenu.add_cascade(label='Export', menu=self.exportmenu, font=app_font)
		self.filemenu.add_separator()
		self.filemenu.add_command(label='Exit', command=self.quit, accelerator='%s+W' % COMMAND_MODIFIER, font=app_font)
		self.menubar.add_cascade(label='File', menu=self.filemenu, font=app_font)
		
		self.surfacemenu = TK.Menu(self.menubar, tearoff=0)
		self.surfacemenu.add_command(label='Create ngon', command=self.initialise_circular_n_gon, font=app_font)
		self.surfacemenu.add_command(label='Create radial ngon', command=self.initialise_radial_n_gon, font=app_font)
		self.surfacemenu.add_command(label='Information', command=self.show_surface_information, font=app_font)
		self.surfacemenu.add_command(label='Zoom', command=self.auto_zoom, font=app_font)
		self.menubar.add_cascade(label='Surface', menu=self.surfacemenu, font=app_font)
		
		self.laminationmenu = TK.Menu(self.menubar, tearoff=0)
		self.laminationmenu.add_command(label='Store', command=self.store_lamination, accelerator='%s+L' % COMMAND_MODIFIER, font=app_font)
		self.laminationmenu.add_command(label='Tighten', command=self.tighten_lamination, font=app_font)
		self.laminationmenu.add_command(label='Erase', command=self.destroy_lamination, accelerator='F5', font=app_font)
		self.menubar.add_cascade(label='Lamination', menu=self.laminationmenu, state='disabled', font=app_font)
		
		self.mappingclassmenu = TK.Menu(self.menubar, tearoff=0)
		self.storemappingclassmenu = TK.Menu(self.menubar, tearoff=0)
		self.storemappingclassmenu.add_command(label='Twist', command=self.store_twist, accelerator='%s+T' % COMMAND_MODIFIER, font=app_font)
		self.storemappingclassmenu.add_command(label='Half twist', command=self.store_halftwist, accelerator='%s+H' % COMMAND_MODIFIER, font=app_font)
		self.storemappingclassmenu.add_command(label='Isometry', command=self.store_isometry, accelerator='%s+I' % COMMAND_MODIFIER, font=app_font)
		self.storemappingclassmenu.add_command(label='Composition', command=self.store_composition, accelerator='%s+M' % COMMAND_MODIFIER, font=app_font)
		self.mappingclassmenu.add_cascade(label='Store...', menu=self.storemappingclassmenu, font=app_font)
		self.mappingclassmenu.add_command(label='Apply', command=self.show_apply, font=app_font)
		self.mappingclassmenu.add_command(label='Order', command=self.order, font=app_font)
		self.mappingclassmenu.add_command(label='Type', command=self.NT_type, font=app_font)
		self.mappingclassmenu.add_command(label='Invariant lamination', command=self.invariant_lamination, font=app_font)
		self.mappingclassmenu.add_command(label='Build bundle', command=self.build_bundle, font=app_font)
		self.menubar.add_cascade(label='Mapping class', menu=self.mappingclassmenu, state='disabled', font=app_font)
		
		##########################################
		self.settingsmenu = TK.Menu(self.menubar, tearoff=0)
		
		self.sizemenu = TK.Menu(self.menubar, tearoff=0)
		self.sizemenu.add_radiobutton(label='Small', var=self.options.size_var, value=Flipper.application.options.SIZE_SMALL, font=app_font)
		self.sizemenu.add_radiobutton(label='Medium', var=self.options.size_var, value=Flipper.application.options.SIZE_MEDIUM, font=app_font)
		self.sizemenu.add_radiobutton(label='Large', var=self.options.size_var, value=Flipper.application.options.SIZE_LARGE, font=app_font)
		# self.sizemenu.add_radiobutton(label='Extra large', var=self.options.size_var, value=Flipper.application.options.SIZE_XLARGE, font=app_font)
		
		self.edgelabelmenu = TK.Menu(self.menubar, tearoff=0)
		self.edgelabelmenu.add_radiobutton(label=Flipper.application.options.LABEL_EDGES_NONE, var=self.options.label_edges_var, font=app_font)
		self.edgelabelmenu.add_radiobutton(label=Flipper.application.options.LABEL_EDGES_INDEX, var=self.options.label_edges_var, font=app_font)
		self.edgelabelmenu.add_radiobutton(label=Flipper.application.options.LABEL_EDGES_GEOMETRIC, var=self.options.label_edges_var, font=app_font)
		# self.edgelabelmenu.add_radiobutton(label=Flipper.application.options.LABEL_EDGES_ALGEBRAIC, var=self.options.edge_labels_var, font=app_font)
		
		self.laminationdrawmenu = TK.Menu(self.menubar, tearoff=0)
		self.laminationdrawmenu.add_radiobutton(label=Flipper.application.options.RENDER_LAMINATION_FULL, var=self.options.render_lamination_var, font=app_font)
		self.laminationdrawmenu.add_radiobutton(label=Flipper.application.options.RENDER_LAMINATION_C_TRAIN_TRACK, var=self.options.render_lamination_var, font=app_font)
		self.laminationdrawmenu.add_radiobutton(label=Flipper.application.options.RENDER_LAMINATION_W_TRAIN_TRACK, var=self.options.render_lamination_var, font=app_font)
		
		self.settingsmenu.add_cascade(label='Sizes', menu=self.sizemenu, font=app_font)
		self.settingsmenu.add_cascade(label='Edge label', menu=self.edgelabelmenu, font=app_font)
		self.settingsmenu.add_cascade(label='Draw lamination', menu=self.laminationdrawmenu, font=app_font)
		self.settingsmenu.add_checkbutton(label='Show internal edges', var=self.options.show_internals_var, font=app_font)
		self.menubar.add_cascade(label='Settings', menu=self.settingsmenu, font=app_font)
		
		self.helpmenu = TK.Menu(self.menubar, tearoff=0)
		self.helpmenu.add_command(label='Help', command=self.show_help, accelerator='F1', font=app_font)
		self.helpmenu.add_separator()
		self.helpmenu.add_command(label='About', command=self.show_about, font=app_font)
		
		self.menubar.add_cascade(label='Help', menu=self.helpmenu, font=app_font)
		self.parent.config(menu=self.menubar)
		
		self.parent.bind('<%s-n>' % COMMAND_MODIFIER_BINDING, lambda event: self.initialise())
		self.parent.bind('<%s-o>' % COMMAND_MODIFIER_BINDING, lambda event: self.load())
		self.parent.bind('<%s-s>' % COMMAND_MODIFIER_BINDING, lambda event: self.save())
		self.parent.bind('<%s-w>' % COMMAND_MODIFIER_BINDING, lambda event: self.quit())
		self.parent.bind('<%s-l>' % COMMAND_MODIFIER_BINDING, lambda event: self.store_lamination())
		self.parent.bind('<%s-t>' % COMMAND_MODIFIER_BINDING, lambda event: self.store_twist())
		self.parent.bind('<%s-h>' % COMMAND_MODIFIER_BINDING, lambda event: self.store_halftwist())
		self.parent.bind('<%s-m>' % COMMAND_MODIFIER_BINDING, lambda event: self.store_composition())
		self.parent.bind('<Key>', self.parent_key_press)
		
		self.parent.protocol('WM_DELETE_WINDOW', self.quit)
		
		self.unsaved_work = False
		
		self.vertices = []
		self.edges = []
		self.triangles = []
		self.curve_components = []
		self.train_track_blocks = []
		
		self.zeta = 0
		self.abstract_triangulation = None
		self.current_lamination = None
		self.laminations = {}
		self.lamination_names = {}
		self.mapping_classes = {}
		self.mapping_class_names = {}
		# We will cache properties of laminations and mapping classes.
		# The rule is that we will cache anything that we cannot compute in
		# polynomial time.
		self.cache = {}
		
		self.selected_object = None
	
	def initialise(self):
		if self.unsaved_work:
			result = tkMessageBox.showwarning('Unsaved work', 'Save before unsaved work is lost?', type='yesnocancel')
			if (result == 'yes' and not self.save()) or result == 'cancel':
				return False
		
		self.select_object(None)
		self.destroy_all_vertices()
		self.colour_picker.reset()
		
		self.unsaved_work = False
		return True
	
	def valid_name(self, strn):
		# A name is valid if it consists of letters, numbers, underscores and starts with a letter.
		if not strn or strn[0] not in string.ascii_letters or any(x not in (string.ascii_letters + string.digits + '_') for x in strn):
			tkMessageBox.showerror('Name', 'Not a valid name. A valid name must start with a letter and contain only letters, numbers and underscores.')
			return False
		
		return True
	
	def valid_specification(self, strn):
		# A specification is valid if it is non-empty and consists of letter.
		if not strn or any(x not in string.ascii_letters for x in strn):
			tkMessageBox.showerror('Specification', 'Not a valid specification. A valid specification name must contain only letters.')
			return False
		
		return True
	
	def valid_isometry(self, strn):
		# A isometry is valid if it matched 'num:num num:num num:num'.
		if re.match(r'\d+:\d+ \d+:\d+ \d+:\d+', strn) is None:
			tkMessageBox.showerror('Isometry', 'Not a valid isometry specification. A valid specification must be of the form "<num>:<num> <num>:<num> <num>:<num>".')
			return False
		
		return True
	
	def valid_composition(self, strn):
		# A composition is valid if it is a list of mapping class names and inverse names separated by periods.
		if any(x not in self.mapping_classes for x in strn.split('.')):
			tkMessageBox.showerror('Composition', 'Not a valid composition. A valid composition must consist of mapping class names and inverse names separated by periods.')
			return False
		
		return True
	
	def add_lamination(self, lamination, name):
		if name in self.laminations:
			self.treeview_objects.delete(*[child for child in self.treeview_objects.get_children('laminations') if self.lamination_names[child] == name])
		
		iid = self.treeview_objects.insert('laminations', 'end', text=name, tags=['txt', 'lamination'])
		self.laminations[name] = lamination
		self.lamination_names[iid] = name
		multicurve_string = lamination.is_multicurve()
		twistable_string = lamination.is_twistable()
		halftwistable_string = lamination.is_halftwistable()
		filling_string = '??' if not multicurve_string else 'False'
		
		# Set up all the properties to appear under this label.
		# We will also set up self.lamination_names to point each item under this to <name> too.
		tagged_actions = [
			('Show', 'show_lamination'),
			]
		for label, tag in tagged_actions:
			self.lamination_names[self.treeview_objects.insert(iid, 'end', text=label, tags=['txt', tag])] = name
		
		iid_properties = self.treeview_objects.insert(iid, 'end', text='Properties', tags=['txt'])
		tagged_properties = [
			('Multicurve: %s' %multicurve_string, 'multicurve_lamination'),
			('Twistable: %s' % twistable_string, 'twist_lamination'),
			('Half twistable: %s' % halftwistable_string, 'half_twist_lamination'),
			('Filling: %s' % filling_string, 'filling_lamination')
			]
		for label, tag in tagged_properties:
			self.lamination_names[self.treeview_objects.insert(iid_properties, 'end', text=label, tags=['txt', tag])] = name
		
		self.cache[lamination] = {}
		
		self.unsaved_work = True
	
	def add_mapping_class(self, mapping_class, name):
		name_inverse = name.swapcase()
		if name in self.mapping_classes:
			self.treeview_objects.delete(*[child for child in self.treeview_objects.get_children('mapping_classes') if self.mapping_class_names[child] in [name, name_inverse]])
		
		iid = self.treeview_objects.insert('mapping_classes', 'end', text=name, tags=['txt', 'mapping_class'])
		self.mapping_classes[name] = mapping_class
		self.mapping_classes[name_inverse] = mapping_class.inverse()
		self.mapping_class_names[iid] = name
		order = mapping_class.order()
		order_string = 'Infinite' if order == 0 else str(order)
		type_string = '?' if order == 0 else 'Periodic'
		invariant_string = '??' if order == 0 else 'x'
		
		# Set up all the properties to appear under this label.
		# We will also set up self.mapping_class_names to point each item under this to <name> too.
		tagged_actions = [
			('Apply', 'apply_mapping_class'),
			('Apply inverse', 'apply_mapping_class_inverse'),
			]
		for label, tag in tagged_actions:
			self.mapping_class_names[self.treeview_objects.insert(iid, 'end', text=label, tags=['txt', tag])] = name
		
		iid_properties = self.treeview_objects.insert(iid, 'end', text='Properties', tags=['txt'])
		tagged_properties = [
			('Order: %s' % order_string, 'mapping_class_order'),
			('Type: %s' % type_string, 'mapping_class_type'),
			('Invariant lamination: %s' % invariant_string, 'mapping_class_invariant_lamination')
			]
		for label, tag in tagged_properties:
			self.mapping_class_names[self.treeview_objects.insert(iid_properties, 'end', text=label, tags=['txt', tag])] = name
		
		self.cache[mapping_class] = {}
		
		self.unsaved_work = True
	
	def save(self):
		path = tkFileDialog.asksaveasfilename(defaultextension='.flp', filetypes=[('Flipper files', '.flp'), ('all files', '.*')], title='Save Flipper File')
		if path != '':
			try:
				spec = 'A Flipper file.'
				version = self.options.version
				vertices = [(vertex[0], vertex[1]) for vertex in self.vertices]
				edges = [(self.vertices.index(edge[0]), self.vertices.index(edge[1]), self.edges.index(edge.equivalent_edge) if edge.equivalent_edge is not None else None) for edge in self.edges]
				abstract_triangulation = self.abstract_triangulation
				lamination_names = [self.treeview_objects.item(child)['text'] for child in self.treeview_objects.get_children('laminations')]
				mapping_class_names = [self.treeview_objects.item(child)['text'] for child in self.treeview_objects.get_children('mapping_classes')]
				laminations = self.laminations
				mapping_classes = self.mapping_classes
				cache = self.cache
				data = (vertices, edges, abstract_triangulation, lamination_names, mapping_class_names, laminations, mapping_classes, cache)
				
				pickle.dump((spec, version, data), open(path, 'wb'))
				self.unsaved_work = False
				return True
			except IOError:
				tkMessageBox.showwarning('Save Error', 'Could not open: %s' % path)
		
		return False
	
	def load(self):
		path = tkFileDialog.askopenfilename(defaultextension='.flp', filetypes=[('Flipper files', '.flp'), ('all files', '.*')], title='Open Flipper File')
		if path != '':
			try:
				spec, version, data =  pickle.load(open(path, 'rb'))
				if Flipper.version.version_tuple(version) != Flipper.version.version_tuple(self.option.version):
					raise ValueError('Wrong version of Flipper.')
				else:
					(vertices, edges, abstract_triangulation) = data[0:3]
					(lamination_names, mapping_class_names, laminations) = data[3:6]
					(mapping_classes, cache) = data[6:9]
					if self.initialise():
						if spec != 'A Flipper file.':
							raise ValueError('Not a valid specification.')
						
						for vertex in vertices:
							self.create_vertex(vertex)
						
						for edge in edges:
							start_index, end_index, glued_to_index = edge
							self.create_edge(self.vertices[start_index], self.vertices[end_index])
						
						for index, edge in enumerate(edges):
							start_index, end_index, glued_to_index = edge
							if glued_to_index is not None and glued_to_index > index:
								self.create_edge_identification(self.edges[index], self.edges[glued_to_index])
						
						self.abstract_triangulation = abstract_triangulation
						
						for name in lamination_names:
							self.add_lamination(laminations[name], name)
						
						for name in mapping_class_names:
							self.add_mapping_class(mapping_classes[name], name)
						
						self.cache = cache
						
						self.unsaved_work = False
			except IOError:
				tkMessageBox.showwarning('Load Error', 'Could not open: %s' % path)
			except ValueError:
				tkMessageBox.showerror('Load Error', '%s is not a Flipper %s file.' % (path, self.options.version))
	
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
					disk_file = open(path, 'w')
					
					twists = [(mapping_class, self.mapping_classes[mapping_class][1][1].vector) for mapping_class in self.mapping_classes if self.mapping_classes[mapping_class][1][0] == 'twist' and self.mapping_classes[mapping_class][1][2] == +1]
					halfs = [(mapping_class, self.mapping_classes[mapping_class][1][1].vector) for mapping_class in self.mapping_classes if self.mapping_classes[mapping_class][1][0] == 'half' and self.mapping_classes[mapping_class][1][2] == +1]
					isoms = [(mapping_class, self.mapping_classes[mapping_class][1][1].edge_map) for mapping_class in self.mapping_classes if self.mapping_classes[mapping_class][1][0] == 'isometry' and self.mapping_classes[mapping_class][1][2] == +1]
					
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
					
					disk_file.write(example)
				except IOError:
					tkMessageBox.showwarning('Export Error', 'Could not open: %s' % path)
				finally:
					disk_file.close()
		else:
			tkMessageBox.showwarning('Export Error', 'Cannot export incomplete surface.')
	
	def quit(self):
		if self.initialise():
			self.parent.quit()
	
	def show_help(self):
		datadir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
		disk_file = os.path.join(datadir, 'docs', 'Flipper.pdf')
		if sys.platform.startswith('darwin'):
			command = 'open'
		elif sys.platform.startswith('win'):
			command = 'start'
		else:
			command = 'xdg-open'
		os.system(command + ' ' + disk_file)
	
	def show_about(self):
		tkMessageBox.showinfo('About', 'Flipper (Version %s).\nCopyright (c) Mark Bell 2013.' % self.options.version)
	
	def translate(self, dx, dy):
		for vertex in self.vertices:
			vertex[0] = vertex[0] + dx
			vertex[1] = vertex[1] + dy
		
		for curve_component in self.curve_components + self.train_track_blocks:
			for i in range(len(curve_component.vertices)):
				curve_component.vertices[i] = curve_component.vertices[i][0] + dx, curve_component.vertices[i][1] + dy
		
		self.canvas.move('all', dx, dy)
	
	def zoom(self, scale):
		for vertex in self.vertices:
			vertex[0], vertex[1] = scale * vertex[0], scale * vertex[1]
			vertex.update()
		for edge in self.edges:
			edge.update()
		for triangle in self.triangles:
			triangle.update()
		for curve_component in self.curve_components + self.train_track_blocks:
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
	
	def object_here(self, p):
		for piece in self.vertices + self.edges + self.triangles:
			if p in piece:
				return piece
		return None
	
	def redraw(self):  # !?! To do.
		self.build_edge_labels()
		
		for vertex in self.vertices:
			vertex.update()
		self.canvas.itemconfig('line', width=self.options.line_size)
		self.canvas.itemconfig('curve', width=self.options.line_size)
		
		for edge in self.edges:
			edge.hide(not self.options.show_internals and edge.is_internal())
		self.canvas.tag_raise('polygon')
		self.canvas.tag_raise('line')
		self.canvas.tag_raise('oval')
		self.canvas.tag_raise('train_track')
		self.canvas.tag_raise('curve')
		self.canvas.tag_raise('label')
		self.canvas.tag_raise('edge_label')
	
	def select_object(self, selected_object):
		self.selected_object = selected_object
		for x in self.vertices + self.edges + self.curve_components + self.train_track_blocks:
			x.set_current_colour()
		if self.selected_object is not None:
			self.selected_object.set_current_colour(DEFAULT_SELECTED_COLOUR)
	
	
	######################################################################
	
	
	def initialise_radial_n_gon(self):
		gluing = Flipper.application.get_input('Surface specification', 'New specification for radial ngon:', validate=self.valid_specification)
		if gluing is not None:
			if self.initialise():
				n = len(gluing)
				w = int(self.canvas.winfo_width())
				h = int(self.canvas.winfo_height())
				r = min(w, h) * (1 + self.options.zoom_fraction) / 4
				
				self.create_vertex((w / 2, h / 2))
				for i in range(n):
					self.create_vertex((w / 2 + sin(2*pi*(i+0.5) / n) * r, h / 2 + cos(2*pi*(i+0.5) / n) * r))
				for i in range(1, n):
					self.create_edge(self.vertices[i], self.vertices[i+1])
				self.create_edge(self.vertices[n], self.vertices[1])
				for i in range(n):
					self.create_edge(self.vertices[0], self.vertices[i+1])
				for i, j in combinations(range(n), r=2):
					if gluing[i] == gluing[j].swapcase():
						self.create_edge_identification(self.edges[i], self.edges[j])
				
				self.unsaved_work = True
	
	def initialise_circular_n_gon(self):
		gluing = Flipper.application.get_input('Surface specification', 'New specification for ngon:', validate=self.valid_specification)
		if gluing is not None:
			if self.initialise():
				n = len(gluing)
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
				
				for i, j in combinations(range(n), r=2):
					if gluing[i] == gluing[j].swapcase():  # !?! Get rid of the swapcase()?
						self.create_edge_identification(self.edges[i], self.edges[j])
				
				self.unsaved_work = True
	
	def show_surface_information(self):
		if self.is_complete():
			num_marked_points = self.abstract_triangulation.num_vertices
			Euler_characteristic = self.abstract_triangulation.Euler_characteristic
			genus = (2 - Euler_characteristic - num_marked_points) // 2
			tkMessageBox.showinfo('Surface information', 'Underlying surface has genus %d and %d marked point(s). (Euler characteristic %d.)' % (genus, num_marked_points, Euler_characteristic))
		else:
			tkMessageBox.showwarning('Surface information', 'Cannot compute information about an incomplete surface.')
	
	
	######################################################################
	
	
	def create_vertex(self, point):
		self.vertices.append(Flipper.application.Vertex(self.canvas, point, self.options))
		self.unsaved_work = True
		self.redraw()
		self.build_abstract_triangulation()
		return self.vertices[-1]
	
	def destroy_vertex(self, vertex=None):
		if vertex is None: vertex = self.vertices[-1]
		while True:
			for edge in self.edges:
				if edge[0] == vertex or edge[1] == vertex:
					self.destroy_edge(edge)
					break
			else:
				break
		self.canvas.delete(vertex.drawn)
		self.vertices.remove(vertex)
		self.unsaved_work = True
		self.redraw()
		self.build_abstract_triangulation()
	
	def destroy_all_vertices(self):
		while self.vertices:
			self.destroy_vertex()
		self.build_abstract_triangulation()
	
	def create_edge(self, v1, v2):
		# Don't create a new edge if one already exists.
		if any(set([edge[0], edge[1]]) == set([v1, v2]) for edge in self.edges):
			return None
		
		# Don't create a new edge if it would intersect one that already exists.
		if any(Flipper.application.lines_intersect(edge[0], edge[1], v1, v2, self.options.float_error, True)[1] for edge in self.edges):
			return None
		
		e0 = Flipper.application.Edge(self.canvas, [v1, v2], self.options)
		self.edges.append(e0)
		# Add in any needed triangles.
		for e1, e2 in combinations(self.edges, r=2):
			if e1 != e0 and e2 != e0:
				if e1.free_sides() > 0 and e2.free_sides() > 0:
					if len(set([e[0] for e in [e0, e1, e2]] + [e[1] for e in [e0, e1, e2]])) == 3:
						self.create_triangle(e0, e1, e2)
		self.unsaved_work = True
		self.redraw()
		self.build_abstract_triangulation()
		return self.edges[-1]
	
	def destroy_edge(self, edge=None):
		if edge is None: edge = self.edges[-1]
		self.canvas.delete(edge.drawn)
		for triangle in edge.in_triangles:
			self.destroy_triangle(triangle)
		self.destroy_edge_identification(edge)
		self.edges.remove(edge)
		self.unsaved_work = True
		self.redraw()
		self.build_abstract_triangulation()
	
	def create_triangle(self, e1, e2, e3):
		assert(e1 != e2 and e1 != e3 and e2 != e3)
		
		if any([set(triangle.edges) == set([e1, e2, e3]) for triangle in self.triangles]):
			return None
		
		new_triangle = Flipper.application.Triangle(self.canvas, [e1, e2, e3], self.options)
		self.triangles.append(new_triangle)
		
		corner_vertices = [e[0] for e in [e1, e2, e3]] + [e[1] for e in [e1, e2, e3]]
		if any(vertex in new_triangle and vertex not in corner_vertices for vertex in self.vertices):
			self.destroy_triangle(new_triangle)
			return None
		
		self.unsaved_work = True
		self.redraw()
		self.build_abstract_triangulation()
		return self.triangles[-1]
	
	def destroy_triangle(self, triangle=None):
		if triangle is None: triangle = self.triangles[-1]
		self.canvas.delete(triangle.drawn)
		for edge in self.edges:
			if triangle in edge.in_triangles:
				edge.in_triangles.remove(triangle)
				self.destroy_edge_identification(edge)
		self.triangles.remove(triangle)
		self.unsaved_work = True
		self.redraw()
		self.build_abstract_triangulation()
	
	def create_edge_identification(self, e1, e2):
		assert(e1.equivalent_edge is None and e2.equivalent_edge is None)
		assert(e1.free_sides() == 1 and e2.free_sides() == 1)
		e1.equivalent_edge = e2
		e2.equivalent_edge = e1
		
		# Change colour.
		new_colour = self.colour_picker.get_colour()
		e1.set_colour(new_colour)
		e2.set_colour(new_colour)
		self.unsaved_work = True
		self.build_abstract_triangulation()
	
	def destroy_edge_identification(self, edge):
		if edge.equivalent_edge is not None:
			other_edge = edge.equivalent_edge
			other_edge.set_colour()
			edge.set_colour()
			self.canvas.itemconfig(other_edge.drawn, fill=other_edge.default_colour)
			self.canvas.itemconfig(edge.drawn, fill=edge.default_colour)
			
			edge.equivalent_edge.equivalent_edge = None
			edge.equivalent_edge = None
			self.unsaved_work = True
		self.build_abstract_triangulation()
	
	def create_curve_component(self, vertices, multiplicity=1, counted=False):
		self.curve_components.append(Flipper.application.CurveComponent(self.canvas, vertices, self.options, multiplicity, counted))
		return self.curve_components[-1]
	
	def destory_curve_component(self, curve_component):
		self.canvas.delete(curve_component.drawn)
		self.curve_components.remove(curve_component)
	
	def create_train_track_block(self, vertices, multiplicity=1, counted=False):
		self.train_track_blocks.append(Flipper.application.TrainTrackBlock(self.canvas, vertices, self.options, multiplicity, counted))
		return self.train_track_blocks[-1]
	
	def destroy_train_track_block(self, curve_component):
		self.canvas.delete(curve_component.drawn)
		self.train_track_blocks.remove(curve_component)
	
	def destroy_lamination(self):
		while self.curve_components != []:
			self.destory_curve_component(self.curve_components[-1])
		
		while self.train_track_blocks != []:
			self.destroy_train_track_block(self.train_track_blocks[-1])
		
		self.current_lamination = self.abstract_triangulation.empty_lamination()
		self.select_object(None)
		self.redraw()
	
	
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
				self.canvas.create_text((edge[0][0] + edge[1][0]) / 2, (edge[0][1] + edge[1][1]) / 2, text=str(edge.index), tag='edge_label', font=self.options.canvas_font, fill=DEFAULT_EDGE_LABEL_COLOUR)
		elif self.options.label_edges == 'Geometric':
			lamination = self.canvas_to_lamination()
			for edge in self.edges:
				self.canvas.create_text((edge[0][0] + edge[1][0]) / 2, (edge[0][1] + edge[1][1]) / 2, text='%0.4f' % lamination[edge.index], tag='edge_label', font=self.options.canvas_font, fill=DEFAULT_EDGE_LABEL_COLOUR)
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
		self.current_lamination = self.abstract_triangulation.empty_lamination()
		self.create_edge_labels()
		self.treeview_objects.insert('', 'end', 'laminations', text='Laminations:', open=True, tags=['txt', 'menu'])
		self.treeview_objects.insert('', 'end', 'mapping_classes', text='Mapping Classes:', open=True, tags=['txt', 'menu'])
		self.menubar.entryconfig('Lamination', state='normal')
		self.menubar.entryconfig('Mapping class', state='normal')
	
	def destroy_abstract_triangulation(self):
		self.clear_edge_indices()
		self.destroy_edge_labels()
		self.destroy_lamination()
		self.abstract_triangulation = None
		self.current_lamination = None
		self.laminations = {}
		self.lamination_names = {}
		self.mapping_classes = {}
		self.mapping_class_names = {}
		self.cache = {}
		for child in self.treeview_objects.get_children(''):
			self.treeview_objects.delete(child)
		self.menubar.entryconfig('Lamination', state='disabled')
		self.menubar.entryconfig('Mapping class', state='disabled')
	
	def build_abstract_triangulation(self):
		if self.is_complete() and self.abstract_triangulation is None:
			self.create_abstract_triangulation()
		elif not self.is_complete() and self.abstract_triangulation is not None:
			self.destroy_abstract_triangulation()
	
	
	######################################################################
	
	
	def canvas_to_lamination(self):
		vector = [0] * self.zeta
		
		# This version takes into account bigons between interior edges.
		for curve in self.curve_components:
			if not curve.counted:
				meets = []  # We store (index of edge intersection, should we double count).
				for i in range(len(curve.vertices)-1):
					this_segment_meets = [(Flipper.application.lines_intersect(curve.vertices[i], curve.vertices[i+1], edge[0], edge[1], self.options.float_error, edge.equivalent_edge is None), edge.index) for edge in self.edges]
					for (d, double), index in sorted(this_segment_meets):
						if d >= -self.options.float_error:
							if len(meets) > 0 and meets[-1][0] == index:
								meets.pop()
							else:
								meets.append((index, double))
				
				for index, double in meets:
					vector[index] += (2 if double else 1) * curve.multiplicity
		
		if all(isinstance(x, Flipper.kernel.Integer_Type) and x % 2 == 0 for x in vector):
			vector = [i // 2 for i in vector]
		else:
			vector = [i / 2 for i in vector]
		
		current_vector = self.current_lamination.vector
		new_vector = [a+b for a, b in zip(vector, current_vector)]
		self.current_lamination = self.abstract_triangulation.lamination(new_vector)
		
		return self.current_lamination
	
	def lamination_to_canvas(self, lamination):
		self.destroy_lamination()
		
		# Choose the right way to render this lamination.
		if not lamination.is_multicurve() or lamination.weight() > MAX_DRAWABLE: 
			if self.options.render_lamination == Flipper.application.options.RENDER_LAMINATION_FULL:
				render = Flipper.application.options.RENDER_LAMINATION_W_TRAIN_TRACK
			else:
				render = self.options.render_lamination
		else:
			render = self.options.render_lamination
		
		# We'll do everything with floats now because these are accurate enough for drawing to the screen with.
		vb = self.options.vertex_buffer  # We are going to use this a lot.
		a_weights = [float(x) for x in lamination]
		if render == Flipper.application.options.RENDER_LAMINATION_W_TRAIN_TRACK:
			master_scale = max(a_weights)
			if master_scale == 0: master_scale = float(1)
		
		for triangle in self.triangles:
			a_tri_weights = [a_weights[edge.index] for edge in triangle.edges]
			a_dual_weights = [(a_tri_weights[(j+1)%3] + a_tri_weights[(j+2)%3] - a_tri_weights[(j+0)%3]) / 2 for j in range(3)]
			for i in range(3):
				a = triangle[i-1] - triangle[i]
				b = triangle[i-2] - triangle[i]
				
				if render == Flipper.application.options.RENDER_LAMINATION_W_TRAIN_TRACK:
					if a_dual_weights[i] > 0:
						# We first do the edge to the left of the vertex.
						# Correction factor to take into account the weight on this edge.
						s_a = a_weights[triangle.edges[i-2].index] / master_scale
						# The fractions of the distance of the two points on this edge.
						scale_a = vb * s_a + (1 - s_a) / 2
						scale_a2 = scale_a + (1 - 2*vb) * s_a * a_dual_weights[i] / (a_dual_weights[i] + a_dual_weights[i-1])
						# The actual points of intersection.
						start_point = triangle[i][0] + a[0] * scale_a, triangle[i][1] + a[1] * scale_a
						start_point2 = triangle[i][0] + a[0] * scale_a2, triangle[i][1] + a[1] * scale_a2
						
						# Now repeat for the other edge of the triangle.
						s_b = a_weights[triangle.edges[i-1].index] / master_scale
						scale_b = vb * s_b + (1 - s_b) / 2
						scale_b2 = scale_b + (1 - 2*vb) * s_b * a_dual_weights[i] / (a_dual_weights[i] + a_dual_weights[i-2])
						end_point = triangle[i][0] + b[0] * scale_b, triangle[i][1] + b[1] * scale_b
						end_point2 = triangle[i][0] + b[0] * scale_b2, triangle[i][1] + b[1] * scale_b2
						
						vertices = [start_point, end_point, end_point2, start_point2]
						self.create_train_track_block(vertices, counted=True)  # We've counted this so don't set the multiplicity.
				elif render == Flipper.application.options.RENDER_LAMINATION_FULL:  # We can ONLY use this method when the lamination is a multicurve.
					# Also it is VERY slow (O(n) not O(log(n))).
					# Here we need the exact dual weights so we had better work them out.
					weights = [lamination[edge.index] for edge in triangle.edges]
					dual_weights = [(weights[(j+1)%3] + weights[(j+2)%3] - weights[(j+0)%3]) // 2 for j in range(3)]
					for j in range(int(dual_weights[i])):
						scale_a = float(1) / 2 if weights[i-2] == 1 else vb + (1 - 2*vb) * j / (weights[i-2] - 1)
						scale_b = float(1) / 2 if weights[i-1] == 1 else vb + (1 - 2*vb) * j / (weights[i-1] - 1)
						start_point = triangle[i][0] + a[0] * scale_a, triangle[i][1] + a[1] * scale_a
						end_point = triangle[i][0] + b[0] * scale_b, triangle[i][1] + b[1] * scale_b
						vertices = [start_point, end_point]
						self.create_curve_component(vertices, counted=True)  # We've counted this so don't set the multiplicity.
				elif render == Flipper.application.options.RENDER_LAMINATION_C_TRAIN_TRACK:
					if a_dual_weights[i] > 0:
						scale = float(1) / 2
						start_point = triangle[i][0] + a[0] * scale, triangle[i][1] + a[1] * scale
						end_point = triangle[i][0] + b[0] * scale, triangle[i][1] + b[1] * scale
						vertices = [start_point, end_point]
						self.create_curve_component(vertices, counted=True)  # We've counted this so don't set the multiplicity.
		
		self.current_lamination = lamination
		self.create_edge_labels()
	
	def tighten_lamination(self):
		if self.is_complete():
			try:
				lamination = self.canvas_to_lamination()
				self.lamination_to_canvas(lamination)
			except Flipper.AssumptionError:
				tkMessageBox.showwarning('Curve', 'Not an essential lamination.')
	
	def store_lamination(self, lamination=None):
		if self.is_complete():
			if lamination is None:
				try:
					lamination = self.canvas_to_lamination()
				except Flipper.AssumptionError:
					tkMessageBox.showwarning('Curve', 'Not an essential lamination.')
					return
			
			name = Flipper.application.get_input('Name', 'New lamination name:', validate=self.valid_name)
			if name is not None:
				self.add_lamination(lamination, name)
				self.destroy_lamination()
	
	def store_twist(self, lamination=None):
		if self.is_complete():
			if lamination is None:
				try:
					lamination = self.canvas_to_lamination()
				except Flipper.AssumptionError:
					tkMessageBox.showwarning('Curve', 'Not an essential lamination.')
					return
			
			if lamination.is_twistable():
				name = Flipper.application.get_input('Name', 'New twist name:', validate=self.valid_name)
				if name is not None:
					self.add_mapping_class(lamination.encode_twist(), name)
					self.add_lamination(lamination, name)
					self.destroy_lamination()
			else:
				tkMessageBox.showwarning('Curve', 'Cannot twist about this, it is not a curve with punctured complementary regions.')
	
	def store_halftwist(self, lamination=None):
		if self.is_complete():
			if lamination is None:
				try:
					lamination = self.canvas_to_lamination()
				except Flipper.AssumptionError:
					tkMessageBox.showwarning('Curve', 'Not an essential lamination.')
					return
			
			if lamination.is_halftwistable():
				name = Flipper.application.get_input('Name', 'New half twist name:', validate=self.valid_name)
				if name is not None:
					self.add_mapping_class(lamination.encode_halftwist(), name)
					self.add_lamination(lamination, name)
					self.destroy_lamination()
			else:
				tkMessageBox.showwarning('Curve', 'Cannot half-twist about this, it is not an essential curve bounding a pair of pants with a punctured complement.')
	
	def store_isometry(self):
		if self.is_complete():
			specification = Flipper.application.get_input('Isometry specification', 'New isometry:', validate=self.valid_isometry)
			if specification is not None:
				from_edges, to_edges = zip(*[[int(d) for d in x.split(':')] for x in specification.split(' ')])
				try:
					# Some of this should really go in self.valid_isometry.
					possible_isometry = [isom for isom in self.abstract_triangulation.all_isometries(self.abstract_triangulation) if all(isom.edge_map[from_edge] == to_edge for from_edge, to_edge in zip(from_edges, to_edges))]
					isometry = possible_isometry[0]
				except IndexError:
					tkMessageBox.showwarning('Isometry', 'Information does not specify an isometry.')
				else:
					name = Flipper.application.get_input('Name', 'New isometry name:', validate=self.valid_name)
					if name is not None:
						self.add_mapping_class(isometry.encode_isometry(), name)
	
	def create_composition(self, return_name=False):
		# Assumes that each of the named mapping classes exist.
		if self.is_complete():
			composition = Flipper.application.get_input('Composition', 'New composition:', validate=self.valid_composition)
			if composition is not None:
				mapping_class = self.abstract_triangulation.Id_EncodingSequence()
				for twist in composition.split('.'):
					if twist in self.mapping_classes:
						mapping_class = mapping_class * self.mapping_classes[twist]
					elif twist.swapcase() in self.mapping_classes:
						mapping_class = mapping_class * self.mapping_classes[twist].inverse()
					else:
						tkMessageBox.showwarning('Mapping class', 'Unknown mapping class: %s' % twist)
						raise Flipper.AssumptionError()
				
				if return_name:
					return composition, mapping_class
				else:
					return mapping_class
			else:
				if return_name:
					return None, None
				else:
					return None
	
	def store_composition(self):
		if self.is_complete():
			mapping_class = self.create_composition()
			if mapping_class is not None:
				name = Flipper.application.get_input('Name', 'New composition name:', validate=self.valid_name)
				if name is not None:
					self.add_mapping_class(mapping_class, name)
	
	def show_apply(self, mapping_class=None):
		if self.is_complete():
			try:
				lamination = self.canvas_to_lamination()
			except Flipper.AssumptionError:
				tkMessageBox.showwarning('Curve', 'Not an essential lamination.')
			else:
				if mapping_class is None:
					mapping_class = self.create_composition()
				
				if mapping_class is not None:
					self.lamination_to_canvas(mapping_class * lamination)
	
	
	######################################################################
	
	
	def order(self):
		if self.is_complete():
			composition, mapping_class = self.create_composition(return_name=True)
			if mapping_class is not None:
				tkMessageBox.showinfo('Order', '%s order: %s.' % (composition, mapping_class.order_string()))
	
	def NT_type(self):
		if self.is_complete():
			composition, mapping_class = self.create_composition(return_name=True)
			if mapping_class is not None:
				try:
					NT_type = Flipper.application.apply_progression(mapping_class.NT_type, indeterminant=False)
					
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
	
	
	def invariant_lamination(self):
		if self.is_complete():
			composition, mapping_class = self.create_composition(return_name=True)
			if mapping_class is not None:
				try:
					lamination = Flipper.application.apply_progression(mapping_class.invariant_lamination)
					# dilatation = mapping_class.dilatation(lamination)
				except Flipper.AssumptionError:
					tkMessageBox.showwarning('Lamination', 'Cannot find any projectively invariant laminations of %s, it is periodic.' % composition)
				except Flipper.ComputationError:
					tkMessageBox.showwarning('Lamination', 'Could not find any projectively invariant laminations of %s. It is probably reducible.' % composition)
				else:
					self.lamination_to_canvas(lamination)
	
	def build_bundle(self):
		if self.is_complete():
			composition, mapping_class = self.create_composition(return_name=True)
			if mapping_class is not None:
				path = tkFileDialog.asksaveasfilename(defaultextension='.tri', filetypes=[('SnapPy Files', '.tri'), ('all files', '.*')], title='Export SnapPy Triangulation')
				if path != '':
					try:
						disk_file = open(path, 'w')
						try:
							splitting = mapping_class.splitting_sequence()
						except Flipper.AssumptionError:
							tkMessageBox.showwarning('Lamination', 'Cannot find any projectively invariant laminations of %s, it is not pseudo-Anosov.' % composition)
						except Flipper.ComputationError:
							tkMessageBox.showwarning('Lamination', 'Could not find any projectively invariant laminations of %s. It is probably reducible.' % composition)
						else:
							# There may be more than one isometry, for now let's just pick the first. We'll worry about this eventually.
							M = splitting.bundle(0, composition)
							disk_file.write(M.snappy_string())
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
						disk_file.close()
	
	
	######################################################################
	
	
	def canvas_left_click(self, event):
		shift_pressed = (event.state & BIT_SHIFT) == BIT_SHIFT
		
		x, y = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))
		possible_object = self.object_here((x, y))
		
		if self.is_complete() and not shift_pressed:
			if self.selected_object is None:
				self.select_object(self.create_curve_component([(x, y), (x, y)]))
			elif isinstance(self.selected_object, Flipper.application.CurveComponent):
				self.selected_object.append_point((x, y))
		else:
			if self.selected_object is None:
				if possible_object is None:
					self.select_object(self.create_vertex((x, y)))
				elif isinstance(possible_object, Flipper.application.Edge):
					self.destroy_edge_identification(possible_object)
					if possible_object.free_sides() > 0:
						self.select_object(possible_object)
				elif isinstance(possible_object, Flipper.application.Vertex):
					self.select_object(possible_object)
			elif isinstance(self.selected_object, Flipper.application.Vertex):
				if possible_object == self.selected_object:
					self.select_object(None)
				elif possible_object is None:
					new_vertex = self.create_vertex((x, y))
					self.create_edge(self.selected_object, new_vertex)
					self.select_object(new_vertex)
				elif isinstance(possible_object, Flipper.application.Vertex):
					self.create_edge(self.selected_object, possible_object)
					self.select_object(possible_object)
				elif isinstance(possible_object, Flipper.application.Edge):
					if possible_object.free_sides() > 0:
						self.select_object(possible_object)
			elif isinstance(self.selected_object, Flipper.application.Edge):
				if possible_object == self.selected_object:
					self.select_object(None)
				elif possible_object is None:
					new_vertex = self.create_vertex((x, y))
					self.create_edge(self.selected_object[0], new_vertex)
					self.create_edge(self.selected_object[1], new_vertex)
					self.select_object(None)
				elif isinstance(possible_object, Flipper.application.Vertex):
					if possible_object != self.selected_object[0] and possible_object != self.selected_object[1]:
						self.create_edge(self.selected_object[0], possible_object)
						self.create_edge(self.selected_object[1], possible_object)
						self.select_object(None)
					else:
						self.select_object(possible_object)
				elif isinstance(possible_object, Flipper.application.Edge):
					if (self.selected_object.free_sides() == 1 or self.selected_object.equivalent_edge is not None) and (possible_object.free_sides() == 1 or possible_object.equivalent_edge is not None):
						self.destroy_edge_identification(self.selected_object)
						self.destroy_edge_identification(possible_object)
						self.create_edge_identification(self.selected_object, possible_object)
						self.select_object(None)
					else:
						self.select_object(possible_object)
	
	def canvas_right_click(self, event):
		if self.selected_object is not None:
			if isinstance(self.selected_object, Flipper.application.CurveComponent):
				if len(self.selected_object.vertices) > 2:
					(x, y) = self.selected_object.vertices[-1]
					self.selected_object.pop_point()
					self.selected_object.move_point(-1, x, y)
				else:
					self.destory_curve_component(self.selected_object)
					self.select_object(None)
			else:
				self.select_object(None)
	
	def canvas_double_left_click(self, event):
		if self.selected_object is not None:
			if isinstance(self.selected_object, Flipper.application.CurveComponent):
				self.selected_object.pop_point()
			
			self.select_object(None)
	
	def canvas_move(self, event):
		x, y = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))
		if isinstance(self.selected_object, Flipper.application.CurveComponent):
			self.selected_object.move_point(-1, x, y)
	
	def parent_key_press(self, event):
		key = event.keysym
		if key in ('Delete', 'BackSpace'):
			if isinstance(self.selected_object, Flipper.application.Vertex):
				self.destroy_vertex(self.selected_object)
				self.select_object(None)
			elif isinstance(self.selected_object, Flipper.application.Edge):
				self.destroy_edge(self.selected_object)
				self.select_object(None)
			elif isinstance(self.selected_object, Flipper.application.CurveComponent):
				self.canvas_right_click(event)
		elif key == 'Escape':
			self.canvas_right_click(event)
		elif key == 'F1':
			self.show_help()
		elif key == 'F5':
			self.destroy_lamination()
		elif key == 'Prior':
			self.zoom_centre(1.05)
		elif key == 'Next':
			self.zoom_centre(0.95)
	
	def treeview_objects_left_click(self, event):
		iid = self.treeview_objects.identify('row', event.x, event.y)
		tags = self.treeview_objects.item(iid, 'tags')
		
		if 'show_lamination' in tags:
			self.lamination_to_canvas(self.laminations[self.lamination_names[iid]])
		elif 'apply_mapping_class' in tags:
			self.show_apply(self.mapping_classes[self.mapping_class_names[iid]])
		elif 'apply_mapping_class_inverse' in tags:
			self.show_apply(self.mapping_classes[self.mapping_class_names[iid].swapcase()])
		else:
			pass  # !?! To do.
	
	def treeview_objects_double_left_click(self, event):
		self.treeview_objects_left_click(event)
		iid = self.treeview_objects.identify('row', event.x, event.y)
		tags = self.treeview_objects.item(iid, 'tags')
		
		if 'multicurve_lamination' in tags:
			pass
		elif 'twist_lamination' in tags:
			lamination = self.laminations[self.lamination_names[iid]]
			if lamination.is_twistable():
				name = Flipper.application.get_input('Name', 'New twist name:', validate=self.valid_name)
				if name is not None:
					self.add_mapping_class(lamination.encode_twist(), name)
		elif 'half_twist_lamination' in tags:
			lamination = self.laminations[self.lamination_names[iid]]
			if lamination.is_halftwistable():
				name = Flipper.application.get_input('Name', 'New half twist name:', validate=self.valid_name)
				if name is not None:
					self.add_mapping_class(lamination.encode_halftwist(), name)
		elif 'filling_lamination' in tags:
			try:
				lamination = self.laminations[self.lamination_names[iid]]
				if 'filling' not in self.cache[lamination]:
					self.cache[lamination]['filling'] = Flipper.application.apply_progression(lamination.is_filling)
					self.unsaved_work = True
				self.treeview_objects.item(iid, text='Filling: %s' % self.cache[lamination]['filling'])
			except Flipper.AbortError:
				pass
		elif 'mapping_class_order' in tags:
			mapping_class = self.mapping_classes[self.mapping_class_names[iid]]
			order = mapping_class.order()
			self.treeview_objects.item(iid, text='Order: %s' % ('Infinite' if order == 0 else str(order)))
		elif 'mapping_class_type' in tags:
			try:
				mapping_class = self.mapping_classes[self.mapping_class_names[iid]]
				if 'NT_type' not in self.cache[mapping_class]:
					# self.cache[mapping_class]['NT_type'] = Flipper.application.apply_progression(mapping_class.NT_type, indeterminant=False)
					self.cache[mapping_class]['NT_type'] = Flipper.application.apply_progression(mapping_class.NT_type_alternate)
					self.unsaved_work = True
				self.treeview_objects.item(iid, text='Type: %s' % self.cache[mapping_class]['NT_type'])
			except Flipper.AbortError:
				pass
		elif 'mapping_class_invariant_lamination' in tags:
			try:
				mapping_class = self.mapping_classes[self.mapping_class_names[iid]]
				if 'invariant_lamination' not in self.cache[mapping_class]:
					self.cache[mapping_class]['invariant_lamination'] = Flipper.application.apply_progression(mapping_class.invariant_lamination)
					self.unsaved_work = True
				self.treeview_objects.item(iid, text='Invariant lamination')
				self.lamination_to_canvas(self.cache[mapping_class]['invariant_lamination'])
			except Flipper.AssumptionError:
				tkMessageBox.showwarning('Lamination', 'Cannot find any projectively invariant laminations, mapping class is periodic.')
			except Flipper.ComputationError:
				tkMessageBox.showwarning('Lamination', 'Could not find any projectively invariant laminations. Mapping class is probably reducible.')
			except Flipper.AbortError:
				pass
		else:
			pass


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

