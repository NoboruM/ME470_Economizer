
import tkinter
import customtkinter
from functools import partial

DARK_MODE = "dark"
customtkinter.set_appearance_mode(DARK_MODE)
customtkinter.set_default_color_theme("blue")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Home")
        self.geometry(f"{1100}x{580}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
