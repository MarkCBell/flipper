
try:
	import Tkinter as TK
	import tkFont as TK_FONT
except ImportError:  # Python 3.
	import tkinter as TK
	import tkinter.font as TK_FONT

try:
	import ttk as TTK
except ImportError:  # Python 3.
	from tkinter import ttk as TTK

RENDER_LAMINATION_FULL = 'Full'
RENDER_LAMINATION_W_TRAIN_TRACK = 'Weighted train track'
RENDER_LAMINATION_C_TRAIN_TRACK = 'Compressed train track'
LABEL_EDGES_NONE = 'None'
LABEL_EDGES_INDEX = 'Index'
LABEL_EDGES_GEOMETRIC = 'Geometric'
LABEL_EDGES_ALGEBRAIC = 'Algebraic'
SIZE_SMALL, SIZE_MEDIUM, SIZE_LARGE = 0, 1, 2
# SIZE_XLARGE = 3

class Options(object):
	def __init__(self, parent):
		self.parent = parent
		self.application_font = TK_FONT.Font(family='TkDefaultFont', size=10)
		self.canvas_font = TK_FONT.Font(family='TkDefaultFont', size=10)
		
		self.render_lamination_var = TK.StringVar(value=RENDER_LAMINATION_FULL)
		self.show_internals_var = TK.BooleanVar(value=False)
		self.show_orientations_var = TK.BooleanVar(value=False)
		self.straight_laminations_var = TK.BooleanVar(value=False)
		self.projectivise_var = TK.BooleanVar(value=False)
		self.label_edges_var = TK.StringVar(value=LABEL_EDGES_NONE)
		self.size_var = TK.IntVar(value=SIZE_SMALL)
		
		self.render_lamination = RENDER_LAMINATION_FULL
		self.show_internals = False
		self.show_orientations = False
		self.straight_laminations = False
		self.label_edges = LABEL_EDGES_NONE
		self.projectivise = False
		self.line_size = 2
		self.dot_size = 3
		self.arrow_shape = (12, 15, 5)
		
		# Set it so that self.update() will be called whenever these variables are changed.
		self.render_lamination_var.trace('w', self.update)
		self.show_internals_var.trace('w', self.update)
		self.show_orientations_var.trace('w', self.update)
		self.straight_laminations_var.trace('w', self.update)
		self.projectivise_var.trace('w', self.update)
		self.label_edges_var.trace('w', self.update)
		self.size_var.trace('w', self.update)
		
		# Drawing parameters.
		self.epsilon = 10
		self.float_error = 0.001
		
		self.vertex_buffer = 0.2  # Must be in (0, 0.5)
		self.zoom_fraction = 0.8 # Must be in (0, 1)
	
	def update(self, *args):
		self.render_lamination = str(self.render_lamination_var.get())
		self.show_internals = bool(self.show_internals_var.get())
		self.show_orientations = bool(self.show_orientations_var.get())
		self.straight_laminations = bool(self.straight_laminations_var.get())
		self.projectivise = bool(self.projectivise_var.get())
		self.label_edges = str(self.label_edges_var.get())
		if self.size_var.get() == SIZE_SMALL:
			self.line_size = 2
			self.dot_size = 3
			self.arrow_shape = (12, 15, 5)
			self.application_font.configure(size=10)
			self.canvas_font.configure(size=10)
		elif self.size_var.get() == SIZE_MEDIUM:
			self.line_size = 4
			self.dot_size = 5
			self.arrow_shape = (16, 20, 6)
			self.application_font.configure(size=11)
			self.canvas_font.configure(size=12)
		elif self.size_var.get() == SIZE_LARGE:
			self.line_size = 6
			self.dot_size = 7
			self.arrow_shape = (24, 30, 9)
			self.application_font.configure(size=12)
			self.canvas_font.configure(size=14)
		
		self.parent.treeview_objects.tag_configure('txt', font=self.application_font)
		TTK.Style().configure('Treeview', font=self.application_font)
		self.parent.redraw()

