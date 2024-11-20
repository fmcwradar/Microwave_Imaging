import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as sc
import csv
import os
import pathlib

#Define targets (x-coordinate, y-coordinate).
targets = [(10,70),(30,60),(20,65)]
#Define number of points.
points = 1000
#Define bandwidth of the FMCW radar system.
bandwidth = 8e9
#Define ramp duration.
T_c = 200e-6
#Define start frequency of the ramp.
f_0 = 6e9
#Define stop frequency of the ramp.
f_1 = 14e9
#Define initial x-position of antenna.
start_antenna = 0
#Define end x-position of antenna.
end_antenna = 45
#Define increment of antenna.
increment_antenna = 1
#Find current folder.
current_dir = os.path.dirname(__file__)
#Check if necessary folder exists and if not create it.
path = pathlib.Path(r'{0}\Ideal Data Radar'.format(current_dir))
path.mkdir(parents=True, exist_ok=True)

time = np.linspace(0, T_c, int(points))

antenna_positions = np.linspace(start_antenna, end_antenna, int((end_antenna-start_antenna)/increment_antenna + 1))

center_frequency = (f_1 - f_0)/2

center_wavelength = sc.speed_of_light/center_frequency

counter = 0

for antenna_location in antenna_positions:

    IF_signal_I = np.zeros(int(points))
    IF_signal_Q = np.zeros(int(points))
    
    for single_target in targets:
    
        distance = (np.sqrt((single_target[0]-antenna_location)**2 + single_target[1]**2))/100
    
        f_IF = (bandwidth/T_c)*2*distance/sc.speed_of_light
        
        phase = 2*np.pi*f_0*2*distance/sc.speed_of_light
        
        IF_signal_I = np.cos(2*np.pi*f_IF*time+phase) + IF_signal_I
        
        IF_signal_Q = np.sin(2*np.pi*f_IF*time+phase) + IF_signal_Q
        
        filepath = r"{0}\Ideal Data Radar\{1}.csv".format(current_dir,counter)
        if os.path.exists(filepath):
            os.remove(filepath)

        with open(r"{0}\Ideal Data Radar\{1}.csv".format(current_dir,counter), 'w', newline='') as csvfile:
            writer=csv.writer(csvfile, delimiter=',')
            writer.writerows(zip(time, IF_signal_I, IF_signal_Q))

    counter = counter + 1
