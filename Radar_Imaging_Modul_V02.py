import numpy as np
import matplotlib.pyplot as plt
import pickle
import os
import seaborn as sns
from scipy import interpolate
import pathlib
from datetime import datetime
from tqdm import tqdm

class radar_imaging:

    """
    Class that calculates the image based on the IF spectra measured with an FMCW radar system.
    
    INPUTS:
        list_of_measurements: (list) list of objects. Every object represents one FMCW radar measurement at a certain position.
        distance: (numpy.ndarray) distance vector measured by the FMCW radar system.
        offset: (float) offset value that needs to be subtracted from the distance vector.
        number_of_points_x: (int) number of points along the x_axis.
        number_of_points_y: (int) number of points along the y_axis.
        start_x: (float) start value of the x-axis in the image.
        start_y: (float) start value of the y-axis in the image.
        end_x: (float) end value of the x-axis in the image.
        end_y: (float) end value of the y_axis in the image.
        antenna_distance: (float) distance between the antenna centers.
        antenna_start: (float) start position of the antennas along the linear axis.
        antenna_end: (float) end position of the antennas along the linear axis.
        dynamic_range: (float) dynamic range of the image.
        number_of_measurements: (int) number of measurents that shall be evaluated for the image generation.
    """

    def __init__(self,list_of_measurements,distance,offset,number_of_points_x,number_of_points_y,start_x,start_y,end_x,end_y,antenna_distance,antenna_start,antenna_end,dynamic_range,number_of_measurements,settings):
        self.list_of_measurements = list_of_measurements
        self.distance = distance
        self.offset = offset
        self.number_of_points_x = number_of_points_x
        self.number_of_points_y = number_of_points_y
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.antenna_distance = antenna_distance
        self.antenna_start = antenna_start
        self.antenna_end = antenna_end
        self.dynamic_range = dynamic_range
        self.number_of_measurements = number_of_measurements
        self.settings = settings
        
    def calculate_image(self):
    
        plt.rcParams.update(plt.rcParamsDefault)
        #Define the offset of the EM waves due to cables, adapters etc. For ideal data the offset is zero.
        distance = (self.distance-self.offset)*100
        distance *= 2
        
        distance_increment = distance[10]-distance[9]

        antenna_positions = np.linspace(self.antenna_start, self.antenna_end, self.number_of_measurements)
        counter = 0
        
        self.image_matrix = np.zeros((self.number_of_points_y, self.number_of_points_x), dtype = complex)
        
        #Start Image Calculation
        for antenna_x in tqdm(antenna_positions, desc="Calculating image", unit="iteration"):

            #Calculate Index Matrix
            x_axis = np.linspace(self.start_x, self.end_x, self.number_of_points_x)
            y_axis = np.linspace(self.start_y, self.end_y, self.number_of_points_y)

            x_coordinates, y_coordinates = np.meshgrid(x_axis, y_axis)

            distance_a = np.sqrt(np.abs((x_coordinates-(antenna_x))**2 + y_coordinates**2+(self.antenna_distance/2)**2))    #Forward wave.
            
            distance_b = np.sqrt(np.abs((x_coordinates-(antenna_x))**2 + y_coordinates**2-(self.antenna_distance/2)**2))    #Backward wave.
            
            distance_image = distance_a + distance_b
            
            spectrum_single_measurement = self.list_of_measurements[counter].spectrum_up
            
            #Build Interpolator
            f_abs = interpolate.interp1d(distance, np.abs((spectrum_single_measurement)), kind = 'cubic')
            f_angle = interpolate.interp1d(distance, np.unwrap(np.angle((spectrum_single_measurement))), kind = 'cubic')
            
            image_matrix_cache_abs = f_abs(distance_image)
            image_matrix_cache_angle = f_angle(distance_image)
            
            image_matrix_cache = image_matrix_cache_abs * np.exp(1j*image_matrix_cache_angle)

            self.image_matrix = self.image_matrix + image_matrix_cache

            counter = counter + 1

        self.image_matrix = self.image_matrix**2

        image_matrix_norm = self.image_matrix/np.max(np.abs(self.image_matrix))
                
        ax = sns.heatmap(10*np.log10(np.abs(image_matrix_norm)), cbar = True, cmap = 'jet',square = True, vmax = 0, vmin = -self.dynamic_range, cbar_kws={'label': 'Normalized Intensity (dB)'})    

        x_ticks = (np.round(np.linspace(self.start_x, self.end_x, int(np.round((np.abs(self.end_x)+np.abs(self.start_x))/5,0)+1)),1))
        x_ticks_location = np.linspace(0, len(x_axis), int(np.round((np.abs(self.end_x)+np.abs(self.start_x))/5,0)+1))

        y_ticks = (np.round(np.linspace(self.start_y, self.end_y, int(np.round((np.abs(self.end_y)-np.abs(self.start_y))/5,0)+1)),1))
        y_ticks_location = np.linspace(0, len(y_axis), int(np.round((np.abs(self.end_y)-np.abs(self.start_y))/5,0)+1))

        ax.invert_yaxis()
        cbar_axes = ax.figure.axes[-1]
        ax.figure.axes[-1].yaxis.label.set_size(22.5)
        plt.xticks(x_ticks_location, x_ticks, fontsize = 22.5) 
        plt.yticks(y_ticks_location, y_ticks, fontsize = 22.5) 
        plt.xlabel("x (cm)", fontsize = 22.5)
        plt.ylabel("y (cm)", fontsize = 22.5)
        cax = ax.figure.axes[-1]
        cax.tick_params(labelsize=22.5)
        plt.show()

        #Save the result in .pkl-file and create log-file.
        current_dir = os.path.dirname(__file__)

        date_today = datetime.today().strftime('%Y-%m-%d')

        time_today = datetime.today().strftime('%H-%M-%S')

        path = pathlib.Path(r'{0}\Pickle_Files\{1}_{2}'.format(current_dir,date_today,time_today))
        path.mkdir(parents=True, exist_ok=True)
        
        with open(r"{0}\image_radar.pkl".format(path), 'wb') as file: 
              
            # A new file will be created. 
            pickle.dump(image_matrix_norm, file) 
        
        with open(r'{0}\Settings.txt'.format(path), 'a') as the_file:
            the_file.write('f_0 = {0} GHz\n'.format(self.settings[0]/1e9))
            the_file.write('f_1 = {0} GHz\n'.format(self.settings[1]/1e9))
            the_file.write('B = {0} GHz\n'.format(self.settings[2]/1e9))
            the_file.write('T_c = {0} µs\n'.format(self.settings[3]*1e6))
            the_file.write('Number of ramps = {0}\n'.format(self.settings[4]))
            the_file.write('Number of points in FFT = {0}\n'.format(self.settings[5]))
            the_file.write('Windowing = {0}\n'.format(self.settings[6]))
            the_file.write('Calibration = {0}\n'.format(self.settings[7]))
            the_file.write('Filtering = {0}\n'.format(self.settings[8]))
            the_file.write('fc_low = {0} kHz\n'.format(self.settings[9]/1e3))
            the_file.write('fc_high = {0} kHz\n'.format(self.settings[10]/1e3))
            the_file.write('Filterorder = {0}\n'.format(self.settings[11]))
            the_file.write('Background subtraction = {0}\n'.format(self.settings[12]))
            the_file.write('Hilbert = {0}\n'.format(self.settings[13]))
            the_file.write('offset = {0}\n'.format(self.settings[14]))
            the_file.write('start_x = {0} cm\n'.format(self.settings[15]))
            the_file.write('start_y = {0} cm\n'.format(self.settings[16]))
            the_file.write('end_x = {0} cm\n'.format(self.settings[17]))
            the_file.write('end_y = {0} cm\n'.format(self.settings[18]))
            the_file.write('antenna_distance = {0} cm\n'.format(self.settings[19]))
            the_file.write('antenna_start = {0} cm\n'.format(self.settings[20]))
            the_file.write('antenna_end = {0} cm\n'.format(self.settings[21]))
            the_file.write('Number of points x = {0}\n'.format(self.settings[22]))
            the_file.write('Number of points y = {0}\n'.format(self.settings[23]))
            the_file.write('Filepath: {0}\n'.format(self.settings[24]))
        
    def run_radar_imaging(self):
    
        self.calculate_image()