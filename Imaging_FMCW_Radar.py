import numpy as np
import matplotlib.pyplot as plt
import pickle
import os
import seaborn as sns
from scipy import interpolate

#############################################################
#Load Data from Radar Measurement
from Load_Data_for_Map_Plot import load_data
current_dir = os.path.dirname(__file__)
increment = 1
use_test_data = False

loaded_values = load_data(use_test_data,increment,current_dir)

#Define the offset of the EM waves due to cables, adapters etc.
offset = 1.445
distance = (loaded_values[0]-offset)*100
distance *= 2
list_of_radar_spectra = loaded_values[1]
distance_increment = distance[10]-distance[9]

#General settings of the grid.
number_of_points_x = 201
number_of_points_y = 201
start_x = 0
end_x = 40
start_y = 60
end_y = 100

image_matrix = np.zeros((number_of_points_y, number_of_points_x), dtype = complex)

#Define antenna positions.
number_of_files = len(list_of_radar_spectra)
antenna_positions = np.linspace(0, (number_of_files-1)*increment, number_of_files)
counter = 0
antenna_distance = 10   #Difference between the center positions of TX and RX antenna.

#Dynamic range of the image (dB).
dynamic_range = 30

#############################################################
#Start Image Calculation
for antenna_x in antenna_positions:

    print(antenna_x)

    #############################################################
    #Calculate Index Matrix
    x_axis = np.linspace(start_x, end_x, number_of_points_x)
    y_axis = np.linspace(start_y, end_y, number_of_points_y)

    x_coordinates, y_coordinates = np.meshgrid(x_axis, y_axis)

    distance_a = np.sqrt((x_coordinates-(end_x-antenna_x-antenna_distance/2+start_x))**2 + y_coordinates**2)    #Forward wave.
    
    distance_b = np.sqrt((x_coordinates-(end_x-antenna_x+antenna_distance/2+start_x))**2 + y_coordinates**2)    #Backward wave.
    
    distance_image = distance_a + distance_b
    
    spectrum_single_measurement = list_of_radar_spectra[counter,:]
    
    #Build Interpolator
    f_abs = interpolate.interp1d(distance, np.abs((spectrum_single_measurement)), kind = 'cubic')
    f_angle = interpolate.interp1d(distance, np.unwrap(np.angle((spectrum_single_measurement))), kind = 'cubic')
    
    image_matrix_cache_abs = f_abs(distance_image)
    image_matrix_cache_angle = f_angle(distance_image)
    
    image_matrix_cache = image_matrix_cache_abs * np.exp(1j*image_matrix_cache_angle)

    image_matrix = image_matrix + image_matrix_cache

    counter = counter + 1

image_matrix = image_matrix**2

image_matrix_norm = image_matrix/np.max(np.abs(image_matrix))

ax = sns.heatmap(10*np.log10(np.abs(image_matrix_norm)), cbar = True, cmap = 'jet',square = True, vmax = 0, vmin = -dynamic_range, cbar_kws={'label': 'Normalized Intensity (dB)'})   

x_ticks = np.flip(np.round(np.linspace(start_x, end_x, int(np.round((np.abs(end_x)+np.abs(start_x))/2,0)+1)),1))
x_ticks_location = np.linspace(0, len(x_axis), int(np.round((np.abs(end_x)+np.abs(start_x))/2,0)+1))

y_ticks = (np.round(np.linspace(start_y, end_y, int(np.round((np.abs(end_y)-np.abs(start_y))/2,0)+1)),1))
y_ticks_location = np.linspace(0, len(y_axis), int(np.round((np.abs(end_y)-np.abs(start_y))/2,0)+1))

ax.invert_yaxis()
cbar_axes = ax.figure.axes[-1]
ax.figure.axes[-1].yaxis.label.set_size(22.5)
plt.xticks(x_ticks_location, x_ticks, fontsize = 22.5) 
plt.yticks(y_ticks_location, y_ticks, fontsize = 22.5) 
plt.xlabel("x (cm)", fontsize = 22.5)
plt.ylabel("y (cm)", fontsize = 22.5)
cax = ax.figure.axes[-1]
cax.tick_params(labelsize=22.5)
plt.show()

filepath = r'{0}\Pickle Files\final_image.pkl'.format(current_dir)
        
if os.path.exists(filepath):
    os.remove(filepath)

with open(r'{0}\Pickle Files\final_image.pkl'.format(current_dir), 'wb') as file: 
      
    # A new file will be created 
    pickle.dump(image_matrix_norm, file) 
