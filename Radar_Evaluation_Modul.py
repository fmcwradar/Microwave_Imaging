from pandas import read_csv
import numpy as np
import csv
import matplotlib.pyplot as plt

class radar_measurement_evaluation:

    def __init__(self,path,name,B,T_c,c,number_of_ramps,total):
        self.path = path
        self.name = name
        self.bandwidth = B
        self.chirp_time = T_c
        self.speed = c
        self.number_of_ramps = number_of_ramps
        self.total = total

    def getdata(self,swap_IQ = True):
    
        #Reads the data from the .csv-file. The .csv-file contains the time, I and Q.
        #If swap_IQ = True then I and Q are swapped.
      
        filepath = str(r"{0}\{1}.csv".format(self.path,self.name))
        columns = ['time','I','Q']
        
        data = read_csv(filepath,names=columns)
        
        time =  np.array(data['time'].tolist())
        Q = np.array(data['I'].tolist())
        I = np.array(data['Q'].tolist())
         
        if swap_IQ == True:
            I = np.array(data['Q'].tolist())
            Q = np.array(data['I'].tolist())   
         
        timestep = np.round(time[1]-time[0],8)

        number_of_points = int(len(I))

        self.I = I
        self.Q = Q
        self.timestep = timestep
        self.number_of_points = number_of_points
        self.samples_per_ramp = (self.chirp_time)/(timestep)
        
    def find_starting_point(self):
    
        #Gets the starting point of the frequency ramp. It is based on the fact, there is a phase jump at the transition from up-ramp to down-ramp.
        
        data_slice = self.I+1j*self.Q
     
        phase_slice = np.unwrap(np.angle(data_slice))
        
        # Im Zweifelsfall Hardcoden des Startpunktes
        
        starting_point_ramp = int(np.argmin(phase_slice[0:2500]))
        
        ramps_in_samples = int(len(data_slice)/2000)-20
        
        offset = 0
        
        lineup = []
        
        for ramp_index in range(0, ramps_in_samples):
                
            potential_start = starting_point_ramp + 2000*ramp_index + offset 
            
            if phase_slice[potential_start] < phase_slice[potential_start-1] and phase_slice[potential_start] < phase_slice[potential_start+1]:
            
                lineup.append(potential_start)
                
            else:
                
                offset = offset - 1

        self.lineup = lineup
        
        
    def collect_ramp_data(self): 
              
        #This function collects the data of the up-ramp and the down-ramp and writes it into the corresponding data matrices (data_matrix_up and data_matrix_down).
        #The dimensions of data_matrix_up and data_matrix_down are (samples_per_ramp, number_of_ramps).     
        lineup = self.lineup
        I = self.I
        Q = self.Q 
        number_of_ramps = self.number_of_ramps
        samples_per_ramp = int(self.samples_per_ramp) + 1
        timestep = self.timestep
        S = self.bandwidth/self.chirp_time
        c = self.speed
        
        #Define Data Matrix for Sampling of Up-Ramp and Down-Ramp
        data_matrix_down = np.zeros((number_of_ramps,samples_per_ramp), dtype = complex)
        
        #Calculate new Frequency Axis
        time = np.linspace(0, timestep*samples_per_ramp,samples_per_ramp)
        N = int(len(time))
        dt = float(time[1] - time[0])
        fa = (1/dt) # scan frequency
        X = np.linspace(0, fa, N, endpoint=True)
        distance = X*c/(2*S)
        frequency = X/1e3
        
        #Prepare for Collect Data from Down-Ramp
        counter = 1
        
        start = lineup[0]   #Starting point is at the transition from down-ramp to up-ramp. This why you have to "jump" one ramp forward to start with the negative slope.
        stop = start + samples_per_ramp
        
        #Collect Data from Down-Ramp
        for counter in range(1,number_of_ramps+1):
            
            
            
            ramp_data_down = I[start:stop] + 1j*Q[start:stop] #A down-ramp will translate into I - 1j*Q.
            
            #Write Ramp Data into Corresponding Matrix Row
            data_matrix_down[counter-1,:] = ramp_data_down
            
            
            if counter == 200 and self.name == "0":
            
                plt.plot(I)
                plt.plot(Q)
                x_axis_cut = np.arange(start, stop)
                plt.plot(x_axis_cut, Q[start:stop])
                plt.show()
            
            
            #Change Start and Stop Values for next Ramp
            counter = counter + 1
            start = lineup[counter-1]   #Starting point is at the transition from down-ramp to up-ramp. This why you have to "jump" one ramp forward to start with the negative slope.
            stop = start + samples_per_ramp
        
        self.matrix_down = data_matrix_down
        self.distance = distance
        self.N = N

    def average_data(self,windowing = True):
    
        #This function is used for averaging of the sampled data.
    
        data_matrix_down = self.matrix_down
        T_c = self.chirp_time
        samples_per_ramp = self.samples_per_ramp + 1

        time = np.linspace(0, T_c, int(samples_per_ramp))
        fs = 1/(time[1]-time[0])
        frequency = np.linspace(0, fs, int(len(time)))

        #Calculate Average of Down-Ramp Data
        mean_value_down_raw = (np.mean(data_matrix_down, axis = 0))

        from scipy import signal

        if windowing == True:
            mean_value_down_final = mean_value_down_raw*np.kaiser(1001, beta = 3.5)

        if windowing == False:
            mean_value_down_final = mean_value_down_raw

        total_N = self.total

        #Calculate the IF Spectrum
        
        distance_corrected = np.linspace(self.distance[0], self.distance[len(self.distance)-1], total_N)
        
        distance_step = distance_corrected[2]-distance_corrected[1]
              
        compensation_term = 2*np.pi*6e9*(2*distance_corrected)/299792458

        zeroes_right = np.zeros(int(total_N - samples_per_ramp))
        
        padded_signal = np.hstack((mean_value_down_final, zeroes_right))

        spectrum_down = np.fft.fft(padded_signal, norm = 'forward')
        
        spectrum_down_corr = spectrum_down*np.exp(-1j*compensation_term)
        
        self.signal_down = mean_value_down_final
        self.spectrum_down = spectrum_down_corr
        self.frequency = frequency
        self.distance_corrected = distance_corrected

    def run_radar_evaluation(self):
    
        self.getdata(swap_IQ = True)
        self.find_starting_point()  
        self.collect_ramp_data()
        self.average_data(windowing = True)
