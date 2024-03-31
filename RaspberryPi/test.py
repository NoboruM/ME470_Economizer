import tkinter as tk

class MainScreen(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Home")
        self.master.configure(bg="light gray")

        # Creating the home icon (you can replace 'home_icon.png' with your icon file)
        self.home_icon = tk.PhotoImage(file="home_icon.png")
        self.home_icon_label = tk.Label(self.master, image=self.home_icon)
        self.home_icon_label.grid(row=0, column=0, sticky="nw", padx=5, pady=5)

        # Title label
        self.title_label = tk.Label(self.master, text="Home", font=("Arial", 16))
        self.title_label.grid(row=0, column=1, padx=10, pady=5)

        # Button frame
        self.button_frame = tk.Frame(self.master)
        self.button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Buttons
        self.installation_button = tk.Button(self.button_frame, text="Installation: Set Parameters for New System",
                                             command=self.installation_action)
        self.installation_button.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.view_data_button = tk.Button(self.button_frame, text="View Downloaded Data",
                                          command=self.view_data_action)
        self.view_data_button.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.download_data_button = tk.Button(self.button_frame, text="Download Data",
                                              command=self.download_data_action)
        self.download_data_button.grid(row=2, column=0, sticky="w", padx=5, pady=5)

    def installation_action(self):
        print("Executing Installation Action")

    def view_data_action(self):
        print("Switching to View Data Screen")

    def download_data_action(self):
        print("Switching to Download Data Screen")

def main():
    root = tk.Tk()
    root.attributes('-fullscreen', True)  # Set main screen dimensions
    app = MainScreen(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()
