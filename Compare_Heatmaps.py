import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pickle 
from matplotlib.pyplot import figure

current_dir = os.path.dirname(__file__)

with open(r"{0}\Pickle Files\final_image_VNA.pkl".format(current_dir), 'rb') as file: 
            image_vna = pickle.load(file) 
            
with open(r"{0}\Pickle Files\final_image_radar.pkl".format(current_dir), 'rb') as file: 
            image_radar = pickle.load(file) 

dynamic_range = 20

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

#Inititalize Figure
fig, (ax1, ax2) = plt.subplots(nrows = 1, ncols=2)

#Image VNA
sns.heatmap((10*np.log10(np.abs(image_vna))), cmap = 'jet', square = True, vmax = 0, vmin = -dynamic_range, cbar_kws={'label': 'Normalized Amplitude (dB)'}, ax = ax1, cbar = False)

#Image Radar
im = sns.heatmap((10*np.log10(np.abs(image_radar))), xticklabels = x_ticks, yticklabels = np.round(y_axis,0), cmap = 'jet', square = True, vmax = 0, vmin = -dynamic_range, cbar_kws={'label': 'Normalized Amplitude (dB)'}, ax = ax2, cbar = False)

####################################################################
#Figure Settings
fig.set_figwidth(18)
fig.set_figheight(15)

size_setting = 30

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