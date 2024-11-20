import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as sc
import csv
import os
import skrf as rf
from skrf import Frequency
from skrf.constants import to_meters
from skrf.media import MLine, RectangularWaveguide
import pathlib

#Define targets (x-coordinate, y-coordinate).
targets = [(20,60)]
#Define number of points.
points = 801
#Define start frequency.
f_0 = 6e9
#Define stop frequency.
f_1 = 14e9
#Define initial x-position of antenna.
start_antenna = 0
#Define end x-position of antenna.
end_antenna = 45
#Define increment of antenna.
increment_antenna = 1
#Find current folder.
current_dir = os.path.dirname(__file__)
#Create frequency vector.
frequency_vector = Frequency(f_0,f_1,points,'Hz')
#Create substrate from parameters.
mlin  =  MLine(frequency_vector,w = 0.2e-3,h = 100e-6,t = 18e-6,ep_r = 3.66,rho = 1.68e-08)
#Determine phase velocity.
v_p = np.real(mlin.v_p)
antenna_positions = np.linspace(start_antenna, end_antenna, int((end_antenna-start_antenna)/increment_antenna + 1))
#Check if necessary folder exists and if not create it.
path = pathlib.Path(r'{0}\Ideal Data VNA'.format(current_dir))
path.mkdir(parents=True, exist_ok=True)



counter = 0

for antenna_location in antenna_positions:

    target_counter = 0

    for single_target in targets:
    
        if target_counter == 0:
    
            length = 2*(np.sqrt((single_target[0]-antenna_location)**2 + single_target[1]**2))/100
            
            length = length/(sc.speed_of_light/v_p)
            
            #Create the transmission line network.
            mlin_length = mlin.line(length, unit = 'm')
        
        if target_counter != 0:
        
            length = 2*(np.sqrt((single_target[0]-antenna_location)**2 + single_target[1]**2))/100
            
            length = length/(sc.speed_of_light/v_p)
            
            #Create the transmission line network.
            mlin_length = mlin.line(length, unit = 'm') + mlin_length
        
        target_counter = target_counter + 1
        
    mlin_length.write_touchstone(r"{0}\Ideal Data VNA\{1}.s2p".format(current_dir,counter), r_ref = 50)
        
    counter = counter + 1
