
import flipper
import flipper.application
from flipper.application.spinning_icon import SPINNING_ICON

from multiprocessing import Process
from multiprocessing import JoinableQueue as Queue

try:
	from Queue import Empty
except ImportError:  # Python 3.
	from queue import Empty

try:
	import Tkinter as TK
except ImportError:  # Python 3.
	import tkinter as TK

# Note: Because of how memory is managed in Python the _worker_thread
# works with a copy of the main memory. Therefore any changes it makes to the
# objects involved, such as caching results, will NOT be done to the origional
# objects. Hence all such changes will be lost when the thread completes.
def _worker_thread(function, args, answer):
	try:
		result = function(*args)
		answer.put(result)
	except Exception as error:
		answer.put(error)  # Return any errors that occur.

class ProgressApp(object):
	def __init__(self, host_app_parent=None):
		if host_app_parent is None: host_app_parent = TK._default_root
		self.host_app_parent = host_app_parent
		self.parent = TK.Toplevel(self.host_app_parent)
		self.parent.withdraw()  # Hide self while we set up the geometry.
		
		self.parent.title('flipper: Computing...')
		self.parent.protocol('WM_DELETE_WINDOW', self.cancel)  # To catch when users click the 'x' to close the window.
		
		self.progress = flipper.application.AnimatedCanvas(self.parent, frames_contents=SPINNING_ICON)
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
				result = answer.get(True, 0.05)  # Try and get some more information.
			except Empty:
				self.host_app_parent.update()
			else:
				self.cancel()
				if isinstance(result, Exception):
					raise result
				else:
					return result
		
		# If we reach this point then the calculation was aborted.
		raise flipper.AbortError

def apply_progression(function, args=None, host_app_parent=None):
	return ProgressApp(host_app_parent).apply(function, args)

