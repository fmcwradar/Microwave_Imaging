#Import of Necessary Python Libraries.
import scipy.constants as sc
import matplotlib.pyplot as plt
import numpy as np
import os
import pathlib
import pickle
from scipy import interpolate
import seaborn as sns
from tqdm import tqdm
import sys

def calculate_image(spectrum,distance,offset,radar_position_x,radar_position_z,image_matrix,start_x,start_y,start_z,end_x,end_y,end_z,number_of_points_x,number_of_points_y,number_of_points_z,antenna_spacing):
    
        
        #Define the offset of the EM waves due to cables, adapters etc. For ideal data the offset is zero.
        distance = (distance-offset)*100
        distance *= 2
        
        #Calculate Index Matrix
        x_axis = np.linspace(start_x, end_x, number_of_points_x)
        y_axis = np.linspace(start_y, end_y, number_of_points_y)
        z_axis = np.linspace(start_z, end_z, number_of_points_z)

        x_coordinates, y_coordinates, z_coordinates = np.meshgrid(x_axis, y_axis, z_axis)
      
        distance_a = np.sqrt((x_coordinates-radar_position_x)**2 + y_coordinates**2 + (z_coordinates-radar_position_z+antenna_spacing/2)**2)    #Forward wave.
        
        distance_b = np.sqrt((x_coordinates-radar_position_x)**2 + y_coordinates**2 + (z_coordinates-radar_position_z-antenna_spacing/2)**2)    #Backward wave.
        
        distance_image = distance_a + distance_b
        
        # Build Interpolator
        f_abs = interpolate.interp1d(distance, np.abs((spectrum)), kind = 'cubic')
        f_angle = interpolate.interp1d(distance, np.unwrap(np.angle((spectrum))), kind = 'cubic')
        
        image_matrix_cache_abs = f_abs(distance_image)
        image_matrix_cache_angle = f_angle(distance_image)
        
        image_matrix_cache = image_matrix_cache_abs * np.exp(1j*image_matrix_cache_angle)

        return image_matrix_cache

#Get current directory.
current_dir = os.path.dirname(__file__)
current_dir = f"{current_dir}\\Test-3D"

path_pickle = r"{0}\Pickle Files for 3D Imaging".format(current_dir)

from os import walk

file_names = next(walk(path_pickle), (None, None, []))[2]  # [] if no file

#Settings for Imaging.
offset = 1
# distance = single_measurement.distance_corrected
number_of_points_x = 101
number_of_points_y = 101
number_of_points_z = 101
start_x = 0
end_x = 40
start_y = 30
end_y = 70
start_z = 0
end_z = 40
image_matrix_clear = np.zeros((number_of_points_y, number_of_points_x, number_of_points_z), dtype = complex)
image_matrix_total = np.zeros((number_of_points_y, number_of_points_x, number_of_points_z), dtype = complex)

antenna_spacing = 10

with open(r'{0}\distance.pkl'.format(path_pickle), 'rb') as file:   
            # Call load method to deserialze. 
            distance = pickle.load(file) 

for name in tqdm(file_names, total=len(file_names), desc = "Processing files", unit = "file", file = sys.stdout):
    
    with open(r'{0}\{1}'.format(path_pickle,name), 'rb') as file: 
            # Call load method to deserialze. 
            spectrum = pickle.load(file) 
            
    name = name[:-4] #Delete the ".pkl" of the file name.
    
    if name != "distance":
    
        radar_position_z = float(name.split('_')[0])/10 #convert mm to cm
        
        radar_position_x = float(name.split('_')[1])/10 #convert mm to cm
    
        # print(radar_position_x)
    
        image_matrix_cache = calculate_image(spectrum,distance,offset,radar_position_x,radar_position_z,image_matrix_clear,start_x,start_y,start_z,end_x,end_y,end_z,number_of_points_x,number_of_points_y,number_of_points_z,antenna_spacing)
        
        image_matrix_total = image_matrix_total + image_matrix_cache
  
x_axis = np.linspace(start_x, end_x, number_of_points_x)
y_axis = np.linspace(start_y, end_y, number_of_points_y)
z_axis = np.linspace(start_z, end_z, number_of_points_z)

#Save image  
        
filepath = r"{0}\Final_3D_Files\final_3D_image.pkl".format(current_dir)
                
if os.path.exists(filepath):
    os.remove(filepath)

with open(filepath, 'wb') as file: 
    pickle.dump(image_matrix_total, file) 
    
#Save axes    
    
filepath = r"{0}\Final_3D_Files\x_axis.pkl".format(current_dir)
                
if os.path.exists(filepath):
    os.remove(filepath)

with open(filepath, 'wb') as file: 
    pickle.dump(x_axis, file) 

filepath = r"{0}\Final_3D_Files\y_axis.pkl".format(current_dir)
                
if os.path.exists(filepath):
    os.remove(filepath)

with open(filepath, 'wb') as file: 
    pickle.dump(y_axis, file) 
    
filepath = r"{0}\Final_3D_Files\z_axis.pkl".format(current_dir)
                
if os.path.exists(filepath):
    os.remove(filepath)

with open(filepath, 'wb') as file: 
    pickle.dump(z_axis, file)     