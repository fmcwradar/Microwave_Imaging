from pandas import read_csv
import numpy as np
import csv
import matplotlib.pyplot as plt

class radar_measurement_evaluation:

     """
    Class that performs transient analysis of the dynamical system, defined by the 
    blocks and connecions. It manages all the blocks and connections and the timestep update.

    The global system equation is evaluated by fixed point iteration, so the information from 
    each timestep gets distributed within the entire system and is available for all blocks at 
    all times.

    The minimum number of fixed-point iterations 'iterations_min' is set to 'None' by default 
    and then the length of the longest internal signal path (with passthrough) is used as the 
    estimate for minimum number of iterations needed for the information to reach all instant 
    time blocks in each timestep. Dont change this unless you know that the actual path is 
    shorter or something similar that prohibits instant time information flow. 

    Convergence check for the fixed-point iteration loop with 'tolerance_fpi' is based on 
    relative error to previous iteration and should not be touched.

    Multiple numerical integrators are implemented in the 'pathsim.solvers' module. 
    The default solver is a fixed timestep 2nd order Strong Stability Preserving Runge Kutta 
    (SSPRK22) method which is quite fast and has ok accuracy, especially if you are forced to 
    take small steps to cover the behaviour of forcing functions. Adaptive timestepping and 
    implicit integrators are also available.
    
    INPUTS:
        blocks         : (list of 'Block' objects) blocks that make up the system
        connections    : (list of 'Connection' objects) connections that connect the blocks
        dt             : (float) transient simulation timestep
        dt_min         : (float) lower bound for timestep, default '0.0'
        dt_max         : (float) upper bound for timestep, default 'None'
        Solver         : ('Solver' class) solver for numerical integration from pathsim.solvers
        tolerance_fpi  : (float) relative tolerance for convergence of fixed-point iterations
        tolerance_lte  : (float) absolute tolerance for local truncation error (integrator error controller)
        iterations_min : (int) minimum number of fixed-point iterations for system function evaluation
        iterations_max : (int) maximum allowed number of fixed-point iterations for system function evaluation
        log            : (bool, string) flag to enable logging (alternatively a path can be specified)
    """
    
    def __init__(self,path,name,B,T_c,c0,number_of_ramps,total,f0,f1,windowing):
        self.path = path
        self.name = name
        self.bandwidth = B
        self.chirp_time = T_c
        self.speed = c0
        self.number_of_ramps = number_of_ramps
        self.total = total
        self.f0 = f0
        self.f1 = f1
        self.windowing = windowing

    def getdata(self,swap_IQ = True):
        #This function reads the data from the .csv-file. The .csv-file contains the time, I and Q.
        #If swap_IQ = True then I and Q are swapped. This is necessary if IF-I is connected to channel 2 of the oscilloscope and IF-Q to channel 1.
        
        filepath = str(r"{0}\{1}.csv".format(self.path,self.name))
        columns = ['time','I','Q']
        
        data = read_csv(filepath,names=columns)
        
        time =  np.array(data['time'].tolist())
        I = np.array(data['I'].tolist())
        Q = np.array(data['Q'].tolist())
         
        if swap_IQ == True:
            I,Q = Q,I
         
        timestep = np.round(np.mean(np.diff(time)),12)
        
        number_of_points = len(I)

        self.I = I
        self.Q = Q
        self.timestep = timestep
        self.number_of_points = number_of_points
        self.samples_per_ramp = int((self.chirp_time)/(timestep))
        
         
    def find_starting_point(self):
        #This function determines the starting points of the up-ramps.
        
        data_slice = self.I+1j*self.Q
     
        phase_slice = np.unwrap(np.angle(data_slice))
        
        starting_point_ramp = np.argmin(phase_slice[0:int(2.5*self.samples_per_ramp)])
        
        ramps_in_samples = int(len(data_slice)/(int(2*self.samples_per_ramp)))-20
        
        offset = 0
        
        lineup = []
             
        for ramp_index in range(0, ramps_in_samples):
                
            potential_start = int(starting_point_ramp + (2*self.samples_per_ramp)*ramp_index + offset)
            
            if phase_slice[potential_start] < phase_slice[potential_start-1] and phase_slice[potential_start] < phase_slice[potential_start+1]:
                
                lineup.append(potential_start)
                
            else:
                
                offset = offset - 1

        self.lineup = lineup
        
    def collect_ramp_data(self):  
        #This function collects the data of the up-ramp and writes it into the matrix data_matrix_up.
        #The dimensions of data_matrix_up are (samples_per_ramp, number_of_ramps).     
        S = self.bandwidth/self.chirp_time
        
        #Define data matrix for collecting data of up-ramp.
        data_matrix_up = np.zeros((self.number_of_ramps,self.samples_per_ramp), dtype = complex)
        
        #Calculate new frequency axis
        time = np.linspace(0, self.timestep*(self.samples_per_ramp-1),self.samples_per_ramp)
            
        N = int(len(time))
        dt = float(time[1] - time[0])
        fa = (1/dt) # scan frequency
        X = np.linspace(0, fa, N, endpoint=True)
        distance = X*self.speed/(2*S)
        frequency = X/1e3
        
        #Prepare for collect data from up-ramp
        counter = 1
        start = self.lineup[0]   
        stop = start + self.samples_per_ramp
        
        #Collect data from up-ramp
        for counter in range(1,self.number_of_ramps+1):
        
            ramp_data_up = self.I[start:stop] + 1j*self.Q [start:stop] #A down-ramp will translate into I - 1j*Q.
            
            #Write Ramp Data into Corresponding Matrix Row
            data_matrix_up[counter-1,:] = ramp_data_up
            
            #Change start and stop values for next ramp.
            counter = counter + 1
            start = self.lineup[counter-1]   #Starting point is at the transition from down-ramp to up-ramp. This why you have to "jump" one ramp forward to start with the negative slope.
            stop = start + self.samples_per_ramp
        
        self.matrix_up = data_matrix_up
        self.distance = distance
        self.N = N

    def average_data_calculate_FTT(self):
        #This function is used for averaging of the sampled data and calculating the range FFT. Finally the range FFT is multiplied with the phase correction term.
        data_matrix_up = self.matrix_up
        #Calculate average of up-ramp data.
        mean_value_up_raw = (np.mean(data_matrix_up, axis = 0))

        from scipy import signal

        if self.windowing == True:
            mean_value_up_final = mean_value_up_raw*np.kaiser(self.samples_per_ramp, beta = 3.5)

        if self.windowing == False:
            mean_value_up_final = mean_value_up_raw

        #Calculate the IF spectrum.
        distance_corrected = np.linspace(self.distance[0], self.distance[len(self.distance)-1], self.total) #Adjust distance vector to the zero-padding.
        
        compensation_term = 2*np.pi*self.f0*(2*distance_corrected)/self.speed

        spectrum_up = np.fft.fft(mean_value_up_final, norm = 'forward', n = self.total)
        
        spectrum_up_corr = spectrum_up*np.exp(-1j*compensation_term)    #Multiply the range FFT with the phase correction term.
        
        self.signal_up = mean_value_up_final
        self.spectrum_up = spectrum_up_corr
        self.distance_corrected = distance_corrected

    def run_radar_evaluation(self):
    
        self.getdata(swap_IQ = True)
        self.find_starting_point()  
        self.collect_ramp_data()
        self.average_data_calculate_FTT()
