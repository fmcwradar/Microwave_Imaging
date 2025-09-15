# %%
#Import of necessary Python libraries.
import scipy.constants as sc
import matplotlib.pyplot as plt
import numpy as np
import os
import pathlib
from tqdm import tqdm
import sys
from datetime import datetime
from dataclasses import dataclass
#Import of customized radar package.
from RSP_Toolbox_MM.prepare import prepare_radar_measurement
from RSP_Toolbox_MM.imaging_public import DAS_imaging

#Get current directory.
current_dir = os.path.dirname(__file__)

def load_config(path_config):
    config = {}
    with open(path_config, 'r') as file:
        for line in file:
            if '=' in line and not line.strip().startswith("#"):
                key, value = line.strip().split('=', 1)
                key = key.strip()
                value = value.strip()
                # Typumwandlung
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                else:
                    try:
                        value = float(value)
                        # Ints bleiben int, wenn möglich
                        if value.is_integer():
                            value = int(value)
                    except ValueError:
                        pass  # String bleibt String
                config[key] = value
    return config

path_config = f"{current_dir}\Radar_Config.txt"

config = load_config(path_config)

f0 = config['f0']
f1 = config['f1']
B = f1 - f0
T_c = config['T_c']
c0 = sc.speed_of_light
number_of_ramps = config['number_of_ramps']
total = config['total']
windowing = config['windowing']
ideal = config['ideal']
swap_IQ = config['swap_IQ']
fc_low = config['fc_low']
fc_high = config['fc_high']
filterorder = config['filterorder']
hilbert = config['hilbert']
offset = config['offset']
start_x_ROI = config['start_x_ROI']
end_x_ROI = config['end_x_ROI']
start_y_ROI = config['start_y_ROI']
end_y_ROI = config['end_y_ROI']
calibration = config['calibration']
fontsize = config['fontsize']
antenna_distance = config['antenna_distance']
antenna_start = config['antenna_start']
antenna_end = config['antenna_end']
number_of_measurements = config['number_of_measurements']
overall_maximum = config['overall_maximum']
number_of_points_x = config['number_of_points_x']

#Path in which the .csv-files are located.
path_csv = f"{current_dir}\Ideal_Data_Radar"

#Check if all necessary folders exist and if not create them.
path = pathlib.Path(r'{0}\Pickle_Files'.format(current_dir))
path.mkdir(parents=True, exist_ok=True)

file_names = []

for number in range(0, number_of_measurements):
    file_names.append("0.0_{0}".format(float(10*number)))

filtering = False
save_last_measurement = False
background_subtraction = False
hilbert = False
dynamic_range_DAS = 60
#End of define settings.

list_of_measurements = []

#Iterate over the measurements.
for name in tqdm(file_names, desc="Preparing IF data", unit="iteration", file=sys.stdout):
    #Initialize single_measurement.
    single_measurement = prepare_radar_measurement(
    path_csv=path_csv,
    name=name,
    B=B,
    T_c=T_c,
    c0=c0,
    number_of_ramps=number_of_ramps,
    total=total,
    f0=f0,
    f1=f1,
    windowing=windowing,
    ideal=ideal,
    swap_IQ=swap_IQ,
    calibration=calibration,
    filtering=filtering,
    fc_low=fc_low,
    fc_high=fc_high,
    filterorder=filterorder,
    distance_offset=offset,
    save_last_measurement=save_last_measurement,
    background_subtraction=background_subtraction,
    hilbert=hilbert,
    execution_path=current_dir)

    #Run radar evaluation of single measurement.
    single_measurement.run_radar_evaluation()
    #Save object to list that includes all measurements.
    list_of_measurements.append(single_measurement)

#Define settings for Radar_Imaging_Modul.
distance = single_measurement.distance_corrected

number_of_points_z = 1

start_x = 0
end_x = 60
start_y = 0
end_y = 100
start_z = 0
end_z = 0

draw_ROI = False

#Create folder in which the results shall be saved.
date_today = datetime.today().strftime('%Y-%m-%d')
time_today = datetime.today().strftime('%H-%M-%S')
path_results = pathlib.Path(r'{0}\Pickle_Files\{1}_{2}'.format(current_dir,date_today,time_today))
path_results.mkdir(parents=True, exist_ok=True)

#Define settings for DAS image.
number_of_points_y = int(number_of_points_x*((end_y-start_y)/(end_x-start_x)))

imagepath = f"{current_dir}\Radar_Image.png"

#End of define settings for DAS image.
settings = [f0,f1,B,np.round(T_c,8),number_of_ramps,total,windowing,calibration,filtering,fc_low,fc_high,filterorder,background_subtraction,hilbert,offset,start_x,start_y,end_x,end_y,antenna_distance,antenna_start,antenna_end,number_of_points_x,number_of_points_y,path_csv]
DAS = DAS_imaging(
    list_of_measurements=list_of_measurements,
    distance=distance,
    offset=offset,
    number_of_points_x=number_of_points_x,
    number_of_points_y=number_of_points_y,
    start_x=start_x,
    start_y=start_y,
    end_x=end_x,
    end_y=end_y,
    antenna_distance=antenna_distance,
    antenna_start=antenna_start,
    antenna_end=antenna_end,
    dynamic_range=dynamic_range_DAS,
    number_of_measurements=number_of_measurements,
    settings=settings,
    fontsize_mm=fontsize,
    calibration=calibration,
    background_subtraction=background_subtraction,
    path_results=path_results,
    start_x_ROI=start_x_ROI,
    end_x_ROI=end_x_ROI,
    start_y_ROI=start_y_ROI,
    end_y_ROI=end_y_ROI,
    draw_ROI=draw_ROI,
    path_csv=path_csv,
    overall_maximum=overall_maximum,
    imagepath = imagepath,
    normalize=True
)
DAS.run_radar_imaging()