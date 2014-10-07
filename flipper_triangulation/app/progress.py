
import flipper
import flipper.app
from flipper.app.spinning_icon import SPINNING_ICON

from multiprocessing import Process
from multiprocessing import JoinableQueue as Queue
import inspect

try:
	from Queue import Empty
except ImportError:  # Python 3.
	from queue import Empty

try:
	import Tkinter as TK
except ImportError:  # Python 3.
	import tkinter as TK

CATEGORY_RESULT, CATEGORY_PROGRESS, CATEGORY_ERROR = range(3)

# Note: Because of how memory is managed in Python the _worker_thread
# works with a copy of the main memory. Therefore any changes it makes to the
# objects involved, such as caching results, will NOT be done to the origional
# objects. Hence all such changes will be lost when the thread completes.
def _worker_thread(function, args, answer, determinant=False):
	try:
		if determinant:
			answer.put((CATEGORY_PROGRESS, 0))
			result = function(*args, log_progress=lambda v: answer.put((CATEGORY_PROGRESS, v)))
		else:
			result = function(*args)
		answer.put((CATEGORY_RESULT, result))
	except Exception as error:
		answer.put((CATEGORY_ERROR, error))  # Return any errors that occur.

class ProgressAppDeterminant(object):
	def __init__(self, host_app_parent=None):
		if host_app_parent is None: host_app_parent = TK._default_root
		self.host_app_parent = host_app_parent
		self.parent = TK.Toplevel(self.host_app_parent)
		self.parent.withdraw()  # Hide self while we set up the geometry.
		
		self.parent.title('flipper: Computing...')
		self.parent.protocol('WM_DELETE_WINDOW', self.cancel)  # To catch when users click the 'x' to close the window.
		
		self.progress = flipper.app.Meter(self.parent)
		self.progress.pack(padx=2, pady=2)
		
		self.button_cancel = TK.Button(self.parent, text='Cancel', command=self.cancel)
		self.button_cancel.pack(padx=5, pady=5, side='right')
		
		self.running = False
		self.worker = None
		
		self.parent.resizable(0, 0)
		self.parent.withdraw()
		self.parent.lift()
		self.button_cancel.focus()
		self.parent.update_idletasks()
		x = self.host_app_parent.winfo_rootx() + self.host_app_parent.winfo_width() // 2 - self.parent.winfo_width() // 2
		y = self.host_app_parent.winfo_rooty() + self.host_app_parent.winfo_height() // 2 - self.parent.winfo_height() // 2
		self.parent.update_idletasks()
		self.parent.geometry('+%d+%d' % (x, y))
		self.parent.deiconify()
		self.parent.transient(self.host_app_parent)  # Lock this window on top.
		self.parent.grab_set()  # Make sure this window always has focus.
		self.parent.update_idletasks()
	
	def cancel(self):
		if self.running:
			self.running = False
			self.worker.terminate()
			self.host_app_parent.focus_set()
			self.parent.destroy()
	
	def apply(self, function, args=None):
		# If we are expecting the function to report its progress then check it has a 'log_progress' argument.
		assert('log_progress' in inspect.getargspec(function).args)
		
		if args is None: args = []
		answer = Queue()
		self.worker = Process(target=_worker_thread, args=(function, args, answer, True))
		self.worker.deamon = True  # Making the worker a deamon of this thread stops it if the main thread is killed.
		self.running = True
		self.worker.start()
		
		while self.running:  # So long as the calculation hasn't been aborted.
			try:
				category, value = answer.get(True, 0.05)  # Try and get some more information.
				if category == CATEGORY_RESULT:  # We got the answer.
					self.cancel()
					return value
				elif category == CATEGORY_PROGRESS:  # We're not done yet but we got an update.
					self.update_bar(value)
				elif category == CATEGORY_ERROR:  # An error occurred.
					self.cancel()
					raise value
			except Empty:
				pass
		
		# If we reach this point then the calculation was aborted.
		raise flipper.AbortError
	
	def update_bar(self, value, text=None):
		self.progress.set(value, text)
		self.host_app_parent.update()

class ProgressApp(object):
	def __init__(self, host_app_parent=None):
		if host_app_parent is None: host_app_parent = TK._default_root
		self.host_app_parent = host_app_parent
		self.parent = TK.Toplevel(self.host_app_parent)
		self.parent.withdraw()  # Hide self while we set up the geometry.
		
		self.parent.title('flipper: Computing...')
		self.parent.protocol('WM_DELETE_WINDOW', self.cancel)  # To catch when users click the 'x' to close the window.
		
		self.progress = flipper.app.AnimatedCanvas(self.parent, frames_contents=SPINNING_ICON)
		self.progress.pack(padx=130, pady=5)
		
		self.button_cancel = TK.Button(self.parent, text='Cancel', command=self.cancel)
		self.button_cancel.pack(padx=5, pady=5, side='right')
		
		self.running = False
		self.worker = None
		
		self.parent.resizable(0, 0)
		self.parent.withdraw()
		self.parent.lift()
		self.button_cancel.focus()
		self.parent.update_idletasks()
		x = self.host_app_parent.winfo_rootx() + self.host_app_parent.winfo_width() // 2 - self.parent.winfo_width() // 2
		y = self.host_app_parent.winfo_rooty() + self.host_app_parent.winfo_height() // 2 - self.parent.winfo_height() // 2
		self.parent.update_idletasks()
		self.parent.geometry('+%d+%d' % (x, y))
		self.parent.deiconify()
		self.parent.transient(self.host_app_parent)  # Lock this window on top.
		self.parent.grab_set()  # Make sure this window always has focus.
		self.parent.update_idletasks()
	
	def cancel(self):
		if self.running:
			self.running = False
			self.worker.terminate()
			self.host_app_parent.focus_set()
			self.parent.destroy()
	
	def apply(self, function, args=None):
		if args is None: args = []
		answer = Queue()
		self.worker = Process(target=_worker_thread, args=(function, args, answer))
		self.worker.deamon = True  # Making the worker a deamon of this thread stops it if the main thread is killed.
		self.running = True
		self.worker.start()
		
		while self.running:  # So long as the calculation hasn't been aborted.
			try:
				category, value = answer.get(True, 0.05)  # Try and get some more information.
				if category == CATEGORY_RESULT:  # We got the answer.
					self.cancel()
					return value
				elif category == CATEGORY_ERROR:  # An error occurred.
					self.cancel()
					raise value
			except Empty:
				self.host_app_parent.update()
		
		# If we reach this point then the calculation was aborted.
		raise flipper.AbortError

def apply_progression_determinant(function, args=None, indeterminant=True, host_app_parent=None):
	return ProgressAppDeterminant(host_app_parent).apply(function, args, indeterminant)

def apply_progression(function, args=None, host_app_parent=None):
	return ProgressApp(host_app_parent).apply(function, args)

