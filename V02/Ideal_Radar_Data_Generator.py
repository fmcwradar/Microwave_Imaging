import numpy as np
import matplotlib.pyplot as plt
import scipy.constants as sc
import csv
import os
import pathlib

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
                        if value.is_integer():
                            value = int(value)
                    except ValueError:
                        pass  # String bleibt String
                config[key] = value
    return config

#Load configuration.
path_config = f"{current_dir}\Radar_Config.txt"
config = load_config(path_config)

#Define targets (x-coordinate, y-coordinate).
targets = [(10,60),(50,70)]

#Define number of points.
points = 1000
#Define bandwidth of the FMCW radar system.
f_0 = config['f0']
f_1 = config['f1']
bandwidth = f_1 - f_0
#Define ramp duration.
T_c = config['T_c']
#Define initial x-position of antenna.
start_antenna = config['antenna_start']
#Define end x-position of antenna.
end_antenna = config['antenna_end']
number_of_measurements = config['number_of_measurements']
#Define increment of antenna.
increment_antenna = (end_antenna - start_antenna)/(number_of_measurements-1)
#Check if necessary folder exists and if not create it.
path = pathlib.Path(r'{0}\Ideal_Data_Radar'.format(current_dir))
path.mkdir(parents=True, exist_ok=True)

time = np.linspace(0, T_c, int(points))

antenna_positions = np.linspace(start_antenna, end_antenna, number_of_measurements)

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
        
        filepath = r"{0}\Ideal_Data_Radar\0.0_{1}.csv".format(current_dir,float(counter*10))
        if os.path.exists(filepath):
            os.remove(filepath)

        with open(filepath, 'w', newline='') as csvfile:
            writer=csv.writer(csvfile, delimiter=',')
            writer.writerows(zip(time, IF_signal_I, IF_signal_Q))

    counter = counter + 1
