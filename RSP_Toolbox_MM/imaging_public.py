import numpy as np
import matplotlib.pyplot as plt
import pickle
import os
import seaborn as sns
from scipy import interpolate
import pathlib
from tqdm import tqdm
import openpyxl
from openpyxl import Workbook
import matplotlib as mpl

class DAS_imaging:

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
        settings: (list) that contains all configurations of the script which are saved later in a text file.
        fontsize_mm: (float) fontsize of the image.
        calibration: (bool) provides information if the measurement data was calibrated or not. Relevant for the normalization. 
        path_results: (string) path to the folder in which the results shall be saved.
    """

    def __init__(self,list_of_measurements,distance,offset,number_of_points_x,number_of_points_y,start_x,start_y,end_x,end_y,antenna_distance,antenna_start,antenna_end,dynamic_range,number_of_measurements,settings,fontsize_mm,calibration,background_subtraction,path_results,start_x_ROI,end_x_ROI,start_y_ROI,end_y_ROI,draw_ROI,path_csv,overall_maximum,imagepath,draw_ABC = False, draw_target = False, draw_antenna_coupling = False, draw_modified_background = False, draw_reflector = False, draw_plastic_block = False, draw_ghost_target = False, draw_metal_cylinder = False, draw_walls = False, draw_first_inclusion = False, draw_second_inclusion = False, vmax = 0, normalize = False, tickstep = 10):
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
        self.fontsize_mm = fontsize_mm
        self.calibration = calibration
        self.path_results = path_results
        self.start_x_ROI = start_x_ROI
        self.start_y_ROI = start_y_ROI
        self.end_x_ROI = end_x_ROI
        self.end_y_ROI = end_y_ROI
        self.draw_ROI = draw_ROI
        self.filepath = path_csv
        self.overall_maximum = overall_maximum
        self.background_subtraction = background_subtraction
        self.imagepath = imagepath
        self.normalize = normalize
        self.tickstep = tickstep
        self.vmax = vmax

    def calculate_image(self):
    
        plt.rcParams.update(plt.rcParamsDefault)
        #Subtract offset value from distance vector.
        distance = (self.distance-self.offset)*100
        #Double distance because the classic formula for the distance obtained with an FMCW radar includes a factor of 2 in the demoninator.
        distance *= 2
        #Calculate distance increment.
        distance_increment = distance[10]-distance[9]
        #Create array of antenna/measurement positions.
        antenna_positions = np.linspace(self.antenna_start, self.antenna_end, self.number_of_measurements)
        #Create empty matrix.
        self.image_matrix = np.zeros((self.number_of_points_y, self.number_of_points_x), dtype = complex)
        #Define horizontal taper.
        window = np.hanning(self.number_of_measurements + 2)
        
        #Start image calculation. 
        counter = 0

        #Define axes.
        x_axis = np.linspace(self.start_x, self.end_x, self.number_of_points_x)
        y_axis = np.linspace(self.start_y, self.end_y, self.number_of_points_y)

        for antenna_x in tqdm(antenna_positions, desc="Calculating DAS image", unit="iteration"):

                #Generate matrix.
                x_coordinates, y_coordinates = np.meshgrid(x_axis, y_axis)

                #Calculate distance matrix.
                distance_a = np.sqrt(np.abs((x_coordinates-(antenna_x))**2 + y_coordinates**2+(self.antenna_distance/2)**2))    #Forward wave.
                distance_b = np.sqrt(np.abs((x_coordinates-(antenna_x))**2 + y_coordinates**2-(self.antenna_distance/2)**2))    #Backward wave.
                distance_image = distance_a + distance_b
                
                #Load measurement and multiply with horizontal taper.
                spectrum_single_measurement = self.list_of_measurements[counter].spectrum_up * window[counter + 1]
                
                #Build interpolator.
                f_abs = interpolate.interp1d(distance, np.abs((spectrum_single_measurement)), kind = 'cubic')
                f_angle = interpolate.interp1d(distance, np.unwrap(np.angle((spectrum_single_measurement))), kind = 'cubic')
                
                #Apply interpolator.
                image_matrix_cache_abs = f_abs(distance_image)
                image_matrix_cache_angle = f_angle(distance_image)
                image_matrix_cache = image_matrix_cache_abs * np.exp(1j*image_matrix_cache_angle)

                #Update matrix.
                self.image_matrix = self.image_matrix + image_matrix_cache

                counter = counter + 1

        #Square the result to transform from voltage to power.
        self.image_matrix = (self.image_matrix**2)

        #Normalize matrix.

        if self.normalize == True:

            image_matrix_norm = self.image_matrix/np.max(np.abs(self.image_matrix))
        
        if self.normalize == False:

            image_matrix_norm = self.image_matrix/self.overall_maximum

        #Load font. Delete if CMU serif is not installed on your computer.
        mpl.rcParams['text.usetex']    = False
        mpl.rcParams['font.family']    = 'serif'
        mpl.rcParams['font.serif']     = ['CMU Serif']
        mpl.rcParams['mathtext.fontset'] = 'cm'
        
        #Create figure and plot heatmap.
        plt.figure(figsize=(40, 30))

        ax = sns.heatmap(10*np.log10(np.abs(image_matrix_norm)), cbar = True, cmap = 'viridis',square = True, vmax = self.vmax, vmin = self.vmax -self.dynamic_range, cbar_kws={'label': 'Normalized intensity (dB)'})    

        x_ticks = (np.round(np.linspace(self.start_x, self.end_x, int(np.round((np.abs(self.end_x)-np.abs(self.start_x))/self.tickstep,0)+1)),1))
        
        x_ticks = [int(entry) for entry in x_ticks]
        
        x_ticks_location = np.linspace(0, len(x_axis), int(np.round((np.abs(self.end_x)-np.abs(self.start_x))/self.tickstep,0)+1))

        y_ticks = (np.round(np.linspace(self.start_y, self.end_y, int(np.round((np.abs(self.end_y)-np.abs(self.start_y))/self.tickstep,0)+1)),1))
        
        y_ticks = [int(entry) for entry in y_ticks]
        
        y_ticks_location = np.linspace(0, len(y_axis), int(np.round((np.abs(self.end_y)-np.abs(self.start_y))/self.tickstep,0)+1))
                
        ax.xaxis.set_tick_params(pad=25)
        ax.yaxis.set_tick_params(pad=25)

        textsize_MM = self.fontsize_mm

        #Draw ROI.
        if self.draw_ROI == True:

            index_0 = np.argmax(x_axis > self.start_x_ROI)
            index_1 = np.argmax(x_axis > self.end_x_ROI)
            index_2 = np.argmax(y_axis > self.start_y_ROI)
            index_3 = np.argmax(y_axis > self.end_y_ROI)
        
            plt.hlines(index_2, index_0, index_1, linewidth = 15.0, color = 'r')
            plt.hlines(index_3, index_0, index_1, linewidth = 15.0, color = 'r')
            
            plt.vlines(index_0, index_2, index_3, linewidth = 15.0, color = 'r')
            plt.vlines(index_1, index_2, index_3, linewidth = 15.0, color = 'r')
        
        #Prepare heatmap for appealing visualization.
        ax.invert_yaxis()
        cbar_axes = ax.figure.axes[-1]
        ax.figure.axes[-1].yaxis.label.set_size(self.fontsize_mm)
        plt.xticks(x_ticks_location, x_ticks, fontsize = self.fontsize_mm) 
        plt.yticks(y_ticks_location, y_ticks, fontsize = self.fontsize_mm) 
        plt.xlabel("Cross-range x (cm)", fontsize = self.fontsize_mm)
        plt.ylabel("Down-range y (cm)", fontsize = self.fontsize_mm)
        cax = ax.figure.axes[-1]
        cax.tick_params(labelsize=self.fontsize_mm)
        
        aspect_ratio = (self.end_y - self.start_y)/(self.end_x - self.start_x)
        
        ax.set_box_aspect(aspect_ratio)

        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

        plt.xticks(rotation=0)     # rotate all x-tick labels 90°
        
        plt.savefig(self.imagepath, bbox_inches='tight', pad_inches=0.0)
        
        with open(r"{0}\image_radar_DAS.pkl".format(self.path_results), 'wb') as file: 
              
            # A new file will be created. 
            pickle.dump(image_matrix_norm, file) 
        
        with open(r'{0}\Settings_DAS.txt'.format(self.path_results), 'a') as the_file:
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