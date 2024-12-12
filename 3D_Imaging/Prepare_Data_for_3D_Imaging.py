#Import of Necessary Python Libraries.
import scipy.constants as sc
import matplotlib.pyplot as plt
import numpy as np
import os
import pathlib
#Import of the Radar Measurement Evaluation Modul.
from Radar_Evaluation_Modul_for_3D_Imaging import radar_measurement_evaluation
#Get current directory.
current_dir = os.path.dirname(__file__)
#Path in which the .csv-files are located.
path_csv = r"C:\Users\Martin\Desktop\Kalibrierung Micha\MXO-Phantom_Messung"
#Check if all necessary folders exist and if not create them.
path = pathlib.Path(r'{0}\Pickle Files for 3D Imaging'.format(current_dir))
path.mkdir(parents=True, exist_ok=True)
path = pathlib.Path(r'{0}\Results\Plot_IF_Signal'.format(current_dir))
path.mkdir(parents=True, exist_ok=True)
path = pathlib.Path(r'{0}\Results\Plot_IF_Spectrum'.format(current_dir))
path.mkdir(parents=True, exist_ok=True)
path = pathlib.Path(r'{0}\Pickle Files'.format(current_dir))
path.mkdir(parents=True, exist_ok=True)
path = pathlib.Path(r'{0}\Final_3D_Files'.format(current_dir))
path.mkdir(parents=True, exist_ok=True)
path = pathlib.Path(r'{0}\Final_3D_Files\Cuts'.format(current_dir))
path.mkdir(parents=True, exist_ok=True)

from os import walk

file_names = next(walk(path_csv), (None, None, []))[2]  # [] if no file

#Define settings for Radar_Evaluation_Modul.
f0 = 6e9
f1 = 14e9
B = (f1-f0)
T_c = 200*1e-6
c0 = sc.speed_of_light
number_of_ramps = 300
total = 8192
windowing = True
ideal = False
swap_IQ = True
calibration = False
filtering = True
plotting = False
fc_low = 300e3
fc_high = 500e3
filterorder = 10
#End of define settings.

measurement_offset = 0

list_of_measurements = []

#Iterate over the measurements.
for count, name in enumerate(file_names):
    print("Evaluated Measurement {0}".format(count))
    print(name)
    single_measurement = radar_measurement_evaluation(path_csv,name,B,T_c,c0,number_of_ramps,total,f0,f1,windowing,ideal,swap_IQ,calibration,plotting,filtering,fc_low,fc_high,filterorder,measurement_offset)
    single_measurement.run_radar_evaluation()
    list_of_measurements.append(single_measurement)
