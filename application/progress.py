
try:
	import Tkinter as TK
	# import ttk as TTK
except ImportError: # Python 3
	import tkinter as TK
	# from tkinter import ttk as TTK

import Flipper

class ProgressApp(object):
	def __init__(self, host_app):
		self.host_app = host_app
		self.parent = TK.Toplevel(self.host_app.parent)
		self.parent.protocol('WM_DELETE_WINDOW', self.cancel)  # To catch when users click the 'x' to close the window.
		
		self.label = TK.Label(self.parent, text='Computing:', anchor='w')
		self.label.pack(fill='x', expand=True)
		
		#self.progress = TTK.Progressbar(self.parent, mode='determinate', length=300)  # We could use ttk's progress bar.
		self.progress = Flipper.application.widgets.Meter(self.parent)
		self.progress.pack(padx=2, pady=2)
		
		self.button_cancel = TK.Button(self.parent, text='Cancel', command=self.cancel)
		self.button_cancel.pack(padx=2, pady=2, side='right')
		
		self.running = True
		
		self.parent.resizable(0, 0)
		self.parent.withdraw()
		self.parent.lift()
		self.button_cancel.focus()
	
	def cancel(self):
		self.running = False
		self.parent.destroy()
	
	def update_bar(self, value):
		if not self.running: raise Flipper.AbortError()
		self.parent.deiconify()
		
		#self.progress['value'] = int(value * 100)
		self.progress.set(value, '%0.1f %%' % (value * 100))
		self.host_app.parent.update()
