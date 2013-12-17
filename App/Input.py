
import os
try:
	import Tkinter as TK
except ImportError: # Python 3
	import tkinter as TK

class Input_Box(TK.Toplevel):
	def __init__(self, parent, title=None):
		TK.Toplevel.__init__(self, parent)
		self.transient(parent)
		if title: self.title(title)
		
		self.parent = parent
		self.result = None
		self.main_frame = TK.Frame(self)
		self.body(self.main_frame)
		self.main_frame.pack(padx=5, pady=5)
		
		box = TK.Frame(self)
		w = TK.Button(box, text='OK', width=10, command=self.ok, default=TK.ACTIVE)
		w.pack(side=TK.LEFT, padx=5, pady=5)
		w = TK.Button(box, text='Cancel', width=10, command=self.cancel)
		w.pack(side=TK.LEFT, padx=5, pady=5)
		
		self.bind('<Return>', self.ok)
		self.bind('<Escape>', self.cancel)
		
		box.pack()
		
		self.grab_set()
		self.protocol('WM_DELETE_WINDOW', self.cancel)
		self.geometry('+%d+%d' % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
		self.focus_set()
		self.wait_window(self)
	
	# construction hooks
	def body(self, master):
		# create dialog body.  return widget that should have
		# initial focus.  this method should be overridden
		pass
	
	# standard button semantics
	def ok(self, event=None):
		self.withdraw()
		self.update_idletasks()
		self.apply()
		self.cancel()
	
	def cancel(self, event=None):
		# put focus back to the parent window
		self.parent.focus_set()
		self.destroy()
	
	def apply(self):
		pass # override
