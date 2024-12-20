#Import of Necessary Python Libraries.
import scipy.constants as sc
import matplotlib.pyplot as plt
import numpy as np
import os
import pathlib
#Import of the Radar Measurement Evaluation Modul and the Radar_Imaging_Modul.
from Radar_Evaluation_Modul import radar_measurement_evaluation
from Radar_Imaging_Modul import radar_imaging
#Get current directory.
current_dir = os.path.dirname(__file__)
#Path in which the .csv-files are located.
path_csv = r"{0}\Ideal Data Radar".format(current_dir)
number_of_files = 45
#Check if all necessary folders exist and if not create them.
path = pathlib.Path(r'{0}\Pickle Files'.format(current_dir))
path.mkdir(parents=True, exist_ok=True)
path = pathlib.Path(r'{0}\Results\Plot_IF_Signal'.format(current_dir))
path.mkdir(parents=True, exist_ok=True)
path = pathlib.Path(r'{0}\Results\Plot_IF_Spectrum'.format(current_dir))
path.mkdir(parents=True, exist_ok=True)

number_of_measurements = 46

file_names = []

for number in range(0, number_of_measurements):
    file_names.append("{0}".format(number))

#Define settings for Radar_Evaluation_Modul.
f0 = 6e9
f1 = 14e9
B = (f1-f0)
T_c = 200*1e-6
c0 = sc.speed_of_light
number_of_ramps = 300
total = 8192
windowing = True
ideal = True
swap_IQ = False
calibration = False
plotting = False
filtering = False
fc_low = 750e3
fc_high = 900e3
filterorder = 10
#End of define settings for Radar_Evaluation_Modul.

list_of_measurements = []

#Iterate over the measurements.
for count, name in enumerate(file_names):
    print("Evaluated Measurement {0}".format(count))
    single_measurement = radar_measurement_evaluation(path_csv,name,B,T_c,c0,number_of_ramps,total,f0,f1,windowing,ideal,swap_IQ,calibration,plotting,filtering,fc_low,fc_high,filterorder)
    single_measurement.run_radar_evaluation()
    list_of_measurements.append(single_measurement)

#Define settings for Radar_Imaging_Modul.
offset = 0  #This value must be zero for ideal data.
distance = single_measurement.distance_corrected
number_of_points_x = 401
number_of_points_y = 401
start_x = 0
end_x = 40
start_y = 50
end_y = 90
antenna_distance = 10
antenna_start = 0
antenna_end = 45
dynamic_range = 30
#End of define settings for Radar_Imaging_Modul.

radar_imaging = radar_imaging(list_of_measurements,distance,offset,number_of_points_x,number_of_points_y,start_x,start_y,end_x,end_y,antenna_distance,antenna_start,antenna_end,dynamic_range,number_of_measurements)
radar_imaging.run_radar_imaging()