import tkinter
import customtkinter as ctk
from functools import partial
import os
import serial
from csv import writer as CsvWriter
from CTkPopupKeyboard import PopupKeyboard, PopupNumpad

DARK_MODE = "dark"
ctk.set_appearance_mode(DARK_MODE)
ctk.set_default_color_theme("blue")

class ToplevelWindow(ctk.CTkToplevel):
    def __init__(self, title_, text_,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")
        self.title(title_)
        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure((0,1), weight=1)
        self.label = ctk.CTkLabel(self, text=text_)
        self.label.grid(row=0, column=0, columnspan=2, padx=20, pady=20)

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
            self.lockout_temp = self.lockout_temp_input.get()
            self.min_OAT = self.min_OAT_input.get()
            self.RAT = self.RAT_input.get()
            self.LL_Lockout = self.LL_Lockout_input.get()
            self.HL_Lockout = self.HL_Lockout_input.get()
            self.MAT = self.MAT_input.get()
            self.SR = self.SR_input.get()

            self.hours = self.time_input1.get()
            self.minutes = self.time_input2.get()
            self.date = self.date_input.get()
            
            parameters = "M%OA," + self.min_OAT + "\nRAT," + self.RAT + "\nLLT," + self.LL_Lockout + "\nHLT," + self.HL_Lockout + "\niMAT," + self.MAT + "\nSR," + self.SR
            print(parameters)
            with open(system_name + ".csv", 'w', newline='') as new_file:
                csv_writer = CsvWriter(new_file) # create the new file or start writing to existing file
                csv_writer.writerow(parameters) # Write first row as the user parameters
            #to do: add the date
            # at end if everything is good, move to last page
            self.toggle_frame_by_id("download")

    def Num_Validation(self, input): 
        if input.isdigit(): 
            return True                
        if input == "": 
            return True
        return False
            
        
    def create_home_frame(self, frame_id):
        App.frames[frame_id] = ctk.CTkFrame(self, corner_radius=8, fg_color="#212121")
        self.title("Home")
    
        # configure the grid, but doesn't set size. I think if you keep adding stuff it works
        App.frames[frame_id].grid_columnconfigure((0, 1), weight=1)
        App.frames[frame_id].grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
    
        home_label = ctk.CTkLabel(App.frames[frame_id], text="Home", font=("Arial", 25))
        home_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
    
        home_icon = ctk.CTkImage(light_image=Image.open('home_icon2.png'), dark_image=Image.open('home_icon2.png'), size=(50, 50))
        image1 = ctk.CTkLabel(App.frames[frame_id], text="", image=home_icon)
        image1.grid(row=0, column=1, padx=20, pady=20, sticky="e")
    
        button1 = ctk.CTkButton(App.frames[frame_id], text="Installation: Set Parameters for New System")
        button1.grid(row=1, column=0, padx=20, pady=20, sticky="w", command=partial(self.toggle_frame_by_id, "input"))
    
        button2 = ctk.CTkButton(App.frames[frame_id], text="View Downloaded Data")
        button2.grid(row=2, column=0, padx=20, pady=20, sticky="w")
    
        button3 = ctk.CTkButton(App.frames[frame_id], text="Download Data")
        button3.grid(row=3, column=0, padx=20, pady=20, sticky="w")
    
        button4 = ctk.CTkButton(App.frames[frame_id], text="Back")
        button4.grid(row=5, column=1, padx=20, pady=20, sticky="e")

    def create_download_frame(self, frame_id):
        App.frames[frame_id] = ctk.CTkFrame(self, corner_radius=8, fg_color="#212121")
        self.title("Download Data")

        num_val = (App.frames[frame_id].register(self.Num_Validation), '%P')
   
        # configure the grid, but doesn't set size. I think if you keep adding stuff it works
        App.frames[frame_id].grid_columnconfigure((0, 1, 2, 3), weight=1)
        App.frames[frame_id].grid_rowconfigure((0, 1, 2, 3), weight=1)
        
        search_label = ctk.CTkLabel(App.frames[frame_id], text="Search Existing:")
        search_label.grid(row=0, column=0,padx=10, pady=10, sticky="w")
        self.search_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ")
        self.search_input.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="w")

        self.new_download_button = ctk.CTkButton(App.frames[frame_id], text="Download New System")
        self.new_download_button.grid(row=0, column=3, padx=10, pady=10, sticky="ew")


        
        # create scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(App.frames[frame_id])
        self.scrollable_frame.grid(row=1, column=0, columnspan=4, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame_files = []
        self.selected_file = None
        self.file_names = self.GetAvailableFiles()
        for i, file in enumerate(self.file_names):
            button = ctk.CTkButton(self.scrollable_frame, text=file, anchor="w", fg_color="#39334f", command=partial(self.FileSelection, file))
            button.grid(row=i, column=0, padx=0, pady=10, sticky="nsew")
            self.scrollable_frame_files.append(button)

        self.search_input.bind("<KeyRelease>", self.FilterFiles)
        self.error_info_label = ctk.CTkLabel(App.frames[frame_id], text = "")
        self.error_info_label.grid(row=2, column=1, columnspan=2, pady=0)
        self.select_system_button = ctk.CTkButton(App.frames[frame_id], text="Select System", command=self.DownloadDataFromPi, corner_radius=100)
        self.select_system_button.grid(row=3, column=1, columnspan = 2, padx=20, pady=20, sticky="ew")

        self.back_button = ctk.CTkButton(App.frames[frame_id], command=partial(self.toggle_frame_by_id, "home"), text="Back")
        self.back_button.grid(row=3, column=3, padx=20, pady=20, sticky="ew")
        
    def FilterFiles(self, event):
        text = self.search_input.get()
        self.filtered_frame_files = []
        for file in self.scrollable_frame_files:
            if file.cget("text").startswith(text):
                self.filtered_frame_files.append(file)
            else:
                file.grid_forget()
        for i, file in enumerate(self.filtered_frame_files):
            file.grid(row=i, column=0, padx=0, pady=10, sticky="nsew")
        # reset the colors? Seems like a bit extra
            

    def GetAvailableFiles(self):
        files = os.listdir("csv_files")
        for i in range(len(files)):
            files[i] = files[i].split(".")[0]
        files.sort()
        return files

    def FileSelection(self, file_name):
        self.error_info_label.configure(text="", )
        curr_input = self.search_input.get()
        self.search_input.delete(0,len(curr_input))
        self.search_input.insert(0, file_name)
        # change the color of the button to be slightly greyed out
        # reset the colors of all of the other buttons
        for i in range(len(self.scrollable_frame_files)):
            text = self.scrollable_frame_files[i].cget("text")
            if (text == file_name):
                self.selected_file = i
                self.scrollable_frame_files[i].configure(fg_color="#635888")
            else:
                self.scrollable_frame_files[i].configure(fg_color="#39334f")
    
    def KeyboardCallback(self, event):
        self.keyboard= PopupKeyboard(self.system_name_input, x=100, y=200)
        self.keyboard.disable = False

    def NumKeyboardCallback(self, event):
        self.numkeyboard= PopupNumpad(event, x=850, y=200)
        self.numkeyboard.disable = False

    def DownloadDataFromPi(self):
        if self.selected_file is None:
            self.error_info_label.configure(text="*No File Selected", )
            return
        print("selected " + self.scrollable_frame_files[self.selected_file].cget("text"))
        # set up serial communication
        # double check with the arduino that this system matches. if not, pop up window?
        doesnt_match = False
        if doesnt_match:
            self.toplevel_window = ToplevelWindow(self, "WARNING", "File does not match this data logger. \nContinuing will overwrite this file")
            self.continue_button = ctk.CTkButton(self.toplevel_window, text="Continue")
            self.continue_button.grid(row=1, column=0, padx=10, pady=10)
            self.cancel_button = ctk.CTkButton(self.toplevel_window, text="Cancel", command=self.DestroyTopLevel)
            self.cancel_button.grid(row=1, column=1, padx=10, pady=10)
            return
        self.downloading_pop_up = ToplevelWindow(self, "Loading", "")
        # tell the arduino we're ready to receive data
        ser = serial.Serial('/dev/ttyACM0', 115200)
        ser.write("Begin Download")
        # wait for response
        # get the system and parameters of the system
        system_name = ser.readline().decode().strip()
        params = ser.readline().decode().strip()
        
        self.oat_data = []
        self.mat_data = []
        self.date_data = []
        self.time_data = []
        self.motor_data = []
        with open(system_name + ".csv", 'w', newline='') as new_file:
            csv_writer = CsvWriter(new_file) # create the new file or start writing to existing file
            csv_writer.writerow(params) # Write first row as the user parameters
            # start downloading the data
            while True: # uh... how to know when to stop?
                # Read data from serial port
                data = ser.readline().decode().strip()
                print(data)
                
                if (len(data.split(',')) < 5):
                    print(data)
                    print('not enough data')
                    continue    
                # write to the CSV file
                csv_writer.writerow(data)

                # Split the received data into x and y values
                date, oat, mat, time, motor = data.split(',')
                
                # Append data points to lists
                self.oat_data.append(float(oat[:-2]))
                self.mat_data.append(float(mat))
                self.date_data.append(date)
                self.time_data.append(time)
                self.motor_data.append(bool(motor))
            
        
    def DestroyTopLevel(self):
        self.toplevel_window.destroy()
        self.search_input.focus() # to prevent keyboard from previous window from popping up randomly. Idk why

    def toggle_frame_by_id(self, frame_id):
        if App.frames[frame_id] is not None:
            if App.current is App.frames[frame_id]:
                App.current.pack_forget()
                App.current = None
            elif App.current is not None:
                print("changing frames!")
                App.current.pack_forget()
                App.current = App.frames[frame_id]
                App.current.pack(in_=self.main_container, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
            else:
                App.current = App.frames[frame_id]
                App.current.pack(in_=self.main_container, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)

a = App()
a.mainloop()
