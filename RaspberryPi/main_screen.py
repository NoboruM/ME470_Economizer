import tkinter as tk
from installation_screen import InstallationScreen
from view_data_screen import ViewDataScreen
#from download_data_screen import DownloadDataScreen

class MainScreen(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Home")
        self.master.configure(bg="light gray")  # Set background color
        # self.master.geometry("800x600")  # Set window dimensions

        # Creating the home icon (you can replace 'home_icon.png' with your icon file)
        self.home_icon = tk.PhotoImage(file="home_icon.png").subsample(10, 10)
        self.home_icon_label = tk.Label(self.master, image=self.home_icon)
        self.home_icon_label.grid(row=0, column=1, sticky="ne", padx=5, pady=5)

        # Title label
        self.title_label = tk.Label(self.master, text="Home", font=("Arial", 16))
        self.title_label.grid(row=0, column=1, padx=10, pady=5)

        # Button frame
        self.button_frame = tk.Frame(self.master)
        self.button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # Buttons
        self.installation_button = tk.Button(self.button_frame, text="Installation: Set Parameters for New System",
                                             command=self.show_installation_screen)
        self.installation_button.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.view_data_button = tk.Button(self.button_frame, text="View Downloaded Data",
                                          command=self.show_view_data_screen)
        self.view_data_button.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.download_data_button = tk.Button(self.button_frame, text="Download Data",
                                              command=self.show_download_data_screen)
        self.download_data_button.grid(row=2, column=0, sticky="w", padx=5, pady=5)

        # Initialize frames for proceeding screens
        self.installation_screen = InstallationScreen(self.master)
        self.view_data_screen = ViewDataScreen(self.master)
        #self.download_data_screen = DownloadDataScreen(self.master)

    def show_installation_screen(self):
        self.hide_all_screens()
        self.installation_screen.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    def show_view_data_screen(self):
        self.hide_all_screens()
        self.view_data_screen.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    def show_download_data_screen(self):
        self.hide_all_screens()
        self.download_data_screen.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    def hide_all_screens(self):
        self.installation_screen.grid_remove()
        self.view_data_screen.grid_remove()
        #self.download_data_screen.grid_remove()

def main():
    root = tk.Tk()
    root.attributes('-fullscreen', True)  # Make the window full screen
    app = MainScreen(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()
