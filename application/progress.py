
from multiprocessing import Process
from multiprocessing import JoinableQueue as Queue

try:
	from Queue import Empty
except ImportError:
	from queue import Empty

try:
	import Tkinter as TK
	# import ttk as TTK
except ImportError: # Python 3
	import tkinter as TK
	# from tkinter import ttk as TTK

import Flipper

def _worker_thread(function, args, answer, indeterminant):
	# What if an error occurs?
	if not indeterminant:
		result = function(*args, progression=lambda v: answer.put((False, v)))
	else:
		result = function(*args)
	answer.put((True, result))

class ProgressApp(object):
	def __init__(self, host_app, indeterminant=False):
		self.host_app = host_app
		self.indeterminant = indeterminant
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
		self.worker = None
		
		self.parent.resizable(0, 0)
		self.parent.withdraw()
		self.parent.lift()
		self.button_cancel.focus()
		self.parent.deiconify()
	
	def cancel(self):
		self.running = False
		self.worker.terminate()
		self.parent.destroy()
	
	def process(self, function, args=[]):
		answer = Queue()
		self.worker = Process(target=_worker_thread, args=(function, args, answer, self.indeterminant))
		self.worker.deamon = True
		self.worker.start()
		
		if self.indeterminant:
			while True:
				try:
					complete, value = answer.get(True, 0.05)
					if complete:
						result = value
						break
				except Empty:
					# Increase the bar by 1%.
					self.update_bar(self.progress.get()[0] % 1 + 0.01, '')
		else:
			while True:
				complete, value = answer.get()
				if complete: 
					result = value
					break
				self.update_bar(value)
		
		self.cancel()
		return result
	
	def update_bar(self, value, text=None):
		if not self.running: raise Flipper.AbortError()
		# self.parent.deiconify()
		
		#self.progress['value'] = int(value * 100)
		self.progress.set(value, text)
		self.host_app.parent.update()
