
try:
	import Tkinter as TK
except ImportError: # Python 3
	import tkinter as TK

import Flipper

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

class Meter(TK.Frame):
	def __init__(self, master, width=300, height=20, bg='white', fillcolour='orchid1', value=0.0, text=None, font=None, textcolour='black', *args, **kw):
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
	
	def set(self, value=0.0, text=None):
		# Make the value failsafe:
		value = min(max(value, 0.0), 1.0)
		if self._canv.winfo_width() * abs(self._value - value) > 1 or text is not None:  # Only bother updating if there has been a noticable change.
			self._value = value
			if text is None: text = '%0.1f %%' % (100 * value)  # If no text is specified use the default percentage string.
			self._canv.coords(self._rect, 0, 0, self._canv.winfo_width() * value, self._canv.winfo_height())
			self._canv.itemconfigure(self._text, text=text)
			self._canv.update_idletasks()

class Progress_App:
	def __init__(self, host_app):
		self.host_app = host_app
		self.parent = TK.Toplevel(self.host_app.parent)
		self.parent.protocol('WM_DELETE_WINDOW', self.cancel)  # To catch when users click the 'x' to close the window.
		
		self.label = TK.Label(self.parent, text='Computing:', anchor='w')
		self.label.pack(fill='x', expand=True)
		
		self.progress = Meter(self.parent)
		self.progress.pack(padx=2, pady=2)
		
		self.button_cancel = TK.Button(self.parent, text='Cancel', command=self.cancel)
		self.button_cancel.pack(padx=2, pady=2, side='right')
		
		self.running = True
		
		self.parent.resizable(0,0)
		self.parent.lift()
		self.button_cancel.focus()
	
	def cancel(self):
		self.running = False
		self.parent.destroy()
	
	def update_bar(self, value):
		if not self.running: raise Flipper.kernel.error.AbortError()
		
		self.progress.set(value, '%0.1f %%' % (value * 100))
		self.host_app.parent.update()
