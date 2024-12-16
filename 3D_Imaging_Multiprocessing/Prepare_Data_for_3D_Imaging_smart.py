#Import of Necessary Python Libraries.
import scipy.constants as sc
import matplotlib.pyplot as plt
import numpy as np
import os
import pathlib
from os import walk
import sys

from multiprocessing import Pool, Manager
from tqdm import tqdm

#Import of the Radar Measurement Evaluation Modul.
from Radar_Evaluation_Modul_for_3D_Imaging_smart import radar_measurement_evaluation

#Define settings for Radar_Evaluation_Modul.
f0 = 6e9
f1 = 14e9
B = (f1-f0)
T_c = 200*1e-6
c0 = sc.speed_of_light
number_of_ramps = 200
total = 8192
windowing = True
ideal = False
swap_IQ = True
calibration = False
filtering = True
plotting = False
fc_low = 300e3
fc_high = 600e3
filterorder = 10
#End of define settings.

measurement_offset = 0
list_of_measurements = []
def process_data_in_file(file_info):
    # global measurement_offset
    """
    Function to process data for a single file.
    Receives a tuple: (file_path, file_name)
    """
    working_dir, measurement_offset, file_path, file_name = file_info

    path_csv = file_path
    name = file_name

    single_measurement = radar_measurement_evaluation(path_csv, name, B, T_c, c0, number_of_ramps, total, f0, f1,windowing, ideal, swap_IQ, calibration, plotting, filtering,fc_low, fc_high, filterorder, measurement_offset, working_dir)
    single_measurement.run_radar_evaluation()
    list_of_measurements.append(single_measurement)

    return file_name
    return processed_folders
    
def main():
    # storage_folder = input("Please enter the folder name where the output files should be stored: ")
    storage_folder = input("Geben Sie den Ordnername ein, in dem die Pickle Dateien gespeichert werden sollen: ")
   
    print(f"storage_folder: \t{storage_folder}")

    # Get current directory.
    current_dir = os.path.dirname(__file__)
    # Setting working directory
    working_dir = f"{current_dir}\{storage_folder}"
    # Check if all necessary folders exist and if not create them.
    path = pathlib.Path(working_dir)
    path.mkdir(parents=True, exist_ok=True)
    # Change operation path to desire path
    current_dir = path

    # Check if all necessary folders exist and if not create them.
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

    # Base path containing the measurement folders
    base_path = r"D:\Measurement_Data_Cache\Vollständiges_Alu_IC_Logo"

    #Checks if there are any folders and returns the number of files in these folders.
    folder_info = []
    for entry in os.scandir(base_path):
        if entry.is_dir():
            # Count the number of files in the folder
            file_count = len([f for f in os.listdir(f"{base_path}\{entry.name}") if os.path.isfile(os.path.join(f"{base_path}\{entry.name}", f))])
            # Append the tuple (folder name, file count) to the list
            folder_info.append((entry.name, file_count))

    print(f"Es wurden {len(folder_info)} Ordner für die Bearbeitung gefunden.")

    results = []
    processed_folders = []
    for folder_name in folder_info:

        #Count the number of folders.
        count = folder_info.index(folder_name)
        print(f"Processing folder {folder_info.index(folder_name)} of {len(folder_info)}")
        #Multiply folder number with offset.
        measurement_offset = 40 * count

        folder_path = os.path.join(base_path, folder_name[0])

        # Collect all files in the folder with their paths and names.
        file_info = [(working_dir, measurement_offset, folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

        # Use multiprocessing to process files in this folder
        with Pool(8) as pool:
            with tqdm(total=len(file_info), desc="Processing files", unit="file", file=sys.stdout) as pbar:
                # Use imap_unordered to process files and update progress bar
                for name in pool.imap_unordered(process_data_in_file, file_info):
                    pbar.update(1)

            processed_folders.append(folder_name)

    # print("Processing completed for folders:", processed_folders)


if __name__ == "__main__":
    import time
    # start time
    start_time = time.time()

    main()

    # end time
    end_time = time.time()
    compute_time = end_time - start_time
    compute_time_min = compute_time / 60
    print(f"{round(compute_time, 3)} seconds ({round(compute_time_min, 2)} min.) passed while executing.")