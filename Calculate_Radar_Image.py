#Import of necessary Python libraries.
import scipy.constants as sc
import matplotlib.pyplot as plt
import numpy as np
import os
import pathlib
from tqdm import tqdm
#Import of the Radar Measurement Evaluation Modul.
from Radar_Evaluation_Modul import radar_measurement_evaluation
from Radar_Imaging_Modul_V02 import radar_imaging
import sys

#Get current directory.
current_dir = os.path.dirname(__file__)
#Path in which the .csv-files are located.
path_csv = r"{0}\Ideal_Data_Radar".format(current_dir)
#Check if all necessary folders exist and if not create them.
path = pathlib.Path(r'{0}\Pickle_Files'.format(current_dir))
path.mkdir(parents=True, exist_ok=True)

number_of_measurements = 46

file_names = []

for number in range(0, number_of_measurements):
    file_names.append("0.0_{0}".format(float(10*number)))

#Define settings for Radar_Evaluation_Modul.
f0 = 6e9
f1 = 14e9
B = (f1-f0)
T_c = 200*1e-6
c0 = sc.speed_of_light
number_of_ramps = 100
total = 8192
windowing = False
ideal = True
swap_IQ = False
calibration = False
filtering = False
fc_low = 350e3
fc_high = 500e3
filterorder = 10
save_last_measurement = False
background_subtraction = False
hilbert = False
offset = 0
#End of define settings.

list_of_measurements = []

#Iterate over the measurements.
for name in tqdm(file_names, desc="Preparing IF data", unit="iteration", file=sys.stdout):
    single_measurement = radar_measurement_evaluation(path_csv,name,B,T_c,c0,number_of_ramps,total,f0,f1,windowing,ideal,swap_IQ,calibration,filtering,fc_low,fc_high,filterorder,offset,save_last_measurement,background_subtraction,hilbert)
    single_measurement.run_radar_evaluation()
    list_of_measurements.append(single_measurement)

print(len(list_of_measurements))
#Define settings for Radar_Imaging_Modul.
distance = single_measurement.distance_corrected
number_of_points_x = 401
number_of_points_y = 401
number_of_points_z = 1
start_x = 0
end_x = 50
start_y = 40
end_y = 90
start_z = 0
end_z = 0

antenna_distance = 10
antenna_start = 0
antenna_end = 45
dynamic_range = 40
image_matrix = np.zeros((number_of_points_z, number_of_points_y, number_of_points_x), dtype = complex)
image_matrix = np.zeros((number_of_points_y, number_of_points_x), dtype = complex)
#End of define settings.

settings = [f0,f1,B,np.round(T_c,8),number_of_ramps,total,windowing,calibration,filtering,fc_low,fc_high,filterorder,background_subtraction,hilbert,offset,start_x,start_y,end_x,end_y,antenna_distance,antenna_start,antenna_end,number_of_points_x,number_of_points_y,path_csv]

radar_imaging = radar_imaging(list_of_measurements,distance,offset,number_of_points_x,number_of_points_y,start_x,start_y,end_x,end_y,antenna_distance,antenna_start,antenna_end,dynamic_range,number_of_measurements,settings)
radar_imaging.run_radar_imaging()



