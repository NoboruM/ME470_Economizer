import matplotlib.pyplot as plt
import numpy as np

def plot_curve(x_data, y_data):
    # Create a plot
    plt.figure()
    plt.title('Ideal Economizer Curve')
    plt.xlabel('Outside Air Temperature (F)')
    plt.ylabel('Mixed Air Temperature (F)')

    # Plot the data points
    plt.scatter(x_data, y_data, alpha=0)

    # Connect data points with lines to form a curve
    plt.plot(x_data, y_data, color='blue')

    # Show the plot
    plt.show()

# parameters; change to user inputs
minimum_percent_outside_air = 0.2
return_air_temp = 72
low_lockout_temp = -30
high_lockout_temp = 70
ideal_mat = 55 

# could do this but could also calculate and plot the 
# five main points anddraw out lines between them
oat = np.arange(-30, 121)
minimum_oa_mat = return_air_temp * (1 - minimum_percent_outside_air) + oat * minimum_percent_outside_air
actual_mat = np.array([])

for o, m in zip(oat, minimum_oa_mat):
  if (m < ideal_mat or o <= low_lockout_temp or o >= high_lockout_temp):
    actual_mat = np.append(actual_mat, m)
  elif (o < ideal_mat):
    actual_mat = np.append(actual_mat, ideal_mat)
  elif (o < m):
      actual_mat = np.append(actual_mat, o)
  else:
    actual_mat = np.append(actual_mat, m)

# Plot the curve
plot_curve(oat, actual_mat)
