
# Provides several Tkinter widgets:
#	1) Meter - a progress bar, and
#	2) SplitButton - a button with additional menu of actions.

try:
	import Tkinter as TK
	DOWN_ARROW = unichr(9660)
except ImportError:  # Python 3.
	try:
		import tkinter as TK
		DOWN_ARROW = chr(9660)
	except ImportError:
		raise ImportError('Tkinter not available.')

class SplitButton(TK.Frame):
	def __init__(self, parent, commands, **options):
		''' A SplitButton is a button with an additional
		drop down menu of other commands.
		
		It is initalised by passing a list of pairs of the form:
		(label, command). The first item in this list is
		used as the main function of the button and others are
		added to the drop down menu, this must be provided.
		
		Additional options for the underlying Frame can also be
		passed in. '''
		
		# Initalise.
		TK.Frame.__init__(self, parent, **options)
		
		# Setup controls.
		if len(commands) == 0:
			raise TypeError('At least one label and command must be provided.')
		
		# Build the widget.
		main_text, main_command = commands[0]
		self._main = TK.Button(self, text=main_text, command=main_command)
		self._more = TK.Menubutton(self, text=DOWN_ARROW, relief='raised')
		self._menu = TK.Menu(self._more, tearoff=0)
		self._more['menu'] = self._menu
		self._main.grid(column=0, row=0, sticky='nsew')
		self._more.grid(column=1, row=0, sticky='nsew', pady=1)
		
		# Add each command to the menu.
		for label, command in commands[1:]:
			self._menu.add_command(label=label, command=command)
		
		# Make it resizable with 75% of the size going to the button.
		self.columnconfigure(0, weight=3)
		self.columnconfigure(1, weight=1)
		self.rowconfigure(0, weight=1)

class Meter(TK.Frame):
	def __init__(self, master, width=300, height=20, bg='white', fillcolour='midnight blue', value=0.0, text=None, font=None, textcolour='black', *args, **kw):
		''' A simple progress bar widget for TK.
		
		INITIALIZATION OPTIONS:
		The widget subclasses a TK.Frame and adds:
		
			fillcolour -- the colour that is used to indicate the progress of the
						 corresponding process; default is "orchid1".
			value -- a float value between 0.0 and 1.0 (corresponding to 0% - 100%)
					 that represents the current status of the process; values higher
					 than 1.0 (lower than 0.0) are automagically set to 1.0 (0.0); default is 0.0 .
			text -- the text that is displayed inside the widget; if set to None the widget
					displays its value as percentage; if you don't want any text, use text="";
					default is None.
			font -- the font to use for the widget's text; the default is system specific.
			textcolour -- the colour to use for the widget's text; default is "black".
		
		WIDGET METHODS:
		All methods of a TK.Frame can be used; additionally there are two widget specific methods:
		
			get() -- returns a tuple of the form (value, text)
			set(value, text) -- updates the widget's value and the displayed text;
								if value is omitted it defaults to 0.0 , text defaults to None .
		'''
		
		TK.Frame.__init__(self, master, bg=bg, width=width, height=height, *args, **kw)
		self._value = value
		
		self._canv = TK.Canvas(self, bg=self['bg'], width=self['width'], height=self['height'], highlightthickness=0, relief='flat', bd=0)
		self._canv.pack(fill='both', expand=1)
		self._rect = self._canv.create_rectangle(0, 0, 0, self._canv.winfo_reqheight(), fill=fillcolour, width=0)
		self._text = self._canv.create_text(self._canv.winfo_reqwidth()/2, self._canv.winfo_reqheight()/2, text='', fill=textcolour)
		if font: self._canv.itemconfigure(self._text, font=font)
		
		self.set(value, text)
		self.bind('<Configure>', self._update_coords)
	
	def _update_coords(self, event):
		'''Updates the position of the text and rectangle inside the canvas when the size of
		the widget gets changed.'''
		# Looks like we have to call update_idletasks() twice to make sure to get the results we expect
		self._canv.update_idletasks()
		self._canv.coords(self._text, self._canv.winfo_width()/2, self._canv.winfo_height()/2)
		self._canv.coords(self._rect, 0, 0, self._canv.winfo_width()*self._value, self._canv.winfo_height())
		self._canv.update_idletasks()
	
	def get(self):
		return self._value, self._canv.itemcget(self._text, 'text')
	
	def set(self, value=0.0, text=None, lower_value=0.0):
		# Make the value failsafe:
		value = min(max(value, 0.0), 1.0)
		if self._canv.winfo_width() * abs(self._value - value) > 1 or text is not None:  # Only bother updating if there has been a noticeable change.
			self._value = value
			if text is None:
				text = '%0.1f%%' % (100 * value)  # If no text is specified use the default percentage string.
			textcolour = 'black' if value < 0.5 else 'white'
			self._canv.coords(self._rect, self._canv.winfo_width() * lower_value, 0, self._canv.winfo_width() * value, self._canv.winfo_height())
			self._canv.itemconfigure(self._text, text=text, fill=textcolour)
			self._canv.update_idletasks()

