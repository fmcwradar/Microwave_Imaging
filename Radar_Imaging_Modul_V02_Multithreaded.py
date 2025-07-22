import numpy as np
import matplotlib.pyplot as plt
import pickle
import os
import seaborn as sns
from scipy import interpolate
import pathlib
from datetime import datetime
from tqdm import tqdm
import sys
from multiprocessing import Pool

class radar_imaging:
    """
    Class that calculates the image based on the IF spectra measured with an FMCW radar system.
    
    INPUTS:
        list_of_measurements: (list) list of objects. Every object represents one FMCW radar measurement at a certain position.
        distance: (numpy.ndarray) distance vector measured by the FMCW radar system.
        offset: (float) offset value that needs to be subtracted from the distance vector.
        number_of_points_x: (int) number of points along the x_axis.
        number_of_points_y: (int) number of points along the y_axis.
        number_of_points_z: (int) number of points along the z_axis.
        start_x: (float) start value of the x-axis in the image.
        start_y: (float) start value of the y-axis in the image.
        start_z: (float) start value of the z-axis in the image.
        end_x: (float) end value of the x-axis in the image.
        end_y: (float) end value of the y_axis in the image.
        end_z: (float) end value of the z_axis in the image.
        antenna_distance: (float) distance between the antenna centers.
        antenna_start: (float) start position of the antennas along the linear axis.
        antenna_end: (float) end position of the antennas along the linear axis.
        dynamic_range: (float) dynamic range of the image.
        number_of_measurements: (int) number of measurents that shall be evaluated for the image generation.
    """

    def __init__(self,distance,offset,number_of_points_x,number_of_points_y,number_of_points_z,start_x,start_y,start_z,end_x,end_y,end_z,antenna_distance,dynamic_range,settings):
        # self.list_of_measurements = list_of_measurements
        self.distance = distance
        self.offset = offset
        self.number_of_points_x = number_of_points_x
        self.number_of_points_y = number_of_points_y
        self.number_of_points_z = number_of_points_z
        self.start_x = start_x
        self.start_y = start_y
        self.start_z = start_z
        self.end_x = end_x
        self.end_y = end_y
        self.end_z = end_z
        self.antenna_distance = antenna_distance
        self.dynamic_range = dynamic_range
        self.settings = settings

        # self.antenna_start = antenna_start
        # self.antenna_end = antenna_end
        # self.number_of_measurements = number_of_measurements

    def calculate_image(self, prepared_data_names):
        plt.rcParams.update(plt.rcParamsDefault)
        #Define the offset of the EM waves due to cables, adapters etc. For ideal data the offset is zero.
        distance = (self.distance-self.offset)*100
        distance *= 2
        self.image_matrix = np.zeros((self.number_of_points_x,self.number_of_points_y, self.number_of_points_z), dtype = complex)

        #Start Image Calculation

        #Calculate Index Matrix
        x_axis = np.linspace(self.start_x, self.end_x, self.number_of_points_x)
        y_axis = np.linspace(self.start_y, self.end_y, self.number_of_points_y)
        z_axis = np.linspace(self.start_z, self.end_z, self.number_of_points_z)

        x_coordinates, y_coordinates, z_coordinates = np.meshgrid(x_axis, y_axis, z_axis, indexing='ij')

        with open(f"{self.settings[26]}\Prepared_Data\\{prepared_data_names}.pkl", 'rb') as file:
            # with open(f"{working_dir}\Final_3D_Files\\final_3D_image.pkl", 'rb') as file:
            # Call load method to deserialze.
            measurement = pickle.load(file)

        # name includes the whole file name without the file type, e.g. 0.0_10.0
        # split splits name at the '_'- symbol, e.g. 0.0 and 10.0
        radar_position_z = float(str(prepared_data_names).split('_')[0]) / 10  # convert mm to cm
        radar_position_x = float(str(prepared_data_names).split('_')[1]) / 10  # convert mm to cm

        distance_a = np.sqrt((x_coordinates - radar_position_x) ** 2 + y_coordinates ** 2 + (z_coordinates - radar_position_z + self.antenna_distance / 2) ** 2)  # Forward wave.
        distance_b = np.sqrt((x_coordinates - radar_position_x) ** 2 + y_coordinates ** 2 + (z_coordinates - radar_position_z - self.antenna_distance / 2) ** 2)  # Backward wave.

        distance_image = distance_a + distance_b

        spectrum_single_measurement = measurement   #.spectrum_up

        #Build Interpolator
        f_abs = interpolate.interp1d(distance, np.abs((spectrum_single_measurement)), kind = 'cubic')
        f_angle = interpolate.interp1d(distance, np.unwrap(np.angle((spectrum_single_measurement))), kind = 'cubic')

        image_matrix_cache_abs = f_abs(distance_image)
        image_matrix_cache_angle = f_angle(distance_image)

        image_matrix_cache = image_matrix_cache_abs * np.exp(1j*image_matrix_cache_angle)

        self.image_matrix = self.image_matrix + image_matrix_cache

        return self.image_matrix

    def run_radar_imaging(self):
        plotting = True
        save_cuts = True
        image_matrix = np.zeros((self.number_of_points_x, self.number_of_points_y, self.number_of_points_z), dtype=complex)
        # walking through directory and collecting file names for multithreading in a later step
        from os import walk
        file_names = next(walk(self.settings[25]), (None, None, []))[2]  # [] if no file

        calculation_info = []
        for count, name in enumerate(file_names):
            if not name.startswith("distance"):
                # combining all info needed for multithreading in an array called calculation_info
                calculation_info.append((self.settings[25], self.distance, file_names[count], self.settings[19]))
    
        prepared_data_names = [os.path.splitext(f)[0] for f in os.listdir(f"{self.settings[26]}\Prepared_Data") if f.endswith(".pkl")]

        thread_number = 8
        with Pool(thread_number) as pool:
            with tqdm(total=len(calculation_info), desc="Calculating image", unit=" file", file=sys.stdout) as pbar:
                # Use imap_unordered to process files and update progress bar
                for result in pool.imap_unordered(self.calculate_image, prepared_data_names):
                    image_matrix += result
                    pbar.update(1)

        path = self.settings[26]

        with open(r"{0}\image_radar.pkl".format(path), 'wb') as file:
            # A new file will be created.
            pickle.dump(image_matrix, file)

        image_matrix = image_matrix ** 2
        image_matrix_norm = image_matrix / np.max(np.abs(image_matrix))

        if plotting == True:
            fig = plt.figure("Multithreaded")
            fig.figsize = (20, 20)

            ax = sns.heatmap(10 * np.log10(np.abs(image_matrix_norm)[:,:,0].T), cbar=True, cmap='jet', square=True, vmax=0,
                             vmin=-self.dynamic_range, cbar_kws={'label': 'Normalized Intensity (dB)'})

            x_axis = np.linspace(self.start_x, self.end_x, self.number_of_points_x)
            y_axis = np.linspace(self.start_y, self.end_y, self.number_of_points_y)
            z_axis = np.linspace(self.start_z, self.end_z, self.number_of_points_z)

            x_ticks = (np.round(np.linspace(self.start_x, self.end_x,int(np.round((np.abs(self.end_x) + np.abs(self.start_x)) / 5, 0) + 1)), 1))
            x_ticks_location = np.linspace(0, len(x_axis),int(np.round((np.abs(self.end_x) + np.abs(self.start_x)) / 5, 0) + 1))

            y_ticks = (np.round(np.linspace(self.start_y, self.end_y,int(np.round((np.abs(self.end_y) - np.abs(self.start_y)) / 5, 0) + 1)), 1))
            y_ticks_location = np.linspace(0, len(y_axis),int(np.round((np.abs(self.end_y) - np.abs(self.start_y)) / 5, 0) + 1))

            z_ticks = (np.round(np.linspace(self.start_z, self.end_z,int(np.round((np.abs(self.end_z) - np.abs(self.start_z)) / 5, 0) + 1)), 1))
            z_ticks_location = np.linspace(0, len(z_axis),int(np.round((np.abs(self.end_z) - np.abs(self.start_z)) / 5, 0) + 1))

            ax.invert_yaxis()
            cbar_axes = ax.figure.axes[-1]
            ax.figure.axes[-1].yaxis.label.set_size(22.5)
            plt.xticks(x_ticks_location, x_ticks, fontsize=10)
            plt.yticks(y_ticks_location, y_ticks, fontsize=22.5)
            plt.xlabel("x (cm)", fontsize=22.5)
            plt.ylabel("y (cm)", fontsize=22.5)
            cax = ax.figure.axes[-1]
            cax.tick_params(labelsize=22.5)
            fig.set_tight_layout(True)

            filepath = f'{path}\z_0.0_cm.png'
            plt.savefig(filepath, format="png")

            plt.show()

        if len(z_axis) != 1 and save_cuts == True:
            size_setting = 10

            output_path = pathlib.Path(f'{path}\Cuts')
            output_path.mkdir(parents=True, exist_ok=True)

            for index in tqdm(range(0, len(y_ticks)), desc="Generating y-cuts", unit=" cut", file=sys.stdout):
                fig = plt.figure()
                fig.figsize = (20, 20)

                slice_image = np.transpose(image_matrix_norm[:, index, :])
                ax = sns.heatmap(10 * np.log10(np.abs(slice_image)), square=True, cbar=True, vmax=0,
                                 vmin=-self.dynamic_range, cmap='jet', cbar_kws={'label': 'Normalized Amplitude (dB)'})
                ax.set_xticks(x_ticks_location, np.flip(x_ticks), fontsize=size_setting)
                ax.set_yticks(y_ticks_location, y_ticks, fontsize=size_setting)
                ax.set_xlabel("x (cm)", fontsize=size_setting)
                ax.set_ylabel("y (cm)", fontsize=size_setting)
                ax.invert_yaxis()
                ax.set_title("z = {} cm".format(np.round(z_axis[index], 2)), fontsize=size_setting, x=0.45, y=1)
                fig.set_tight_layout(True)

                filepath = f'{path}\Cuts\z_{np.round(z_axis[index], 2)}_cm.png'

                plt.savefig(filepath, format="png")
                plt.clf()
                plt.cla()
                plt.close('all')

        with open(r'{0}\Settings.txt'.format(path), 'a') as the_file:
            the_file.write('f_0 = {0} GHz\n'.format(self.settings[0] / 1e9))
            the_file.write('f_1 = {0} GHz\n'.format(self.settings[1] / 1e9))
            the_file.write('B = {0} GHz\n'.format(self.settings[2] / 1e9))
            the_file.write('T_c = {0} µs\n'.format(self.settings[3] * 1e6))
            the_file.write('Number of ramps = {0}\n'.format(self.settings[4]))
            the_file.write('Number of points in FFT = {0}\n'.format(self.settings[5]))
            the_file.write('Windowing = {0}\n'.format(self.settings[6]))
            the_file.write('Calibration = {0}\n'.format(self.settings[7]))
            the_file.write('Filtering = {0}\n'.format(self.settings[8]))
            the_file.write('fc_low = {0} kHz\n'.format(self.settings[9] / 1e3))
            the_file.write('fc_high = {0} kHz\n'.format(self.settings[10] / 1e3))
            the_file.write('Filterorder = {0}\n'.format(self.settings[11]))
            the_file.write('Background subtraction = {0}\n'.format(self.settings[12]))
            the_file.write('Hilbert = {0}\n'.format(self.settings[13]))
            the_file.write('offset = {0}\n'.format(self.settings[14]))
            the_file.write('start_x = {0} cm\n'.format(self.settings[15]))
            the_file.write('start_y = {0} cm\n'.format(self.settings[16]))
            the_file.write('start_z = {0} cm\n'.format(self.settings[17]))
            the_file.write('end_x = {0} cm\n'.format(self.settings[18]))
            the_file.write('end_y = {0} cm\n'.format(self.settings[19]))
            the_file.write('end_z = {0} cm\n'.format(self.settings[20]))
            the_file.write('antenna_distance = {0} cm\n'.format(self.settings[21]))
            the_file.write('Number of points x = {0}\n'.format(self.settings[22]))
            the_file.write('Number of points y = {0}\n'.format(self.settings[23]))
            the_file.write('Number of points z = {0}\n'.format(self.settings[24]))
            the_file.write('Filepath: {0}\n'.format(self.settings[25]))