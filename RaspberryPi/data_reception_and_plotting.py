# The main program to be run on the Raspberry Pi

import serial
import matplotlib.pyplot as plt
import ideal_economizer_curve_generation

def data_reception_and_graphing():
    # Initialize serial connection (change port and baudrate as needed)
    ser = serial.Serial('/dev/ttyACM0', 115200)
    
    # Initialize lists to store data points
    oat_data = []
    mat_data = []
    date_data = []
    time_data = []
    motor_data = []
    
    # Create a plot
    plt.figure()
    plt.title('Data Points Against Ideal Economizer Curve')
    plt.xlabel('Outside Air Temperature (F)')
    plt.ylabel('Mixed Air Temperature (F)')
    
    # Function to update plot with new data
    def update_plot():
        plt.scatter(oat_data, mat_data)
        plt.draw()

    # Main loop to receive and plot data
    try:
        while True:
            # Read data from serial port
            data = ser.readline().decode().strip()
            print(data)
            
            if (len(data.split(',')) < 5):
                print(data)
                print('not enough data')
                continue
                
            # Split the received data into x and y values
            date, oat, mat, time, motor = data.split(',')
            
            # # Append data points to lists
            oat_data.append(float(oat[:-2]))
            mat_data.append(float(mat))
            date_data.append(date)
            time_data.append(time)
            motor_data.append(bool(motor))w
            
            # # Update the plot
            update_plot()
    except KeyboardInterrupt:
        print("Plotting stopped by user")
    
    # Close serial connection
    ser.close()
    
    # return the plot
    return plt.gca()

# Recieve Parameters from User
def main():
    minimum_percent_outside_air = int(input("Enter Minimum Percent Outside Air:"))
    return_air_temp = input("Enter Return Air Temperature in Farenheit:")
    low_lockout_temp = input("Enter Low Lockout Temperature in Farenheit")
    high_lockout_temp = input("Enter High Lockout Temperature in Farenheit")
    ideal_mat = input("Enter Ideal Mixed Air Temperature in Farenheit")

    # creates and returns a scatterplot of the raw data but does not show it
    graphed_raw_data = data_reception_and_graphing()

    # overlays the ideal economizer curve generated from user inputs onto graphed_raw_data; outputs the finalized graph
    plot_curve_w_user_inputs_and_raw_data(graphed_raw_data, minimum_percent_outside_air, return_air_temp, low_lockout_temp, high_lockout_temp, ideal_mat)
