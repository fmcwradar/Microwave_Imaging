#Import of Necessary Python Libraries.
import scipy.constants as sc
import matplotlib.pyplot as plt
import numpy as np
import os
#Import of the Radar Measurement Evaluation Modul.
from Radar_Evaluation_Modul import radar_measurement_evaluation
#Get current directory.
current_dir = os.path.dirname(__file__)
#Path in which the .csv-files are located.
path = r"{0}\Ideal Data Radar".format(current_dir)
number_of_files = 45

file_names = []

for number in range(0, number_of_files+1):
    file_names.append("{0}".format(number))

#Define settings for Radar_Evaluation_Modul.
f0 = 6e9
f1 = 14e9
B = (f1-f0)
T_c = 200*1e-6
c0 = sc.speed_of_light
number_of_ramps = 1
total = 4096
windowing = True
ideal = True

measurement_list_no_target = []
measurement_list_time_domain_up = []
measurement_list_time_domain_up = []

spectrum_matrix = np.zeros((len(file_names),total), dtype = complex)

#Iterate over the measurements.
for count, name in enumerate(file_names):
    print(count)
    single_measurement = radar_measurement_evaluation(path,name,B,T_c,c0,number_of_ramps,total,f0,f1,windowing,ideal)
    single_measurement.run_radar_evaluation()
    spectrum_matrix[count,:] = single_measurement.spectrum_up
    
distance_corrected = single_measurement.distance_corrected   
      
#Save the results in pickle files.
import pickle
import os   

current_dir = os.path.dirname(__file__)

filepath = r'{0}\Pickle Files\spectrum.pkl'.format(current_dir)
        
if os.path.exists(filepath):
    os.remove(filepath)

filepath = r'{0}\Pickle Files\distance.pkl'.format(current_dir)
        
if os.path.exists(filepath):
    os.remove(filepath)
            
with open(r'{0}\Pickle Files\spectrum.pkl'.format(current_dir), 'wb') as file: 
      
    # A new file will be created.
    pickle.dump(spectrum_matrix, file) 

with open(r'{0}\Pickle Files\distance.pkl'.format(current_dir), 'wb') as file: 
      
    # A new file will be created. 
    pickle.dump(distance_corrected, file) 


