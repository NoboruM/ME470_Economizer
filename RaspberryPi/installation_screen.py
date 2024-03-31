import tkinter as tk

class InstallationScreen(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.configure(bg="light gray")
        self.label = tk.Label(self, text="Installation Screen", font=("Arial", 16))
        self.label.pack(pady=10)