"""
    This script is used to generate an image based on measured S-parameters. 
"""
#Import of necessary Python libraries.
import numpy as np
import matplotlib.pyplot as plt
import skrf as rf
import seaborn as sns
import os
import pickle
import scipy
from scipy import signal
from scipy.constants import speed_of_light
from scipy import interpolate
import pathlib
from datetime import datetime
from tqdm import tqdm

#Get current directory.
current_dir = os.path.dirname(__file__)

#Specifiy path of the corresponding .s2p files.
filepath = r"{0}\Ideal_Data_VNA".format(current_dir)
# filepath_background = Here, you have to specify your own path. For ideal data, the background subtraction does not make any sense.

#Define frequency range.
f_0 = 6e9
f_1 = 14e9

#General settings of the grid.
number_of_points_x = 401
number_of_points_y = 401
start_x = 0
end_x = 50
start_y = 40
end_y = 90
#Define the offset (cm) of the EM waves due to cables, adapters etc. For ideal data the offset is zero.
offset = 0
#Define if the measurement shall be calibrated. This value must be "False" if ideal data shall be used. 
calibration = False
#Define if windowing shall be used.
windowing = False
#Dynamic range of the image (dB).
dynamic_range = 30
#Define total number of points for the IFFT. 
nPad = 8192 
#Define antenna positions.
antenna_start = 0
antenna_end = 45
number_of_measurements = 46
antenna_positions = np.linspace(antenna_start, antenna_end, number_of_measurements)
antenna_counter = 0
antenna_distance = 10   #Difference between the center positions of TX and RX antenna.
#Define speed of light.
c0 = speed_of_light

#Create empty image matrix.
image_matrix = np.zeros((number_of_points_y, number_of_points_x), dtype = complex)

#Iterate over antenna positions.
for antenna_x in tqdm(antenna_positions, desc="Calculating image", unit="iteration"):

    #Prepare s-parameter.
    net = rf.Network(r"{0}\0.0_{1}.s2p".format(filepath, float(antenna_counter*10)))
    
    if calibration == True:
        
        #Load s-parameter of measurement without a target. 
        net_match = rf.Network(r"{0}\0.0_{1}.s2p".format(filepath_background, float(antenna_counter*10)))
        s21_match = net_match.s[:,1,0]
    
        s21_raw = net.s[:,1,0]-s21_match
        
    if calibration == False:
        s21_raw = net.s[:,1,0]
    
    #Get frequency vector and the relevant frequency points.
    frequency_raw = net.f
    index_0 = np.argmax(frequency_raw >= f_0)
    index_1 = np.argmax(frequency_raw >= f_1)

    S = s21_raw[index_0:index_1+1]
    frequency_desired = frequency_raw[index_0:index_1+1]

    #Extract parameter from frequency vector.
    fBu = frequency_desired[0]     #f_0
    fBo = frequency_desired[len(frequency_desired)-1]    #f_1
    df = frequency_desired[1]-frequency_desired[0]  #Frequency step.
    N = len(frequency_desired)

    #Use window function.
    window = np.kaiser(N, beta = 3.5)
    
    if calibration == True:
        
        #Load error_function.
        with open(r"{0}\Pickle_Files\error_function_VNA.pkl".format(current_dir), 'rb') as file: 
            error_function = pickle.load(file) 
    
        if windowing == True:
    
            Sf = S*window*error_function
         
        if windowing == False:

            Sf = S*error_function
         
    if calibration == False:
        
        if windowing == True:
        
            Sf = S*window
    
        if windowing == False:
        
            Sf = S
    
    #Calculate maximum unambigious range and distance vector.
    Lmax = 0.5*c0/df
    lengthAxis = np.linspace(0, Lmax, nPad, endpoint=True)

    #Fill the spectrum with corresponding number of zeroes on the left side.
    Nu, dum = divmod(fBu, df)
    if dum > 0.01:
        print('Warning: f_0 divided by frequency step is not an integer value.')
    Nu = int(Nu)

    Spad = np.hstack((np.zeros(Nu), Sf))

    #Calculate the IFFT. Attention: It is important that the result of the IFFT is a complex signal. Otherwise the phase information will be lost.
    Stp = np.fft.ifft(Spad, n=nPad)

    #Use distance_VNA and spectrum_VNA to make the rest of the script comparable to the image generation with the FMCW radar system.
    distance_VNA = lengthAxis*2*100-2*offset #In cm. Moreover the offset value is subtracted.
    spectrum_VNA = Stp 
    
    #Prepare grid.
    x_axis = np.linspace(start_x, end_x, number_of_points_x)
    y_axis = np.linspace(start_y, end_y, number_of_points_y)

    x_coordinates, y_coordinates = np.meshgrid(x_axis, y_axis)

    distance_a = np.sqrt((x_coordinates-(antenna_x))**2 + y_coordinates**2+(antenna_distance/2)**2)    #Forward wave.
    
    distance_b = np.sqrt((x_coordinates-(antenna_x))**2 + y_coordinates**2-(antenna_distance/2)**2)    #Backward wave.
    
    distance_image = distance_a + distance_b
    
    #Build interpolator.
    f_abs = interpolate.interp1d(distance_VNA, np.abs((spectrum_VNA)), kind = 'cubic')
    f_angle = interpolate.interp1d(distance_VNA, np.unwrap(np.angle((spectrum_VNA))), kind = 'cubic')
    
    image_matrix_cache_abs = f_abs(distance_image)
    image_matrix_cache_angle = f_angle(distance_image)
    
    image_matrix_cache = image_matrix_cache_abs * np.exp(1j*image_matrix_cache_angle)

    image_matrix = image_matrix + image_matrix_cache
    
    antenna_counter = antenna_counter + 1
 
#Square the result. 
image_matrix = image_matrix**2

#Normalize.
image_matrix_norm = image_matrix/np.max(np.abs(image_matrix))

ax = sns.heatmap(10*np.log10(np.abs(image_matrix_norm)), cbar = True, cmap = 'jet',square = True, vmax = 0, vmin = -dynamic_range, cbar_kws={'label': 'Normalized Intensity (dB)'})   

x_ticks = (np.round(np.linspace(start_x, end_x, int(np.round((np.abs(end_x)+np.abs(start_x))/5,0)+1)),1))
x_ticks_location = np.linspace(0, len(x_axis), int(np.round((np.abs(end_x)+np.abs(start_x))/5,0)+1))

y_ticks = (np.round(np.linspace(start_y, end_y, int(np.round((np.abs(end_y)-np.abs(start_y))/5,0)+1)),1))
y_ticks_location = np.linspace(0, len(y_axis), int(np.round((np.abs(end_y)-np.abs(start_y))/5,0)+1))

#Define fontsize of the image.
fontsize_image = 22.5

ax.invert_yaxis()
cbar_axes = ax.figure.axes[-1]
ax.figure.axes[-1].yaxis.label.set_size(fontsize_image)
plt.xticks(x_ticks_location, x_ticks, fontsize = fontsize_image) 
plt.yticks(y_ticks_location, y_ticks, fontsize = fontsize_image) 
plt.xlabel("x (cm)", fontsize = fontsize_image)
plt.ylabel("y (cm)", fontsize = fontsize_image)
cax = ax.figure.axes[-1]
cax.tick_params(labelsize=fontsize_image)

plt.show()

#Save the result in .pkl-file and create log-file.
date_today = datetime.today().strftime('%Y-%m-%d')
time_today = datetime.today().strftime('%H-%M-%S')

path = pathlib.Path(r'{0}\Pickle_Files\{1}_{2}'.format(current_dir,date_today,time_today))
path.mkdir(parents=True, exist_ok=True)

with open(r"{0}\image_vna.pkl".format(path), 'wb') as file: 
      
    # A new file will be created. 
    pickle.dump(image_matrix_norm, file) 

with open(r'{0}\Settings.txt'.format(path), 'a') as the_file:
    the_file.write('f_0 = {0} GHz\n'.format(f_0/1e9))
    the_file.write('f_1 = {0} GHz\n'.format(f_1/1e9))
    the_file.write('Number of points in FFT = {0}\n'.format(nPad))
    the_file.write('Windowing = {0}\n'.format(windowing))
    the_file.write('Calibration = {0}\n'.format(calibration))
    the_file.write('offset = {0} m\n'.format(offset/100))
    the_file.write('start_x = {0} cm\n'.format(start_x))
    the_file.write('start_y = {0} cm\n'.format(start_y))
    the_file.write('end_x = {0} cm\n'.format(end_x))
    the_file.write('end_y = {0} cm\n'.format(end_y))
    the_file.write('antenna_distance = {0} cm\n'.format(antenna_distance))
    the_file.write('antenna_start = {0} cm\n'.format(antenna_start))
    the_file.write('antenna_end = {0} cm\n'.format(antenna_end))
    the_file.write('Number of points x = {0} \n'.format(number_of_points_x))
    the_file.write('Number of points y = {0} \n'.format(number_of_points_y))

    the_file.write('Filepath: {0}\n'.format(filepath))
