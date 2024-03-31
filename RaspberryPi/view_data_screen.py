import tkinter as tk

class ViewDataScreen(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.configure(bg="light gray")
        self.label = tk.Label(self, text="View Data Screen", font=("Arial", 16))
        self.label.pack(pady=10)
