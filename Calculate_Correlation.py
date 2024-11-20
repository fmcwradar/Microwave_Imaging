import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pickle 
from matplotlib.pyplot import figure

#Here starts the computation of the NCC.
def norm_data(data):
    """
    normalize data to have mean=0 and standard_deviation=1
    """
    mean_data=np.mean(data)
    std_data=np.std(data, ddof=1)
    #return (data-mean_data)/(std_data*np.sqrt(data.size-1))
    return (data-mean_data)/(std_data)


def ncc(data0, data1):
    """
    normalized cross-correlation coefficient between two data sets

    Parameters
    ----------
    data0, data1 :  numpy arrays of same size
    """
    return (1.0/(data0.size-1)) * np.sum(norm_data(data0)*norm_data(data1))

current_dir = os.path.dirname(__file__)

with open(r"{0}\Pickle Files\final_image_VNA.pkl".format(current_dir), 'rb') as file: 
            image_vna = pickle.load(file) 
            
with open(r"{0}\Pickle Files\final_image_radar.pkl".format(current_dir), 'rb') as file: 
            image_radar = pickle.load(file) 

dynamic_range = 30

image_vna_db = 10*np.log10(np.abs(image_vna))

image_radar_db = 10*np.log10(np.abs(image_radar))

image_vna_db[image_vna_db < -dynamic_range] = -dynamic_range
image_radar_db[image_radar_db < -dynamic_range] = -dynamic_range

correlation = ncc(image_vna_db, image_radar_db)

print("NCC value is {0}.".format(np.round(correlation,5)))

#Inititalize Figure
fig, (ax1, ax2) = plt.subplots(nrows = 1, ncols=2)

#General Settings
number_of_points_x = 401
number_of_points_y = 401

start_x = 0
end_x = 40

start_y = 50
end_y = 90

x_axis = np.linspace(start_x, end_x, int(number_of_points_x))
y_axis = np.linspace(start_y, end_y, int(number_of_points_y))

x_ticks = (np.round(np.linspace(start_x, end_x, int(np.round((np.abs(end_x)+np.abs(start_x))/4,0)+1)),1))
x_ticks_location = np.linspace(0, len(x_axis), int(np.round((np.abs(end_x)+np.abs(start_x))/4,0)+1))

y_ticks = (np.round(np.linspace(start_y, end_y, int(np.round((np.abs(end_y)-np.abs(start_y))/4,0)+1)),1))
y_ticks_location = np.linspace(0, len(y_axis), int(np.round((np.abs(end_y)-np.abs(start_y))/4,0)+1))

#Image VNA
sns.heatmap(image_vna_db, cmap = 'jet', square = True, vmax = 0, vmin = -dynamic_range, cbar_kws={'label': 'Normalized Amplitude (dB)'}, ax = ax1, cbar = False)

#Image Radar
im = sns.heatmap(image_radar_db, xticklabels = x_ticks, yticklabels = np.round(y_axis,0), cmap = 'jet', square = True, vmax = 0, vmin = -dynamic_range, cbar_kws={'label': 'Normalized Amplitude (dB)'}, ax = ax2, cbar = False)


#Figure Settings
fig.set_figwidth(18)
fig.set_figheight(15)

size_setting = 25

cbar_axes = ax2.figure.axes[-1]
ax1.figure.axes[-1].yaxis.label.set_size(size_setting)
ax1.set_xticks(x_ticks_location, np.flip(x_ticks), fontsize = size_setting) 
ax1.set_yticks(y_ticks_location, y_ticks, fontsize = size_setting) 
ax1.set_xlabel("x (cm)", fontsize = size_setting)
ax1.set_ylabel("y (cm)", fontsize = size_setting)
cax = ax1.figure.axes[-1]
cax.tick_params(labelsize=size_setting) 
ax1.invert_yaxis()

cbar_axes = ax2.figure.axes[-1]
ax2.figure.axes[-1].yaxis.label.set_size(size_setting)
ax2.set_xticks(x_ticks_location, np.flip(x_ticks), fontsize = size_setting) 
ax2.set_yticks(y_ticks_location, y_ticks, fontsize = size_setting) 
ax2.set_xlabel("x (cm)", fontsize = size_setting)
ax2.set_ylabel("y (cm)", fontsize = size_setting)
cax = ax2.figure.axes[-1]
cax.tick_params(labelsize=size_setting) 
ax2.invert_yaxis()

ax1.set_title("VNA", fontsize = size_setting, x=0.45, y=1)
ax2.set_title("FMCW Radar", fontsize = size_setting, x=0.45, y=1)

mappable = im.get_children()[0]
cb = plt.colorbar(mappable, ax = [ax1,ax2],orientation = 'horizontal', label = "Normalized Amplitude (dB)")
cb.ax.tick_params(labelsize=size_setting)
cb.ax.set_xlabel(xlabel = "Normalized Intensity (dB)", fontsize = size_setting)
plt.subplots_adjust(left=0.1, right=0.9, top=0.95, bottom=0.35)
plt.show()