
''' The main window of the flipper GUI application. '''

import flipper
import flipper.application

import re
import os
import sys
import pickle
from math import sin, cos, pi, ceil, sqrt
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
		'compose': 'Command+M'
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


def dot(a, b):
	return a[0] * b[0] + a[1] * b[1]

def helper(glob, method, args):
	result = method(*args)
	
	return glob, result

class FlipperApplication(object):
	def __init__(self, parent):
		self.parent = parent
		self.options = flipper.application.Options(self)
		self.colour_picker = flipper.application.ColourPalette()
		
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
		self.treeview_objects.insert('', 'end', 'triangulation', text='Triangulation: Incomplete', open=True, tags=['txt', 'menu'])
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
		self.filemenu.add_command(label='Open...', command=self.load, accelerator=COMMAND['open'], font=app_font)
		self.filemenu.add_command(label='Open example...', command=self.load_example, font=app_font)
		self.filemenu.add_command(label='Save...', command=self.save, accelerator=COMMAND['save'], font=app_font)
		self.exportmenu = TK.Menu(self.menubar, tearoff=0)
		self.exportmenu.add_command(label='Export image...', command=self.export_image, font=app_font)
		self.exportmenu.add_command(label='Export kernel file...', command=self.export_kernel_file, font=app_font)
		self.filemenu.add_cascade(label='Export', menu=self.exportmenu, font=app_font)
		self.filemenu.add_separator()
		self.filemenu.add_command(label='Exit', command=self.quit, accelerator=COMMAND['save'], font=app_font)
		self.menubar.add_cascade(label='File', menu=self.filemenu, font=app_font)
		
		self.editmenu = TK.Menu(self.menubar, tearoff=0)
		# Add undo and redo here.
		#self.editmenu.add_command(label='Undo', command=self.undo, accelerator=COMMAND['undo'], font=app_font)
		#self.editmenu.add_command(label='Redo', command=self.redo, accelerator=COMMAND['redo'], font=app_font)
		#self.editmenu.add_separator()
		self.editmenu.add_command(label='Tighten lamination', command=self.tighten_lamination, font=app_font)
		self.editmenu.add_command(label='Erase lamination', command=self.destroy_lamination, accelerator=COMMAND['erase'], font=app_font)
		self.menubar.add_cascade(label='Edit', menu=self.editmenu, font=app_font)
		
		self.createmenu = TK.Menu(self.menubar, tearoff=0)
		self.createmenu.add_command(label='Lamination', command=self.store_lamination, accelerator=COMMAND['lamination'], font=app_font)
		self.mappingclassmenu = TK.Menu(self.menubar, tearoff=0)
		self.mappingclassmenu.add_command(label='Twist', command=self.store_twist, accelerator=COMMAND['twist'], font=app_font)
		self.mappingclassmenu.add_command(label='Half twist', command=self.store_halftwist, accelerator=COMMAND['halftwist'], font=app_font)
		self.mappingclassmenu.add_command(label='Isometry', command=self.store_isometry, accelerator=COMMAND['isometry'], font=app_font)
		self.mappingclassmenu.add_command(label='Composition', command=self.store_composition, accelerator=COMMAND['compose'], font=app_font)
		self.createmenu.add_cascade(label='Mapping class', menu=self.mappingclassmenu, font=app_font)  # state='disabled', font=app_font)
		self.menubar.add_cascade(label='Create', menu=self.createmenu, font=app_font)
		
		
		##########################################
		self.settingsmenu = TK.Menu(self.menubar, tearoff=0)
		
		self.sizemenu = TK.Menu(self.menubar, tearoff=0)
		self.sizemenu.add_radiobutton(label='Small', var=self.options.size_var, value=flipper.application.options.SIZE_SMALL, font=app_font)
		self.sizemenu.add_radiobutton(label='Medium', var=self.options.size_var, value=flipper.application.options.SIZE_MEDIUM, font=app_font)
		self.sizemenu.add_radiobutton(label='Large', var=self.options.size_var, value=flipper.application.options.SIZE_LARGE, font=app_font)
		# self.sizemenu.add_radiobutton(label='Extra large', var=self.options.size_var, value=flipper.application.options.SIZE_XLARGE, font=app_font)
		
		self.edgelabelmenu = TK.Menu(self.menubar, tearoff=0)
		self.edgelabelmenu.add_radiobutton(label=flipper.application.options.LABEL_EDGES_NONE, var=self.options.label_edges_var, font=app_font)
		self.edgelabelmenu.add_radiobutton(label=flipper.application.options.LABEL_EDGES_INDEX, var=self.options.label_edges_var, font=app_font)
		self.edgelabelmenu.add_radiobutton(label=flipper.application.options.LABEL_EDGES_GEOMETRIC, var=self.options.label_edges_var, font=app_font)
		self.edgelabelmenu.add_radiobutton(label=flipper.application.options.LABEL_EDGES_ALGEBRAIC, var=self.options.label_edges_var, font=app_font)
		
		self.laminationdrawmenu = TK.Menu(self.menubar, tearoff=0)
		self.laminationdrawmenu.add_radiobutton(label=flipper.application.options.RENDER_LAMINATION_FULL, var=self.options.render_lamination_var, font=app_font)
		self.laminationdrawmenu.add_radiobutton(label=flipper.application.options.RENDER_LAMINATION_C_TRAIN_TRACK, var=self.options.render_lamination_var, font=app_font)
		self.laminationdrawmenu.add_radiobutton(label=flipper.application.options.RENDER_LAMINATION_W_TRAIN_TRACK, var=self.options.render_lamination_var, font=app_font)
		self.laminationdrawmenu.add_separator()
		self.laminationdrawmenu.add_checkbutton(label='Draw laminations straight', var=self.options.straight_laminations_var, font=app_font)
		
		self.zoommenu = TK.Menu(self.menubar, tearoff=0)
		self.zoommenu.add_command(label='Zoom in', command=self.zoom_in, accelerator='+', font=app_font)
		self.zoommenu.add_command(label='Zoom out', command=self.zoom_out, accelerator='-', font=app_font)
		self.zoommenu.add_command(label='Zoom to drawing', command=self.zoom_to_drawing, accelerator='0', font=app_font)
		
		self.settingsmenu.add_cascade(label='Sizes', menu=self.sizemenu, font=app_font)
		self.settingsmenu.add_cascade(label='Edge label', menu=self.edgelabelmenu, font=app_font)
		self.settingsmenu.add_cascade(label='Draw lamination', menu=self.laminationdrawmenu, font=app_font)
		self.settingsmenu.add_cascade(label='Zoom', menu=self.zoommenu, font=app_font)
		self.settingsmenu.add_checkbutton(label='Show internal edges', var=self.options.show_internals_var, font=app_font)
		self.settingsmenu.add_checkbutton(label='Show edge orientations', var=self.options.show_orientations_var, font=app_font)
		
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
		self.output = None
	
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
			iid = self.treeview_objects.insert('laminations', 'end', text=name, tags=['txt', 'lamination', 'show_lamination'])
			self.lamination_names[iid] = name
			
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
				('Invariant lamination...', 'mapping_class_invariant_lamination'),
				('Conjugate to...', 'mapping_class_conjugate'),
				('Bundle...', 'mapping_class_bundle')
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
			- the contents of flipper file, or
			- something that flipper.kernel.package can eat.
		If given nothing it asks the user to select a flipper (kernel) file.
		
		asks for a flipper (kernel) file. Alternatively can be passed the contents of
		a file, a file object or something that flipper.kernel.package can eat. '''
		try:
			if load_from is None or isinstance(load_from, (file, flipper.StringType)):
				if load_from is None:
					file_path = tkFileDialog.askopenfilename(
						defaultextension='.flp',
						filetypes=[('flipper files', '.flp'), ('all files', '.*')],
						title='Open flipper File')
					if file_path == '':  # Cancelled the dialog.
						return
					try:
						string_contents = open(file_path, 'rb').read()
					except IOError:
						raise flipper.AssumptionError('Error 101: Cannot read contents of %s.' % load_from)
				elif isinstance(load_from, file):
					string_contents = load_from.read()
				elif isinstance(load_from, flipper.StringType):
					try:
						string_contents = open(load_from, 'rb').read()
					except IOError:
						string_contents = load_from
				
				try:
					spec, version, data = pickle.loads(string_contents)
				except (EOFError, AttributeError, KeyError):
					raise flipper.AssumptionError('Error 103: Cannot depickle information provided.')
				except ValueError:
					raise flipper.AssumptionError('Error 104: Invalid depickle.')
				
				if version != flipper.__version__:
					raise flipper.AssumptionError('Error 105: This file was created in an older version of flipper (%s)' % version)
				
				if spec != 'A flipper file.':
					raise flipper.AssumptionError('Error 108: Invalid specification.')
				
				try:
					equipped_triangulation, (vertices, edges) = data
				except ValueError:
					raise flipper.AssumptionError('Error 106: Invalid depickle.')
			else:
				if isinstance(load_from, flipper.kernel.EquippedTriangulation):
					equipped_triangulation = load_from
				else:
					try:
						# Creating an equippedTriangulation can raise a ValueError in a lot of different ways.
						equipped_triangulation = flipper.kernel.create_equipped_triangulation(load_from)
					except ValueError as error:
						raise flipper.AssumptionError('Error 102: Cannot package the given data:\n %s.' % error.message)
				
				triangulation = equipped_triangulation.triangulation
				# We don't have any vertices or edges, so we'll create a triangulation ourselves.
				vertices, edges = [], []
				
				# Get a dual tree.
				_, dual_tree = triangulation.tree_and_dual_tree()
				components = triangulation.components()
				num_components = len(components)
				# Make sure we get the right sizes of things.
				self.parent.update_idletasks()
				w = int(self.canvas.winfo_width())
				h = int(self.canvas.winfo_height())
				
				# We will layout the components in a p x q grid.
				# Aim to maximise r === min(w / p, h / q) subject to pq >= num_components.
				# Note that there is probably a closed formula for the optimal value of p (and so q).
				p = max(range(1, num_components+1), key=lambda p: min(w / p, h / ceil(float(num_components) / p)))
				q = int(ceil(float(num_components) / p))
				
				r = min(w / p, h / q) * (1 + self.options.zoom_fraction) / 4
				dx = w / p
				dy = h / q
				
				num_used_vertices = 0
				for index, component in enumerate(components):
					# Get the number of triangles.
					n = len(component) // 3  # Remember component double counts edges.
					ngon = n + 2
					
					# Create the vertices.
					for i in range(ngon):
						vertices.append((
							dx * (index % p) + dx / 2 + r * sin(2 * pi * (i + 0.5) / ngon),
							dy * int(index / p) + dy / 2 + r * cos(2 * pi * (i + 0.5) / ngon)
							))
					
					def num_descendants(edge_label):
						''' Return the number of triangles that can be reached in the dual tree starting at the given edge_label. '''
						
						corner = triangulation.corner_of_edge(edge_label)
						left = (1 + sum(num_descendants(~(corner.labels[2])))) if dual_tree[corner.indices[2]] else 0
						right = (1 + sum(num_descendants(~(corner.labels[1])))) if dual_tree[corner.indices[1]] else 0
						
						return left, right
					
					initial_edge_index = min(i for i in component if i >= 0 and not dual_tree[i])
					to_extend = [(num_used_vertices, num_used_vertices+1, initial_edge_index)]
					# Hmmm, need to be more careful here to ensure that we correctly orient the edges.
					edges.append((num_used_vertices+1, num_used_vertices+0, initial_edge_index, None))
					while to_extend:
						source_vertex, target_vertex, label = to_extend.pop()
						left, right = num_descendants(label)
						far_vertex = target_vertex + left + 1
						corner = triangulation.corner_of_edge(label)
						
						if corner.labels[2] == corner.indices[2]:
							edges.append((far_vertex, target_vertex, corner.indices[2], None))
						else:
							edges.append((target_vertex, far_vertex, corner.indices[2], None))
						if corner.labels[1] == corner.indices[1]:
							edges.append((source_vertex, far_vertex, corner.indices[1], None))
						else:
							edges.append((far_vertex, source_vertex, corner.indices[1], None))
						
						if left > 0:
							to_extend.append((far_vertex, target_vertex, ~(corner.labels[2])))
						
						if right > 0:
							to_extend.append((source_vertex, far_vertex, ~(corner.labels[1])))
					num_used_vertices = len(vertices)
				
				# Glue together sides with the same index.
				for i, j in combinations(range(len(edges)), r=2):
					if edges[i][2] == edges[j][2]:
						edges[i] = (edges[i][0], edges[i][1], edges[i][2], j)
						edges[j] = (edges[j][0], edges[j][1], edges[j][2], i)
			
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
			
			self.equipped_triangulation = equipped_triangulation
			
			self.zoom_to_drawing()
			
			
			for name, lamination in sorted(self.equipped_triangulation.laminations.items(),
				key=lambda x: (len(x[0]), x[0])):
				self.add_lamination(lamination, name)
			
			for name, mapping_class in sorted(self.equipped_triangulation.pos_mapping_classes.items(),
				key=lambda x: (len(x[0]), x[0])):
				self.add_mapping_class(mapping_class, name)
			
			# Get the correct empty lamination.
			self.destroy_lamination()
			
			self.unsaved_work = False
		except (flipper.AssumptionError, IndexError, ValueError) as error:
			tkMessageBox.showerror('Load Error', error.message)
	
	def load_example(self):
		example = flipper.application.get_choice('Open example.', 'Choose example to open.', [
			'Circular n-gon',
			'Radial n-gon',
			'From isomorphism signature',
			'S_{0,4}',
			'S_{1,1}',
			'S_{1,2}',
			'S_{2,1}',
			'S_{3,1}',
			'S_{4,1}',
			'S_{5,1}'])
		if example == 'Circular n-gon':
			self.initialise_circular_n_gon()
		elif example == 'Radial n-gon':
			self.initialise_radial_n_gon()
		elif example == 'From isomorphism signature':
			signature = flipper.application.get_input('Triangulation specification', 'Isomorphism signature:')
			if signature is not None:
				try:
					self.load([flipper.triangulation_from_iso_sig(signature)])
				except AssertionError:
					tkMessageBox.showerror('Load Error', 'Invalid isomorphism signature.')
		elif example == 'S_{0,4}':
			self.load(flipper.load('S_0_4'))
		elif example == 'S_{1,1}':
			self.load(flipper.load('S_1_1'))
		elif example == 'S_{1,2}':
			self.load(flipper.load('S_1_2'))
		elif example == 'S_{2,1}':
			self.load(flipper.load('S_2_1'))
		elif example == 'S_{3,1}':
			self.load(flipper.load('S_3_1'))
		elif example == 'S_{4,1}':
			self.load(flipper.load('S_4_1'))
		elif example == 'S_{5,1}':
			self.load(flipper.load('S_5_1'))
	
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
					example = flipper.kernel.package(self.equipped_triangulation)
					with open(path, 'wb') as disk_file:
						disk_file.write(example)
				except IOError:
					tkMessageBox.showwarning('Export Error', 'Could not open: %s' % path)
				finally:
					disk_file.close()
		else:
			tkMessageBox.showwarning('Export Error', 'Cannot export incomplete surface.')
	
	def quit(self):
		# Write down our current state for output. If we are incomplete then this is just None.
		self.output = self.equipped_triangulation
		
		if self.initialise():
			# Apparantly there are some problems with comboboxes, see:
			#  http://stackoverflow.com/questions/15448914/python-tkinter-ttk-combobox-throws-exception-on-quit
			self.parent.eval('::ttk::CancelRepeat')
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
	
	def object_here(self, point):
		for piece in self.vertices + self.edges + self.triangles:
			if point in piece:
				return piece
		return None
	
	def redraw(self):
		self.build_edge_labels()
		
		for vertex in self.vertices:
			vertex.update()
		self.canvas.itemconfig('line', width=self.options.line_size)
		self.canvas.itemconfig('curve', width=self.options.line_size)
		self.canvas.itemconfig('line', arrow='last' if self.options.show_orientations else '')
		self.canvas.itemconfig('line', arrowshape=self.options.arrow_shape)
		
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
			isinstance(selected_object, (flipper.application.CanvasVertex, flipper.application.CanvasEdge, flipper.application.CurveComponent)))
		self.selected_object = selected_object
		for x in self.vertices + self.edges + self.curve_components + self.train_track_blocks:
			x.set_current_colour()
		if self.selected_object is not None:
			self.selected_object.set_current_colour(DEFAULT_SELECTED_COLOUR)
	
	
	######################################################################
	
	
	def initialise_radial_n_gon(self):
		gluing = flipper.application.get_input('Surface specification', 'Boundary pattern for radial ngon:', validate=self.valid_specification)
		if gluing is not None:
			if self.initialise():
				n = len(gluing)
				self.parent.update_idletasks()
				w = int(self.canvas.winfo_width())
				h = int(self.canvas.winfo_height())
				r = min(w, h)
				
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
				
				self.zoom_to_drawing()
				
				self.unsaved_work = True
	
	def initialise_circular_n_gon(self):
		gluing = flipper.application.get_input('Surface specification', 'Boundary pattern for circular ngon:', validate=self.valid_specification)
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
				
				self.zoom_to_drawing()
				
				self.unsaved_work = True
	
	
	######################################################################
	
	
	def create_vertex(self, point):
		self.vertices.append(flipper.application.CanvasVertex(self.canvas, point, self.options))
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
		# Check that the vertices are distinct
		if len(set([v1, v2])) != 2:
			return None
		
		# Check that this edge doesn't already exist.
		if any(set([edge[0], edge[1]]) == set([v1, v2]) for edge in self.edges):
			return None
		
		# Check that this edge doesn't intersect an existing one.
		if any(flipper.application.lines_intersect(edge[0], edge[1], v1, v2, self.options.float_error, True)[1] for edge in self.edges):
			return None
		
		e0 = flipper.application.CanvasEdge(self.canvas, [v1, v2], self.options)
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
		self.build_equipped_triangulation()
		self.redraw()
	
	def create_triangle(self, e1, e2, e3):
		# Check that there are 3 edges.
		if len(set([e1, e2, e3])) != 3:
			return None
		
		# Check that this triangle doesn't already exist.
		if any([set(triangle.edges) == set([e1, e2, e3]) for triangle in self.triangles]):
			return None
		
		# Check that there are 3 vertices.
		corner_vertices = list(set(v for e in [e1, e2, e3] for v in e))
		if len(corner_vertices) != 3:
			return None
		
		# Check that there aren't any vertices inside the triangle.
		v0 = corner_vertices[2] - corner_vertices[0]
		v1 = corner_vertices[1] - corner_vertices[0]
		for vertex in self.vertices:
			if vertex not in corner_vertices:
				v2 = vertex - corner_vertices[0]
				
				dot00 = dot(v0, v0)
				dot01 = dot(v0, v1)
				dot02 = dot(v0, v2)
				dot11 = dot(v1, v1)
				dot12 = dot(v1, v2)
				
				invDenom = 1.0 / (dot00 * dot11 - dot01 * dot01)
				u = (dot11 * dot02 - dot01 * dot12) * invDenom
				v = (dot00 * dot12 - dot01 * dot02) * invDenom
				
				if (u >= 0) and (v >= 0) and (u + v <= 1):
					return None
		
		self.triangles.append(flipper.application.CanvasTriangle(self.canvas, [e1, e2, e3], self.options))
		
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
		if e1.equivalent_edge is not None or e2.equivalent_edge is not None:
			return None
		if e1.free_sides() != 1 or e2.free_sides() != 1:
			return None
		
		e1.equivalent_edge, e2.equivalent_edge = e2, e1
		# Now orient the edges so they match.
		[t1], [t2] = e1.in_triangles, e2.in_triangles
		[s1], [s2] = [i for i in range(3) if t1.edges[i] == e1], [i for i in range(3) if t2.edges[i] == e2]
		# Determine if the orientation of e1 (respectively e2) agrees with t1 (resp. t2).
		e1_agrees = e1[0] == t1[s1 + 1]
		e2_agrees = e2[0] == t2[s2 + 1]
		# We need one to agree and one to disagree - so if not then flip the orientation of e2.
		if e1_agrees == e2_agrees:
			e2.flip_orientation()
		
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
	
	def create_curve_component(self, vertices, multiplicity=1, smooth=False):
		self.curve_components.append(flipper.application.CurveComponent(self.canvas, vertices, self.options, multiplicity, smooth))
		return self.curve_components[-1]
	
	def destory_curve_component(self, curve_component):
		if self.selected_object == curve_component: self.select_object(None)
		self.canvas.delete(curve_component.drawn)
		self.curve_components.remove(curve_component)
	
	def create_train_track_block(self, vertices, multiplicity=1, smooth=False):
		self.train_track_blocks.append(flipper.application.TrainTrackBlock(self.canvas, vertices, self.options, multiplicity, smooth))
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
		self.destroy_edge_labels()  # Remove existing labels.
		
		# How to label the edge with given index.
		if self.options.label_edges == 'Index':
			labels = dict((index, str(index)) for index in range(self.zeta))
		elif self.options.label_edges == 'Geometric':
			labels = dict((index, self.current_lamination.geometric[index]) for index in range(self.zeta))
		elif self.options.label_edges == 'Algebraic':
			labels = dict((index, self.current_lamination.algebraic[index]) for index in range(self.zeta))
		elif self.options.label_edges == 'None':
			labels = dict((index, '') for index in range(self.zeta))
		else:
			raise ValueError()
		
		for edge in self.edges:
			self.canvas.create_text(edge.centre(),
				text=labels[edge.index],
				tag='edge_label',
				font=self.options.canvas_font,
				fill=DEFAULT_EDGE_LABEL_COLOUR)
	
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
		triangulation = self.equipped_triangulation.triangulation
		self.current_lamination = self.equipped_triangulation.triangulation.empty_lamination()
		self.create_edge_labels()
		self.treeview_objects.item('triangulation', text='Triangulation:')
		self.treeview_objects.insert('triangulation', 'end', text='Genus: %d' % triangulation.genus, tags=['txt'])
		self.treeview_objects.insert('triangulation', 'end', text='Punctures: %d' % triangulation.num_vertices, tags=['txt'])
		self.treeview_objects.insert('triangulation', 'end', text='Euler characteristic: %d' % triangulation.euler_characteristic, tags=['txt'])
		#self.menubar.entryconfig('Lamination', state='normal')
		#self.menubar.entryconfig('Mapping class', state='normal')
	
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
		self.treeview_objects.item('triangulation', text='Triangulation: Incomplete')
		self.treeview_objects.delete(*self.treeview_objects.get_children('triangulation'))
	
	def build_equipped_triangulation(self):
		if self.is_complete() and self.equipped_triangulation is None:
			self.create_equipped_triangulation()
		elif not self.is_complete() and self.equipped_triangulation is not None:
			self.destroy_equipped_triangulation()
	
	
	######################################################################
	
	
	def canvas_to_lamination(self):
		geometric = [0] * self.zeta
		
		# This version takes into account bigons between interior edges.
		for curve in self.curve_components:
			meets = []  # We store (index of edge intersection, should we double count).
			for i in range(len(curve.vertices)-1):
				this_segment_meets = [(flipper.application.lines_intersect(curve.vertices[i], curve.vertices[i+1], edge[0], edge[1], self.options.float_error, edge.equivalent_edge is None), edge.index) for edge in self.edges]
				for (d, double), index in sorted(this_segment_meets):
					if d >= -self.options.float_error:
						if len(meets) > 0 and meets[-1][0] == index:
							meets.pop()
						else:
							meets.append((index, double))
			
			for index, double in meets:
				geometric[index] += (2 if double else 1) * curve.multiplicity
		
		if all(isinstance(x, flipper.IntegerType) and x % 2 == 0 for x in geometric):
			geometric = [i // 2 for i in geometric]
		else:
			geometric = [i / 2 for i in geometric]
		
		self.current_lamination = self.equipped_triangulation.triangulation.lamination(geometric)
		
		return self.current_lamination
	
	def lamination_to_canvas(self, lamination):
		self.destroy_lamination()
		
		# Choose the right way to render this lamination.
		if not lamination.is_multicurve() or lamination.weight() > MAX_DRAWABLE:
			if self.options.render_lamination == flipper.application.options.RENDER_LAMINATION_FULL:
				render = flipper.application.options.RENDER_LAMINATION_W_TRAIN_TRACK
			else:
				render = self.options.render_lamination
		else:
			render = self.options.render_lamination
		
		# We'll do everything with floats now because these are accurate enough for drawing to the screen with.
		vb = self.options.vertex_buffer  # We are going to use this a lot.
		a_weights = [float(x) for x in lamination]
		master = float(max(a_weights))
		if master == 0: master = float(1)
		
		for triangle in self.triangles:
			a_tri_weights = [a_weights[edge.index] for edge in triangle.edges]
			a_dual_weights = [(a_tri_weights[(j+1)%3] + a_tri_weights[(j+2)%3] - a_tri_weights[(j+0)%3]) / 2 for j in range(3)]
			for i in range(3):
				a = triangle[i-1] - triangle[i]
				b = triangle[i-2] - triangle[i]
				
				if render == flipper.application.options.RENDER_LAMINATION_W_TRAIN_TRACK:
					if a_dual_weights[i] > 0.00001:  # Should be 0 but we have a floating point approximation.
						# We first do the edge to the left of the vertex.
						# Correction factor to take into account the weight on this edge.
						s_a = a_weights[triangle.edges[i-2].index] / master
						# The fractions of the distance of the two points on this edge.
						scale_a = vb * s_a + (1 - s_a) / 2
						scale_a2 = scale_a + (1 - 2*vb) * s_a * a_dual_weights[i] / (a_dual_weights[i] + a_dual_weights[i-1])
						
						# Now repeat for the other edge of the triangle.
						s_b = a_weights[triangle.edges[i-1].index] / master
						scale_b = vb * s_b + (1 - s_b) / 2
						scale_b2 = scale_b + (1 - 2*vb) * s_b * a_dual_weights[i] / (a_dual_weights[i] + a_dual_weights[i-2])
						
						S1, P1, Q1, E1 = flipper.application.interpolate(triangle[i-1], triangle[i], triangle[i-2], scale_a, scale_b)
						S2, P2, Q2, E2 = flipper.application.interpolate(triangle[i-1], triangle[i], triangle[i-2], scale_a2, scale_b2)
						if self.options.straight_laminations:
							self.create_train_track_block([S1, E1, E2, S2])
						else:
							self.create_train_track_block([S1, S1, P1, Q1, E1, E1, E2, E2, Q2, P2, S2, S2, S1, S1], smooth=True)
				elif render == flipper.application.options.RENDER_LAMINATION_FULL:  # We can ONLY use this method when the lamination is a multicurve.
					# Also it is VERY slow (O(n) not O(log(n))).
					# Here we need the exact dual weights so we had better work them out.
					weights = [lamination(edge.index) for edge in triangle.edges]
					wa, wb = weights[i-2], weights[i-1]
					dual_weights = [(weights[j-2] + weights[j-1] - weights[j]) // 2 for j in range(3)]
					for j in range(int(dual_weights[i])):
						scale_a = 0.5 if wa == 1 else vb + (1 - 2*vb) * ((wa - 1) * (master - wa) + 2 * wa * j) / (2 * (wa - 1) * master)
						scale_b = 0.5 if wb == 1 else vb + (1 - 2*vb) * ((wb - 1) * (master - wb) + 2 * wb * j) / (2 * (wb - 1) * master)
						
						S, P, Q, E = flipper.application.interpolate(triangle[i-1], triangle[i], triangle[i-2], scale_a, scale_b)
						if self.options.straight_laminations:
							self.create_curve_component([S, E])
						else:
							self.create_curve_component([S, P, Q, E], smooth=True)
				elif render == flipper.application.options.RENDER_LAMINATION_C_TRAIN_TRACK:
					if a_dual_weights[i] > 0:
						scale = 0.5
						S, P, Q, E = flipper.application.interpolate(triangle[i-1], triangle[i], triangle[i-2], scale, scale)
						if self.options.straight_laminations:
							self.create_curve_component([S, E])
						else:
							self.create_curve_component([S, P, Q, E], smooth=True)
		
		self.current_lamination = lamination
		self.create_edge_labels()
	
	def tighten_lamination(self):
		if self.is_complete():
			self.lamination_to_canvas(self.current_lamination)
	
	def store_lamination(self):
		if self.is_complete():
			name = flipper.application.get_input('Name', 'New lamination name:', validate=self.valid_name)
			if name is not None:
				self.add_lamination(self.current_lamination, name)
		else:
			tkMessageBox.showwarning('Incomplete triangulation', 'Cannot store lamination when triangulation is incomplete.')
	
	def store_twist(self):
		if self.is_complete():
			lamination = self.current_lamination
			
			if lamination.is_twistable():
				name = flipper.application.get_input('Name', 'New twist name:', validate=self.valid_name)
				if name is not None:
					self.add_mapping_class(lamination.encode_twist(), name)
			else:
				tkMessageBox.showwarning('Curve', 'Cannot twist about this, it is not a curve with punctured complementary regions.')
		else:
			tkMessageBox.showwarning('Incomplete triangulation', 'Cannot compute twist when triangulation is incomplete.')
	
	def store_halftwist(self):
		if self.is_complete():
			lamination = self.current_lamination
			
			if lamination.is_halftwistable():
				name = flipper.application.get_input('Name', 'New half twist name:', validate=self.valid_name)
				if name is not None:
					self.add_mapping_class(lamination.encode_halftwist(), name)
			else:
				tkMessageBox.showwarning('Curve', 'Cannot half-twist about this, it is not an essential curve bounding a pair of pants with a punctured complement.')
		else:
			tkMessageBox.showwarning('Incomplete triangulation', 'Cannot compute half twist when triangulation is incomplete.')
	
	def store_isometry(self):
		if self.is_complete():
			isometries = self.equipped_triangulation.triangulation.self_isometries()
			
			# Chop off the 'Isometry [' and ditch the ']'. Return at most max_char characters.
			max_char = 40
			name_shrinker = lambda strn: strn[10:].replace(']', '') if len(strn) < max_char + 11 else strn[10:7 + max_char] + '...'
			
			specification = flipper.application.get_choice('Available Isometries.', 'Use isometry mapping edges 0, 1, ... to: ',
				[name_shrinker(str(isom)) for isom in sorted(isometries, key=lambda isom: (isom(0) < 0, abs(isom(0))))])
			if specification is not None:
				[isometry] = [isom for isom in isometries if name_shrinker(str(isom)) == specification]
				name = flipper.application.get_input('Name', 'New isometry name:', validate=self.valid_name)
				if name is not None:
					self.add_mapping_class(isometry.encode(), name)
		else:
			tkMessageBox.showwarning('Incomplete triangulation', 'Cannot compute isometry when triangulation is incomplete.')
	
	def store_composition(self):
		if self.is_complete():
			composition = flipper.application.get_input('Composition', 'New composition:', validate=self.valid_composition)
			if composition is not None:
				name = flipper.application.get_input('Name', 'New composition name:', default=composition.replace('.', '_'), validate=self.valid_name)
				if name is not None:
					# self.valid_composition made sure that this wont fail.
					mapping_class = self.equipped_triangulation.mapping_class(composition)
					self.add_mapping_class(mapping_class, name)
		else:
			tkMessageBox.showwarning('Incomplete triangulation', 'Cannot compute composition when triangulation is incomplete.')
	
	
	######################################################################
	
	
	def canvas_left_click(self, event):
		self.canvas.focus_set()
		shift_pressed = (event.state & BIT_SHIFT) == BIT_SHIFT
		
		x, y = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))
		possible_object = self.object_here((x, y))
		
		if self.is_complete() and not shift_pressed:
			if self.selected_object is None:
				if possible_object is None:
					self.select_object(self.create_curve_component([(x, y), (x, y)]))
			elif isinstance(self.selected_object, flipper.application.CurveComponent):
				if possible_object is not None:
					self.selected_object.append_point((x, y))
					self.canvas_to_lamination()
				else:
					self.canvas_to_lamination()
					self.select_object(None)
		else:
			if self.selected_object is None:
				if possible_object is None:
					self.select_object(self.create_vertex((x, y)))
				elif isinstance(possible_object, flipper.application.CanvasEdge):
					self.destroy_edge_identification(possible_object)
					if possible_object.free_sides() > 0:
						self.select_object(possible_object)
				elif isinstance(possible_object, flipper.application.CanvasVertex):
					self.select_object(possible_object)
				elif isinstance(possible_object, flipper.application.CurveComponent):
					self.select_object(possible_object)
			elif isinstance(self.selected_object, flipper.application.CanvasVertex):
				if possible_object == self.selected_object:
					self.select_object(None)
				elif possible_object is None:
					new_vertex = self.create_vertex((x, y))
					self.create_edge(self.selected_object, new_vertex)
					self.select_object(new_vertex)
				elif isinstance(possible_object, flipper.application.CanvasVertex):
					self.create_edge(self.selected_object, possible_object)
					self.select_object(possible_object)
				elif isinstance(possible_object, flipper.application.CanvasEdge):
					if possible_object.free_sides() > 0:
						self.select_object(possible_object)
			elif isinstance(self.selected_object, flipper.application.CanvasEdge):
				if possible_object == self.selected_object:
					self.select_object(None)
				elif possible_object is None:
					new_vertex = self.create_vertex((x, y))
					self.create_edge(self.selected_object[0], new_vertex)
					self.create_edge(self.selected_object[1], new_vertex)
					self.select_object(None)
				elif isinstance(possible_object, flipper.application.CanvasVertex):
					if possible_object != self.selected_object[0] and possible_object != self.selected_object[1]:
						self.create_edge(self.selected_object[0], possible_object)
						self.create_edge(self.selected_object[1], possible_object)
						self.select_object(None)
					else:
						self.select_object(possible_object)
				elif isinstance(possible_object, flipper.application.CanvasEdge):
					if (self.selected_object.free_sides() == 1 or self.selected_object.equivalent_edge is not None) and (possible_object.free_sides() == 1 or possible_object.equivalent_edge is not None):
						self.destroy_edge_identification(self.selected_object)
						self.destroy_edge_identification(possible_object)
						self.create_edge_identification(self.selected_object, possible_object)
						self.select_object(None)
					else:
						self.select_object(possible_object)
	
	def canvas_right_click(self, event):
		if self.selected_object is not None:
			if isinstance(self.selected_object, flipper.application.CurveComponent):
				if len(self.selected_object.vertices) > 2:
					(x, y) = self.selected_object.vertices[-1]
					self.selected_object.pop_point()
					self.selected_object.move_point(-1, x, y)
				else:
					self.destory_curve_component(self.selected_object)
					self.select_object(None)
				self.canvas_to_lamination()
			else:
				self.select_object(None)
	
	def canvas_move(self, event):
		x, y = int(self.canvas.canvasx(event.x)), int(self.canvas.canvasy(event.y))
		if isinstance(self.selected_object, flipper.application.CurveComponent):
			self.selected_object.move_point(-1, x, y)
	
	def canvas_focus_lost(self, event):
		self.select_object(None)
	
	def parent_key_press(self, event):
		key = event.keysym
		focus = self.parent.focus_get()
		if key in ('Delete', 'BackSpace'):
			if focus == self.canvas:
				if isinstance(self.selected_object, flipper.application.CanvasVertex):
					self.destroy_vertex(self.selected_object)
					self.select_object(None)
				elif isinstance(self.selected_object, flipper.application.CanvasEdge):
					self.destroy_edge(self.selected_object)
					self.select_object(None)
				elif isinstance(self.selected_object, flipper.application.CurveComponent):
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
		elif key == 'equal' or key == 'plus':
			self.zoom_in()
		elif key == 'minus' or key == 'underscore':
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
			self.lamination_to_canvas(self.equipped_triangulation.mapping_classes[name](self.current_lamination))
		elif 'apply_mapping_class_inverse' in tags:
			self.lamination_to_canvas(self.equipped_triangulation.mapping_classes[name.swapcase()](self.current_lamination))
	
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
		
		if 'mapping_class_type' in tags:
			try:
				result = self.update_cache(self.equipped_triangulation.mapping_classes[name].nielsen_thurston_type)
				
				self.treeview_objects.item(iid, text='Type: %s' % result)
				self.unsaved_work = True
			except flipper.ComputationError:
				tkMessageBox.showerror('Mapping class', 'Could not find any projectively invariant laminations. Mapping class is probably reducible.')
			except flipper.AbortError:
				pass
		elif 'mapping_class_invariant_lamination' in tags:
			try:
				result = self.update_cache(self.equipped_triangulation.mapping_classes[name].invariant_lamination)
				
				self.lamination_to_canvas(result)
				self.unsaved_work = True
			except flipper.AssumptionError:
				tkMessageBox.showwarning('Lamination', 'Cannot find any projectively invariant laminations, mapping class is not pseudo-Anosov.')
				self.unsaved_work = True
			except flipper.ComputationError:
				tkMessageBox.showerror('Lamination', 'Could not find any projectively invariant laminations. Mapping class is probably reducible.')
			except flipper.AbortError:
				pass
		elif 'mapping_class_conjugate' in tags:
			other = flipper.application.get_choice('Conjugate.', 'Is this mapping class conjugate to...',
				sorted(set(self.mapping_class_names.values()), key=lambda x: (len(x), x)))
			if other is not None:
				try:
					result = self.update_cache(
						self.equipped_triangulation.mapping_classes[name].is_conjugate_to,
						args=(self.equipped_triangulation.mapping_classes[other],)
						)
					
					if result:
						tkMessageBox.showinfo('Conjugate', '%s and %s are conjugate.' % (name, other))
					else:
						tkMessageBox.showinfo('Conjugate', '%s and %s are not conjugate.' % (name, other))
					
					self.unsaved_work = True
				except flipper.AssumptionError:
					tkMessageBox.showwarning('Conjugate', 'Could not determine conjugacy, mapping class is not pseudo-Anosov.')
					self.unsaved_work = True
				except flipper.ComputationError:
					tkMessageBox.showerror('Conjugate', 'Could not find any projectively invariant laminations. Mapping class is probably reducible.')
				except flipper.AbortError:
					pass
		elif 'mapping_class_bundle' in tags:
			path = tkFileDialog.asksaveasfilename(defaultextension='.tri', filetypes=[('SnapPy Files', '.tri'), ('all files', '.*')], title='Export SnapPy Triangulation')
			if path != '':
				try:
					bundle = self.update_cache(self.equipped_triangulation.mapping_classes[name].bundle)
					with open(path, 'wb') as disk_file:
						disk_file.write(bundle.snappy_string())
				except flipper.AssumptionError:
					tkMessageBox.showwarning('Bundle', 'Cannot build bundle, mapping class is not pseudo-Anosov.')
				except flipper.ComputationError:
					tkMessageBox.showwarning('Bundle', 'Could not build bundle, mapping class is probably reducible.')
				except flipper.AbortError:
					pass
				except IOError:
					tkMessageBox.showwarning('Save Error', 'Could not write to: %s' % path)
		else:
			pass
	
	def update_cache(self, method, args=None):
		# So we need to be really careful here. Linux uses copy-on-write (COW) so
		# when we spawn a new thread in a progress bar if we ever do something
		# non-pure and write into that data structure a copy is taken first.
		# This means that things may not match up later as, for example, laminations
		# now exist on a copy of this triangulation.
		#
		# I guess this is a strong argument in favour of making functions / methods pure.
		
		if args is None: args = []
		self.equipped_triangulation, result = flipper.application.apply_progression(helper, args=(self.equipped_triangulation, method, args))
		
		# Don't forget that what is drawn on the canvas is still thought of as a lamination on the old triangulation.
		self.canvas_to_lamination()
		
		return result


def start(load_from=None):
	root = TK.Tk()
	root.title('flipper')
	flipper_application = FlipperApplication(root)
	root.minsize(300, 300)
	root.geometry('700x500')
	if load_from is not None: flipper_application.load(load_from=load_from)
	# Set the icon.
	# Make sure to get the right path if we are in a cx_Freeze compiled executable.
	# See: http://cx-freeze.readthedocs.org/en/latest/faq.html#using-data-files
	datadir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
	icon_path = os.path.join(datadir, 'icon', 'icon.gif')
	img = TK.PhotoImage(file=icon_path)
	root.tk.call('wm', 'iconphoto', root._w, img)
	root.mainloop()
	root.destroy()
	return flipper_application.output

if __name__ == '__main__':
	start()

