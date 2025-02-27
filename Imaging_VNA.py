"""
    This script is used to generate an image based on measured S-parameters.
"""

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

current_dir = os.path.dirname(__file__)

#Specifiy path of the corresponding .s2p files.
path = r"C:\Users\Martin\Desktop\Messungen 06-11-2024\Run 3\Wasser 1 Run 2"

#General settings of the grid.
number_of_points_x = 401
number_of_points_y = 401
start_x = 0
end_x = 40
start_y = 50
end_y = 90
#Define the offset (cm) of the EM waves due to cables, adapters etc. For ideal data the offset is zero.
offset = 141.3
#Define if the measurement shall be calibrated. This value must "False" if ideal data shall be used. 
calibration = True
#Create empty image matrix.
image_matrix = np.zeros((number_of_points_y, number_of_points_x), dtype = complex)

c0 = speed_of_light

#Define total number of points for the IFFT. 
nPad = 8192 #Zero Padding

#Define antenna positions.
antenna_start = 0
antenna_end = 45
number_of_measurements = 46
antenna_positions = np.linspace(antenna_start, antenna_end, number_of_measurements)
antenna_counter = 0
antenna_distance = 10   #Difference between the center positions of TX and RX antenna.

#Dynamic range of the image (dB).
dynamic_range = 30

#Iterate over antenna positions.
for antenna_x in antenna_positions:

    print(antenna_x)

    #Prepare s-parameter.
    net = rf.Network("{0}\{1}.s2p".format(path, int(antenna_counter)))
    
    if calibration == True:
        
        #Load s-parameter of measurement without a target.
        net_match = rf.Network(r"C:\Users\Martin\Desktop\Messungen 06-11-2024\Run 3\Leermessung Sweep\{0}.s2p".format(int(antenna_counter)))
        s21_match = net_match.s[:,1,0]
    
        s21_raw = net.s[:,1,0]-s21_match
        
    if calibration == False:
        s21_raw = net.s[:,1,0]
    
    #Get frequency vector and the relevant frequency points.
    frequency_raw = net.f
    index_0 = np.argmax(frequency_raw >= 6e9)
    index_1 = np.argmax(frequency_raw >= 14e9)

    S = s21_raw[index_0:index_1+1]
    frequency_desired = frequency_raw[index_0:index_1+1]

    #Extract parameter from frequency vector.
    fBu = frequency_desired[0]     #f_0
    fBo = frequency_desired[len(frequency_desired)-1]    #f_1
    df = frequency_desired[1]-frequency_desired[0]  #Frequency step.
    N = len(frequency_desired)

    print('Frequency Sweep: ', fBu, fBo, df, N)

    #Use window function.
    window = np.kaiser(N, beta = 3.5)
    
    if calibration == True:
        
        #Load error_function.
         with open(r"{0}\Pickle Files\error_function_VNA.pkl".format(current_dir), 'rb') as file: 
            error_function = pickle.load(file) 
    
         Sf = S*window*error_function
         
    if calibration == False:
        Sf = S*window
    
    #Calculate maximum unambigious range and distance vector.
    Lmax = 0.5*c0/df
    print('Lmax ',Lmax)
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
    
    #Prepare Grid
    x_axis = np.linspace(start_x, end_x, number_of_points_x)
    y_axis = np.linspace(start_y, end_y, number_of_points_y)

    x_coordinates, y_coordinates = np.meshgrid(x_axis, y_axis)

    distance_a = np.sqrt((x_coordinates-(end_x-antenna_x+start_x))**2 + y_coordinates**2+(antenna_distance/2)**2)    #Forward wave.
    
    distance_b = np.sqrt((x_coordinates-(end_x-antenna_x+start_x))**2 + y_coordinates**2-(antenna_distance/2)**2)    #Backward wave.
    
    distance_image = distance_a + distance_b
    
    #Build Interpolator.
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

x_ticks = np.flip(np.round(np.linspace(start_x, end_x, int(np.round((np.abs(end_x)+np.abs(start_x))/2,0)+1)),1))
x_ticks_location = np.linspace(0, len(x_axis), int(np.round((np.abs(end_x)+np.abs(start_x))/2,0)+1))

y_ticks = (np.round(np.linspace(start_y, end_y, int(np.round((np.abs(end_y)-np.abs(start_y))/2,0)+1)),1))
y_ticks_location = np.linspace(0, len(y_axis), int(np.round((np.abs(end_y)-np.abs(start_y))/2,0)+1))

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

#Save result in .pkl-file.

#Check if the necessary folder exists and if not creates it.
path = pathlib.Path(r'{0}\Pickle Files'.format(current_dir))
path.mkdir(parents=True, exist_ok=True)

filepath = r'{0}\Pickle Files\final_image_VNA.pkl'.format(current_dir)
        
if os.path.exists(filepath):
    os.remove(filepath)

with open(r'{0}\Pickle Files\final_image_VNA.pkl'.format(current_dir), 'wb') as file: 
      
    # A new file will be created 
    pickle.dump(image_matrix_norm, file) 
