import os
import pickle 
import numpy as np

def load_data(use_test_data,increment,current_dir):
    
    if use_test_data == 0:

        # Open the file in binary mode.
        with open(r'{0}\Pickle Files\spectrum.pkl'.format(current_dir), 'rb') as file: 
            
            # Call load method to deserialze. 
            spectrum_difference_array_down = pickle.load(file) 
            
        with open(r'{0}\Pickle Files\distance.pkl'.format(current_dir), 'rb') as file: 
            
            # Call load method to deserialize. 
            distance = pickle.load(file) 
            
    return [distance, spectrum_difference_array_down]
