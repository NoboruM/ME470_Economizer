# Remember to install matplotlib with "pip install matplotlib"

import serial
import matplotlib.pyplot as plt

# Initialize serial connection (change port and baudrate as needed)
ser = serial.Serial('/dev/ttyUSB2', 9600)

# Initialize lists to store data points
oat_data = []
mat_data = []

# Create a plot
plt.figure()
plt.title('Data Points Againt Ideal Economizer Curve')
plt.xlabel('Outside Air Temperature (F)')
plt.ylabel('Mixed Air Temperature (F)')

# Create a scatter plot
plot = plt.scatter([], [])

# Function to update plot with new data
def update_plot():
    plot.set_offsets(zip(oat_data, mat_data))
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
        
        # Split the received data into x and y values
        oat, mat = map(float, data.split(','))
        
        # Append data points to lists
        oat_data.append(oat)
        mat_data.append(mat)
        
        # Update the plot
        update_plot()
except KeyboardInterrupt:
    print("Plotting stopped by user")

# Close serial connection
ser.close()

# Show the plot
plt.show()
