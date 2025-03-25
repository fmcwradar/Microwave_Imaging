#Import of necessary Python libraries.
import pickle
import sys
import scipy.constants as sc
import matplotlib.pyplot as plt
import numpy as np
import os
import pathlib
from tqdm import tqdm
#Import of the Radar Measurement Evaluation Modul.
from Radar_Evaluation_Modul import radar_measurement_evaluation
from Radar_Imaging_Modul_V02_Multithreaded import radar_imaging

from multiprocessing import Pool
from pathlib import Path

#Get current directory.
current_dir = os.path.dirname(__file__)
#Path in which the .csv-files are located.
# path_csv = r"{0}\Ideal_Data_Radar".format(current_dir)
path_csv = r"E:\Measurement_Data_Cache\vollstaendiges-3D-Phantom_mit_unterschiedlich_gefuellten_Bohrungen"
# path_csv = r"E:\Measurement_Data_Cache\SCHNITT-Phantom-mit-langen-Bohrungen-gefuellt-mit-Wasser"
#Check if all necessary folders exist and if not create them.
path = pathlib.Path(r'{0}\Pickle_Files'.format(current_dir))
path.mkdir(parents=True, exist_ok=True)

list_of_measurements = []

# file_names = []

# for number in range(0, number_of_measurements):
#     file_names.append("0.0_{0}".format(float(10*number)))

def check_folder_contents(folder_path):
    folder_name = pathlib.Path(folder_path)
    contains_folder = any(p.is_dir() for p in folder_name.iterdir())
    contains_files = any(p.is_file() for p in folder_name.iterdir())
    file_names = [f.name for f in folder_name.iterdir() if f.is_file()]
    if contains_files == True and contains_folder == False:
        return contains_files, file_names
    if contains_folder == True:
        return False, "None"
    else:
        return "None", "None"

def process_data_in_file(file_info):
    """
    Function to process data for a single file.
    Receives (working_dir, file_path, file_name)
    """
    working_dir, file_path, file_name = file_info
    path_csv = file_path
    name = Path(file_name).with_suffix('')

    single_measurement = radar_measurement_evaluation(path_csv, name, B, T_c, c0, number_of_ramps, total, f0, f1,
                                                      windowing, ideal, swap_IQ, calibration, filtering, fc_low,
                                                      fc_high, filterorder, offset, save_last_measurement,
                                                      background_subtraction, hilbert)
    single_measurement.run_radar_evaluation()
    list_of_measurements.append(single_measurement)

    # return file_name
    return single_measurement

contains_content, content = check_folder_contents(path_csv)

file_info = []
processed_folders = []
for file in content:
    folder_path = path_csv
    # Collect file info in measurement folder, needed for multithreading
    file_info.append((current_dir, folder_path, file))

#Define settings for Radar_Evaluation_Modul.
f0 = 6e9
f1 = 14e9
B = (f1-f0)
T_c = 200*1e-6
c0 = sc.speed_of_light
number_of_ramps = 50
total = 8192
windowing = True
ideal = False
swap_IQ = True
calibration = True
filtering = True
fc_low = 350e3
fc_high = 500e3
filterorder = 10
save_last_measurement = False
background_subtraction = False
hilbert = False
offset = 0.935
#End of define settings.

# list_of_measurements = []

#Iterate over the measurements.
# for name in tqdm(file_names, desc="Preparing IF data", unit=" files", file=sys.stdout):
#     single_measurement = radar_measurement_evaluation(path_csv,name,B,T_c,c0,number_of_ramps,total,f0,f1,windowing,ideal,swap_IQ,calibration,filtering,fc_low,fc_high,filterorder,offset,save_last_measurement,background_subtraction,hilbert)
#     single_measurement.run_radar_evaluation()
#     list_of_measurements.append(single_measurement)

def main():
    global radar_imaging

    # Save the result in .pkl-file and create log-file.
    current_dir = os.path.dirname(__file__)
    from datetime import datetime
    date_today = datetime.today().strftime('%Y-%m-%d')
    time_today = datetime.today().strftime('%H-%M-%S')
    path = pathlib.Path(r'{0}\Pickle_Files\{1}_{2}'.format(current_dir, date_today, time_today))
    path.mkdir(parents=True, exist_ok=True)
    prepared_data_path = pathlib.Path(f"{path}\Prepared_Data")
    prepared_data_path.mkdir(parents=True, exist_ok=True)

    # Pool(8) means 8 threads are used to process multiple files at the same time
    with Pool(8) as pool:
        # tqdm generates Progressbar with length=total
        with tqdm(total=len(file_info), desc="Preparing files", unit=" file", file=sys.stdout) as pbar:
            # Use imap_unordered to process files and update progress bar
            for single_measurement in pool.imap_unordered(process_data_in_file, file_info):
                # list_of_measurements.append(single_measurement)
                with open(f"{prepared_data_path}\{single_measurement.name}.pkl", 'wb') as file:
                    # A new file will be created.
                    pickle.dump(single_measurement.spectrum_up, file)
                pbar.update(1)

    # Save the result in .pkl-file and create log-file.
    # current_dir = os.path.dirname(__file__)
    # from datetime import datetime
    # date_today = datetime.today().strftime('%Y-%m-%d')
    # time_today = datetime.today().strftime('%H-%M-%S')
    #
    # path = pathlib.Path(r'{0}\Pickle_Files\{1}_{2}'.format(current_dir, date_today, time_today))
    # path.mkdir(parents=True, exist_ok=True)
    # prepared_data_path = pathlib.Path(f"{path}\Prepared_Data")
    # prepared_data_path.mkdir(parents=True, exist_ok=True)
    #
    # for i in range(0, len(list_of_measurements)):
    #     # Save the individual measurement objects for more efficient memory usage during image calculation
    #     with open(f"{prepared_data_path}\{list_of_measurements[i].name}.pkl", 'wb') as file:
    #         # A new file will be created.
    #         pickle.dump(list_of_measurements[i], file)

    #Define settings for Radar_Imaging_Modul.
    distance = single_measurement.distance_corrected
    number_of_points_x = 201
    number_of_points_y = 201
    number_of_points_z = 201
    start_x = 0
    end_x = 45
    start_y = 40
    end_y = 80
    start_z = 0
    end_z = 23

    antenna_distance = 10
    # antenna_start = 0
    # antenna_end = 45
    # number_of_measurements = 46
    dynamic_range = 30
    # image_matrix = np.zeros((number_of_points_z, number_of_points_y, number_of_points_x))
    #End of define settings.

    settings = [f0,f1,B,np.round(T_c,8),number_of_ramps,total,windowing,calibration,filtering,fc_low,fc_high,filterorder,background_subtraction,hilbert,offset,start_x,start_y,start_z,end_x,end_y,end_z,antenna_distance,number_of_points_x,number_of_points_y,number_of_points_z,path_csv, path]

    # radar_imaging = radar_imaging(list_of_measurements,distance,offset,number_of_points_x,number_of_points_y,number_of_points_z,start_x,start_y,start_z,end_x,end_y,end_z,antenna_distance,antenna_start,antenna_end,dynamic_range,number_of_measurements,settings)
    radar_imaging = radar_imaging(distance, offset, number_of_points_x, number_of_points_y,
                                  number_of_points_z, start_x, start_y, start_z, end_x, end_y, end_z, antenna_distance,
                                  dynamic_range, settings)

    radar_imaging.run_radar_imaging()

if __name__ == "__main__":
    import time
    # start time
    start_time = time.time()

    main()

    # end time
    end_time = time.time()
    # Calculate total processing time
    compute_time = end_time - start_time
    compute_time_min = compute_time / 60
    print(f"{round(compute_time, 3)} seconds ({round(compute_time_min, 2)} min.) passed while executing.")