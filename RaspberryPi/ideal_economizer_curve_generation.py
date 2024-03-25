import matplotlib.pyplot as plt
import numpy as np
import random

# Curently not being used
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
    return plt.gca();

# Plots a data set onto an existing plot; for overlaying two plots together
def plot_curve_on_exisiting_plot(plot, x_data, y_data):
    plot.scatter(x_data, y_data, alpha=0)
    plot.plot(x_data, y_data, color='blue')
    return plot.gca()

# Plots ideal economizer curve onto an existing plot given parameters
def plot_curve_w_user_inputs_and_raw_data(graphed_raw_data, minimum_percent_outside_air, return_air_temp, low_lockout_temp, high_lockout_temp, ideal_mat):
    # parameters; change to user inputs
    # minimum_percent_outside_air = 0.2
    # return_air_temp = 72
    # low_lockout_temp = -30
    # high_lockout_temp = 70
    # ideal_mat = 55 
    
    oat = np.arange(-30, 121)
    minimum_oat_mat = return_air_temp * (1 - minimum_percent_outside_air) + oat * minimum_percent_outside_air
    actual_mat = np.array([])
    
    for o, m in zip(oat, minimum_oat_mat):
      if (m < ideal_mat or o <= low_lockout_temp or o >= high_lockout_temp):
        actual_mat = np.append(actual_mat, m)
      elif (o < ideal_mat):
        actual_mat = np.append(actual_mat, ideal_mat)
      elif (o < m):
          actual_mat = np.append(actual_mat, o)
    
    # Plot the curve
    plot = plot_curve_on_exisiting_plot(graphed_raw_data, oat, actual_mat)
    plot.show()
    # return plot

def PlotIdealCurve(min_outside_air, rat, low_lockout_temp, high_lockout_temp, ideal_mat):
  oat = np.arange(-37, 111, 1)
  MAT_at_min_OA = rat*(1 - min_outside_air) + min_outside_air*oat
  MAT = np.zeros((len(oat), 1))
  for i, temp in enumerate(oat):
    if (MAT_at_min_OA[i] < ideal_mat or temp <= low_lockout_temp or temp >= high_lockout_temp):
       MAT[i] = MAT_at_min_OA[i]
    elif (temp < ideal_mat):
        MAT[i] = ideal_mat
    else:
        MAT[i] = oat[i]
  rand_data = GenerateRandomData(oat, MAT)
  plt.rcParams.update({'font.size': 12})
  plt.figure()
  plt.plot(oat, MAT)
  plt.scatter(rand_data[:,0], rand_data[:,1], color = "green")
  plt.xlabel("Outside Air Temperature (Farenheit)")
  plt.ylabel("Mixed Air Temperature (Farenheit)")
  plt.title("Ideal Economizer Plot")
  plt.show()

def GenerateRandomData(OAT, MAT):
  max_idx = len(OAT)
  data = np.zeros((len(OAT), 2))
  for _ in range(10000*max_idx):
    rand_num = random.gauss(74, max_idx/12)
    while (rand_num < 0 or rand_num > max_idx):
      rand_num = random.gauss(0, max_idx/12)
    rand_idx = int(rand_num)
    # use range of maybe +-3 degrees?
    rand_data = random.random()*5 + MAT[rand_idx] - 2.5
    data[rand_idx][1] = rand_data
    data[rand_idx][0] = OAT[rand_idx]
  mask = data[:, 1] > 40
  data = data[mask]
  
  return data

PlotIdealCurve(0.2, 72, -30, 70, 55)


