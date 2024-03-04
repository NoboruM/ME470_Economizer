import serial
import matplotlib.pyplot as plt

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

# Create a scatter plot
# plot = plt.scatter([], [])

# Function to update plot with new data
def update_plot():
    plt.scatter(oat_data, mat_data)
    plt.draw()

# Need to modify if we are including time in our analysis
# raw data should be in the format:
# [oat1], [mat1]
# [oat2], [mat2]

# Main loop to receive and plot data
try:
    while True:
        # Read data from serial port
        data = ser.readline().decode().strip()
        print(data)
        
        if (len(data.split(',')) < 5):
            print(data)
            print('not enough data??')
            continue
        # Split the received data into x and y values
        date, oat, mat, time, motor = data.split(',')
        
        # # Append data points to lists
        oat_data.append(float(oat[:-2]))
        mat_data.append(float(mat))
        date_data.append(date)
        time_data.append(time)
        motor_data.append(motor)
        
        # # Update the plot
        update_plot()
except KeyboardInterrupt:
    print("Plotting stopped by user")

# Close serial connection
ser.close()

# Show the plot
plt.show()
