#This script is used to generate a .gif based on the the files obtained with Calculate_Radar_Image_Animated.py.

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle

number_of_measurements = 46

plt.rcParams["figure.figsize"] = (16,13)

#Here, you have to specify the folder with the results you want to animate.
folder = r"C:\Users\Martin\Desktop\Preparing_GitHub_13_03_25\Pickle_Files\2025-03-13_11-10-45"

#Obtain these setting from the logfile.
dynamic_range = 30

start_x = 0
end_x = 45

start_y = 40
end_y = 85

number_of_points_x = 401
number_of_points_y = 401

x_axis = np.linspace(start_x, end_x, number_of_points_x)
y_axis = np.linspace(start_y, end_y, number_of_points_y)

x_ticks = (np.round(np.linspace(start_x, end_x, int(np.round((np.abs(end_x)+np.abs(start_x))/5,0)+1)),1))
x_ticks_location = np.linspace(0, len(x_axis), int(np.round((np.abs(end_x)+np.abs(start_x))/5,0)+1))

y_ticks = (np.round(np.linspace(start_y, end_y, int(np.round((np.abs(end_y)-np.abs(start_y))/5,0)+1)),1))
y_ticks_location = np.linspace(0, len(y_axis), int(np.round((np.abs(end_y)-np.abs(start_y))/5,0)+1))

fontsize_MM = 25

for counter in range(0, number_of_measurements):

    filepath = "{0}\image_radar_{1}.pkl".format(folder,float(counter))
    
    with open(filepath, 'rb') as file: 
         image = pickle.load(file)
         
    ax = sns.heatmap(10*np.log10(np.abs(image)), cbar = True, cmap = 'jet', vmax = 0, vmin = -dynamic_range, cbar_kws={'label': 'Normalized Intensity (dB)'})    

    x_location_line = counter*number_of_points_x/(end_x-start_x)

    ax.vlines(x_location_line,0,60, linewidth = 7.0, color = 'white')

    ax.invert_yaxis()
    cbar_axes = ax.figure.axes[-1]
    ax.figure.axes[-1].yaxis.label.set_size(25)
    plt.xticks(x_ticks_location, x_ticks, fontsize = 25) 
    plt.yticks(y_ticks_location, y_ticks, fontsize = 25) 
    plt.xlabel("x (cm)", fontsize = 25)
    plt.ylabel("y (cm)", fontsize = 25)
    cax = ax.figure.axes[-1]
    cax.tick_params(labelsize=25)
    plt.savefig(r"{0}\image_radar_00{1}.png".format(folder,int(counter)))
    plt.close('all')
    
from PIL import Image
import os
import glob

# Path pattern for the images
file_path_pattern = r"{0}\*.png".format(folder)

# Output GIF file name
output_file = "{0}\Animated_Measurement.gif".format(folder)
# Duration each frame will be displayed (in milliseconds)
frame_duration = 200  # milliseconds

# Get list of image files
image_files = glob.glob(file_path_pattern)

# Sort images by modification time
image_files.sort(key=lambda x: os.path.getmtime(x))

# Open images and prepare frames list
frames = [Image.open(image) for image in image_files]

# Save frames as an animated GIF
frames[0].save(
    output_file,
    save_all=True,
    append_images=frames[1:],
    duration=frame_duration,
    loop=0  # 0 means infinite loop
)

print(f"GIF saved as {output_file}")
