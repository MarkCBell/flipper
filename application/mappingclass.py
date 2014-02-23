
try:
	import Tkinter as TK
except ImportError: # Python 3
	import tkinter as TK

import Flipper

class MappingClassApp(object):
	def __init__(self, host_app, name, mapping_class):
		self.host_app = host_app
		self.name = name
		self.mapping_class = mapping_class
		
		self.parent = TK.Toplevel(self.host_app.parent)
		self.parent.title('Mapping class: %s' % self.name)
		self.type = None
		self.invariant_lamination = None
		
		self.label_order = TK.Label(self.parent, anchor='w', text='Order: ')
		self.label_order_answer = TK.Label(self.parent, text='Unknown')
		self.button_order = TK.Button(self.parent, text='Compute', command=self.compute_order)
		
		self.label_type = TK.Label(self.parent, text='Type: ', justify='left')
		self.label_type_answer = TK.Label(self.parent, text='Unknown')
		self.button_type = TK.Button(self.parent, text='Compute', command=self.compute_type)
		
		self.label_invariant_lamination = TK.Label(self.parent, text='Invariant lamination: ', anchor='w')
		self.label_invariant_lamination_answer = TK.Label(self.parent, text='Unknown')
		self.button_invariant_lamination = TK.Button(self.parent, text='Compute', command=self.compute_invariant_lamination)
		
		self.label_order.grid(row=0, column=0)
		self.label_order_answer.grid(row=0, column=1)
		self.button_order.grid(row=0, column=2)
		
		self.label_type.grid(row=1, column=0)
		self.label_type_answer.grid(row=1, column=1)
		self.button_type.grid(row=1, column=2)
		
		self.label_invariant_lamination.grid(row=2, column=0)
		self.label_invariant_lamination_answer.grid(row=2, column=1)
		self.button_invariant_lamination.grid(row=2, column=2)
		
		self.parent.columnconfigure(0, pad=10)
		self.parent.columnconfigure(1, pad=10)
		self.parent.columnconfigure(2, pad=10)
		self.parent.rowconfigure(0, pad=10)
		self.parent.rowconfigure(1, pad=10)
		self.parent.rowconfigure(2, pad=10)
		
		self.parent.resizable(False, False)
		self.parent.lift()

	def compute_order(self):
		order = self.mapping_class.order()
		self.label_order_answer.config(text=('Infinite' if order == 0 else str(order)))
	
	def compute_type(self):
		order = self.mapping_class.order()
		self.label_order_answer.config(text=('Infinite' if order == 0 else str(order)))
	
	def compute_invariant_lamination(self):
		order = self.mapping_class.order()
		self.label_order_answer.config(text=('Infinite' if order == 0 else str(order)))

