
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

CATEGORY_RESULT, CATEGORY_PROGRESS, CATEGORY_ERROR = range(3)

def _worker_thread(function, args, answer, indeterminant):
	# What if an error occurs?
	try:
		if indeterminant:
			result = function(*args)
		else:
			result = function(*args, progression=lambda v: answer.put((CATEGORY_PROGRESS, v)))
		answer.put((CATEGORY_RESULT, result))
	except Exception as e:
		answer.put((CATEGORY_ERROR, e))

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
		self.parent.transient(self.host_app.parent)  # Lock this window on top.
		# print(self.parent.geometry())  # and start it in the center.
		x = self.host_app.parent.winfo_rootx() + self.host_app.parent.winfo_width() // 2 - self.parent.winfo_width() // 2
		y = self.host_app.parent.winfo_rooty() + self.host_app.parent.winfo_height() // 2 - self.parent.winfo_height() // 2
		self.parent.geometry('+%d+%d' % (x, y))
	
	def cancel(self):
		self.running = False
		self.worker.terminate()
		self.parent.destroy()
	
	def process(self, function, args=None):
		if args is None: args = []
		answer = Queue()
		self.worker = Process(target=_worker_thread, args=(function, args, answer, self.indeterminant))
		self.worker.deamon = True
		self.worker.start()
		
		while self.running:  # So long as the calculation hasn't been aborted.
			try:
				category, value = answer.get(True, 0.05)  # Try and get some more information
				if category == CATEGORY_RESULT:  # We got the answer.
					self.cancel()
					return value
				elif category == CATEGORY_PROGRESS:  # We're not done yet but we got an update.
					self.update_bar(value)
				elif category == CATEGORY_ERROR:  # An error occurred.
					self.cancel()
					raise value
			except Empty:
				# Increase the bar by 1%.
				if self.indeterminant: self.update_bar(self.progress.get()[0] % 1 + 0.01, '')
		
		# If we reach this point then the calculation was aborted.
		raise Flipper.AbortError
	
	def update_bar(self, value, text=None):
		#self.progress['value'] = int(value * 100)
		self.progress.set(value, text)
		self.host_app.parent.update()
