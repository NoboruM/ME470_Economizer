
import tkinter
import customtkinter as ctk
from functools import partial
import os
import serial
import csv
from CTkPopupKeyboard import PopupKeyboard, PopupNumpad
from PIL import Image
from time import strftime, localtime, time, sleep
import datetime
import calendar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

DARK_MODE = "dark"
ctk.set_appearance_mode(DARK_MODE)
ctk.set_default_color_theme("blue")

#MARK: CustomSerial
def CustomSerial(message, baud_rate):
    ser = serial.Serial('/dev/ttyACM0', baud_rate, timeout=1)
    ser.write("{}\r\n".format(message).encode())
    start_time = time()
    response = ser.readline().decode().strip()
    while (time() - start_time) < 6 and response == "":
        ser.write("{}\r\n".format(message).encode())
        response = ser.readline().decode().strip()
        # print("response: '{}'".format(response))
    ser.close()
    return response

class ToplevelWindow(ctk.CTkToplevel):
    def __init__(self, title_, text_,*args, **kwargs):
        super().__init__()
        # self.geometry("400x300")
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
        self.wm_attributes('-fullscreen', True)
        self.state('normal')
        self.my_font = ctk.CTkFont(family="TkTextFont", size=15, weight="bold")
        self.home_font = ctk.CTkFont(family="TkTextFont", size=30, weight="bold")

        # root!
        self.main_container = ctk.CTkFrame(self, corner_radius=8, fg_color=self.bg)
        self.main_container.pack(fill=tkinter.BOTH, expand=True, padx=2, pady=2)
        self.oat_data = []
        self.mat_data = []
        self.date_data = []
        self.motor_data = []
        self.use_local_data = True
        self.filter_files = True
        # create each of th e frames. Maybe set the first one to 
        self.create_input_frame("input")
        self.create_home_frame("home")
        self.create_download_frame("download")
        self.create_loading_frame('loading')
        # self.create_download_frame("curve")
        
        # set the initial frame to display  
        App.current = App.frames["home"]
        App.current.pack(in_=self.main_container, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
# MARK: Creat input frame
    def create_input_frame(self, frame_id):
        App.frames[frame_id] = ctk.CTkFrame(self, corner_radius=8, fg_color="#212121")
        self.title("Installation: Set Parameters for New System")

        num_val = (App.frames[frame_id].register(self.Num_Validation), '%P')
   
        # configure the grid, but doesn't set size. I think if you keep adding stuff it works
        App.frames[frame_id].grid_columnconfigure((1, 2, 3), weight=1)
        App.frames[frame_id].grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), weight=1)

        # first row is the system name, which has text and user input ->  2 columns
        system_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="New System Name:", width=200)
        system_label.grid(row=0, column = 0, padx=10, pady=10, sticky="nsew")
        self.system_name_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text="Enter System Name", font=self.my_font, height=40)
        self.system_name_input.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        self.system_name_input.bind("<FocusIn>", self.KeyboardCallback(self.system_name_input, 25, 200))

        # # next section is 4 columns, 9 rows
        Label_column_width = 600
        set_inputs_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Set Inputs:")
        set_inputs_label.grid(row=1, column=0,padx=10, pady=5, sticky="nsew")

        min_OAT_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Min % Outside Air Temp:", width=Label_column_width)
        min_OAT_label.grid(row=1, column=1,padx=10, pady=5, sticky="e")
        self.min_OAT_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key")
        self.min_OAT_input.grid(row=1, column=2, padx=10, pady=5, sticky="nsew")
        min_OAT_unit_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text = "%")
        min_OAT_unit_label.grid(row=1, column=3, padx=10, pady=5,sticky="nsw")
        self.min_OAT_input.bind("<1>", self.NumKeyboardCallback(self.min_OAT_input, 750, 50))

        RAT_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Estimated Return Air Temp:", width=Label_column_width)
        RAT_label.grid(row=2, column=1,padx=10, pady=5, sticky="e")
        self.RAT_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key")
        self.RAT_input.grid(row=2, column=2, padx=10, pady=5, sticky="nsew")
        RAT_unit_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text = u"\u00b0"+"F")
        RAT_unit_label.grid(row=2, column=3, padx=10, pady=5,sticky="nsw")
        self.RAT_input.bind("<1>", self.NumKeyboardCallback(self.RAT_input, 750, 50))


        LL_Lockout_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Low Limit Lockout Temp:", width=Label_column_width)
        LL_Lockout_label.grid(row=3, column=1,padx=10, pady=5, sticky="e")
        self.LL_Lockout_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key")
        self.LL_Lockout_input.grid(row=3, column=2, padx=10, pady=5, sticky="nsew")
        LL_Lockout_unit_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text = u"\u00b0"+"F")
        LL_Lockout_unit_label.grid(row=3, column=3, padx=10, pady=5,sticky="nsw")
        self.LL_Lockout_input.bind("<1>", self.NumKeyboardCallback(self.LL_Lockout_input, 750, 50))

    
        HL_Lockout_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="High Limit Lockout Temp:", width=Label_column_width)
        HL_Lockout_label.grid(row=4, column=1,padx=10, pady=5, sticky="e")
        self.HL_Lockout_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key")
        self.HL_Lockout_input.grid(row=4, column=2, padx=10, pady=5, sticky="nsew")
        HL_Lockout_unit_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text = u"\u00b0"+"F")
        HL_Lockout_unit_label.grid(row=4, column=3, padx=10, pady=5,sticky="nsw")
        self.HL_Lockout_input.bind("<1>", self.NumKeyboardCallback(self.HL_Lockout_input, 750, 50))

        #stopped here
        MAT_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Ideal Mixed Air Temp:", width=Label_column_width)
        MAT_label.grid(row=5, column=1,padx=10, pady=5, sticky="e")
        self.MAT_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key")
        self.MAT_input.grid(row=5, column=2, padx=10, pady=5, sticky="nsew")
        MAT_unit_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text = u"\u00b0"+"F")
        MAT_unit_label.grid(row=5, column=3, padx=10, pady=5,sticky="nsw")
        self.MAT_input.bind("<1>", self.NumKeyboardCallback(self.MAT_input, 750, 50))


        SR_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Sampling Rate:", width=Label_column_width)
        SR_label.grid(row=6, column=1,padx=10, pady=5, sticky="e")
        self.SR_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key")
        self.SR_input.grid(row=6, column=2, padx=10, pady=5, sticky="nsew")
        SR_unit_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text = "min")
        SR_unit_label.grid(row=6, column=3, padx=10, pady=5,sticky="nsw")
        self.SR_input.bind("<1>", self.NumKeyboardCallback(self.SR_input, 750, 50))

        time_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Set Current Time:", width=Label_column_width)
        time_label.grid(row=7, column=1,padx=10, pady=5, sticky="e")
        
        time_frame = ctk.CTkFrame(App.frames[frame_id], fg_color="#212121")
        time_frame.grid(row=7, column=2, padx = 10, pady=5, sticky="nsew")
        time_frame.grid_rowconfigure(0, weight=1)
        time_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.time_input1 = ctk.CTkEntry(time_frame, placeholder_text=" ", validate="key")
        self.time_input1.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        time_label = ctk.CTkLabel(time_frame, font=self.my_font, text=":", text_color="#fff")
        time_label.grid(row=0, column=1,sticky="nsew")
        self.time_input2 = ctk.CTkEntry(time_frame, placeholder_text=" ", validate="key")
        self.time_input2.grid(row=0, column=2, padx=(10, 0), sticky="nsew")

        self.time_unit_label = ctk.CTkOptionMenu(App.frames[frame_id], values=["AM", "PM"], fg_color=self.bg, font=self.my_font)
        self.time_unit_label.grid(row=7, column=3, padx=10, pady=5,sticky="nsw")        
        self.time_input1.bind("<1>", self.NumKeyboardCallback(self.time_input1, 750, 50))
        self.time_input2.bind("<1>", self.NumKeyboardCallback(self.time_input2, 750, 50))

        date_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Date:", width=Label_column_width)
        date_label.grid(row=8, column=1,padx=10, pady=5, sticky="e")
        
        date_frame = ctk.CTkFrame(App.frames[frame_id], fg_color="#212121")
        date_frame.grid(row=8, column=2, padx = 10, pady=5, sticky="nsew")
        date_frame.grid_rowconfigure(0, weight=1)
        date_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        self.month_input = ctk.CTkEntry(date_frame, placeholder_text=" ", validate="key")
        self.month_input.grid(row=0, column=0, padx=(0, 10), sticky="ns")
        slash_label = ctk.CTkLabel(date_frame, font=self.my_font, text="/", text_color="#fff")
        slash_label.grid(row=0, column=1, padx=10, sticky="ns")
        self.day_input = ctk.CTkEntry(date_frame, placeholder_text=" ", validate="key")
        self.day_input.grid(row=0, column=2, padx=10, sticky="ns")
        slash_label_2 = ctk.CTkLabel(date_frame, font=self.my_font, text="/", text_color="#fff")
        slash_label_2.grid(row=0, column=3, padx=10, sticky="ns")
        self.year_input = ctk.CTkEntry(date_frame, placeholder_text=" ", validate="key")
        self.year_input.grid(row=0, column=4, padx=(10, 0), sticky="ns")

        date_unit_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text = "Month/Day/Year")
        date_unit_label.grid(row=8, column=3, padx=10, pady=0,sticky="nsw")

        # for running on this computer
        self.month_input.bind("<1>", self.NumKeyboardCallback(self.month_input, 750, 50))
        self.day_input.bind("<1>", self.NumKeyboardCallback(self.day_input, 750, 50))
        self.year_input.bind("<1>", self.NumKeyboardCallback(self.year_input, 750, 50))

        # end is 3 buttons for going to each page
        
        # self.view_plot_button = ctk.CTkButton(App.frames[frame_id], font=self.my_font, text="View Ideal Economizer Curve", command=partial(self.handle_parameters_for_curve_view, App.frames[frame_id]), height=35, corner_radius=4)
        # self.view_plot_button.grid(row=10, column=1, padx=20, pady=20, sticky="ew")

        self.cancel_button = ctk.CTkButton(App.frames[frame_id], command=self.CancelInputFrame, font=self.my_font, text="Cancel", height=40, corner_radius=4)
        self.cancel_button.grid(row=9, column=2, padx=20, pady=20, sticky="ew")
        self.save_exit_button = ctk.CTkButton(App.frames[frame_id], font=self.my_font, text="Save & Begin Logging", command=self.handle_install_inputs, height=40, width=600, corner_radius=4)
        self.save_exit_button.grid(row=9, column=3, padx=20, pady=20, sticky="ew")
    
    # MARK: CancelInputFrame
    def CancelInputFrame(self):
        # remove all of the inputs 
        self.system_name_input.delete(0,len(self.system_name_input.get()))
        self.min_OAT_input.delete(0,len(self.min_OAT_input.get()))
        self.RAT_input.delete(0,len(self.RAT_input.get()))
        self.LL_Lockout_input.delete(0,len(self.LL_Lockout_input.get()))
        self.HL_Lockout_input.delete(0,len(self.HL_Lockout_input.get()))
        self.MAT_input.delete(0,len(self.MAT_input.get()))
        self.SR_input.delete(0,len(self.SR_input.get()))
        self.time_input1.delete(0,len(self.time_input1.get()))
        self.time_input2.delete(0,len(self.time_input2.get()))
        self.month_input.delete(0,len(self.month_input.get()))
        self.day_input.delete(0,len(self.day_input.get()))
        self.year_input.delete(0,len(self.year_input.get()))

        # return all of the colors
        self.system_name_input.configure(fg_color = self.bg)
        self.min_OAT_input.configure(fg_color = self.bg)
        self.RAT_input.configure(fg_color = self.bg)
        self.LL_Lockout_input.configure(fg_color = self.bg)
        self.HL_Lockout_input.configure(fg_color = self.bg)
        self.MAT_input.configure(fg_color = self.bg)
        self.SR_input.configure(fg_color = self.bg)
        self.time_input1.configure(fg_color = self.bg)
        self.time_input2.configure(fg_color = self.bg)
        self.month_input.configure(fg_color = self.bg)
        self.day_input.configure(fg_color = self.bg)
        self.year_input.configure(fg_color = self.bg)
        self.toggle_frame_by_id("home")

# MARK: HandleCurveParams
    def handle_parameters_for_curve_view(self, frame):
        self.system_name = self.system_name_input.get()
        numerical_inputs = []
        numerical_inputs.append(self.min_OAT_input)
        numerical_inputs.append(self.RAT_input)
        numerical_inputs.append(self.LL_Lockout_input)
        numerical_inputs.append(self.HL_Lockout_input)
        numerical_inputs.append(self.MAT_input)
        numerical_inputs.append(self.SR_input)
        numerical_inputs.append(self.time_input1)
        numerical_inputs.append(self.time_input2)
        numerical_inputs.append(self.month_input)
        numerical_inputs.append(self.day_input)
        numerical_inputs.append(self.year_input)
        inputs_valid = True
        for input in numerical_inputs:
            if input.get() == "":
                print("input is blank")
                inputs_valid = False
                input.configure(fg_color= "#754543")
            else:
                input.configure(fg_color= self.bg)
        inputs_valid = True
        if inputs_valid:
            # clear all inputs?
            self.min_OAT = float(numerical_inputs[0].get())
            self.RAT = float(numerical_inputs[1].get())
            self.LL_Lockout = float(numerical_inputs[2].get())
            self.HL_Lockout = float(numerical_inputs[3].get())
            self.MAT = float(numerical_inputs[4].get())
            self.SR = float(numerical_inputs[5].get())

        if (inputs_valid):
            # Create arrays for plotting
            oat = np.arange(-37, 111, 1)
            MAT_at_min_OA = self.RAT*(1 - (self.min_OAT/100)) + self.min_OAT*oat
            MAT = np.zeros((len(oat), 1))
            for i, temp in enumerate(oat):
                if (MAT_at_min_OA[i] < self.MAT or temp <= self.LL_Lockout or temp >= self.HL_Lockout):
                    MAT[i] = MAT_at_min_OA[i]
                elif (temp < self.MAT):
                    MAT[i] = self.MAT
                else:
                    MAT[i] = oat[i]

            # Create a new Tkinter window
            popup_window = ctk.CTkToplevel(frame)
            popup_window.title("Pop-up Window")
            
            # Create a frame inside the pop-up window
            popup_frame = ctk.CTkFrame(popup_window)
            popup_frame.pack(fill=ctk.BOTH, expand=True)
            
            # Example plot using matplotlib
            fig, ax = plt.subplots()
            ax.plot(oat, MAT)
            ax.set_xlabel('Outside Air Temperature [°F]')
            ax.set_ylabel('Mixed Air Temperature [°F]')
            ax.set_title('Ideal Econimzer Curve for ' + self.system_name)
            ax.set_xlim(-30, 110)
            ax.set_ylim(30, 100)
            
            # Embed the matplotlib plot in the frame
            canvas = FigureCanvasTkAgg(fig, master=popup_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()

# MARK: HandleInstallInputs
    #STORE INTO CSV FILE????
    def handle_install_inputs(self):
        self.system_name = self.system_name_input.get()
        numerical_inputs = []
        numerical_inputs.append(self.min_OAT_input)
        numerical_inputs.append(self.RAT_input)
        numerical_inputs.append(self.LL_Lockout_input)
        numerical_inputs.append(self.HL_Lockout_input)
        numerical_inputs.append(self.MAT_input)
        numerical_inputs.append(self.SR_input)
        numerical_inputs.append(self.time_input1)
        numerical_inputs.append(self.time_input2)
        numerical_inputs.append(self.month_input)
        numerical_inputs.append(self.day_input)
        numerical_inputs.append(self.year_input)
        inputs_valid = True
        for input in numerical_inputs:
            if input.get() == "":
                print("input is blank")
                inputs_valid = False
                input.configure(fg_color= "#754543")
            else:
                input.configure(fg_color= self.bg)
        inputs_valid = True
        if inputs_valid:
            # clear all inputs?
            self.min_OAT = self.min_OAT_input.get()
            self.RAT = self.RAT_input.get()
            self.LL_Lockout = self.LL_Lockout_input.get()
            self.HL_Lockout = self.HL_Lockout_input.get()
            self.MAT = self.MAT_input.get()
            self.SR = self.SR_input.get()

            self.hours = self.time_input1.get()
            if (self.time_unit_label.get() == "PM"):
                self.hours = str(int(self.hours) + 12)
            self.minutes = self.time_input2.get()
            self.month = self.month_input.get()
            self.day = self.day_input.get()
            self.year = self.year_input.get()
                
            self.current_epoch_time = self.mm_dd_yy_to_epoch(self.month, self.day, self.year, self.hours, self.minutes)
            # send data to the arduino:
            

            # store in CSV file
            parameters = [self.min_OAT,self.RAT,self.LL_Lockout,self.HL_Lockout,self.MAT, self.SR]
            print(parameters)
            file_store = "/home/eat/Documents/ME470_Economizer/RaspberryPi/ParamFiles/" + self.system_name + ".params"
            with open(file_store, 'w', newline='') as new_file:
               csv_writer = csv.writer(new_file) # create the new file or start writing to existing file
               csv_writer.writerow(parameters) # Write first row as the user parameters
            # at end if everything is good, move to last page
            self.create_end_frame("logging")
            self.toggle_frame_by_id("logging")
            App.current.update()
            self.SendInstallationInputs()
# MARK:SendInstallInputs
    def SendInstallationInputs(self):
        response = CustomSerial("-p?\r\n", 115200)
        print("response: ", response)
        if (response != "AOK"):
            # TODO: give some indication of error
            return
        filename = self.system_name + '.params'
        response = CustomSerial("-n={}.csv\r\n".format(self.system_name), 115200) # set the recording filename
        response = CustomSerial("-t={}\r\n".format(self.current_epoch_time), 115200) # set date/time
        response = CustomSerial("-p={},{},{},{},{},{}\r\n".format(filename, self.min_OAT, self.RAT, self.LL_Lockout, self.HL_Lockout, self.MAT), 115200) #params in order of M%OA,RAT,LLT,HLT,iMAT
        response = CustomSerial("-f={}\r\n".format(self.SR), 115200) # set sample rate
        print("Sample rate: ", CustomSerial("-f?", 115200))

        response = CustomSerial("-s=1\r\n", 115200) # start recording
    def Num_Validation(self, input): 
        if input.isdigit(): 
            return True                
        if input == "": 
            return True
        return False
#MARK: HomeFrame            
    def create_home_frame(self, frame_id):
        App.frames[frame_id] = ctk.CTkFrame(self, corner_radius=8, fg_color="#212121")
        self.title("Home")
    
        # configure the grid, but doesn't set size. I think if you keep adding stuff it works
        App.frames[frame_id].grid_columnconfigure((0, 1), weight=1)
        App.frames[frame_id].grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=0, minsize=90)


        home_label = ctk.CTkLabel(App.frames[frame_id], text="Welcome to EATPi", font=self.home_font)
        home_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
    
        home_icon = ctk.CTkImage(light_image=Image.open('/home/eat/Documents/ME470_Economizer/RaspberryPi/home_icon2.png'), dark_image=Image.open('/home/eat/Documents/ME470_Economizer/RaspberryPi/home_icon2.png'), size=(50, 50))
        image1 = ctk.CTkLabel(App.frames[frame_id], text="", image=home_icon)
        image1.grid(row=0, column=1, padx=20, pady=20, sticky="e")
    
        button1 = ctk.CTkButton(App.frames[frame_id], font=self.my_font, text="Installation: Set Parameters for New System",  command=partial(self.toggle_frame_by_id, "input"))
        button1.grid(row=1, column=0, padx=20, pady=20, sticky="nsw")
    
        button2 = ctk.CTkButton(App.frames[frame_id], font=self.my_font, text="View Downloaded Data", command=partial(self.DetermineDownloadSource, "View Downloaded Data"))
        button2.grid(row=2, column=0, padx=20, pady=20, sticky="nsw")

        button4 = ctk.CTkButton(App.frames[frame_id], font=self.my_font, text="Select Existing System", command=partial(self.DetermineDownloadSource, "View Downloaded Data"))
        button4.grid(row=4, column=0, padx=60, pady=20, sticky="nsw")
        button4.grid_forget()

        button5 = ctk.CTkButton(App.frames[frame_id], font=self.my_font, text="Create New System", command=partial(self.toggle_frame_by_id, "input"))
        button5.grid(row=5, column=0, padx=60, pady=20, sticky="nsw")
        button5.grid_forget() 

        # button3 = ctk.CTkButton(App.frames[frame_id], font=self.my_font, text="Download Data",  command=lambda: self.show_additional_home_buttons(App.frames[frame_id], button3, button4, button5))
        button3 = ctk.CTkButton(App.frames[frame_id], font=self.my_font, text="Download Data",  command=partial(self.DetermineDownloadSource, "Download Data"))
        button3.grid(row=3, column=0, padx=20, pady=20, sticky="nsw")
#MARK: ShowExtraHomeBut
    def show_additional_home_buttons(self, frame, main_button, button1, button2):
        if getattr(main_button, "additional_buttons_shown", False):
            main_button.configure(fg_color="#3668A0")
            # Remove the additional buttons if they are already shown
            button1.grid_forget()
            button2.grid_forget()
            # Update the attribute to indicate that the additional buttons are hidden
            main_button.additional_buttons_shown = False
        else:
            main_button.configure(fg_color="#24476C")
            # Pack the buttons to display them underneath the main button
            button1.grid(row=4, column=0, padx=60, pady=20, sticky="nsw")
            button2.grid(row=5, column=0, padx=60, pady=20, sticky="nsw")

            # Update the attribute to indicate that the additional buttons are shown
            main_button.additional_buttons_shown = True
#MARK: DownloadFrame
    def create_download_frame(self, frame_id):
        App.frames[frame_id] = ctk.CTkFrame(self, corner_radius=8, fg_color="#212121")
        self.title("Download Data")

        num_val = (App.frames[frame_id].register(self.Num_Validation), '%P')
   
        # configure the grid, but doesn't set size. I think if you keep adding stuff it works
        App.frames[frame_id].grid_columnconfigure((0, 1, 2, 3), weight=1)
        App.frames[frame_id].grid_rowconfigure((0, 1, 2, 3), weight=1)
        
        search_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Search:")
        search_label.grid(row=0, column=0,padx=10, pady=10, sticky="w")

        self.search_string_var = ctk.StringVar()
        self.search_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", height=40, font=self.my_font, textvariable=self.search_string_var)
        self.search_input.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.search_input.bind("<FocusIn>", self.KeyboardCallback(self.search_input, 25, 200), add='+')
    

        # create scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(App.frames[frame_id], height=350)
        self.scrollable_frame.grid(row=1, column=0, columnspan=4, padx=(10, 10), pady=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        # self.scrollable_frame_files = []
        self.scrollable_logger_files = []
        self.scrollable_local_files = []
        self.scrollable_logger_file_names = []
        self.scrollable_local_file_names = []
        self.SetScrollableFiles()
        self.search_string_var.trace_add('write', self.FilterFiles)
        self.error_info_label = ctk.CTkLabel(App.frames[frame_id], text = "", font=self.my_font)
        self.error_info_label.grid(row=2, column=1, columnspan=2, pady=0, sticky="s")
        self.select_system_button = ctk.CTkButton(App.frames[frame_id], font=self.my_font, text="Select System", height=40, command=self.CheckDownloadFromPi, corner_radius=4)
        self.select_system_button.grid(row=3, column=1, columnspan = 2, padx=20, pady=20, sticky="ew")

        self.back_button = ctk.CTkButton(App.frames[frame_id], command=self.BackFromDownloadFrame, font=self.my_font, text="Back", height=40)
        self.back_button.grid(row=3, column=3, padx=20, pady=20, sticky="ew")

    def SetScrollableFiles(self):  
        self.scrollable_logger_file_names 
        self.scrollable_local_file_names 
        self.selected_file = None
        self.logger_file_names = self.GetAvailableArduinoFiles()
        self.local_data_file_names, self.local_param_file_names = self.GetAvailableDownloadedFiles()

        for i, file in enumerate(self.logger_file_names):
            if (self.scrollable_logger_file_names.count(file) == 0):
                button = ctk.CTkButton(self.scrollable_frame, text=file, anchor="w", font=self.my_font, fg_color="#39334f", height=50, command=partial(self.FileSelection, file))
                button.grid(row=i, column=0, padx=0, pady=5, sticky="nsew")
                self.scrollable_logger_files.append(button)
                self.scrollable_logger_file_names.append(file)

        for i, file in enumerate(self.local_data_file_names):
            if (self.scrollable_local_file_names.count(file) == 0):
                button = ctk.CTkButton(self.scrollable_frame, text=file, anchor="w", font=self.my_font, fg_color="#39334f", height=50, command=partial(self.FileSelection, file))
                button.grid(row=i, column=0, padx=0, pady=5, sticky="nsew")
                self.scrollable_local_files.append(button)
                self.scrollable_local_file_names.append(file)
        self.InitFilterFiles()

    def BackFromDownloadFrame(self):
        self.error_info_label.configure(text="", )
        self.search_input.delete(0,len(self.search_input.get()))
        self.toggle_frame_by_id("home")

    # three string variable parameters, int32 output
    def mm_dd_yy_to_epoch(self, month, day, year, hour, minute):
        while (len(minute) < 2):
            minute = "0" + minute
            print("minute: ", minute)
        while (len(hour) < 2):
            hour = "0" + hour
            print("hour: ", hour)
        while (len(year) < 4):
            year = "20" + year
            print("year: ", year)
        while (len(month) < 2):
            month = "0" + month
            print("month: ", month)
        while (len(day) < 2):
            day = "0" + day
            print("day: ", day)
        # Parse the month, day, and year strings
        dt_string = f"{month}-{day}-{year} {hour}:{minute}:00"
        print(dt_string)
        dt_object = datetime.datetime.strptime(dt_string, "%m-%d-%Y %H:%M:%S")

        # Convert datetime object to epoch time (int32)
        epoch_time = int(dt_object.timestamp())

        return epoch_time
# MARK: CreateCurveFrame
    def create_curve_frame(self, frame_id, raw_data, curve_parameters):
        #returns three string variables
        def epoch_to_mm_dd_yy(epoch_time):
            # Convert epoch time to datetime object
            print("epoch time: ", "'{}'".format(epoch_time))
            dt_object = datetime.datetime.fromtimestamp(epoch_time)

            # Extract month, day, and year
            month = str(dt_object.month).zfill(2)
            day = str(dt_object.day).zfill(2)
            year = str(dt_object.year)[-2:]

            return month, day, year

        def process_data_points(data_file_name):
            #datetime64[s]
            # Process csv file of data points
            data_file_name = "/home/eat/Documents/ME470_Economizer/RaspberryPi/CSV_Files/" + data_file_name
            data = np.genfromtxt(data_file_name, delimiter=',', skip_header=1, dtype=[('Date', np.int32), ('OAT', 'f8'), ('MAT', 'f8'), ('Motor_State', 'i1')])
            date = data['Date']
            print("date: ", "'{}'".format(date))
            oat = data['OAT']
            mat = data['MAT']
            motor = data['Motor_State']

            date_on = []
            date_off = []
            oat_on = []
            oat_off = []
            mat_on = []
            mat_off = []

            for i in range(len(motor)):
                if motor[i] == 1:
                    date_on.append(date[i])
                    oat_on.append(oat[i])
                    mat_on.append(mat[i])
                else:
                    date_off.append(date[i])
                    oat_off.append(oat[i])
                    mat_off.append(mat[i])

            start_month, start_date, start_year = epoch_to_mm_dd_yy(date[0])
            end_month, end_date, end_year = epoch_to_mm_dd_yy(date[len(date) - 1])
            return start_month, start_date, start_year, end_month, end_date, end_year, date_on, date_off, oat_on, oat_off, mat_on, mat_off
# MARK: ProcessIdealParams
        def process_ideal_curve_parameters(parameters_file_name):
        # Process parameter csv file of ideal curve
            parameters_dictionary = {} # dictionary of length 8
            parameters_file_name = "/home/eat/Documents/ME470_Economizer/RaspberryPi/ParamFiles/" + parameters_file_name
            try:
                with open(parameters_file_name, 'r') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        if not row:
                            continue
                        try:
                            parameters_dictionary['M%OAT'] = float(row[0])
                            parameters_dictionary['RAT'] = float(row[1])
                            parameters_dictionary['LLLT'] = float(row[2])
                            parameters_dictionary['HLLT'] = float(row[3])
                            parameters_dictionary['MAT'] = float(row[4])
                            parameters_dictionary['Sampling Rate'] = row[5]
                        except ValueError:
                            print("Error in reading curve parameters")
            except FileNotFoundError:
                print(f"The file '{parameters_file_name}' does not exist.")
            return parameters_dictionary

#MARK: PlotStandardized Settings
        def plot_standardized_settings(ax):
            # Label and Tweak Plot Design
            ax.set_title(raw_data[:-4], fontsize=13)
            ax.set_xlabel('Outside Air Temperature [°F]', fontsize=13, labelpad=5)
            ax.set_ylabel('Mixed Air Temperature [°F]', fontsize=13, labelpad=5)
            ax.tick_params(axis='both', which='major', labelsize=10)
            ax.set_xlim(-30, 110)
            ax.set_ylim(30, 100)

            left = 0.1
            bottom = 0.1
            width = 0.8
            height = 0.8
            ax.set_position([left, bottom, width, height])
# MARK: DrawIdealCurve
        def draw_ideal_curve(ax, parameters):
            # Process parameters for ideal economizer curve
            min_oat = parameters["M%OAT"] #float

            if (min_oat >1):
                min_oat /= 100
            rat = parameters["RAT"] #float
            lllt = parameters["LLLT"] #float
            hllt = parameters["HLLT"] #float
            i_mat = parameters["MAT"] #float

            # Create ideal economizer curve
            oat_for_plot = np.arange(-37, 111, 1)
            oat_for_plot1 = []
            oat_for_plot2 = []
            oat_for_plot3 = []
            oat_for_plot4 = []
            MAT_at_min_OA = rat*(1 - (min_oat)) + (min_oat)*oat_for_plot
            mat_for_plot1 = [] # maybe dont make them zero?
            mat_for_plot2 = [] # maybe dont make them zero?
            mat_for_plot3 = [] # maybe dont make them zero?
            mat_for_plot4 = [] # maybe dont make them zero?
            for i, temp in enumerate(oat_for_plot):
                if (MAT_at_min_OA[i] < i_mat or temp <= lllt or temp >= hllt):
                    if(temp >= hllt): #Im sorry michael - kyle
                        mat_for_plot4.append(MAT_at_min_OA[i])
                        oat_for_plot4.append(temp)
                    else:
                        mat_for_plot1.append(MAT_at_min_OA[i])
                        oat_for_plot1.append(temp)
                elif (temp < i_mat):
                    mat_for_plot2.append(i_mat)
                    oat_for_plot2.append(temp)
                else:
                    mat_for_plot3.append(oat_for_plot[i])
                    oat_for_plot3.append(temp)

            # Plot ideal economizer curve
            ax.plot(oat_for_plot1, mat_for_plot1, color='#fa8b41', linewidth=2)
            ax.plot(oat_for_plot2, mat_for_plot2, color='#fa8b41', linewidth=2)
            ax.plot(oat_for_plot3, mat_for_plot3, color='#fa8b41', linewidth=2)
            ax.plot(oat_for_plot4, mat_for_plot4, color='#fa8b41', linewidth=2)

# MARK: Handle Date Range
        # ASSUMES THE RAW DATA FILE IS IN TIME ORDER
        def handle_date_range(m1, d1, y1, m2, d2, y2, parameters):
            if (m1 == '') & (d1 == '') & (y1 == '') & (m2 == '') & (d2 == '') & (y2 == ''):
                on_start_index = 0
                off_start_index = 0
                on_end_index = len(date_on) - 1
                off_end_index = len(date_off) - 1
                handle_plot("", oat_on, oat_off, mat_on, mat_off, parameters)
                return #on_start_index, off_start_index, on_end_index, off_end_index

            # if any of the entries are empty, make entries red
            if (m1 == '') | (d1 == '') | (y1 == '') | (m2 == '') | (d2 == '') | (y2 == ''):
                #make buttons red
                print("Please fill in all the entries")
                return #on_start_index, off_start_index, on_end_index, off_end_index

            epoch1 = self.mm_dd_yy_to_epoch(m1, d1, y1, 0, 0) #string
            epoch2 = self.mm_dd_yy_to_epoch(m2, d2, y2, 0, 0) #string

            if epoch1 > epoch2:
                # turn buttons red
                print("First date should be earlier than second date")
                return

            for i in range(len(date_on)):
                if date_on[i] >= epoch1:
                    on_start_index = i
                break
            for i in range(len(date_off)):
                if date_off[i] >= epoch1:
                    off_start_index = i
                break
            for i in range(len(date_on)-1, -1, -1):
                if date_on[i] <= epoch2:
                    on_end_index = i
                break
            for i in range(len(date_off)-1, -1, -1):
                if date_off[i] <= epoch2:
                    off_end_index = i
                break
            handle_plot("", oat_on, oat_off, mat_on, mat_off, parameters)

# MARK:HandlePlot
        def handle_plot(called_from, oat_on, oat_off, mat_on, mat_off, parameters):
            ax.clear()
            if curve_check.get():
                draw_ideal_curve(ax, parameters)
            if called_from == "points":
                if points_check.get() == False:
                    on_check.set(False)
                    off_check.set(False)
                    App.current.update()
                else:
                    on_check.set(True)
                    off_check.set(True)
                    App.current.update()
                    ax.scatter(oat_on[on_start_index:on_end_index], mat_on[on_start_index:on_end_index], marker='o', color='#3668A0', s=0.1)
                    ax.scatter(oat_off[off_start_index:off_end_index], mat_off[off_start_index:off_end_index], marker='o', color='#3668A0', s=0.1)
            else:
                if on_check.get() & off_check.get():
                    points_check.set(True)
                    App.current.update()
                    ax.scatter(oat_on[on_start_index:on_end_index], mat_on[on_start_index:on_end_index], marker='o', color='#3668A0', s=0.1)
                    ax.scatter(oat_off[off_start_index:off_end_index], mat_off[off_start_index:off_end_index], marker='o', color='#3668A0', s=0.1)
                elif on_check.get():
                    points_check.set(True)
                    App.current.update()
                    ax.scatter(oat_on[on_start_index:on_end_index], mat_on[on_start_index:on_end_index], marker='o', color='#3668A0', s=0.1)
                elif off_check.get():
                    points_check.set(True)
                    App.current.update()
                    ax.scatter(oat_off[off_start_index:off_end_index], mat_off[off_start_index:off_end_index], marker='o', color='#3668A0', s=0.1)
                else:
                    points_check.set(False)
                    on_check.set(False)
                    off_check.set(False)
                    App.current.update()

            plot_standardized_settings(ax)
            canvas.draw()
            canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)
#MARK: PlotMatplotlib
        def plot_matplotlib(oat_on, oat_off, mat_on, mat_off, parameters):

            # Plot raw_data
            fig, ax = plt.subplots()
            ax.scatter(oat_on, mat_on, marker='o', color='#3668A0', s=2, alpha=0.4)
            ax.scatter(oat_off, mat_off, marker='o', color='#3668A0', s=2, alpha=0.4)

            draw_ideal_curve(ax, parameters)
            plot_standardized_settings(ax)
            fig.set_size_inches(6, 5)
            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

            return canvas, fig, ax

        start_month, start_date, start_year, end_month, end_date, end_year, date_on, date_off, oat_on, oat_off, mat_on, mat_off = process_data_points(raw_data)
        parameters_array = process_ideal_curve_parameters(curve_parameters)

        on_start_index = 0
        off_start_index = 0
        on_end_index = len(date_on) - 1
        off_end_index = len(date_off) - 1

        App.frames[frame_id] = ctk.CTkFrame(self, corner_radius=8, fg_color="#212121")
        self.title("Ideal Economizer Curve and Data Points")

        num_val = (App.frames[frame_id].register(self.Num_Validation), '%P')

        input_column_width = 350

        # Create subframes for plot and widgets
        plot_frame = ctk.CTkFrame(App.frames[frame_id])
        plot_frame.pack(side=ctk.LEFT, padx=10, pady=10, fill=ctk.BOTH, expand=True)

        widgets_frame = ctk.CTkFrame(App.frames[frame_id], width=input_column_width)
        widgets_frame.pack(side=ctk.RIGHT, padx=10, pady=10, fill=ctk.BOTH)

        # Plot using matplotlib, moved down so it could consider toggles
        canvas, fig, ax = plot_matplotlib(oat_on, oat_off, mat_on, mat_off, parameters_array)

        curve_check = ctk.BooleanVar()
        curve_check.set(True)
        points_check = ctk.BooleanVar()
        points_check.set(True)
        on_check = ctk.BooleanVar()
        on_check.set(True)
        off_check = ctk.BooleanVar()
        off_check.set(True)
        checkbox_dim = 30
        ideal_curve_toggle = ctk.CTkCheckBox(widgets_frame, text="Ideal Curve", font=self.my_font, checkbox_width=checkbox_dim, checkbox_height=checkbox_dim, variable=curve_check, command=partial(handle_plot, "curve", oat_on, oat_off, mat_on, mat_off, parameters_array))
        ideal_curve_toggle.grid(row=1, column=0, sticky='w', pady=5)

        data_points_toggle = ctk.CTkCheckBox(widgets_frame, text="Data Points", font=self.my_font, checkbox_width=checkbox_dim, checkbox_height=checkbox_dim, variable=points_check, command=partial(handle_plot, "points", oat_on, oat_off, mat_on, mat_off, parameters_array))
        data_points_toggle.grid(row=2, column=0, sticky='w', pady=5)

        motor_on_toggle = ctk.CTkCheckBox(widgets_frame, text="Motor On", font=self.my_font, checkbox_width=checkbox_dim, checkbox_height=checkbox_dim, variable=on_check, command=partial(handle_plot, "on", oat_on, oat_off, mat_on, mat_off, parameters_array))
        motor_on_toggle.grid(row=3, column=0, sticky='w', padx=30, pady=5)

        motor_off_toggle = ctk.CTkCheckBox(widgets_frame, text="Motor Off", font=self.my_font, checkbox_width=checkbox_dim, checkbox_height=checkbox_dim, variable=off_check, command=partial(handle_plot, "off", oat_on, oat_off, mat_on, mat_off, parameters_array))
        motor_off_toggle.grid(row=4, column=0, sticky='w', padx=30, pady=5)

        date_range_label = ctk.CTkLabel(widgets_frame, text="Date Range:", font=self.my_font)
        date_range_label.grid(row=5, column=0, sticky='w', pady=5)

        date_range_frame =ctk.CTkFrame(widgets_frame, width=input_column_width, bg_color=widgets_frame.cget("bg_color"), fg_color=widgets_frame.cget("fg_color"))
        date_range_frame.grid_columnconfigure((0, 2, 4), weight=1)
        date_range_frame.grid(row=6, column=0, sticky='ew', pady=5)




        placeholder_width = 2
        input_width = (input_column_width - placeholder_width) // 10

        #color boxes red if input is invalid
        self.month1_entry = ctk.CTkEntry(date_range_frame, placeholder_text=start_month, validate="key", width=input_width)
        self.month1_entry.grid(row=0, column=0, sticky='nsew', pady=5)
        self.month1_entry.bind("<Button-1>", self.NumKeyboardCallback(self.month1_entry, 600, 200))
        slash_label_1 = ctk.CTkLabel(date_range_frame, font=self.my_font, text="/", text_color="#fff")
        slash_label_1.grid(row=0, column=1, sticky="nsew") 
        self.date1_entry = ctk.CTkEntry(date_range_frame, placeholder_text=start_date, validate="key", width=input_width) 
        self.date1_entry.grid(row=0, column=2, sticky='nsew', pady=5)
        self.date1_entry.bind("<Button-1>", self.NumKeyboardCallback(self.date1_entry, 600, 200))
        slash_label_2 = ctk.CTkLabel(date_range_frame, font=self.my_font, text="/", text_color="#fff")
        slash_label_2.grid(row=0, column=3, sticky="nsew")
        self.year1_entry = ctk.CTkEntry(date_range_frame, placeholder_text=start_year, validate="key", width=input_width) 
        self.year1_entry.grid(row=0, column=4, sticky='nsew', pady=5)
        self.year1_entry.bind("<Button-1>", self.NumKeyboardCallback(self.year1_entry, 600, 200))

        to_label = ctk.CTkLabel(date_range_frame, text=" to ")
        to_label.grid(row=1, column=2, sticky='ew', pady=5)

        self.month2_entry = ctk.CTkEntry(date_range_frame, placeholder_text=end_month, validate="key", width=input_width) 
        self.month2_entry.grid(row=2, column=0, sticky='nsew', pady=5)
        self.month2_entry.bind("<Button-1>", self.NumKeyboardCallback(self.month2_entry, 600, 200))
        slash_label_3 = ctk.CTkLabel(date_range_frame, font=self.my_font, text="/", text_color="#fff")
        slash_label_3.grid(row=2, column=1, sticky="nsew")
        self.date2_entry = ctk.CTkEntry(date_range_frame, placeholder_text=end_date, validate="key", width=input_width) 
        self.date2_entry.grid(row=2, column=2, sticky='nsew', pady=5)
        self.date2_entry.bind("<Button-1>", self.NumKeyboardCallback(self.date2_entry, 600, 200))
        slash_label_4 = ctk.CTkLabel(date_range_frame, font=self.my_font, text="/", text_color="#fff")
        slash_label_4.grid(row=2, column=3, sticky="nsew")
        self.year2_entry = ctk.CTkEntry(date_range_frame, placeholder_text=end_year, validate="key", width=input_width) 
        self.year2_entry.grid(row=2, column=4, sticky='nsew', pady=5)
        self.year2_entry.bind("<Button-1>", self.NumKeyboardCallback(self.year2_entry, 600, 200))

        submit_button = ctk.CTkButton(widgets_frame, font=self.my_font, text="Submit", corner_radius=4, width=1, height=40, command=lambda: handle_date_range(self.month1_entry.get(), self.date1_entry.get(), self.year1_entry.get(), 
                    self.month2_entry.get(), self.date2_entry.get(), self.year2_entry.get(), parameters_array)) 
        submit_button.grid(row=7, column=0, sticky='ew', padx=4, pady=5)

        sampling_rate_label = ctk.CTkLabel(widgets_frame, text=f"Sample Rate: {parameters_array['Sampling Rate']} min", font=self.my_font)
        sampling_rate_label.grid(row=8, column=0, sticky='w', pady=5)

        return_home_button = ctk.CTkButton(widgets_frame, font=self.my_font, text="Return Home", height=40, corner_radius=4, command=partial(self.toggle_frame_by_id, "home"))
        return_home_button.grid(row=9, column=0, columnspan= 5, sticky='sew', padx=4, pady=5)

    def InitFilterFiles(self):
        text = self.search_input.get()
        self.filtered_frame_files = []
        scrollable_files = self.scrollable_logger_files
        if (self.use_local_data):
            scrollable_files = self.scrollable_local_files
            for file in self.scrollable_logger_files:
                file.grid_forget()
        else:
            for file in self.scrollable_local_files:
                file.grid_forget()
        for i, file in enumerate(scrollable_files):
            file.grid(row=i, column=0, padx=0, pady=10, sticky="nsew")

#MARK: FilterFiles
    def FilterFiles(self, *args):
        print("in FilterFiles: self.filter_file=", self.filter_files)
        if (self.filter_files):
            text = self.search_input.get()
            self.filtered_frame_files = []
            scrollable_files = self.scrollable_logger_files
            if (self.use_local_data):
                scrollable_files = self.scrollable_local_files
                for file in self.scrollable_logger_files:
                    file.grid_forget()
            else:
                for file in self.scrollable_local_files:
                    file.grid_forget()
            for file in scrollable_files:
                if file.cget("text").lower().startswith(text.lower()):
                    self.filtered_frame_files.append(file)
                else:
                    file.grid_forget()
            for i, file in enumerate(self.filtered_frame_files):
                file.grid(row=i, column=0, padx=0, pady=10, sticky="nsew")

#MARK: GetAvailableArduinoFiles  
    def GetAvailableArduinoFiles(self):
        print("Getting files")
        files = []
        try:
            response = CustomSerial("-p?", 115200)
            if (response != "AOK"):
                print("unexpected response: ", response)
                return files
            files = CustomSerial("-g?", 115200).split(",")

            for i in range(len(files)):
                files[i] = files[i].split(".")[0]
            files.sort()
        except serial.SerialException as e:
            print("Serial connection failed")
        return files
    def GetAvailableDownloadedFiles(self):
        param_files = os.listdir("/home/eat/Documents/ME470_Economizer/RaspberryPi/ParamFiles/")
        data_files = os.listdir("/home/eat/Documents/ME470_Economizer/RaspberryPi/CSV_Files/")

        for i in range(len(param_files)):
            param_files[i] = param_files[i].split(".")[0]
        for i in range(len(data_files)):
            data_files[i] = data_files[i].split(".")[0]
        return data_files, param_files
        
#MARK: SelectFiles
    def FileSelection(self, file_name):
        self.filter_files = False
        print("file selection")
        print("in file section self.filter_files= ", self.filter_files)
        self.error_info_label.configure(text="", )
        curr_input = self.search_input.get()
        self.search_input.delete(0,len(curr_input))
        self.search_input.insert(0, file_name)
        scrollable_files = self.scrollable_logger_files
        if (self.use_local_data):
            scrollable_files = self.scrollable_local_files
        # change the color of the button to be slightly greyed out
        # reset the colors of all of the other buttons
        for i in range(len(scrollable_files)):
            text = scrollable_files[i].cget("text")
            if (text == file_name):
                self.selected_file = i
                scrollable_files[i].configure(fg_color="#635888")
            else:
                scrollable_files[i].configure(fg_color="#39334f")
    def EnableFilter(self, *args):
        self.filter_files = True

    def KeyboardCallback(self, event, x_loc, y_loc):
        self.keyboard = PopupKeyboard(event, x=x_loc, y=y_loc, keyheight=3, keywidth=6)
        self.keyboard.bind('<Map>', self.EnableFilter)
        self.keyboard.disable = False

    def NumKeyboardCallback(self, event, x_loc, y_loc):
        self.numkeyboard= PopupNumpad(event, x=x_loc, y=y_loc, keyheight=60, keywidth=60)
        self.numkeyboard.disable = False
# MARK: Loading Frame
    def create_loading_frame(self, frame_id):
        App.frames[frame_id] = ctk.CTkFrame(self, corner_radius=8, fg_color="#212121")
        self.title("Loading")
        print("creating loading frame")
    
        # configure the grid, but doesn't set size. I think if you keep adding stuff it works
        App.frames[frame_id].grid_columnconfigure(0, weight=1)
        App.frames[frame_id].grid_rowconfigure((0, 1), weight=1)
        text_frame = ctk.CTkFrame(App.frames[frame_id], width=600, height=200, fg_color="#212121")
        text_frame.grid(row=1, column=0, sticky="n")
        text_frame.grid_rowconfigure(0, weight=1)

        loading_label = ctk.CTkLabel(App.frames[frame_id], font=self.home_font, text="Downloading")
        loading_label.grid(row=0, column=0, padx=20, pady=0, sticky="nsew")
        self.progressbar = ctk.CTkProgressBar(text_frame, height=30, width=300, corner_radius=4)
        self.progressbar.grid(row=1, column=0, pady=0, sticky="n")
        self.progressbar.set(0)
        self.percentage_label = ctk.CTkLabel(text_frame, font=self.home_font, text="0%")
        self.percentage_label.grid(row=2, column=0, pady=0, sticky="n")
        
    def CheckDownloadFromPi(self):
        self.select_system_button.configure(state="disabled")
        App.current.after(10, self.CheckDownloadFromPi_2) # force it to wait 1ms until after button is disabled
        self.error_info_label.configure(text="", )
        self.search_input.delete(0,len(self.search_input.get()))

# MARK: CheckDownload
    def CheckDownloadFromPi_2(self):
        print("checking load from pi")
        if self.selected_file is None:
            self.error_info_label.configure(text="*No File Selected", )
            return
        scrollable_files = self.scrollable_logger_files
        if (self.use_local_data):
            self.selected_file_name = self.scrollable_local_files[self.selected_file].cget("text")
            print("file selected: " + self.selected_file_name)

            parameter_files = self.selected_file_name + ".params"
            self.selected_file_name = self.selected_file_name + ".csv"
            self.create_curve_frame("curve", self.selected_file_name, parameter_files)
            self.toggle_frame_by_id("curve")
        else:
            self.selected_file_name = scrollable_files[self.selected_file].cget("text")
            print("file selected: " + self.selected_file_name)
            self.toggle_frame_by_id("loading")
            App.current.after(200, self.DownloadDataFromPi) # force it to wait 50ms until after button is disabled
        self.select_system_button.configure(state="normal")

# MARK: DownloadData
    def DownloadDataFromPi(self):
        if (not self.use_local_data):
            try:
                self.date_data, self.oat_data, self.mat_data, self.motor_data = self.ReadAllData("-g={}.csv".format(self.selected_file_name), 115200)
                parameters = CustomSerial("-x={}.params".format(self.selected_file_name), 115200)
                sample_rate = (self.date_data[10] - self.date_data[0])//600
                print("sample rate: ", sample_rate)
                if parameters == "ER2":
                    print("This parameters file does not exist")
                print("type of parameters", type(parameters))
                params_file_name = 'Param'
                with open('/home/eat/Documents/ME470_Economizer/RaspberryPi/ParamFiles/{}.params'.format(self.selected_file_name), 'w', newline='') as param_file:
                    file_writer = csv.writer(param_file, delimiter=',')
                    parameters = parameters.split(",")
                    parameters.append(sample_rate)
                    file_writer.writerow(parameters)
            except Exception as e:
                print("Arduino Connection error: ", e)
            self.SetScrollableFiles()
            
        parameter_files = self.selected_file_name + ".params"
        self.selected_file_name = self.selected_file_name + ".csv"
        self.create_curve_frame("curve", self.selected_file_name, parameter_files)
        self.toggle_frame_by_id("curve")
        self.progressbar.set(0) # reset loading bar
        self.percentage_label.configure(text="{:.0f}%".format(0))
        
    def DestroyTopLevel(self):
        self.toplevel_window.destroy()
        self.search_input.focus() # to prevent keyboard from previous window from popping up randomly. Idk why

# MARK: End_Frame
    def create_end_frame(self, frame_id):
        App.frames[frame_id] = ctk.CTkFrame(self, corner_radius=8, fg_color="#212121")
        self.title("Home")
    
        # configure the grid, but doesn't set size. I think if you keep adding stuff it works
        App.frames[frame_id].grid_columnconfigure((0, 1), weight=1)
        App.frames[frame_id].grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=0, minsize=90)


        home_label = ctk.CTkLabel(App.frames[frame_id], text="Data Logging Has Begun", font=self.home_font)
        home_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        button3 = ctk.CTkButton(App.frames[frame_id], font=self.my_font, text="Return Home",  command=partial(self.toggle_frame_by_id,"home"))
        button3.grid(row=3, column=0, padx=20, pady=20, sticky="nsw")

    def DetermineDownloadSource(self, button_pressed):
        if button_pressed == "View Downloaded Data":
            self.use_local_data = True
        elif button_pressed == "Download Data":
            self.use_local_data = False
        else:
            print("Incorrect message for downloading data")
        self.InitFilterFiles()
        self.toggle_frame_by_id("download")
    
    #MARK: ReadAllData
    def ReadAllData(self, message, baud_rate): # Randomly generated data with motor -> 17.219s without csv file read
        try:
            print("reading all data: ")
            ser = serial.Serial('/dev/ttyACM0', baud_rate, timeout=2)
            print("{}\r\n".format(message))
            initial_time = time()
            filesize = CustomSerial(message, baud_rate)
            header = ser.readline().decode().strip()
            total_bytes = int(filesize.split("=")[1])
            print("filesize: ", total_bytes)
            tenth_of_total_bytes = total_bytes//10
            increment = 0
            num_bytes_received = 0
            start_time = time()
            # print("initial response: ", response)
            oat_data = []
            mat_data = []
            date_data = []
            motor_data = []
            test_start = time()
            filename = "/home/eat/Documents/ME470_Economizer/RaspberryPi/CSV_Files/{}".format(message[3:])
            with open(filename, 'w', newline='') as csv_file:
                print("opened file")
                csv_writer = csv.writer(csv_file, delimiter=',')
                while (time() - start_time) < 2:
                    response = ser.readline().decode().strip()
                    if (response == "" or len(response.split(',')) < 4):   
                        continue
                    num_bytes_received += len(response)
                    date, OAT, MAT, Motor_state = response.split(',')
                    # write data to CSV
                    csv_writer.writerow([date, OAT, MAT, Motor_state])
                    if (num_bytes_received >= tenth_of_total_bytes*increment):
                        progress = float(num_bytes_received)/float(total_bytes)
                        self.progressbar.set(progress)
                        self.percentage_label.configure(text="{:.0f}%".format(progress*100))
                        App.current.update()
                        increment += 1
                    try:
                        oat_data.append(float(OAT))
                        mat_data.append(float(MAT))
                        date_data.append(date)
                        motor_data.append(bool(Motor_state))
                    except Exception as e:
                        print('appending the data to the list caused: ', e)
                    start_time = time() # restart so we wait a maximum of 6 seconds for each data point. If it's longer, assume that the data transfer is done
            ser.close()
            print("time elapsed: ", time() - test_start)
            self.progressbar.set(1) 
            self.percentage_label.configure(text="{:.0f}%".format(100))
            App.current.update()
        except Exception as e:
            print('reading the data caused: ', e)
            return [], [], [], []
        return date_data, oat_data, mat_data, motor_data


# MARK:toggleFrame
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
                print("third frame change case")
                App.current = App.frames[frame_id]
                App.current.pack(in_=self.main_container, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
        else:
            print("app.frames is none")

a = App()
a.mainloop()
