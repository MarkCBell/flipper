
try:
	import Tkinter as TK
	import tkFont as TK_FONT
except ImportError: # Python 3
	import tkinter as TK
	import tkinter.font as TK_FONT

class Options:
	def __init__(self):
		self.compress_curve = False
		self.show_internals = False
		self.debugging = False
		self.profiling = False
		self.statistics = False
		
		# Drawing parameters.
		self.epsilon = 10
		self.float_error = 0.01
		self.dilatation_error = 0.00001
		self.spacing = 10
		
		self.vertex_buffer = 0.2  # Must be in (0,0.5)
		self.n_gon_fraction = 0.45 # Must be in (0,0.5)
		
		self.dot_size = 3
		self.line_size = 2
		
		self.default_vertex_colour = 'black'
		self.default_edge_colour = 'black'
		self.default_triangle_colour = 'gray90'
		self.default_curve_colour = 'grey'
		self.default_selected_colour = 'red'
		
		self.custom_font = TK_FONT.Font(family='TkDefaultFont', size=10)


class Options_App:
	def __init__(self, host_app):
		self.host_app = host_app
		self.parent = TK.Toplevel(self.host_app.parent)
		self.parent.protocol('WM_DELETE_WINDOW', self.close_window)  # To catch when users click the 'x' to close the window.
		
		self.compress_curve_variable = TK.BooleanVar()
		self.show_internals_variable = TK.BooleanVar()
		self.logging_variable = TK.BooleanVar()
		
		self.frame = TK.Frame(self.parent)
		self.frame.pack(padx=5, pady=5, fill='both', expand=True)
		###
		self.label_draw_thickness = TK.Label(self.frame, text="Draw thickness:")
		self.label_draw_thickness.grid(row=0, column=0, sticky='w')
		
		self.scale_draw_thickness = TK.Scale(self.frame, from_=1, to=10, orient=TK.HORIZONTAL, command=self.draw_thickness_update)
		self.scale_draw_thickness.grid(row=0, column=1, sticky='e')
		
		self.check_compress_curve = TK.Checkbutton(self.frame, text='Compress curve', anchor='w', variable=self.compress_curve_variable, command=self.compress_curve_update)
		self.check_compress_curve.grid(row=1, sticky='we')
		
		self.check_show_internals = TK.Checkbutton(self.frame, text='Show internal edges', anchor='w', variable=self.show_internals_variable, command=self.show_internals_update)
		self.check_show_internals.grid(row=2, sticky='we')
		
		self.button_ok = TK.Button(self.frame, text='Ok', command=self.close_window)
		self.button_ok.grid(row=3, column=1, sticky='e')
		
		self.parent.resizable(0,0)
		###
		
		self.scale_draw_thickness.set(self.host_app.options.line_size)
		self.compress_curve_variable.set(self.host_app.options.compress_curve)
		self.show_internals_variable.set(self.host_app.options.show_internals)
	
	def draw_thickness_update(self, new_value):
		self.host_app.options.line_size = int(self.scale_draw_thickness.get())
		self.host_app.options.dot_size = int(self.scale_draw_thickness.get()) + 1
		self.host_app.options.custom_font.configure(size = int(self.scale_draw_thickness.get()) + 8)
		self.update_parent()
	
	def compress_curve_update(self):
		self.host_app.options.compress_curve = bool(self.compress_curve_variable.get())
		self.update_parent()
	
	def show_internals_update(self):
		self.host_app.options.show_internals = bool(self.show_internals_variable.get())
		self.update_parent()
	
	def update_parent(self):
		for vertex in self.host_app.vertices:
			self.host_app.canvas.coords(vertex.drawn_self, vertex.x-self.host_app.options.dot_size, vertex.y-self.host_app.options.dot_size, vertex.x+self.host_app.options.dot_size, vertex.y+self.host_app.options.dot_size)
		self.host_app.tighten_curve()
		self.host_app.canvas.itemconfig('line', width=self.host_app.options.line_size)
		self.host_app.canvas.itemconfig('curve', width=self.host_app.options.line_size)
		self.host_app.redraw()
	
	def close_window(self):
		self.parent.state('withdrawn')