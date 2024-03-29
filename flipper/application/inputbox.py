
import tkinter as TK

class GetStringApp:
    def __init__(self, title, prompt, default='', validate=None, host_app_parent=None):
        if host_app_parent is None: host_app_parent = TK._default_root
        self.host_app_parent = host_app_parent
        self.validate = validate
        self.result = None
        self.parent = TK.Toplevel(self.host_app_parent)
        self.parent.withdraw()  # Hide self while we set up the geometry.
        self.parent.title(title)
        self.parent.protocol('WM_DELETE_WINDOW', self.cancel)  # To catch when users click the 'x' to close the window.
        
        self.text_label = TK.Label(self.parent, text=prompt, justify='left')
        
        self.button_frame = TK.Frame(self.parent)
        self.button_ok = TK.Button(self.button_frame, text='Ok', command=self.ok)
        self.button_cancel = TK.Button(self.button_frame, text='Cancel', command=self.cancel)
        self.button_ok.pack(pady=2, fill='x', expand=True)
        self.button_cancel.pack(pady=2, fill='x', expand=True)
        
        self.variable = TK.StringVar()
        self.text_entry = TK.Entry(self.parent, width=40, textvariable=self.variable)
        self.variable.set(default)
        self.text_entry.selection_range(0, TK.END)
        
        self.text_label.grid(row=0, column=0, padx=5, pady=5, sticky='nw')
        self.button_frame.grid(row=0, column=1, padx=5, pady=5, sticky='e')
        
        self.text_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='we')
        
        self.parent.bind('<Return>', self.ok)
        self.parent.bind('<Escape>', self.cancel)
        
        self.parent.resizable(0, 0)
        self.parent.withdraw()
        self.parent.lift()
        self.text_entry.focus()
        self.parent.update_idletasks()
        x = self.host_app_parent.winfo_rootx() + self.host_app_parent.winfo_width() // 2 - self.parent.winfo_width() // 2
        y = self.host_app_parent.winfo_rooty() + self.host_app_parent.winfo_height() // 2 - self.parent.winfo_height() // 2
        self.parent.update_idletasks()
        self.parent.geometry('+%d+%d' % (x, y))
        self.parent.deiconify()
        self.parent.transient(self.host_app_parent)  # Lock this window on top.
        self.parent.grab_set()  # Make sure this window always has focus.
        self.parent.update_idletasks()
        self.host_app_parent.update_idletasks()
    
    def get_result(self):
        self.parent.wait_window(self.parent)  # Wait for the window to be killed.
        return self.result
    
    def ok(self, event=None):
        text = self.text_entry.get()
        if not self.validate or self.validate(text):
            self.result = text
            self.cancel()
        else:
            self.text_entry.selection_range(0, 'end')
    
    def cancel(self, event=None):
        self.host_app_parent.focus_set()
        self.parent.destroy()

def get_input(title, prompt, default='', validate=None, host_app_parent=None):
    return GetStringApp(title, prompt, default, validate, host_app_parent).get_result()

