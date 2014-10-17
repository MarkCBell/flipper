
''' The main window of the flipper GUI application. '''

import flipper
import flipper.app

import re
import os
import sys
import pickle
from math import sin, cos, pi
from itertools import combinations

try:
	import Tkinter as TK
	import tkFileDialog
	import tkMessageBox
except ImportError:  # Python 3.
	try:
		import tkinter as TK
		import tkinter.filedialog as tkFileDialog
		import tkinter.messagebox as tkMessageBox
	except ImportError:
		raise ImportError('Tkinter not available.')

try:
	import ttk as TTK
except ImportError:  # Python 3.
	try:
		from tkinter import ttk as TTK
	except ImportError:
		raise ImportError('Ttk not available.')

# Some constants.
if sys.platform in ['darwin']:
	COMMAND = {
		'new': 'Command+N',
		'open': 'Command+O',
		'save': 'Command+S',
		'close': 'Command+W',
		'lamination': 'Command+L',
		'erase': 'Command+D',
		'twist': 'Command+T',
		'halftwist': 'Command+H',
		'isometry': 'Command+I',
		'compose': 'Command+O'
		}
	COMMAND_KEY = {
		'new': '<Command-n>',
		'open': '<Command-o>',
		'save': '<Command-s>',
		'close': '<Command-w>',
		'lamination': '<Command-l>',
		'erase': '<Command-d>',
		'twist': '<Command-t>',
		'halftwist': '<Command-h>',
		'isometry': '<Command-i>',
		'compose': '<Command-m>'
		}
else:
	COMMAND = {
		'new': 'Ctrl+N',
		'open': 'Ctrl+O',
		'save': 'Ctrl+S',
		'close': 'Ctrl+W',
		'lamination': 'Ctrl+L',
		'erase': 'Ctrl+D',
		'twist': 'Ctrl+T',
		'halftwist': 'Ctrl+H',
		'isometry': 'Ctrl+I',
		'compose': 'Ctrl+M'
		}
	COMMAND_KEY = {
		'new': '<Control-n>',
		'open': '<Control-o>',
		'save': '<Control-s>',
		'close': '<Control-w>',
		'lamination': '<Control-l>',
		'erase': '<Control-d>',
		'twist': '<Control-t>',
		'halftwist': '<Control-h>',
		'isometry': '<Control-i>',
		'compose': '<Control-m>'
		}

# Regexs for validating names of things.
VALID_NAME_REGEX = r'[a-zA-Z][a-zA-z0-9_]*$'  # Valid names consist of letters, numbers, underscores and start with a letter.
VALID_SPECIFICATION_REGEX = r'[a-zA-Z]+$'  # Valid specifications are non-empty and consists of letters.
VALID_ISOMETRY_REGEX = r'([0-9]+:[0-9]+( |$))+'  # Valid isometries match 'num:num num:num ...'.

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

DEFAULT_EDGE_LABEL_COLOUR = 'black'
DEFAULT_SELECTED_COLOUR = 'red'
MAX_DRAWABLE = 1000  # Maximum weight of a multicurve to draw fully.

# This helper function should really be inside of
# update_cache_progression but then it wouldn't be
# pickleable and so couldn't be passed to the worker
# thread.
def helper(instance, method):
	try:
		getattr(instance, method)()
	except (flipper.AssumptionError, flipper.ComputationError):
		pass
	return instance

def update_cache_progression(instance, method):
	# Make instance_copy, a copy of instance.
	# Compute instance_copy.method() with a progress bar.
	# Copy instance_copy._cache to instance._cache.
	# Return instance.
	instance_copy = flipper.app.apply_progression(helper, args=(instance, method))
	instance._cache = instance_copy._cache
	return instance

class FlipperApp(object):
	def __init__(self, parent, return_slot=None):
		self.parent = parent
		self.return_slot = return_slot
		self.options = flipper.app.Options(self)
		self.colour_picker = flipper.app.ColourPalette()
		
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
		self.treeview_objects.insert('', 'end', 'laminations', text='Laminations:', open=True, tags=['txt', 'menu'])
		self.treeview_objects.insert('', 'end', 'mapping_classes', text='Mapping Classes:', open=True, tags=['txt', 'menu'])
		
		self.treeview_objects.grid(row=0, column=0, sticky='nesw')
		self.scrollbar_treeview.grid(row=0, column=1, sticky='nws')
		self.frame_interface.grid_rowconfigure(0, weight=1)
		self.frame_interface.grid_columnconfigure(0, weight=1)
		###
		
		self.frame_draw = TK.Frame(self.parent)
		###
		# This needs takefocus set so that we can tell if it has been selected.
		# Also, for some reason which I can't explain, we need this height=1 to prevent the command
		# bar below from collapsing when the application is small.
		self.canvas = TK.Canvas(self.frame_draw, height=1, bg='#dcecff', takefocus=True)
		self.canvas.pack(padx=6, pady=6, fill='both', expand=True)
		self.canvas.bind('<Button-1>', self.canvas_left_click)
		self.canvas.bind('<Double-Button-1>', self.canvas_double_left_click)
		self.canvas.bind('<Button-3>', self.canvas_right_click)
		self.canvas.bind('<Motion>', self.canvas_move)
		self.canvas.bind('<FocusOut>', self.canvas_focus_lost)
		
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
		self.filemenu.add_command(label='New', command=self.initialise, accelerator=COMMAND['new'], font=app_font)
		self.filemenu.add_command(label='Open', command=self.load, accelerator=COMMAND['open'], font=app_font)
		self.filemenu.add_command(label='Open example', command=self.load_example, font=app_font)
		self.filemenu.add_command(label='Save', command=self.save, accelerator=COMMAND['save'], font=app_font)
		self.exportmenu = TK.Menu(self.menubar, tearoff=0)
		self.exportmenu.add_command(label='Export kernel file', command=self.export_kernel_file, font=app_font)
		self.exportmenu.add_command(label='Export image', command=self.export_image, font=app_font)
		self.filemenu.add_cascade(label='Export', menu=self.exportmenu, font=app_font)
		self.filemenu.add_separator()
		self.filemenu.add_command(label='Exit', command=self.quit, accelerator=COMMAND['save'], font=app_font)
		self.menubar.add_cascade(label='File', menu=self.filemenu, font=app_font)
		
		self.surfacemenu = TK.Menu(self.menubar, tearoff=0)
		self.surfacemenu.add_command(label='Create ngon', command=self.initialise_circular_n_gon, font=app_font)
		self.surfacemenu.add_command(label='Create radial ngon', command=self.initialise_radial_n_gon, font=app_font)
		self.surfacemenu.add_command(label='Information', command=self.show_surface_information, font=app_font)
		self.zoommenu = TK.Menu(self.menubar, tearoff=0)
		self.zoommenu.add_command(label='Zoom in', command=self.zoom_in, accelerator='+', font=app_font)
		self.zoommenu.add_command(label='Zoom out', command=self.zoom_out, accelerator='-', font=app_font)
		self.zoommenu.add_command(label='Zoom to drawing', command=self.zoom_to_drawing, accelerator='0', font=app_font)
		self.surfacemenu.add_cascade(label='Zoom...', menu=self.zoommenu, font=app_font)
		self.menubar.add_cascade(label='Surface', menu=self.surfacemenu, font=app_font)
		
		self.laminationmenu = TK.Menu(self.menubar, tearoff=0)
		self.laminationmenu.add_command(label='Store', command=self.store_lamination, accelerator=COMMAND['lamination'], font=app_font)
		self.laminationmenu.add_command(label='Tighten', command=self.tighten_lamination, font=app_font)
		self.laminationmenu.add_command(label='Erase', command=self.destroy_lamination, accelerator=COMMAND['erase'], font=app_font)
		self.menubar.add_cascade(label='Lamination', menu=self.laminationmenu, state='disabled', font=app_font)
		
		self.mappingclassmenu = TK.Menu(self.menubar, tearoff=0)
		self.storemappingclassmenu = TK.Menu(self.menubar, tearoff=0)
		self.storemappingclassmenu.add_command(label='Twist', command=self.store_twist, accelerator=COMMAND['twist'], font=app_font)
		self.storemappingclassmenu.add_command(label='Half twist', command=self.store_halftwist, accelerator=COMMAND['halftwist'], font=app_font)
		self.storemappingclassmenu.add_command(label='Isometry', command=self.store_isometry, accelerator=COMMAND['isometry'], font=app_font)
		self.storemappingclassmenu.add_command(label='Composition', command=self.store_composition, accelerator=COMMAND['compose'], font=app_font)
		self.mappingclassmenu.add_cascade(label='Store...', menu=self.storemappingclassmenu, font=app_font)
		self.mappingclassmenu.add_command(label='Apply', command=self.show_apply, font=app_font)
		self.mappingclassmenu.add_command(label='Order', command=self.order, font=app_font)
		self.mappingclassmenu.add_command(label='Type', command=self.nielsen_thurston_type, font=app_font)
		self.mappingclassmenu.add_command(label='Invariant lamination', command=self.invariant_lamination, font=app_font)
		self.mappingclassmenu.add_command(label='Build bundle', command=self.build_bundle, font=app_font)
		self.menubar.add_cascade(label='Mapping class', menu=self.mappingclassmenu, state='disabled', font=app_font)
		
		##########################################
		self.settingsmenu = TK.Menu(self.menubar, tearoff=0)
		
		self.sizemenu = TK.Menu(self.menubar, tearoff=0)
		self.sizemenu.add_radiobutton(label='Small', var=self.options.size_var, value=flipper.app.options.SIZE_SMALL, font=app_font)
		self.sizemenu.add_radiobutton(label='Medium', var=self.options.size_var, value=flipper.app.options.SIZE_MEDIUM, font=app_font)
		self.sizemenu.add_radiobutton(label='Large', var=self.options.size_var, value=flipper.app.options.SIZE_LARGE, font=app_font)
		# self.sizemenu.add_radiobutton(label='Extra large', var=self.options.size_var, value=flipper.app.options.SIZE_XLARGE, font=app_font)
		
		self.edgelabelmenu = TK.Menu(self.menubar, tearoff=0)
		self.edgelabelmenu.add_radiobutton(label=flipper.app.options.LABEL_EDGES_NONE, var=self.options.label_edges_var, font=app_font)
		self.edgelabelmenu.add_radiobutton(label=flipper.app.options.LABEL_EDGES_INDEX, var=self.options.label_edges_var, font=app_font)
		self.edgelabelmenu.add_radiobutton(label=flipper.app.options.LABEL_EDGES_GEOMETRIC, var=self.options.label_edges_var, font=app_font)
		# self.edgelabelmenu.add_radiobutton(label=flipper.app.options.LABEL_EDGES_ALGEBRAIC, var=self.options.edge_labels_var, font=app_font)
		
		self.laminationdrawmenu = TK.Menu(self.menubar, tearoff=0)
		self.laminationdrawmenu.add_radiobutton(label=flipper.app.options.RENDER_LAMINATION_FULL, var=self.options.render_lamination_var, font=app_font)
		self.laminationdrawmenu.add_radiobutton(label=flipper.app.options.RENDER_LAMINATION_C_TRAIN_TRACK, var=self.options.render_lamination_var, font=app_font)
		self.laminationdrawmenu.add_radiobutton(label=flipper.app.options.RENDER_LAMINATION_W_TRAIN_TRACK, var=self.options.render_lamination_var, font=app_font)
		
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
		
		self.parent.bind(COMMAND_KEY['new'], lambda event: self.initialise())
		self.parent.bind(COMMAND_KEY['open'], lambda event: self.load())
		self.parent.bind(COMMAND_KEY['save'], lambda event: self.save())
		self.parent.bind(COMMAND_KEY['close'], lambda event: self.quit())
		self.parent.bind(COMMAND_KEY['lamination'], lambda event: self.store_lamination())
		self.parent.bind(COMMAND_KEY['erase'], lambda event: self.destroy_lamination())
		self.parent.bind(COMMAND_KEY['twist'], lambda event: self.store_twist())
		self.parent.bind(COMMAND_KEY['halftwist'], lambda event: self.store_halftwist())
		self.parent.bind(COMMAND_KEY['isometry'], lambda event: self.store_isometry())
		self.parent.bind(COMMAND_KEY['compose'], lambda event: self.store_composition())
		self.parent.bind('<Key>', self.parent_key_press)
		
		self.parent.protocol('WM_DELETE_WINDOW', self.quit)
		
		self.unsaved_work = False
		
		self.vertices = []
		self.edges = []
		self.triangles = []
		self.curve_components = []
		self.train_track_blocks = []
		
		self.zeta = 0
		self.equipped_triangulation = None
		self.current_lamination = None
		self.lamination_names = {}
		self.treeview_laminations = []
		self.mapping_class_names = {}
		self.treeview_mapping_classes = []
		
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
		if re.match(VALID_NAME_REGEX, strn) is None:
			tkMessageBox.showerror('Invalid name', 'A valid name must match "%s".' % VALID_NAME_REGEX)
			return False
		
		return True
	
	def valid_specification(self, strn):
		if re.match(VALID_SPECIFICATION_REGEX, strn) is None:
			tkMessageBox.showerror('Invalid specification', 'A valid specification must match "%s".' % VALID_SPECIFICATION_REGEX)
			return False
		
		return True
	
	def valid_isometry(self, strn):
		
		if re.match(VALID_ISOMETRY_REGEX, strn) is None:
			tkMessageBox.showerror('Invalid isometry specification', 'A valid specification must match "%s".' % VALID_ISOMETRY_REGEX)
			return False
		
		return True
	
	def valid_composition(self, strn):
		# A composition is valid if it is a list of mapping class names and inverse names separated by periods.
		try:
			self.equipped_triangulation.mapping_class(strn)
		except KeyError:
			tkMessageBox.showerror('Invalid composition', 'A valid composition must consist of mapping class names and inverse names, with periods to separate ambiguities.')
			return False
		
		return True
	
	def add_lamination(self, lamination, name):
		if self.remove_lamination(name):
			self.equipped_triangulation.laminations[name] = lamination
			iid = self.treeview_objects.insert('laminations', 'end', text=name, tags=['txt', 'lamination'])
			self.lamination_names[iid] = name
			multicurve_string = lamination.is_multicurve()
			twistable_string = lamination.is_twistable()
			halftwistable_string = lamination.is_halftwistable()
			filling_string = '?' if not multicurve_string else 'False'
			
			# Set up all the properties to appear under this label.
			# We will also set up self.lamination_names to point each item under this to <name> too.
			tagged_actions = [
				('Show', 'show_lamination'),
				]
			for label, tag in tagged_actions:
				self.lamination_names[self.treeview_objects.insert(iid, 'end', text=label, tags=['txt', tag])] = name
			
			iid_properties = self.treeview_objects.insert(iid, 'end', text='Properties', tags=['txt', 'properties'])
			tagged_properties = [
				('Multicurve: %s' % multicurve_string, 'multicurve_lamination'),
				('Twistable: %s' % twistable_string, 'twist_lamination'),
				('Half twistable: %s' % halftwistable_string, 'half_twist_lamination'),
				('Filling: %s' % filling_string, 'filling_lamination')
				]
			for label, tag in tagged_properties:
				self.lamination_names[self.treeview_objects.insert(iid_properties, 'end', text=label, tags=['txt', tag])] = name
			
			self.treeview_laminations.append(name)
			
			self.unsaved_work = True
	
	def remove_lamination(self, name):
		if name in self.treeview_laminations:
			if tkMessageBox.showwarning('Remove lamination', 'Remove existing lamination %s?' % name, type='yesno') == 'yes':
				self.equipped_triangulation.laminations.pop(name)
				[entry] = [child for child in self.treeview_objects.get_children('laminations') if self.lamination_names[child] == name]
				self.treeview_objects.delete(entry)
				self.lamination_names = dict((iid, l_name) for iid, l_name in self.lamination_names.items() if l_name != name)
				self.treeview_laminations.remove(name)
			else:
				return False
		
		return True
	
	def add_mapping_class(self, mapping_class, name):
		name_inverse = name.swapcase()
		if self.remove_mapping_class(name) and self.remove_mapping_class(name_inverse):
			self.equipped_triangulation.pos_mapping_classes[name] = mapping_class
			self.equipped_triangulation.neg_mapping_classes[name_inverse] = mapping_class.inverse()
			self.equipped_triangulation.mapping_classes[name] = mapping_class
			self.equipped_triangulation.mapping_classes[name_inverse] = mapping_class.inverse()
			
			iid = self.treeview_objects.insert('mapping_classes', 'end', text=name, tags=['txt', 'mapping_class'])
			self.mapping_class_names[iid] = name
			order = mapping_class.order()
			order_string = 'Infinite' if order == 0 else str(order)
			type_string = '?' if order == 0 else 'Periodic'
			invariant_string = '?' if order == 0 else 'x'
			
			# Set up all the properties to appear under this label.
			# We will also set up self.mapping_class_names to point each item under this to <name> too.
			tagged_actions = [
				('Apply', 'apply_mapping_class'),
				('Apply inverse', 'apply_mapping_class_inverse'),
				]
			for label, tag in tagged_actions:
				self.mapping_class_names[self.treeview_objects.insert(iid, 'end', text=label, tags=['txt', tag])] = name
			
			iid_properties = self.treeview_objects.insert(iid, 'end', text='Properties', tags=['txt', 'properties'])
			tagged_properties = [
				('Order: %s' % order_string, 'mapping_class_order'),
				('Type: %s' % type_string, 'mapping_class_type'),
				('Invariant lamination: %s' % invariant_string, 'mapping_class_invariant_lamination')
				]
			for label, tag in tagged_properties:
				self.mapping_class_names[self.treeview_objects.insert(iid_properties, 'end', text=label, tags=['txt', tag])] = name
			
			self.treeview_mapping_classes.append(name)
			
			self.unsaved_work = True
	
	def remove_mapping_class(self, name):
		name_inverse = name.swapcase()
		if name in self.treeview_mapping_classes:
			if tkMessageBox.showwarning('Remove mapping class', 'Remove existing mapping class %s?' % name, type='yesno') == 'yes':
				self.equipped_triangulation.pos_mapping_classes.pop(name)
				self.equipped_triangulation.neg_mapping_classes.pop(name_inverse)
				self.equipped_triangulation.mapping_classes.pop(name)
				self.equipped_triangulation.mapping_classes.pop(name_inverse)
				
				[entry] = [child for child in self.treeview_objects.get_children('mapping_classes') if self.mapping_class_names[child] == name]
				self.treeview_objects.delete(entry)
				self.mapping_class_names = dict((iid, m_name) for iid, m_name in self.mapping_class_names.items() if m_name != name)
				self.treeview_mapping_classes.remove(name)
			else:
				return False
		
		return True
	
	def save(self):
		path = tkFileDialog.asksaveasfilename(defaultextension='.flp', filetypes=[('flipper files', '.flp'), ('all files', '.*')], title='Save Flipper File')
		if path != '':
			try:
				spec = 'A flipper file.'
				version = flipper.__version__
				vertices = [(vertex[0], vertex[1]) for vertex in self.vertices]
				edges = [(self.vertices.index(edge[0]), self.vertices.index(edge[1]), edge.index, self.edges.index(edge.equivalent_edge) if edge.equivalent_edge is not None else None) for edge in self.edges]
				equipped_triangulation = self.equipped_triangulation
				canvas_objects = (vertices, edges)
				data = (equipped_triangulation, canvas_objects)
				
				pickled_objects = pickle.dumps((spec, version, data))
				open(path, 'wb').write(pickled_objects)
				self.unsaved_work = False
				return True
			except IOError:
				tkMessageBox.showwarning('Save Error', 'Could not open: %s' % path)
		
		return False
	
	def load(self, load_from=None):
		''' Load up some information.
		
		We can load from:
			- the path to a flipper file,
			- the contents of flipper file,
			- a file objects, or
			- something that flipper.package can eat.
		If given nothing it asks the user to select a flipper (kernel) file.
		
		asks for a flipper (kernel) file. Alternatively can be passed the contents of
		a file, a file object or something that flipper.package can eat. '''
		try:
			if load_from is None:
				load_from = tkFileDialog.askopenfilename(
					defaultextension='.flp',
					filetypes=[('flipper files', '.flp'), ('all files', '.*')],
					title='Open flipper File')
				if load_from == '':  # Cancelled the dialog.
					return
				string_contents = open(load_from, 'rb').read()
			elif isinstance(load_from, file):
				string_contents = load_from.read()
			elif isinstance(load_from, flipper.StringType):
				try:
					string_contents = open(load_from, 'rb').read()
				except IOError:
					string_contents = load_from
			else:
				string_contents = flipper.package(load_from)
			
			try:
				spec, version, data = pickle.loads(string_contents)
			except AttributeError:
				raise ValueError('Not a valid flipper file.')
			if version != flipper.__version__:
				raise ValueError('This file was created in flipper %s and cannot be opened in flipper %s.' % (version, flipper.__version__))
			if spec == 'A flipper file.':
				equipped_triangulation, (vertices, edges) = data
			elif spec == 'A flipper kernel file.':
				equipped_triangulation = data
				triangulation = equipped_triangulation.triangulation
				
				# We don't have any vertices or edges, so see if we can use the current triangulation's.
				if self.equipped_triangulation is not None and triangulation.is_isometric_to(self.equipped_triangulation.triangulation):
					isom = self.equipped_triangulation.triangulation.isometries_to(triangulation)[0]
					vertices = [(vertex[0], vertex[1]) for vertex in self.vertices]
					edges = [(self.vertices.index(edge[0]), self.vertices.index(edge[1]), isom.index_map[edge.index], self.edges.index(edge.equivalent_edge) if edge.equivalent_edge is not None else None) for edge in self.edges]
				else:  # If not then we'll create a triangulation ourselves.
					vertices, edges = [], []
					
					n = triangulation.num_triangles
					ngon = n + 2
					self.parent.update_idletasks()
					w = int(self.canvas.winfo_width())
					h = int(self.canvas.winfo_height())
					r = min(w, h) * (1 + self.options.zoom_fraction) / 4
					
					# Create the vertices.
					for i in range(ngon):
						vertices.append((w / 2 + r * sin(2 * pi * (i + 0.5) / ngon), h / 2 + r * cos(2 * pi * (i + 0.5) / ngon)))
					
					# Get a dual tree.
					_, dual_tree = equipped_triangulation.triangulation.tree_and_dual_tree()
					
					def num_descendants(edge_label):
						''' Return the number of triangles that can be reached in the dual tree starting at the given edge_label. '''
						
						corner = triangulation.corner_of_edge(edge_label)
						left = (1 + sum(num_descendants(~(corner.labels[2])))) if dual_tree[corner.indices[2]] else 0
						right = (1 + sum(num_descendants(~(corner.labels[1])))) if dual_tree[corner.indices[1]] else 0
						
						return left, right
					
					initial_edge_index = min(i for i in range(triangulation.zeta) if not dual_tree[i])
					to_extend = [(0, 1, initial_edge_index)]
					edges = [(0, 1, initial_edge_index, None)]
					while to_extend:
						source_vertex, target_vertex, label = to_extend.pop()
						left, right = num_descendants(label)
						corner = triangulation.corner_of_edge(label)
						
						edges.append((target_vertex + left + 1, target_vertex, corner.indices[2], None))
						edges.append((source_vertex, target_vertex + left + 1, corner.indices[1], None))
						
						if left > 0:
							to_extend.append((target_vertex + left + 1, target_vertex, ~(corner.labels[2])))
						
						if right > 0:
							to_extend.append((source_vertex, target_vertex + left + 1, ~(corner.labels[1])))
					
					for i, j in combinations(range(len(edges)), r=2):
						if edges[i][2] == edges[j][2]:
							edges[i] = (edges[i][0], edges[i][1], edges[i][2], j)
							edges[j] = (edges[j][0], edges[j][1], edges[j][2], i)
			else:
				raise ValueError('Not a valid specification.')
			
			if not self.initialise():
				return
			
			# Create the vertices.
			for vertex in vertices:
				self.create_vertex(vertex)
			
			# Create the edges.
			for edge in edges:
				start_index, end_index, edge_index, glued_to_index = edge
				self.create_edge(self.vertices[start_index], self.vertices[end_index])
			
			# Create the edge identifications.
			for index, edge in enumerate(edges):
				start_index, end_index, edge_index, glued_to_index = edge
				if glued_to_index is not None and glued_to_index > index:
					self.create_edge_identification(self.edges[index], self.edges[glued_to_index])
			
			# Set the correct edge indices.
			for index, edge in enumerate(edges):
				start_index, end_index, edge_index, glued_to_index = edge
				self.edges[index].index = edge_index
			self.zoom_to_drawing()
			
			self.equipped_triangulation = equipped_triangulation
			
			for name, lamination in sorted(self.equipped_triangulation.laminations.items()):
				self.add_lamination(lamination, name)
			
			for name, mapping_class in sorted(self.equipped_triangulation.pos_mapping_classes.items()):
				self.add_mapping_class(mapping_class, name)
			
			self.unsaved_work = False
		except (IndexError, ValueError):
			tkMessageBox.showerror('Load Error', 'Cannot initialise flipper %s from this.' % flipper.__version__)
	
	def load_example(self):
		example = flipper.app.get_choice('Open example.', 'Choose example surface to open.', [
			'S_{0,4}',
			'S_{1,1}',
			'S_{1,2}',
			'S_{2,1}',
			'S_{3,1}'])
		if example is not None:
			self.load(flipper.load.equipped_triangulation(example.replace('{', '').replace('}', '').replace(',', '_')))
	
	def export_image(self):
		path = tkFileDialog.asksaveasfilename(defaultextension='.ps', filetypes=[('postscript files', '.ps'), ('all files', '.*')], title='Export Image')
		if path != '':
			try:
				self.canvas.postscript(file=path, colormode='color')
			except IOError:
				tkMessageBox.showwarning('Export Error', 'Could not open: %s' % path)
	
	def export_kernel_file(self):
		if self.is_complete():
			path = tkFileDialog.asksaveasfilename(defaultextension='.flp', filetypes=[('flipper kernel file', '.flp'), ('all files', '.*')], title='Export Kernel File')
			if path != '':
				try:
					example = flipper.package(self.equipped_triangulation)
					with open(path, 'wb') as disk_file:
						disk_file.write(example)
				except IOError:
					tkMessageBox.showwarning('Export Error', 'Could not open: %s' % path)
				finally:
					disk_file.close()
		else:
			tkMessageBox.showwarning('Export Error', 'Cannot export incomplete surface.')
	
	def quit(self):
		# If we are complete then write down our current state in the return slot.
		if self.is_complete() and self.return_slot is not None:
			self.return_slot[0] = self.equipped_triangulation
		
		if self.initialise():
			self.parent.quit()
	
	def show_help(self):
		flipper.doc.open_documentation()
	
	def show_about(self):
		tkMessageBox.showinfo('About', 'flipper (Version %s).\nCopyright (c) Mark Bell 2013.' % flipper.__version__)
	
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
	
	def zoom_in(self):
		self.zoom_centre(1.05)
	
	def zoom_out(self):
		self.zoom_centre(0.95)
	
	def zoom_centre(self, scale):
		self.parent.update_idletasks()
		cw = int(self.canvas.winfo_width())
		ch = int(self.canvas.winfo_height())
		self.translate(-cw / 2, -ch / 2)
		self.zoom(scale)
		self.translate(cw / 2, ch / 2)
	
	def zoom_to_drawing(self):
		self.parent.update_idletasks()
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
	
	def redraw(self):
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
		# We can only ever select vertices, edges and curve_components.
		assert(selected_object is None or \
			isinstance(selected_object, (flipper.app.CanvasVertex, flipper.app.CanvasEdge, flipper.app.CurveComponent)))
		self.selected_object = selected_object
		for x in self.vertices + self.edges + self.curve_components + self.train_track_blocks:
			x.set_current_colour()
		if self.selected_object is not None:
			self.selected_object.set_current_colour(DEFAULT_SELECTED_COLOUR)
	
	
	######################################################################
	
	
	def initialise_radial_n_gon(self):
		gluing = flipper.app.get_input('Surface specification', 'New specification for radial ngon:', validate=self.valid_specification)
		if gluing is not None:
			if self.initialise():
				n = len(gluing)
				self.parent.update_idletasks()
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
		gluing = flipper.app.get_input('Surface specification', 'New specification for ngon:', validate=self.valid_specification)
		if gluing is not None:
			if self.initialise():
				n = len(gluing)
				self.parent.update_idletasks()
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
					if gluing[i] == gluing[j].swapcase():
						self.create_edge_identification(self.edges[i], self.edges[j])
				
				self.unsaved_work = True
	
	def show_surface_information(self):
		if self.is_complete():
			num_marked_points = self.equipped_triangulation.triangulation.num_vertices
			euler_characteristic = self.equipped_triangulation.triangulation.euler_characteristic
			genus = (2 - euler_characteristic - num_marked_points) // 2
			tkMessageBox.showinfo('Surface information', 'Underlying surface has genus %d and %d marked point(s). (Euler characteristic %d.)' % (genus, num_marked_points, euler_characteristic))
		else:
			tkMessageBox.showwarning('Surface information', 'Cannot compute information about an incomplete surface.')
	
	
	######################################################################
	
	
	def create_vertex(self, point):
		self.vertices.append(flipper.app.CanvasVertex(self.canvas, point, self.options))
		self.unsaved_work = True
		self.redraw()
		self.build_equipped_triangulation()
		return self.vertices[-1]
	
	def destroy_vertex(self, vertex=None):
		if vertex is None: vertex = self.vertices[-1]
		if self.selected_object == vertex: self.select_object(None)
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
		self.build_equipped_triangulation()
	
	def destroy_all_vertices(self):
		while self.vertices:
			self.destroy_vertex()
		self.build_equipped_triangulation()
	
	def create_edge(self, v1, v2):
		# Don't create a new edge if one already exists.
		if any(set([edge[0], edge[1]]) == set([v1, v2]) for edge in self.edges):
			return None
		
		# Don't create a new edge if it would intersect one that already exists.
		if any(flipper.app.lines_intersect(edge[0], edge[1], v1, v2, self.options.float_error, True)[1] for edge in self.edges):
			return None
		
		e0 = flipper.app.CanvasEdge(self.canvas, [v1, v2], self.options)
		self.edges.append(e0)
		# Add in any needed triangles.
		for e1, e2 in combinations(self.edges, r=2):
			if e1 != e0 and e2 != e0:
				if e1.free_sides() > 0 and e2.free_sides() > 0:
					if len(set([e[0] for e in [e0, e1, e2]] + [e[1] for e in [e0, e1, e2]])) == 3:
						self.create_triangle(e0, e1, e2)
		self.unsaved_work = True
		self.redraw()
		self.build_equipped_triangulation()
		return self.edges[-1]
	
	def destroy_edge(self, edge=None):
		if edge is None: edge = self.edges[-1]
		if self.selected_object == edge: self.select_object(None)
		self.canvas.delete(edge.drawn)
		for triangle in edge.in_triangles:
			self.destroy_triangle(triangle)
		self.destroy_edge_identification(edge)
		self.edges.remove(edge)
		self.unsaved_work = True
		self.redraw()
		self.build_equipped_triangulation()
	
	def create_triangle(self, e1, e2, e3):
		assert(e1 != e2 and e1 != e3 and e2 != e3)
		
		if any([set(triangle.edges) == set([e1, e2, e3]) for triangle in self.triangles]):
			return None
		
		new_triangle = flipper.app.CanvasTriangle(self.canvas, [e1, e2, e3], self.options)
		self.triangles.append(new_triangle)
		
		corner_vertices = [e[0] for e in [e1, e2, e3]] + [e[1] for e in [e1, e2, e3]]
		if any(vertex in new_triangle and vertex not in corner_vertices for vertex in self.vertices):
			self.destroy_triangle(new_triangle)
			return None
		
		self.unsaved_work = True
		self.redraw()
		self.build_equipped_triangulation()
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
		self.build_equipped_triangulation()
	
	def create_edge_identification(self, e1, e2):
		assert(e1.equivalent_edge is None and e2.equivalent_edge is None)
		assert(e1.free_sides() == 1 and e2.free_sides() == 1)
		e1.equivalent_edge, e2.equivalent_edge = e2, e1
		# Now orient the edges so they match.
		[t1], [t2] = e1.in_triangles, e2.in_triangles
		[s1], [s2] = [i for i in range(3) if t1.edges[i] == e1], [i for i in range(3) if t2.edges[i] == e2]
		if e1[0] != t1[s1 + 1]: e1.flip_orientation()  # Set e1 to agree with the orientation of the triangle containing it,
		if e2[0] != t2[s2 + 2]: e2.flip_orientation()  # and e2 to disagree.
		
		# Change colour.
		new_colour = self.colour_picker.get_colour()
		e1.set_colour(new_colour)
		e2.set_colour(new_colour)
		self.unsaved_work = True
		self.build_equipped_triangulation()
	
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
		self.build_equipped_triangulation()
	
	def create_curve_component(self, vertices, multiplicity=1, counted=False):
		self.curve_components.append(flipper.app.CurveComponent(self.canvas, vertices, self.options, multiplicity, counted))
		return self.curve_components[-1]
	
	def destory_curve_component(self, curve_component):
		if self.selected_object == curve_component: self.select_object(None)
		self.canvas.delete(curve_component.drawn)
		self.curve_components.remove(curve_component)
	
	def create_train_track_block(self, vertices, multiplicity=1, counted=False):
		self.train_track_blocks.append(flipper.app.TrainTrackBlock(self.canvas, vertices, self.options, multiplicity, counted))
		return self.train_track_blocks[-1]
	
	def destroy_train_track_block(self, curve_component):
		self.canvas.delete(curve_component.drawn)
		self.train_track_blocks.remove(curve_component)
	
	def destroy_lamination(self):
		while self.curve_components != []:
			self.destory_curve_component(self.curve_components[-1])
		
		while self.train_track_blocks != []:
			self.destroy_train_track_block(self.train_track_blocks[-1])
		
		if self.is_complete():
			self.current_lamination = self.equipped_triangulation.triangulation.empty_lamination()
		
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
				self.canvas.create_text((edge[0][0] + edge[1][0]) / 2, (edge[0][1] + edge[1][1]) / 2, text='%s' % lamination[edge.index], tag='edge_label', font=self.options.canvas_font, fill=DEFAULT_EDGE_LABEL_COLOUR)
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
	
	def create_equipped_triangulation(self):
		# Must start by calling self.set_edge_indices() so that self.zeta is correctly set.
		self.set_edge_indices()
		labels = [[triangle.edges[side].index if triangle[side+1] == triangle.edges[side][0] else ~triangle.edges[side].index for side in range(3)] for triangle in self.triangles]
		self.equipped_triangulation = flipper.kernel.EquippedTriangulation(flipper.create_triangulation(labels), [], [])
		self.current_lamination = self.equipped_triangulation.triangulation.empty_lamination()
		self.create_edge_labels()
		self.menubar.entryconfig('Lamination', state='normal')
		self.menubar.entryconfig('Mapping class', state='normal')
	
	def destroy_equipped_triangulation(self):
		self.destroy_lamination()
		self.clear_edge_indices()
		self.destroy_edge_labels()
		self.equipped_triangulation = None
		self.current_lamination = None
		self.lamination_names = {}
		self.treeview_laminations = []
		self.mapping_class_names = {}
		self.treeview_mapping_classes = []
		for child in self.treeview_objects.get_children('laminations') + self.treeview_objects.get_children('mapping_classes'):
			self.treeview_objects.delete(child)
		self.menubar.entryconfig('Lamination', state='disabled')
		self.menubar.entryconfig('Mapping class', state='disabled')
	
	def build_equipped_triangulation(self):
		if self.is_complete() and self.equipped_triangulation is None:
			self.create_equipped_triangulation()
		elif not self.is_complete() and self.equipped_triangulation is not None:
			self.destroy_equipped_triangulation()
	
	
	######################################################################
	
	
	def canvas_to_lamination(self):
		vector = [0] * self.zeta
		
		# This version takes into account bigons between interior edges.
		for curve in self.curve_components:
			if not curve.counted:
				meets = []  # We store (index of edge intersection, should we double count).
				for i in range(len(curve.vertices)-1):
					this_segment_meets = [(flipper.app.lines_intersect(curve.vertices[i], curve.vertices[i+1], edge[0], edge[1], self.options.float_error, edge.equivalent_edge is None), edge.index) for edge in self.edges]
					for (d, double), index in sorted(this_segment_meets):
						if d >= -self.options.float_error:
							if len(meets) > 0 and meets[-1][0] == index:
								meets.pop()
							else:
								meets.append((index, double))
				
				for index, double in meets:
					vector[index] += (2 if double else 1) * curve.multiplicity
				
				curve.counted = True
		
		if all(isinstance(x, flipper.IntegerType) and x % 2 == 0 for x in vector):
			vector = [i // 2 for i in vector]
		else:
			vector = [i / 2 for i in vector]
		
		current_vector = self.current_lamination.vector
		new_vector = [a+b for a, b in zip(vector, current_vector)]
		try:
			self.current_lamination = self.equipped_triangulation.triangulation.lamination(new_vector)
		except TypeError:
			self.current_lamination = self.equipped_triangulation.triangulation.empty_lamination()
		
		return self.current_lamination
	
	def lamination_to_canvas(self, lamination):
		self.destroy_lamination()
		
		# Choose the right way to render this lamination.
		if not lamination.is_multicurve() or lamination.weight() > MAX_DRAWABLE:
			if self.options.render_lamination == flipper.app.options.RENDER_LAMINATION_FULL:
				render = flipper.app.options.RENDER_LAMINATION_W_TRAIN_TRACK
			else:
				render = self.options.render_lamination
		else:
			render = self.options.render_lamination
		
		# We'll do everything with floats now because these are accurate enough for drawing to the screen with.
		vb = self.options.vertex_buffer  # We are going to use this a lot.
		a_weights = [float(x) for x in lamination]
		if render == flipper.app.options.RENDER_LAMINATION_W_TRAIN_TRACK:
			master_scale = max(a_weights)
			if master_scale == 0: master_scale = float(1)
		
		for triangle in self.triangles:
			a_tri_weights = [a_weights[edge.index] for edge in triangle.edges]
			a_dual_weights = [(a_tri_weights[(j+1)%3] + a_tri_weights[(j+2)%3] - a_tri_weights[(j+0)%3]) / 2 for j in range(3)]
			for i in range(3):
				a = triangle[i-1] - triangle[i]
				b = triangle[i-2] - triangle[i]
				
				if render == flipper.app.options.RENDER_LAMINATION_W_TRAIN_TRACK:
					if a_dual_weights[i] > 0.00001:  # Should be 0 but we have a floating point approximation.
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
				elif render == flipper.app.options.RENDER_LAMINATION_FULL:  # We can ONLY use this method when the lamination is a multicurve.
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
				elif render == flipper.app.options.RENDER_LAMINATION_C_TRAIN_TRACK:
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
			lamination = self.canvas_to_lamination()
			self.lamination_to_canvas(lamination)
	
	def store_lamination(self, lamination=None):
		if self.is_complete():
			if lamination is None:  # Use the one currently drawn.
				lamination = self.canvas_to_lamination()
			
			name = flipper.app.get_input('Name', 'New lamination name:', validate=self.valid_name)
			if name is not None:
				self.add_lamination(lamination, name)
	
	def store_twist(self, lamination=None):
		if self.is_complete():
			if lamination is None:  # Use the one currently drawn.
				lamination = self.canvas_to_lamination()
			
			if lamination.is_twistable():
				name = flipper.app.get_input('Name', 'New twist name:', validate=self.valid_name)
				if name is not None:
					self.add_mapping_class(lamination.encode_twist(), name)
			else:
				tkMessageBox.showwarning('Curve', 'Cannot twist about this, it is not a curve with punctured complementary regions.')
	
	def store_halftwist(self, lamination=None):
		if self.is_complete():
			if lamination is None:  # Use the one currently drawn.
				lamination = self.canvas_to_lamination()
			
			if lamination.is_halftwistable():
				name = flipper.app.get_input('Name', 'New half twist name:', validate=self.valid_name)
				if name is not None:
					self.add_mapping_class(lamination.encode_halftwist(), name)
			else:
				tkMessageBox.showwarning('Curve', 'Cannot half-twist about this, it is not an essential curve bounding a pair of pants with a punctured complement.')
	
	def store_isometry(self):
		if self.is_complete():
			specification = flipper.app.get_input('Isometry specification', 'New isometry:', validate=self.valid_isometry)
			if specification is not None:
				from_edges, to_edges = zip(*[[int(d) for d in x.split(':')] for x in specification.split(' ')])
				try:
					# Some of this should really go in self.valid_isometry.
					isometries_to = self.equipped_triangulation.triangulation.self_isometries()
					[isometry] = [isom for isom in isometries_to if all(isom.index_map[from_edge] == to_edge for from_edge, to_edge in zip(from_edges, to_edges))]
				except ValueError:
					tkMessageBox.showwarning('Isometry', 'Information does not specify a unique isometry.')
				else:
					name = flipper.app.get_input('Name', 'New isometry name:', validate=self.valid_name)
					if name is not None:
						self.add_mapping_class(isometry.encode(), name)
	
	def create_composition(self):
		# Assumes that each of the named mapping classes exist.
		if self.is_complete():
			composition = flipper.app.get_input('Composition', 'New composition:', validate=self.valid_composition)
			if composition is not None:
				# self.valid_composition made sure that this wont fail.
				mapping_class = self.equipped_triangulation.mapping_class(composition)
				
				return composition, mapping_class
			else:
				return None, None
	
	def store_composition(self):
		if self.is_complete():
			_, mapping_class = self.create_composition()
			if mapping_class is not None:
				name = flipper.app.get_input('Name', 'New composition name:', validate=self.valid_name)
				if name is not None:
					self.add_mapping_class(mapping_class, name)
	
	def show_apply(self, mapping_class=None):
		if self.is_complete():
			lamination = self.canvas_to_lamination()
			if mapping_class is None:
				_, mapping_class = self.create_composition()
			
			if mapping_class is not None:
				self.lamination_to_canvas(mapping_class(lamination))
	
	
	######################################################################
	
	
	def order(self):
		if self.is_complete():
			composition, mapping_class = self.create_composition()
			if mapping_class is not None:
				order = mapping_class.order()
				order_string = 'Infinite' if order == 0 else str(order)
				tkMessageBox.showinfo('Order', '%s order: %s.' % (composition, order_string))
	
	def nielsen_thurston_type(self):
		if self.is_complete():
			composition, mapping_class = self.create_composition()
			if mapping_class is not None:
				try:
					nielsen_thurston_type = flipper.app.apply_progression(mapping_class.nielsen_thurston_type)
					tkMessageBox.showinfo('Nielsen-Thurston type', '%s is %s.' % (composition, nielsen_thurston_type))
				except flipper.ComputationError:
					tkMessageBox.showerror('Mapping class', 'Could not find any projectively invariant laminations of %s, it is probably reducible.' % composition)
				except flipper.AbortError:
					pass
	
	
	######################################################################
	
	
	def invariant_lamination(self):
		if self.is_complete():
			composition, mapping_class = self.create_composition()
			if mapping_class is not None:
				try:
					_, lamination = flipper.app.apply_progression(mapping_class.invariant_lamination)
				except flipper.AssumptionError:
					tkMessageBox.showwarning('Lamination', 'Cannot find any projectively invariant laminations of %s, it is not pseudo-Anosov.' % composition)
				except flipper.ComputationError:
					tkMessageBox.showwarning('Lamination', 'Could not find any projectively invariant laminations of %s. It is probably reducible.' % composition)
				else:
					self.lamination_to_canvas(lamination)
	
	def build_bundle(self):
		if self.is_complete():
			composition, mapping_class = self.create_composition()
			if mapping_class is not None:
				path = tkFileDialog.asksaveasfilename(defaultextension='.tri', filetypes=[('SnapPy Files', '.tri'), ('all files', '.*')], title='Export SnapPy Triangulation')
				if path != '':
					try:
						try:
							splittings = mapping_class.splitting_sequences()
						except flipper.AssumptionError:
							tkMessageBox.showwarning('Lamination', 'Cannot build bundle, %s is not pseudo-Anosov.' % composition)
						except flipper.ComputationError:
							tkMessageBox.showwarning('Lamination', 'Could not build bundle, %s is probably reducible.' % composition)
						else:
							# There may be more than one isometry, for now let's just pick the first. We'll worry about this eventually.
							splitting = splittings[0]
							bundle = splitting.bundle()
							with open(path, 'wb') as disk_file:
								disk_file.write(bundle.snappy_string())
							description = 'It was built using the first of %d isometries.\n' % len(splittings) + \
							'It has %d cusp(s) with the following properties (in order):\n' % bundle.num_cusps + \
							'Real types: %s\n' % bundle.real_cusps + \
							'Fibre slopes: %s\n' % bundle.fibre_slopes + \
							'Degeneracy slopes: %s\n' % bundle.degeneracy_slopes
							tkMessageBox.showinfo('Bundle', description)
					except IOError:
						tkMessageBox.showwarning('Save Error', 'Could not write to: %s' % path)
					finally:
						disk_file.close()
	
	
	######################################################################
	
	
	def canvas_left_click(self, event):
		self.canvas.focus_set()
		shift_pressed = (event.state & BIT_SHIFT) == BIT_SHIFT
		
		x, y = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))
		possible_object = self.object_here((x, y))
		
		if self.is_complete() and not shift_pressed:
			if self.selected_object is None:
				self.select_object(self.create_curve_component([(x, y), (x, y)]))
			elif isinstance(self.selected_object, flipper.app.CurveComponent):
				self.selected_object.append_point((x, y))
		else:
			if self.selected_object is None:
				if possible_object is None:
					self.select_object(self.create_vertex((x, y)))
				elif isinstance(possible_object, flipper.app.CanvasEdge):
					self.destroy_edge_identification(possible_object)
					if possible_object.free_sides() > 0:
						self.select_object(possible_object)
				elif isinstance(possible_object, flipper.app.CanvasVertex):
					self.select_object(possible_object)
			elif isinstance(self.selected_object, flipper.app.CanvasVertex):
				if possible_object == self.selected_object:
					self.select_object(None)
				elif possible_object is None:
					new_vertex = self.create_vertex((x, y))
					self.create_edge(self.selected_object, new_vertex)
					self.select_object(new_vertex)
				elif isinstance(possible_object, flipper.app.CanvasVertex):
					self.create_edge(self.selected_object, possible_object)
					self.select_object(possible_object)
				elif isinstance(possible_object, flipper.app.CanvasEdge):
					if possible_object.free_sides() > 0:
						self.select_object(possible_object)
			elif isinstance(self.selected_object, flipper.app.CanvasEdge):
				if possible_object == self.selected_object:
					self.select_object(None)
				elif possible_object is None:
					new_vertex = self.create_vertex((x, y))
					self.create_edge(self.selected_object[0], new_vertex)
					self.create_edge(self.selected_object[1], new_vertex)
					self.select_object(None)
				elif isinstance(possible_object, flipper.app.CanvasVertex):
					if possible_object != self.selected_object[0] and possible_object != self.selected_object[1]:
						self.create_edge(self.selected_object[0], possible_object)
						self.create_edge(self.selected_object[1], possible_object)
						self.select_object(None)
					else:
						self.select_object(possible_object)
				elif isinstance(possible_object, flipper.app.CanvasEdge):
					if (self.selected_object.free_sides() == 1 or self.selected_object.equivalent_edge is not None) and (possible_object.free_sides() == 1 or possible_object.equivalent_edge is not None):
						self.destroy_edge_identification(self.selected_object)
						self.destroy_edge_identification(possible_object)
						self.create_edge_identification(self.selected_object, possible_object)
						self.select_object(None)
					else:
						self.select_object(possible_object)
	
	def canvas_right_click(self, event):
		if self.selected_object is not None:
			if isinstance(self.selected_object, flipper.app.CurveComponent):
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
			if isinstance(self.selected_object, flipper.app.CurveComponent):
				self.selected_object.pop_point()
			
			self.select_object(None)
	
	def canvas_move(self, event):
		x, y = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))
		if isinstance(self.selected_object, flipper.app.CurveComponent):
			self.selected_object.move_point(-1, x, y)
	
	def canvas_focus_lost(self, event):
		self.select_object(None)
	
	def parent_key_press(self, event):
		key = event.keysym
		focus = self.parent.focus_get()
		if key in ('Delete', 'BackSpace'):
			if focus == self.canvas:
				if isinstance(self.selected_object, flipper.app.CanvasVertex):
					self.destroy_vertex(self.selected_object)
					self.select_object(None)
				elif isinstance(self.selected_object, flipper.app.CanvasEdge):
					self.destroy_edge(self.selected_object)
					self.select_object(None)
				elif isinstance(self.selected_object, flipper.app.CurveComponent):
					self.canvas_right_click(event)
			elif focus == self.treeview_objects:
				for iid in self.treeview_objects.selection():
					tags = self.treeview_objects.item(iid, 'tags')
					if 'lamination' in tags:
						self.remove_lamination(self.lamination_names[iid])
					elif 'mapping_class' in tags:
						self.remove_mapping_class(self.mapping_class_names[iid])
		elif key == 'Escape':
			self.canvas_right_click(event)
		elif key == 'F1':
			self.show_help()
		elif key == 'Prior' or key == 'equal' or key == 'plus':
			self.zoom_in()
		elif key == 'Next' or key == 'minus' or key == 'underscore':
			self.zoom_centre(0.95)
		elif key == '0':
			self.zoom_to_drawing()
		elif key == 'Up':
			if focus == self.canvas:
				self.translate(0, 5)
		elif key == 'Down':
			if focus == self.canvas:
				self.translate(0, -5)
		elif key == 'Left':
			if focus == self.canvas:
				self.translate(5, 0)
		elif key == 'Right':
			if focus == self.canvas:
				self.translate(-5, 0)
	
	def treeview_objects_left_click(self, event):
		iid = self.treeview_objects.identify('row', event.x, event.y)
		tags = self.treeview_objects.item(iid, 'tags')
		if iid in self.lamination_names:
			name = self.lamination_names[iid]
		elif iid in self.mapping_class_names:
			name = self.mapping_class_names[iid]
		else:
			name = None
		
		if 'show_lamination' in tags:
			self.lamination_to_canvas(self.equipped_triangulation.laminations[name])
		elif 'apply_mapping_class' in tags:
			self.show_apply(self.equipped_triangulation.mapping_classes[name])
		elif 'apply_mapping_class_inverse' in tags:
			self.show_apply(self.equipped_triangulation.mapping_classes[name.swapcase()])
	
	def treeview_objects_double_left_click(self, event):
		self.treeview_objects_left_click(event)
		iid = self.treeview_objects.identify('row', event.x, event.y)
		tags = self.treeview_objects.item(iid, 'tags')
		if iid in self.lamination_names:
			name = self.lamination_names[iid]
		elif iid in self.mapping_class_names:
			name = self.mapping_class_names[iid]
		else:
			name = None
		
		if 'twist_lamination' in tags:
			self.store_twist(self.equipped_triangulation.laminations[name])
		elif 'half_twist_lamination' in tags:
			self.store_halftwist(self.equipped_triangulation.laminations[name])
		elif 'filling_lamination' in tags:
			try:
				lamination = self.equipped_triangulation.laminations[name]
				update_cache_progression(lamination, 'is_filling')
				
				self.treeview_objects.item(iid, text='Filling: %s' % lamination.is_filling())
				self.unsaved_work = True
			except flipper.AbortError:
				pass
		elif 'mapping_class_type' in tags:
			try:
				mapping_class = self.equipped_triangulation.mapping_classes[name]
				update_cache_progression(mapping_class, 'nielsen_thurston_type')
				
				self.treeview_objects.item(iid, text='Type: %s' % mapping_class.nielsen_thurston_type())
				self.unsaved_work = True
			except flipper.ComputationError:
				tkMessageBox.showerror('Mapping class', 'Could not find any projectively invariant laminations. Mapping class is probably reducible.')
			except flipper.AbortError:
				pass
		elif 'mapping_class_invariant_lamination' in tags:
			try:
				mapping_class = self.equipped_triangulation.mapping_classes[name]
				update_cache_progression(mapping_class, 'invariant_lamination')
				
				_, lamination = mapping_class.invariant_lamination()
				self.treeview_objects.item(iid, text='Invariant lamination')
				self.lamination_to_canvas(lamination)
				self.unsaved_work = True
			except flipper.AssumptionError:
				self.unsaved_work = True
				self.treeview_objects.item(iid, text='Invariant lamination: x')
				tkMessageBox.showwarning('Lamination', 'Cannot find any projectively invariant laminations, mapping class is not pseudo-Anosov.')
			except flipper.ComputationError:
				tkMessageBox.showerror('Lamination', 'Could not find any projectively invariant laminations. Mapping class is probably reducible.')
			except flipper.AbortError:
				pass
		else:
			pass


def start(load_from=None):
	root = TK.Tk()
	root.title('flipper')
	return_slot = [None]
	flipper_app = FlipperApp(root, return_slot)
	root.minsize(300, 300)
	root.geometry('700x500')
	if load_from is not None: flipper_app.load(load_from=load_from)
	# Set the icon.
	# Make sure to get the right path if we are in a cx_Freeze compiled executable.
	# See: http://cx-freeze.readthedocs.org/en/latest/faq.html#using-data-files
	datadir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
	icon_path = os.path.join(datadir, 'icon', 'icon.gif')
	img = TK.PhotoImage(file=icon_path)
	root.tk.call('wm', 'iconphoto', root._w, img)
	root.mainloop()
	root.destroy()
	return flipper_app.return_slot[0]

if __name__ == '__main__':
	start()

