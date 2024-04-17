
import tkinter
import customtkinter as ctk
from functools import partial
import os
import serial
from csv import writer as CsvWriter
from CTkPopupKeyboard import PopupKeyboard, PopupNumpad
from PIL import Image
from time import strftime, localtime, time, sleep
import datetime
import calendar
#import pytz
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

DARK_MODE = "dark"
ctk.set_appearance_mode(DARK_MODE)
ctk.set_default_color_theme("blue")

def CustomSerial(message, baud_rate):
    ser = serial.Serial('/dev/ttyACM0', baud_rate, timeout=2)
    ser.write("{}\r\n".format(message).encode())
    start_time = time()
    response = ser.readline().decode().strip()
    while (time() - start_time) < 6 and response == "":
        ser.write("{}\r\n".format(message).encode())
        response = ser.readline().decode().strip()
        # print("response: '{}'".format(response))
    ser.close()
    return response

def CustomSerialContinuous(message, baud_rate):
    ser = serial.Serial('/dev/ttyACM0', baud_rate, timeout=2)
    print("{}\r\n".format(message))
    response = CustomSerial(message, 115200)
    response = ser.readline().decode().strip()
    response = ser.readline().decode().strip()
    start_time = time()
    # print("initial response: ", response)
    oat_data = []
    mat_data = []
    date_data = []
    motor_data = []
    while (time() - start_time) < 6:
        # ser.write("{}\r\n".format(message).encode())
        response = ser.readline().decode().strip()
        # print("while loop response: '{}'".format(response))
        # print(len(response.split(',')))
        # print("got here 2")
        if (response == "" or len(response.split(',')) < 4):
            # print("not enough data: ", data)
            continue
        # print("got here 1")
        date, OAT, MAT, Motor_state = response.split(',')
        # print("got here 2")
        # print("date: {}, OAT: {}, MAT: {}, Motor_state: {}".format(date, OAT, MAT, Motor_state))
        try:
            print("oat: ", OAT)
            oat_data.append(float(OAT))
            mat_data.append(float(MAT))
            date_data.append(date)
            motor_data.append(bool(Motor_state))
        except Exception as e:
            print('appending the data to the list caused: ', e)
        start_time = time() # restart so we wait a maximum of 6 seconds for each data point. If it's longer, assume that the data transfer is done

    ser.close()
    return date_data, oat_data, mat_data, motor_data

# def CustomFileRead(message, baud_rate):
#     response = /s
#     start_time = time()
#     oat_data = []
#     mat_data = []
#     date_data = []
#     motor_data = []
#     while (time() - start_time) < 6 or response == "":
#         # ser.write(b"message\r\n") # shouldn't need this
#         response = ser.readline().decode().strip()
#         if (len(response.split(',')) < 4):
#             print("not enough data: ", data)
#             continue
#         date, OAT, MAT, Motor_state = response.split(',')
#         oat_data.append(float(oat[:-2]))
#         mat_data.append(float(mat))
#         date_data.append(date)
#         motor_data.append(bool(motor))

#         start_time = time() # restart so we wait a maximum of 6 seconds for each data point. If it's longer, assume that the data transfer is done

#     return date_data, oat_data, mat_data, motor_data


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
        self.my_font = ctk.CTkFont(family="TkTextFont", size=15, weight="bold")
        self.home_font = ctk.CTkFont(family="TkTextFont", size=30, weight="bold")

        # root!
        self.main_container = ctk.CTkFrame(self, corner_radius=8, fg_color=self.bg)
        self.main_container.pack(fill=tkinter.BOTH, expand=True, padx=8, pady=8)
        self.oat_data = []
        self.mat_data = []
        self.date_data = []
        self.motor_data = []
        # create each of th e frames. Maybe set the first one to 
        self.create_input_frame("input")
        self.create_home_frame("home")
        self.create_download_frame("download")
        
        # set the initial frame to display  
        App.current = App.frames["home"]
        App.current.pack(in_=self.main_container, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
# MARK: Creat input frame
    def create_input_frame(self, frame_id):
        App.frames[frame_id] = ctk.CTkFrame(self, corner_radius=8, fg_color="#212121")
        self.title("Installation: Set Parameters for New System")

        num_val = (App.frames[frame_id].register(self.Num_Validation), '%P')
   
        # configure the grid, but doesn't set size. I think if you keep adding stuff it works
        App.frames[frame_id].grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        App.frames[frame_id].grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10), weight=1)

        # first row is the system name, which has text and user input ->  2 columns
        system_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="New System Name:")
        system_label.grid(row=0, column = 0, padx=10, pady=10, sticky="nsew")
        self.system_name_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text="Enter System Name")
        self.system_name_input.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.system_name_input.bind("<Button-1>", self.KeyboardCallback)

        # # next section is 4 columns, 9 rows
        input_column_width =150
        set_inputs_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Set Inputs:")
        set_inputs_label.grid(row=1, column=0,padx=10, pady=5, sticky="nsew")

        lockout_temp_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Lockout Temp:")
        lockout_temp_label.grid(row=1, column=1,padx=10, pady=5, sticky="e")
        self.lockout_temp_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val, width=input_column_width)
        self.lockout_temp_input.grid(row=1, column=2, columnspan=5, padx=10, pady=5, sticky="nsw")
        lockout_temp_unit_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text = u"\u00b0"+"F")
        lockout_temp_unit_label.grid(row=1, column=7, padx=10, pady=5,sticky="nsw")
        self.lockout_temp_input.bind("<Button-1>", self.NumKeyboardCallback(self.lockout_temp_input))

        min_OAT_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Min % Outside Air Temp:")
        min_OAT_label.grid(row=2, column=1,padx=10, pady=5, sticky="e")
        self.min_OAT_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val, width=input_column_width)
        self.min_OAT_input.grid(row=2, column=2, columnspan=5, padx=10, pady=5, sticky="nsw")
        min_OAT_unit_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text = "%")
        min_OAT_unit_label.grid(row=2, column=7, padx=10, pady=5,sticky="nsw")
        self.min_OAT_input.bind("<Button-1>", self.NumKeyboardCallback(self.min_OAT_input))

        RAT_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Estimated Return Air Temp:")
        RAT_label.grid(row=3, column=1,padx=10, pady=5, sticky="e")
        self.RAT_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val, width=input_column_width)
        self.RAT_input.grid(row=3, column=2, columnspan=5, padx=10, pady=5, sticky="nsw")
        RAT_unit_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text = u"\u00b0"+"F")
        RAT_unit_label.grid(row=3, column=7, padx=10, pady=5,sticky="nsw")
        self.RAT_input.bind("<Button-1>", self.NumKeyboardCallback(self.RAT_input))


        LL_Lockout_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Low Limit Lockout Temp:")
        LL_Lockout_label.grid(row=4, column=1,padx=10, pady=10, sticky="e")
        self.LL_Lockout_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val)
        self.LL_Lockout_input.grid(row=4, column=2, columnspan=3, padx=10, pady=10, sticky="ew")
        LL_Lockout_unit_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text = u"\u00b0"+"F")
        LL_Lockout_unit_label.grid(row=4, column=7, padx=10, pady=5,sticky="nsw")
        self.LL_Lockout_input.bind("<Button-1>", self.NumKeyboardCallback(self.LL_Lockout_input))

    
        HL_Lockout_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="High Limit Lockout Temp:")
        HL_Lockout_label.grid(row=5, column=1,padx=10, pady=5, sticky="e")
        self.HL_Lockout_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val, width=input_column_width)
        self.HL_Lockout_input.grid(row=5, column=2, columnspan=5, padx=10, pady=5, sticky="nsw")
        HL_Lockout_unit_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text = u"\u00b0"+"F")
        HL_Lockout_unit_label.grid(row=5, column=7, padx=10, pady=5,sticky="nsw")
        self.HL_Lockout_input.bind("<Button-1>", self.NumKeyboardCallback(self.HL_Lockout_input))

        #stopped here
        MAT_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Ideal Mixed Air Temp:")
        MAT_label.grid(row=6, column=1,padx=10, pady=5, sticky="e")
        self.MAT_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val, width=input_column_width)
        self.MAT_input.grid(row=6, column=2, columnspan=5, padx=10, pady=5, sticky="nsw")
        MAT_unit_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text = u"\u00b0"+"F")
        MAT_unit_label.grid(row=6, column=7, padx=10, pady=5,sticky="nsw")
        self.MAT_input.bind("<Button-1>", self.NumKeyboardCallback(self.MAT_input))


        SR_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Sampling Rate:")
        SR_label.grid(row=7, column=1,padx=10, pady=5, sticky="e")
        self.SR_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val, width=input_column_width)
        self.SR_input.grid(row=7, column=2, columnspan=5, padx=10, pady=5, sticky="nsw")
        SR_unit_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text = "min")
        SR_unit_label.grid(row=7, column=7, padx=10, pady=5,sticky="nsw")
        self.SR_input.bind("<Button-1>", self.NumKeyboardCallback(self.SR_input))

        time_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Set Current Time:")
        time_label.grid(row=8, column=1,padx=10, pady=5, sticky="e")
        self.time_input1 = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val, width=input_column_width//3)
        self.time_input1.grid(row=8, column=2, columnspan=2, padx=(10,0), pady=5, sticky="nsw")
        time_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text=":", text_color="#fff")
        time_label.grid(row=8, column=4,padx=0, pady=5, sticky="ew")
        self.time_input2 = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val, width=input_column_width//3)
        self.time_input2.grid(row=8, column=5, columnspan=2, padx=(0,10), pady=5, sticky="nsw")
        time_unit_label = ctk.CTkOptionMenu(App.frames[frame_id], values=["AM", "PM"], fg_color=self.bg)
        time_unit_label.grid(row=8, column=7, padx=10, pady=5,sticky="nsw")        
        self.time_input1.bind("<Button-1>", self.NumKeyboardCallback(self.time_input1))
        self.time_input2.bind("<Button-1>", self.NumKeyboardCallback(self.time_input2))

        date_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Date:")
        date_label.grid(row=9, column=1,padx=10, pady=5, sticky="e")
        self.month_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val, width=input_column_width//4)
        self.month_input.grid(row=9, column=2, columnspan=1, padx=(10, 0), pady=5, sticky="nsw")

        slash_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="/", text_color="#fff")
        slash_label.grid(row=9, column=3,padx=0, pady=5, sticky="ew")
        self.day_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val, width=input_column_width//4)
        self.day_input.grid(row=9, column=4, columnspan=1, padx=0, pady=5, sticky="nsw")
        slash_label_2 = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="/", text_color="#fff")
        slash_label_2.grid(row=9, column=5,padx=0, pady=5, sticky="ew")
        self.year_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ", validate="key", validatecommand=num_val, width=input_column_width//4)
        self.year_input.grid(row=9, column=6, columnspan=1, padx=0, pady=5, sticky="nsw")
        date_unit_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text = "Month/Day/Year")
        date_unit_label.grid(row=9, column=7, padx=10, pady=5,sticky="nsw")

        # for running on this computer
        self.month_input.bind("<Button-1>", self.NumKeyboardCallback(self.month_input))
        self.day_input.bind("<Button-1>", self.NumKeyboardCallback(self.day_input))
        self.year_input.bind("<Button-1>", self.NumKeyboardCallback(self.year_input))

        # end is 3 buttons for going to each page
        
        self.view_plot_button = ctk.CTkButton(App.frames[frame_id], font=self.my_font, text="View Ideal Economizer Curve", command=partial(self.handle_parameters_for_curve_view, App.frames[frame_id]), corner_radius=50)
        self.view_plot_button.grid(row=10, column=1, columnspan = 3, padx=20, pady=20, sticky="ew")

        self.save_exit_button = ctk.CTkButton(App.frames[frame_id], font=self.my_font, text="Save & Begin Logging", command=self.handle_install_inputs, corner_radius=50)
        self.save_exit_button.grid(row=10, column=6, columnspan=2, padx=20, pady=20, sticky="ew")
        self.cancel_button = ctk.CTkButton(App.frames[frame_id], command=partial(self.toggle_frame_by_id, "home"), font=self.my_font, text="Cancel", corner_radius=50)
        self.cancel_button.grid(row=10, column=8, padx=20, pady=20, sticky="ew")

    def handle_parameters_for_curve_view(self, frame):
        self.system_name = self.system_name_input.get()
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
            self.lockout_temp = float(numerical_inputs[0].get())
            self.min_OAT = float(numerical_inputs[1].get())
            self.RAT = float(numerical_inputs[2].get())
            self.LL_Lockout = float(numerical_inputs[3].get())
            self.HL_Lockout = float(numerical_inputs[4].get())
            self.MAT = float(numerical_inputs[5].get())
            self.SR = float(numerical_inputs[6].get())

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

    def handle_install_inputs(self):
        self.system_name = self.system_name_input.get()
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
            self.lockout_temp = self.lockout_temp_input.get()
            self.min_OAT = self.min_OAT_input.get()
            self.RAT = self.RAT_input.get()
            self.LL_Lockout = self.LL_Lockout_input.get()
            self.HL_Lockout = self.HL_Lockout_input.get()
            self.MAT = self.MAT_input.get()
            self.SR = self.SR_input.get()

            self.hours = self.time_input1.get()
            self.minutes = self.time_input2.get()
            self.month = self.month_input.get()
            self.day = self.day_input.get()
            self.year = self.year_input.get()
            #tz = pytz.timezone("US/Central")
            #date_string = datetime.datetime(int(self.year), int(self.month), int(self.day), int(self.hours), int(self.minutes)) 
            #corrected_date = tz.localize(date_string)
            #print("date: ", date_string)
            #epoch_date = calendar.timegm(corrected_date.timetuple())
            #print("epoch_date: ", epoch_date)
            
            # send data to the arduino:
            self.SendInstallationInputs()

            # store in CSV file?
            # TODO: Determine if necessary
            #parameters = "M%OA," + self.min_OAT + "\nRAT," + self.RAT + "\nLLT," + self.LL_Lockout + "\nHLT," + self.HL_Lockout + "\niMAT," + self.MAT + "\nSR," + self.SR
            #print(parameters)
            #with open(system_name + ".csv", 'w', newline='') as new_file:
            #    csv_writer = CsvWriter(new_file) # create the new file or start writing to existing file
            #    csv_writer.writerow(parameters) # Write first row as the user parameters
            # TODO: add the date
            # at end if everything is good, move to last page
            self.toggle_frame_by_id("download")

    def SendInstallationInputs(self):
        response = CustomSerial("-p?\r\n", 115200)
        print("response: ", response)
        if (response != "AOK"):
            # TODO: give some indication of error
            return
        # epoch_date = datetime.datetime(int(self.year), int(self.month), int(self.day), int(self.hours), int(self.minutes)) # TODO: calculate the epoch time
        # epoch_date = calendar.timegm(epoch_date.timetuple())
        epoch_date = 0
        print("epoch_date: ", epoch_date)
        response = CustomSerial("-n={}.csv\r\n".format(self.system_name), 115200) # set the system name
        response = CustomSerial("-t={}\r\n".format(epoch_date), 115200) # set date/time
        response = CustomSerial("-p={},{},{},{},{}\r\n".format(self.min_OAT, self.RAT, self.LL_Lockout, self.HL_Lockout, self.MAT), 115200) #params in order of M%OA,RAT,LLT,HLT,iMAT
        response = CustomSerial("-f={}\r\n".format(self.SR), 115200) # set sample rate
        print("Sample rate: ", CustomSerial("-f?", 115200))

        response = CustomSerial("-s=1\r\n", 115200) # start recording

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
        App.frames[frame_id].grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
    
        home_label = ctk.CTkLabel(App.frames[frame_id], text="Welcome to EATPi", font=self.home_font)
        home_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
    
        home_icon = ctk.CTkImage(light_image=Image.open('home_icon2.png'), dark_image=Image.open('home_icon2.png'), size=(50, 50))
        image1 = ctk.CTkLabel(App.frames[frame_id], text="", image=home_icon)
        image1.grid(row=0, column=1, padx=20, pady=20, sticky="e")
    
        button1 = ctk.CTkButton(App.frames[frame_id], font=self.my_font, text="Installation: Set Parameters for New System",  command=partial(self.toggle_frame_by_id, "input"))
        button1.grid(row=1, column=0, padx=20, pady=20, sticky="w")
    
        button2 = ctk.CTkButton(App.frames[frame_id], font=self.my_font, text="View Downloaded Data",  command=partial(self.toggle_frame_by_id, "download"))
        button2.grid(row=2, column=0, padx=20, pady=20, sticky="w")
    
        button3 = ctk.CTkButton(App.frames[frame_id], font=self.my_font, text="Download Data",  command=lambda: self.show_additional_buttons(App.frames[frame_id], button3))
        button3.grid(row=3, column=0, padx=20, pady=20, sticky="w")
    
        button4 = ctk.CTkButton(App.frames[frame_id], font=self.my_font, text="Back")
        button4.grid(row=6, column=1, padx=20, pady=20, sticky="e")

    def show_additional_buttons(self, frame, button):

        button.configure(fg_color="gray")
        # Create two additional buttons
        button5 = ctk.CTkButton(frame, text="Select Existing System", font=self.my_font, command=partial(self.toggle_frame_by_id, "download"))
        button6 = ctk.CTkButton(frame, text="Create New System", font=self.my_font, command=partial(self.toggle_frame_by_id, "input"))
        
        # Pack the buttons to display them underneath the main button
        button5.grid(row=4, column=0, padx=100, sticky="w")
        button6.grid(row=5, column=0, padx=100, sticky="w")

    def create_download_frame(self, frame_id):
        App.frames[frame_id] = ctk.CTkFrame(self, corner_radius=8, fg_color="#212121")
        self.title("Download Data")

        num_val = (App.frames[frame_id].register(self.Num_Validation), '%P')
   
        # configure the grid, but doesn't set size. I think if you keep adding stuff it works
        App.frames[frame_id].grid_columnconfigure((0, 1, 2, 3), weight=1)
        App.frames[frame_id].grid_rowconfigure((0, 1, 2, 3), weight=1)
        
        search_label = ctk.CTkLabel(App.frames[frame_id], font=self.my_font, text="Search Existing:")
        search_label.grid(row=0, column=0,padx=10, pady=10, sticky="w")
        self.search_input = ctk.CTkEntry(App.frames[frame_id], placeholder_text=" ")
        self.search_input.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="w")

        #self.new_download_button = ctk.CTkButton(App.frames[frame_id], text="Download New System")
        #self.new_download_button.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

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
        self.select_system_button = ctk.CTkButton(App.frames[frame_id], font=self.my_font, text="Select System", command=self.DownloadDataFromPi, corner_radius=100)
        self.select_system_button.grid(row=3, column=1, columnspan = 2, padx=20, pady=20, sticky="ew")

        self.back_button = ctk.CTkButton(App.frames[frame_id], command=partial(self.toggle_frame_by_id, "home"), font=self.my_font, text="Back")
        self.back_button.grid(row=3, column=3, padx=20, pady=20, sticky="ew")
        
    def create_curve_frame(self, frame_id):
        def plot_matplotlib():
            # Example plot using matplotlib
            fig, ax = plt.subplots()
            # ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
            print("oat_data: ", self.oat_data)
            print("mat_data: ", self.mat_data)
            ax.scatter(self.oat_data, self.mat_data, s=0.5, alpha=0.5)
            ax.set_xlabel('Outside Air Temperature [°F]')
            ax.set_ylabel('Mixed Air Temperature [°F]')

            fig.set_size_inches(6, 3)
            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.draw()
            canvas.get_tk_widget().grid()

        App.frames[frame_id] = ctk.CTkFrame(self, corner_radius=8, fg_color="#212121")
        self.title("Ideal Economizer Curve and Raw Data")
        # App.frames[frame_id].geometry(f"{1100}x{580}")
        App.frames[frame_id].grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        App.frames[frame_id].grid_columnconfigure((0, 1, 2), weight=1)

        # Create title for page
        title_label = ctk.CTkLabel(App.frames[frame_id], text="Ideal Economizer Curve and Raw Data", font=('Arial', 25, 'bold'))
        title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # Create title for plot
        title_label = ctk.CTkLabel(App.frames[frame_id], text="MAT vs OAT")
        title_label.grid(row=1, column=0, columnspan=2, rowspan=1, padx=20, pady=20, sticky="n")

        # Create subframes for plot and widgets
        plot_frame = ctk.CTkFrame(App.frames[frame_id])
        plot_frame.grid(row=2, column=0, columnspan=2, rowspan=5, padx=20, pady=20, sticky="w")

        # Plot using matplotlib
        plot_matplotlib()

        # Create widgets on the right side
        label1 = ctk.CTkLabel(App.frames[frame_id], text="Toggles:", font=('Arial', 18, 'bold'))
        label1.grid(row=1, column=2, sticky='w', pady=5)

        toggle1 = ctk.CTkCheckBox(App.frames[frame_id], text="Ideal Curve")
        toggle1.grid(row=2, column=2, sticky='w', pady=5)

        toggle2 = ctk.CTkCheckBox(App.frames[frame_id], text="Data Points")
        toggle2.grid(row=3, column=2, sticky='w', pady=5)

        label2 = ctk.CTkLabel(App.frames[frame_id], text="Data Range:", font=('Arial', 18, 'bold'))
        label2.grid(row=4, column=2, sticky='w', pady=5)

        range_input_frame = ctk.CTkFrame(App.frames[frame_id])
        range_input_frame.grid(row=5, column=2, padx=20, pady=20, sticky="w")

        start_date = ctk.CTkEntry(range_input_frame)
        start_date.grid(row=0, column=0, sticky='w', pady=5)
        start_date.bind("<Button-1>", self.NumKeyboardCallback(start_date))

        label3 = ctk.CTkLabel(range_input_frame, text="to")
        label3.grid(row=0, column=1, sticky='n', pady=5)

        end_date = ctk.CTkEntry(range_input_frame)
        end_date.grid(row=0, column=2, sticky='e', pady=5)
        end_date.bind("<Button-1>", self.NumKeyboardCallback(end_date))

        sampling_rate_frame = ctk.CTkFrame(App.frames[frame_id])
        sampling_rate_frame.grid(row=6, column=2, padx=20, pady=20, sticky="n")

        label4 = ctk.CTkLabel(sampling_rate_frame, text="Sampling Rate:", font=('Arial', 18, 'bold'))
        label4.grid(row=0, column=0, sticky='w', pady=5)

        # need to refer to the input data
        label5 = ctk.CTkLabel(sampling_rate_frame, text="15", font=('Arial', 18, 'bold'))
        label5.grid(row=0, column=1, sticky='n', pady=5)

        label5 = ctk.CTkLabel(sampling_rate_frame, text="min", font=('Arial', 18, 'bold'))
        label5.grid(row=0, column=2, sticky='e', pady=5)

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
        self.numkeyboard= PopupNumpad(event, x=750, y=200)
        self.numkeyboard.disable = False

# MARK: DownloadData
    def DownloadDataFromPi(self):
        if self.selected_file is None:
            self.error_info_label.configure(text="*No File Selected", )
            return
        selected_file_name = self.scrollable_frame_files[self.selected_file].cget("text")
        print("file selected: " + selected_file_name)
        # set up serial communication

        # double check with the arduino that this system matches. if not, pop up window?
        doesnt_match = False
        if doesnt_match:
            self.toplevel_window = ToplevelWindow(self, "WARNING", "File does not match this data logger. \nContinuing will overwrite this file")
            self.continue_button = ctk.CTkButton(self.toplevel_window, text="Continue")
            self.continue_button.grid(row=1, column=0, padx=10, pady=10)
            self.cancel_button = ctk.CTkButton(self.toplevel_window, text="Cancel", command=self.DestroyTopLevel)
            self.cancel_button.grid(row=1, column=1, padx=10, pady=10)
            returns

        self.downloading_pop_up = ToplevelWindow(self, "Loading", "")
        sleep(1)
        # tell the arduino we're ready to receive data
        try:
            self.date_data, self.oat_data, self.mat_data, self.motor_data = CustomSerialContinuous("-g={}.csv".format(selected_file_name), 115200)
            print("download data response: ", date_data)
        except:
            print("Arduino Connection error")
        # wait for response
        self.create_curve_frame("curve")

        self.toggle_frame_by_id("curve")
        #with open(system_name + ".csv", 'w', newline='') as new_file:
        #    csv_writer = CsvWriter(new_file) # create the new file or start writing to existing file
        #    csv_writer.writerow(params) # Write first row as the user parameters
        #    # start downloading the data
        #    while True: # uh... how to know when to stop?
        #        # Read data from serial port
        #        data = ser.readline().decode().strip()
        #        print(data)
                
        #        if (len(data.split(',')) < 5):
        #            print(data)
        #            print('not enough data')
        #            continue    
        #        # write to the CSV file
        #        csv_writer.writerow(data)

        #        # Split the received data into x and y values
        #        date, oat, mat, time, motor = data.split(',')
                
        #        # Append data points to lists
        #        self.oat_data.append(float(oat[:-2]))
        #        self.mat_data.append(float(mat))
        #        self.date_data.append(date)
        #        self.time_data.append(time)
        #        self.motor_data.append(bool(motor))
            
        
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
