import Tkinter as TK

DOWN_ARROW = unichr(9660)

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

if __name__ == '__main__':
	def f():
		print('x')

	def g():
		print('y')

	root = TK.Tk()
	t = SplitButton(root, [('Call the function f()', f), ('Call g()', g), ('Call g() also', g)])
	b = TK.Button(root, text='Quit', command=exit)

	t.pack(fill='both', expand=True)
	b.pack()

	TK.mainloop()

