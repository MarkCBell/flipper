
try:
	import Tkinter as TK
except ImportError:  # Python 3.
	try:
		import tkinter as TK
	except ImportError:
		raise ImportError('Tkinter not available.')
from time import sleep

textFont1 = ('Arial', 10, 'bold italic')
textFont2 = ('Arial', 16, 'bold')
textFont3 = ('Arial', 8, 'bold')

class LabelWidget(TK.Entry):
	def __init__(self, master, x, y, text, **options):
		self.text = TK.StringVar(value=text)
		self.text.set(text)
		#super(LabelWidget, self).__init__(self, master=master)
		if 'state' not in options: options['state'] = 'readonly'
		options['textvariable'] = self.text
		TK.Entry.__init__(self, master=master, **options)
		self.grid(column=x, row=y)

class Grid(TK.Frame):
	def __init__(self, parent, data, **options):
		TK.Frame.__init__(self, parent, **options)
		
		assert(len(data) > 0)
		assert(all(len(row) == len(data[0]) for row in data))
		
		self.parent = parent
		self._data = data
		
		self._num_rows = len(self._data)
		self._num_columns = len(self._data[0])
		
		self._variables = [[TK.StringVar(value=entry) for entry in row] for row in self._data]
		self._entries = [[TK.Entry(self, textvariable=var) for var in row] for row in self._variables]
		self._entries = [[LabelWidget(self, i, j, text=entry) for j, entry in enumerate(row)] for i, row in enumerate(self._data)]
		for i in range(self._num_rows):
			for j in range(self._num_columns):
				self._entries[i][j].grid(column=j, row=i, sticky='nsew')
		
		for i in range(self._num_rows):
			self.grid_rowconfigure(i, weight=1)
		for j in range(self._num_columns):
			self.grid_columnconfigure(j, weight=1)

class TestApp(object):
	def __init__(self, parent):
		
		self.parent = parent
		data = [['A', 'B', 'C', 'D'] for i in range(10)]
		self.grid = Grid(self.parent, data)
		self.grid.pack(padx=6, pady=6, fill='both', expand=True)







class EntryGrid(TK.Tk):
	''' Dialog box with Entry widgets arranged in columns and rows.'''
	def __init__(self, colList, rowList, title='Entry Grid'):
		self.cols = colList[:]
		self.colList = colList[:]
		self.colList.insert(0, '')
		self.rowList = rowList
		TK.Tk.__init__(self)
		self.title(title)
	
		self.mainFrame = TK.Frame(self)
		self.mainFrame.config(padx='3.0m', pady='3.0m')
		self.mainFrame.grid()
		self.make_header()
	
		self.gridDict = {}
		for i in range(1, len(self.colList)):
			for j in range(len(self.rowList)):
				w = EntryWidget(self.mainFrame, i, j+1)
				self.gridDict[(i-1,j)] = w.value
				def handler(event, col=i-1, row=j):
					return self.__entryhandler(col, row)
				w.bind(sequence='<FocusOut>', func=handler)
		self.mainloop()
	
	def make_header(self):
		self.hdrDict = {}
		for i, label in enumerate(self.colList):
			def handler(event, col=i, row=0, text=label):
				return self.__headerhandler(col, row, text)
			w = LabelWidget(self.mainFrame, i, 0, label)
			self.hdrDict[(i,0)] = w
			w.bind(sequence='<KeyRelease>', func=handler)
	
		for i, label in enumerate(self.rowList):
			def handler(event, col=0, row=i+1, text=label):
				return self.__headerhandler(col, row, text)
			w = LabelWidget(self.mainFrame, 0, i+1, label)
			self.hdrDict[(0,i+1)] = w
			w.bind(sequence='<KeyRelease>', func=handler)
	
	def __entryhandler(self, col, row):
		s = self.gridDict[(col,row)].get()
		if s.upper().strip() == 'EXIT':
			self.destroy()
		elif s.strip():
			print(s)
	
	def __headerhandler(self, col, row, text):
		''' has no effect when Entry state=readonly '''
		self.hdrDict[(col,row)].text.set(text)
	
	def get(self, x, y):
		return self.gridDict[(x,y)].get()
	
	def set(self, x, y, v):
		self.gridDict[(x,y)].set(v)
		return v

if __name__ == '__main__':
	root = TK.Tk()
	app = TestApp(root)
	root.mainloop()

