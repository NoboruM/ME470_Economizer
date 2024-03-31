import tkinter
import customtkinter as ctk
from functools import partial
import os
from CTkPopupKeyboard import PopupKeyboard, PopupNumpad

DARK_MODE = "dark"
ctk.set_appearance_mode(DARK_MODE)
ctk.set_default_color_theme("blue")


class App(ctk.CTk):

    frames = {}
    current = None
    bg = ""


    def __init__(self):
        super().__init__()
        self.bg = self.cget("fg_color")
        self.num_of_frames = 0
        # self.state('withdraw')
        self.title("Change Frames")

        # screen size
        self.geometry(f"{1100}x{580}")

        # root!
        self.main_container = ctk.CTkFrame(self, corner_radius=8, fg_color=self.bg)
        self.main_container.pack(fill=tkinter.BOTH, expand=True, padx=8, pady=8)

        # create each of th e frames. Maybe set the first one to 
        self.create_input_frame("input")
        self.create_home_frame("home")
        self.create_download_frame("download")
        
        # set the initial frame to display  
        App.current = App.frames["input"]
        App.current.pack(in_=self.main_container, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)

    def create_input_frame(self, frame_id):
        App.frames[frame_id] = ctk.CTkFrame(self, corner_radius=8, fg_color="#212121")
        self.title("Installation: Set Parameters for New System")

        num_val = (App.frames[frame_id].register(self.Num_Validation), '%P')
   
        # configure the grid, but doesn't set size. I think if you keep adding stuff it works
        App.frames[frame_id].grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        App.frames[frame_id].grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), weight=1)

        # first row is the system name, which has text and user input ->  2 columns
        system_label = ctk.CTkLabel(App.frames[frame_id], text="New System Name:")
        system_label.grid(row=0, column = 0, padx=20, pady=20, sticky="nsew")
        self.system_name_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text="Enter System Name")
        self.system_name_input.grid(row=0, column=1, padx=20, pady=20, sticky="ew")
        self.system_name_input.bind("<Button-1>", self.KeyboardCallback)

        # # next section is 4 columns, 9 rows
        set_inputs_label = ctk.CTkLabel(App.frames[frame_id], text="Set Inputs:")
        set_inputs_label.grid(row=1, column=0,padx=10, pady=10, sticky="nsew")

        lockout_temp_label = ctk.CTkLabel(App.frames[frame_id], text="Lockout Temp:")
        lockout_temp_label.grid(row=1, column=1,padx=10, pady=10, sticky="e")
        self.lockout_temp_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val)
        self.lockout_temp_input.grid(row=1, column=2, columnspan=3, padx=10, pady=10, sticky="ew")
        lockout_temp_unit_label = ctk.CTkLabel(App.frames[frame_id], text = u"\u00b0"+"F")
        lockout_temp_unit_label.grid(row=1, column=5, padx=10, pady=10,sticky="w")
        self.lockout_temp_input.bind("<Button-1>", self.NumKeyboardCallback(self.lockout_temp_input))

        min_OAT_label = ctk.CTkLabel(App.frames[frame_id], text="Min % Outside Air Temp Temp:")
        min_OAT_label.grid(row=2, column=1,padx=10, pady=10, sticky="e")
        self.min_OAT_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val)
        self.min_OAT_input.grid(row=2, column=2, columnspan=3, padx=10, pady=10, sticky="ew")
        min_OAT_unit_label = ctk.CTkLabel(App.frames[frame_id], text = "%")
        min_OAT_unit_label.grid(row=2, column=5, padx=10, pady=10,sticky="w")
        self.min_OAT_input.bind("<Button-1>", self.NumKeyboardCallback(self.min_OAT_input))

        RAT_label = ctk.CTkLabel(App.frames[frame_id], text="Estimated Return Air Temp:")
        RAT_label.grid(row=3, column=1,padx=10, pady=10, sticky="e")
        self.RAT_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val)
        self.RAT_input.grid(row=3, column=2, columnspan=3, padx=10, pady=10, sticky="ew")
        RAT_unit_label = ctk.CTkLabel(App.frames[frame_id], text = u"\u00b0"+"F")
        RAT_unit_label.grid(row=3, column=5, padx=10, pady=10,sticky="w")
        self.RAT_input.bind("<Button-1>", self.NumKeyboardCallback(self.RAT_input))


        LL_Lockout_label = ctk.CTkLabel(App.frames[frame_id], text="Low Limit Lockout Temp:")
        LL_Lockout_label.grid(row=4, column=1,padx=10, pady=10, sticky="e")
        self.LL_Lockout_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val)
        self.LL_Lockout_input.grid(row=4, column=2, columnspan=3, padx=10, pady=10, sticky="ew")
        LL_Lockout_unit_label = ctk.CTkLabel(App.frames[frame_id], text = u"\u00b0"+"F")
        LL_Lockout_unit_label.grid(row=4, column=5, padx=10, pady=10,sticky="w")
        self.LL_Lockout_input.bind("<Button-1>", self.NumKeyboardCallback(self.LL_Lockout_input))


        HL_Lockout_label = ctk.CTkLabel(App.frames[frame_id], text="High Limit Lockout Temp:")
        HL_Lockout_label.grid(row=5, column=1,padx=10, pady=10, sticky="e")
        self.HL_Lockout_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val)
        self.HL_Lockout_input.grid(row=5, column=2, columnspan=3, padx=10, pady=10, sticky="ew")
        HL_Lockout_unit_label = ctk.CTkLabel(App.frames[frame_id], text = u"\u00b0"+"F")
        HL_Lockout_unit_label.grid(row=5, column=5, padx=10, pady=10,sticky="w")
        self.HL_Lockout_input.bind("<Button-1>", self.NumKeyboardCallback(self.HL_Lockout_input))


        MAT_label = ctk.CTkLabel(App.frames[frame_id], text="Ideal Mixed Air Temp:")
        MAT_label.grid(row=6, column=1,padx=10, pady=10, sticky="e")
        self.MAT_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val)
        self.MAT_input.grid(row=6, column=2, columnspan=3, padx=10, pady=10, sticky="ew")
        MAT_unit_label = ctk.CTkLabel(App.frames[frame_id], text = u"\u00b0"+"F")
        MAT_unit_label.grid(row=6, column=5, padx=10, pady=10,sticky="w")
        self.MAT_input.bind("<Button-1>", self.NumKeyboardCallback(self.MAT_input))


        SR_label = ctk.CTkLabel(App.frames[frame_id], text="Sampling Rate:")
        SR_label.grid(row=7, column=1,padx=10, pady=10, sticky="e")
        self.SR_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val)
        self.SR_input.grid(row=7, column=2, columnspan=3, padx=10, pady=10, sticky="ew")
        SR_unit_label = ctk.CTkLabel(App.frames[frame_id], text = "min")
        SR_unit_label.grid(row=7, column=5, padx=10, pady=10,sticky="w")
        self.SR_input.bind("<Button-1>", self.NumKeyboardCallback(self.SR_input))

        time_label = ctk.CTkLabel(App.frames[frame_id], text="Set Current Time:")
        time_label.grid(row=8, column=1,padx=10, pady=10, sticky="e")
        self.time_input1 = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val)
        self.time_input1.grid(row=8, column=2, columnspan=1, padx=0, pady=10, sticky="ew")
        time_label = ctk.CTkLabel(App.frames[frame_id], text=":", text_color="#fff")
        time_label.grid(row=8, column=3,padx=10, pady=10, sticky="nsew")
        self.time_input2 = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val)
        self.time_input2.grid(row=8, column=4, columnspan=1, padx=0, pady=10, sticky="ew")
        time_unit_label = ctk.CTkOptionMenu(App.frames[frame_id], values=["AM", "PM"], fg_color=self.bg)
        time_unit_label.grid(row=8, column=5, padx=10, pady=10,sticky="w")
        self.time_input1.bind("<Button-1>", self.NumKeyboardCallback(self.time_input1))
        self.time_input2.bind("<Button-1>", self.NumKeyboardCallback(self.time_input2))

        date_label = ctk.CTkLabel(App.frames[frame_id], text="Date:")
        date_label.grid(row=9, column=1,padx=10, pady=10, sticky="e")
        self.date_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val)
        self.date_input.grid(row=9, column=2, columnspan=3, padx=10, pady=10, sticky="ew")
        date_unit_label = ctk.CTkLabel(App.frames[frame_id], text = "min")
        date_unit_label.grid(row=9, column=5, padx=10, pady=10,sticky="w")
        self.date_input.bind("<Button-1>", self.NumKeyboardCallback(self.date_input))

        # end is 3 buttons for going to each page
        
        self.view_plot_button = ctk.CTkButton(App.frames[frame_id], text="View Ideal Economizer Curve", command=partial(self.toggle_frame_by_id, "view_curve"), corner_radius=100)
        self.view_plot_button.grid(row=10, column=1, columnspan = 3, padx=20, pady=20, sticky="ew")

        self.save_exit_button = ctk.CTkButton(App.frames[frame_id], text="Save & Exit", command=self.handle_install_inputs, corner_radius=100)
        self.save_exit_button.grid(row=10, column=4, padx=20, pady=20, sticky="ew")
        self.cancel_button = ctk.CTkButton(App.frames[frame_id], command=partial(self.toggle_frame_by_id, "download"), text="Cancel")
        self.cancel_button.grid(row=10, column=5, padx=20, pady=20, sticky="ew")

    def handle_install_inputs(self):
        system_name = self.system_name_input.get()
        numerical_inputs = []
        numerical_inputs.append(self.lockout_temp_input)
        numerical_inputs.append(self.min_OAT_input)
        numerical_inputs.append(self.RAT_input)
        numerical_inputs.append(self.LL_Lockout_input)
        numerical_inputs.append(self.HL_Lockout_input)
        numerical_inputs.append(self.MAT_input)
        numerical_inputs.append(self.SR_input)
        numerical_inputs.append(self.time_input1)
        numerical_inputs.append(self.time_input2)
        numerical_inputs.append(self.date_input)
        inputs_valid = True
        for input in numerical_inputs:
            if input.get() == "":
                print("input is blank")
                inputs_valid = False
                input.configure(fg_color= "#754543")
            else:
                input.configure(fg_color= self.bg)

        if inputs_valid:
            # clear all inputs?

            # at end if everything is good, move to last page
            self.toggle_frame_by_id("download")

    def Num_Validation(self, input): 
        if input.isdigit(): 
            return True                
        if input == "": 
            return True
        return False
            
         


    def create_home_frame(self, frame_id):
        App.frames[frame_id] = ctk.CTkFrame(self.main_container, corner_radius=8, fg_color="#323232")

        test_button = ctk.CTkButton(App.frames[frame_id], text=str(frame_id),command=partial(self.toggle_frame_by_id, "input"), corner_radius=8)
        test_button.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
        # App.current = App.frames[frame_id]
        # App.current.pack(in_=self.main_container, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)

    def create_download_frame(self, frame_id):
        App.frames[frame_id] = ctk.CTkFrame(self, corner_radius=8, fg_color="#212121")
        self.title("Download Data")

        num_val = (App.frames[frame_id].register(self.Num_Validation), '%P')
   
        # configure the grid, but doesn't set size. I think if you keep adding stuff it works
        App.frames[frame_id].grid_columnconfigure((0, 1, 2, 3), weight=1)
        App.frames[frame_id].grid_rowconfigure((0, 1, 2), weight=1)
        
        search_label = ctk.CTkLabel(App.frames[frame_id], text="Search:")
        search_label.grid(row=0, column=0,padx=10, pady=10, sticky="w")
        self.search_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ")
        self.search_input.grid(row=0, column=1, columnspan=3, padx=10, pady=10, sticky="w")
        
        # create scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(App.frames[frame_id])
        self.scrollable_frame.grid(row=1, column=0, columnspan=4, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame_files = []
        file_names = self.GetAvailableFiles()
        for i, file in enumerate(file_names):
            button = ctk.CTkButton(self.scrollable_frame, text=file, command=partial(self.FileSelection, file))
            button.grid(row=i, column=0, padx=0, pady=10, sticky="nsew")
            self.scrollable_frame_files.append(button)
        
        self.select_system_button = ctk.CTkButton(App.frames[frame_id], text="Select System", command=partial(self.toggle_frame_by_id, "view_curve"), corner_radius=100)
        self.select_system_button.grid(row=2, column=1, columnspan = 2, padx=20, pady=20, sticky="ew")

        self.back_button = ctk.CTkButton(App.frames[frame_id], command=partial(self.toggle_frame_by_id, "home"), text="Back")
        self.back_button.grid(row=2, column=3, padx=20, pady=20, sticky="ew")
        

    def GetAvailableFiles(self):
        files = os.listdir("csv_files")
        for i in range(len(files)):
            files[i] = files[i].split(".")[0]
        
        return files

    def FileSelection(self, file_name):
        curr_input = self.search_input.get()
        self.search_input.delete(0,len(curr_input))
        self.search_input.insert(0, file_name)
        # change the color of the button to be slightly greyed out
        # reset the colors of all of the other buttons
    
    def KeyboardCallback(self, event):
        print("making keybaord")
        self.keyboard= PopupKeyboard(self.system_name_input)
        self.keyboard.disable = False

    def NumKeyboardCallback(self, event):
        print("making num keybaord")
        self.keyboard= PopupNumpad(event)
        self.keyboard.disable = False

    def toggle_frame_by_id(self, frame_id):
        if App.frames[frame_id] is not None:
            if App.current is App.frames[frame_id]:
                App.current.pack_forget()
                App.current = None
            elif App.current is not None:
                App.current.pack_forget()
                App.current = App.frames[frame_id]
                App.current.pack(in_=self.main_container, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
            else:
                App.current = App.frames[frame_id]
                App.current.pack(in_=self.main_container, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)

a = App()
a.mainloop()
