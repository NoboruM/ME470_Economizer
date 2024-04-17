import tkinter
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import csv

# change font in main file

def process_data_points(data_file_name):

    # Process csv file of data points
    data = np.genfromtxt(data_file_name, delimiter=',', skip_header=1, dtype=[('Date', 'datetime64[s]'), ('OAT', 'f8'), ('MAT', 'f8'), ('Motor_State', '?')])
    date = data['Date']
    oat = data['OAT']
    mat = data['MAT']
    motor_state = data['Motor_State']
    
    return date, oat, mat, motor_state

def process_ideal_curve_parameters(parameters_file_name):
# Process parameter csv file of ideal curve
    parameters_array = {} # array of length 8
    try:
        with open(curve_parameters, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if not row:
                    continue
                # Extract variable name and value
                variable_name, value = row
                # Remove any leading or trailing whitespace from the variable name
                variable_name = variable_name.strip()
                # Convert the value to an appropriate data type if needed
                if variable_name == 'Time':
                    # If the variable represents time, keep it as a string
                    parameters_array[variable_name] = value
                elif variable_name == 'Date':
                    # If the variable represents a date, keep it as a string
                    parameters_array[variable_name] = value
                elif variable_name == 'Sampling Rate':
                    # If the variable represents a date, keep it as a string
                    parameters_array[variable_name] = value
                else:
                    try:
                        parameters_array[variable_name] = float(value)
                    except ValueError:
                        print('Error in reading curve paramters')
    except FileNotFoundError:
        print(f"The file '{curve_parameters}' does not exist.")
    return parameters_array

# Define callback functions for checkbox and toggle events
def handle_ideal_curve(visibility):
    curve_line.set_visible(visibility)
    plt.draw()

def handle_data_points(visibility):
    scatter_points.set_visible(visibility)
    plt.draw()

def handle_motor_on(visibility):
    # Filter data points where motor_state is True and update scatter plot
    scatter_points.set_visible(visibility)
    plt.draw()

def handle_motor_off(visibility):
    # Filter data points where motor_state is False and update scatter plot
    scatter_points.set_visible(visibility)
    plt.draw()


# make entries red if blank; take from nobo's code
# look in csv file and limit range, call back to plot_matplotlib to replot plot
def handle_date_range(self): 
    i = 1

def plot_matplotlib(oat, mat, raw_data, parameters):

    # Plot raw_data
    fig, ax = plt.subplots()
    scatter_points = ax.scatter(oat, mat, marker='o', s=0.1)

    # Process parameters for ideal economizer curve
    min_oat = parameters["M%OAT"] #float
    rat = parameters["RAT"] #float
    lllt = parameters["LLLT"] #float
    hllt = parameters["HLLT"] #float
    i_mat = parameters["MAT"] #float

    # Create ideal economizer curve
    oat_for_plot = np.arange(-37, 111, 1)
    MAT_at_min_OA = rat*(1 - (min_oat/100)) + (min_oat/100)*oat_for_plot
    mat_for_plot = np.zeros((len(oat_for_plot), 1)) # maybe dont make them zero?
    for i, temp in enumerate(oat_for_plot):
        if (MAT_at_min_OA[i] < i_mat or temp <= lllt or temp >= hllt):
            mat_for_plot[i] = MAT_at_min_OA[i]
        elif (temp < i_mat):
            mat_for_plot[i] = i_mat
        else:
            mat_for_plot[i] = oat_for_plot[i]

    # Plot ideal economizer curve
    curve_line, = ax.plot(oat_for_plot, mat_for_plot, color='#fa8b41')


    # Label and Tweak Plot Design
    ax.set_title('Ideal Economizer and Raw Data of ' + raw_data, fontsize=8)
    ax.set_xlabel('Outside Air Temperature [°F]', fontsize=6, labelpad=5)
    ax.set_ylabel('Mixed Air Temperature [°F]', fontsize=6, labelpad=5)
    ax.tick_params(axis='both', which='major', labelsize=4)
    ax.set_xlim(-30, 110)
    ax.set_ylim(30, 100)

    left = 0.15
    bottom = 0.15
    width = 0.7
    height = 0.7
    ax.set_position([left, bottom, width, height])

    fig.set_size_inches(4, 3)
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

    return scatter_points, curve_line, canvas, fig, ax


# MAIN PROGRAM STARTS HERE

# example files; delete in main file
raw_data = "Randomly Generated Data.csv"
curve_parameters = "example_curve_parameters.csv"

date, oat_array, mat_array, motor_state = process_data_points("Randomly Generated Data.csv")
parameters_array = process_ideal_curve_parameters("example_curve_parameters.csv")

root = ctk.CTk()
root.title("Ideal Economizer Curve and Data Points")

#delete in main file
root.my_font = ctk.CTkFont(family="TkTextFont", size=15, weight="bold")
root.home_font = ctk.CTkFont(family="TkTextFont", size=30, weight="bold")
root.geometry(f"{1100}x{580}")
input_column_width = 350

# Create main frame
main_frame = ctk.CTkFrame(root)
main_frame.pack(fill=ctk.BOTH, expand=True)

# Create subframes for plot and widgets
plot_frame = ctk.CTkFrame(main_frame)
plot_frame.pack(side=ctk.LEFT, padx=10, pady=10, fill=ctk.BOTH, expand=False)

widgets_frame = ctk.CTkFrame(main_frame, width=input_column_width)
widgets_frame.pack(side=ctk.LEFT, padx=10, pady=10)

# Plot using matplotlib, moved down so it could consider toggles
scatter_points, curve_line, canvas, fig, ax = plot_matplotlib(oat_array, mat_array, raw_data, parameters_array)

ideal_curve_visible = True

ideal_curve_toggle = ctk.CTkCheckBox(widgets_frame, text="Ideal Economizer Curve", font=root.my_font, command=lambda: handle_ideal_curve(visibility)) #, fg_color='#fa8b41'
ideal_curve_toggle.grid(row=1, column=0, sticky='w', pady=5)
ideal_curve_toggle.select()

data_points_toggle = ctk.CTkCheckBox(widgets_frame, text="Data Points", font=root.my_font, command=lambda: handle_data_points(visibility))
data_points_toggle.grid(row=2, column=0, sticky='w', pady=5)
data_points_toggle.select()

motor_on_toggle = ctk.CTkCheckBox(widgets_frame, text="Motor On", font=root.my_font, command=lambda: handle_motor_on(visibility))
motor_on_toggle.grid(row=3, column=0, sticky='w', padx=30, pady=5)
motor_on_toggle.select()

motor_off_toggle = ctk.CTkCheckBox(widgets_frame, text="Motor Off", font=root.my_font, command=lambda: handle_motor_off(visibility))
motor_off_toggle.grid(row=4, column=0, sticky='w', padx=30, pady=5)
motor_off_toggle.select()

date_range_label = ctk.CTkLabel(widgets_frame, text="Date Range:", font=root.my_font)
date_range_label.grid(row=5, column=0, sticky='w', pady=5)

date_range_frame =ctk.CTkFrame(widgets_frame, width=input_column_width, bg_color=widgets_frame.cget("bg_color"), fg_color=widgets_frame.cget("fg_color"))
date_range_frame.grid(row=6, column=0, sticky='ew', pady=5)

placeholder_width = 2
input_width = (input_column_width - placeholder_width) // 10

month1_entry = ctk.CTkEntry(date_range_frame, placeholder_text="MM", validate="key", width=input_width) #validatecommand=num_val, 
month1_entry.grid(row=0, column=0, sticky='ew', padx = 4, pady=5)
slash_label_1 = ctk.CTkLabel(date_range_frame, font=root.my_font, text="/", text_color="#fff")
slash_label_1.grid(row=0, column=1, sticky="nsw")
date1_entry = ctk.CTkEntry(date_range_frame, placeholder_text="DD", validate="key", width=input_width) #validatecommand=num_val, 
date1_entry.grid(row=0, column=2, sticky='nsw', pady=5)
slash_label_2 = ctk.CTkLabel(date_range_frame, font=root.my_font, text="/", text_color="#fff")
slash_label_2.grid(row=0, column=3, sticky="nsw")
year1_entry = ctk.CTkEntry(date_range_frame, placeholder_text="YYYY", validate="key", width=input_width) #validatecommand=num_val, 
year1_entry.grid(row=0, column=4, sticky='nsw', pady=5)

to_label = ctk.CTkLabel(date_range_frame, text=" to ")
to_label.grid(row=0, column=5, sticky='w', pady=5)

month2_entry = ctk.CTkEntry(date_range_frame, placeholder_text="MM", validate="key", width=input_width) #validatecommand=num_val, 
month2_entry.grid(row=0, column=6, sticky='nsw', pady=5)
slash_label_3 = ctk.CTkLabel(date_range_frame, font=root.my_font, text="/", text_color="#fff")
slash_label_3.grid(row=0, column=7, sticky="nsw")
date2_entry = ctk.CTkEntry(date_range_frame, placeholder_text="DD", validate="key", width=input_width) #validatecommand=num_val, 
date2_entry.grid(row=0, column=8, sticky='nsw', pady=5)
slash_label_4 = ctk.CTkLabel(date_range_frame, font=root.my_font, text="/", text_color="#fff")
slash_label_4.grid(row=0, column=9, sticky="nsw")
year2_entry = ctk.CTkEntry(date_range_frame, placeholder_text="YYYY", validate="key", width=input_width) #validatecommand=num_val, 
year2_entry.grid(row=0, column=10, sticky='nse', padx=4, pady=5)

submit_button = ctk.CTkButton(widgets_frame, font=root.my_font, text="Submit", corner_radius=4, width=1) #command=root.handle_date_range, 
submit_button.grid(row=7, column=0, sticky='e', padx=4, pady=5)

sampling_rate_label = ctk.CTkLabel(widgets_frame, text=f"Sampling Rate: {parameters_array['Sampling Rate']} min", font=root.my_font)
sampling_rate_label.grid(row=8, column=0, sticky='w', pady=5)

root.mainloop()