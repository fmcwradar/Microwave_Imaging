#Import of Necessary Python Libraries
import scipy.constants as sc
import matplotlib.pyplot as plt
import numpy as np
#Import of the Radar Measurement Evaluation Modul
from Radar_Evaluation_Modul import radar_measurement_evaluation

#Target
path = r"G:\Meine Ablage\Finaler Vergleich Radar vs. VNA\02-07-2024\Bassi\Radar"
number_of_files = 45

file_names = []

for number in range(0, number_of_files+1):
    file_names.append("{0}".format(number))

start_frequency = 6  #GHz
stop_frequency = 14 #GHz
B = (stop_frequency-start_frequency)*1e9
T_c = 200*1e-6
S = B/T_c
c = sc.speed_of_light
number_of_ramps = 300
total = 5005
measurement_list_no_target = []
measurement_list_time_domain_up = []
measurement_list_time_domain_down = []

spectrum_matrix = np.zeros((len(file_names),total), dtype = complex)

#Iterate over the measurements.
for count, name in enumerate(file_names):

    print(count)
    
    single_measurement = radar_measurement_evaluation(path,name,B,T_c,c,number_of_ramps,total)
    single_measurement.run_radar_evaluation()
    spectrum_matrix[count,:] = single_measurement.spectrum_down
    
distance_corrected = single_measurement.distance_corrected   
      
#Save the Results in Pickle Files
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
      
    # A new file will be created 
    pickle.dump(spectrum_matrix, file) 

with open(r'{0}\Pickle Files\distance.pkl'.format(current_dir), 'wb') as file: 
      
    # A new file will be created 
    pickle.dump(distance_corrected, file) 


