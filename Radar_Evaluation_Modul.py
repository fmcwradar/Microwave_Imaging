from pandas import read_csv
import numpy as np
import csv
import matplotlib.pyplot as plt
from scipy import signal
import pickle
import os

class radar_measurement_evaluation:

    """
    Class that prepares the sampled IF (I,Q) data of an FMCW radar system for the image generation.
    
    INPUTS:
        path: (str) path of the folder that contains the .csv files.
        name: (str) file name of the .csv file that belongs to the measurement that shall be evaluated.
        bandwidth: (float) bandwidth of the FMCW radar system (Hz).
        chirp_time: (float) ramp duration (s).
        speed: (float) propagation velocity of the electromagnetic waves (m/s).
        number_of_ramps: (int) number of ramps that shall be evaluated.
        f0: (float) start frequency of the ramp (Hz).
        f1: (float) stop frequency of the ramp (Hz).
        windowing: (bool) set to "True" if windowing shall be used.
        ideal: (bool) set to "True" if ideal data generated with "Ideal_Radar_Data_Generator.py" is used.
        swap_IQ: (bool) set to "True" if IF-I is sampled with channel 2 of the oscilloscope and IF-Q with channel 1.
        calibration: (bool) set to "True" if the free space calibration shall be applied. For ideal data this has to be set to "False".
        plotting: (bool) set to "True" if plots of intermediate results shall be saved.
        filtering: (bool) set to "True" if a digital band-pass filter shall be applied.
        fc_low: (float) lower cut-off frequency of the band-pass filter.
        fc_high: (float) upper cut-off frequency of the band-pass filter.
        filterorder: (int) filteroder of the the band-pass filter.
    """
    
    def __init__(self,path_csv,name,B,T_c,c0,number_of_ramps,total,f0,f1,windowing,ideal,swap_IQ,calibration,plotting,filtering,fc_low,fc_high,filterorder):
        self.path = path_csv
        self.name = name
        self.bandwidth = B
        self.chirp_time = T_c
        self.speed = c0
        self.number_of_ramps = number_of_ramps
        self.total = total
        self.f0 = f0
        self.f1 = f1
        self.windowing = windowing
        self.ideal = ideal
        self.swap_IQ = swap_IQ
        self.calibration = calibration
        self.plotting = plotting
        self.filtering = filtering
        self.fc_low = fc_low
        self.fc_high = fc_high
        self.filterorder = filterorder
        
        if self.ideal == True:
            self.number_of_ramps = 1

    def getdata(self):
        #This function reads the data from the .csv-file. The .csv-file contains the time, I and Q.  
        filepath = str(r"{0}\{1}.csv".format(self.path,self.name))
        columns = ['time','I','Q']
        
        data = read_csv(filepath,names=columns)
        
        time =  np.array(data['time'].tolist())
        self.I = np.array(data['I'].tolist())
        self.Q = np.array(data['Q'].tolist())
         
        if self.swap_IQ == True:
            self.I,self.Q = self.Q,self.I
         
        timestep = np.round(np.mean(np.diff(time)),12)
        
        number_of_points = len(self.I)

        self.timestep = timestep
        self.number_of_points = number_of_points
        self.samples_per_ramp = int((self.chirp_time)/(timestep))
                
    def find_starting_point(self):
        #This function determines the starting points of the up-ramps.
        #The ideal is only one ramp so it is not necessary to determine the starting point.
        if self.ideal == True:
            lineup = [0,0]
        
        if self.ideal == False:
        
            data_slice = self.I+1j*self.Q
         
            phase_slice = np.unwrap(np.angle(data_slice))
            
            starting_point_ramp = np.argmin(phase_slice[0:int(2.5*self.samples_per_ramp)])
            
            ramps_in_samples = int(len(data_slice)/(2*self.samples_per_ramp))-1
            
            offset = 0
            
            lineup = []
            
            #This part is necessary because it can happen that the xth ramp does not start at starting_point_ramp+2*samples_per_ramp*x, but at
            #starting_point_ramp+2*samples_per_ramp*x-1. This is why every potential starting point gets checked if there is really a phase jump
            #at the corresponding index. If not then starting_point_ramp is decreased by one.
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
        
        #Calculate frequency vector based on timestep and samples_per_ramp.
        time = np.linspace(0, self.timestep*(self.samples_per_ramp-1),self.samples_per_ramp)
        dt = float(time[1] - time[0])
        fa = (1/dt) # scan frequency
        frequency_vector = np.linspace(0, fa, self.samples_per_ramp, endpoint=True)
        
        self.IF = frequency_vector
        
        #Calculate distance based on the frequency_vector.
        distance = frequency_vector*self.speed/(2*S)
        
        #Prepare for collect data from up-ramp
        counter = 1
        start = self.lineup[0]   
        stop = start + self.samples_per_ramp
        
        #Collect data from up-ramp
        for counter in range(1,self.number_of_ramps+1):
        
            ramp_data_up = self.I[start:stop] + 1j*self.Q[start:stop] 
            
            #Write Ramp Data into Corresponding Matrix Row
            data_matrix_up[counter-1,:] = ramp_data_up
            
            #Change start and stop values for next ramp.
            counter = counter + 1
            start = self.lineup[counter-1]   #Starting point is at the transition from down-ramp to up-ramp. This why you have to "jump" one ramp forward to start with the negative slope.
            stop = start + self.samples_per_ramp
        
        self.time = time
        self.matrix_up = data_matrix_up
        self.distance = distance

    def average_data_calculate_FTT(self):
        #This function is used for averaging of the sampled data and calculating the range FFT. In the final step the range FFT is multiplied with the phase correction term.
        data_matrix_up = self.matrix_up
        #Calculate average of up-ramp data.
        mean_value_up_raw = (np.mean(data_matrix_up, axis = 0))
        
        self.IFsignal = mean_value_up_raw
        
        #Generate Bandpass Filter
        sos = signal.butter(self.filterorder, [self.fc_low,self.fc_high], 'bp', fs=1/self.timestep, output='sos')
        
        if self.filtering == True:
        
            filtered_signal = signal.sosfiltfilt(sos, mean_value_up_raw)
        
        if self.filtering == False:
        
            filtered_signal = mean_value_up_raw
        
        current_dir = os.path.dirname(__file__)
        
        #Check if file exists.
        if self.calibration == "True":
            if os.path.isfile(r"{0}\Pickle Files\error_function_radar.pkl".format(current_dir)) == False:
                print("Error: No calibration file in folder!")
                exit(0)
        
            with open(r"{0}\Pickle Files\error_function_radar.pkl".format(current_dir), 'rb') as file: 
                
                # Call load method to deserialze. 
                error_function = pickle.load(file) 
                
        if self.calibration == True:
        
            if self.windowing == True:
                mean_value_up_final = filtered_signal*np.kaiser(self.samples_per_ramp, beta = 3.5)*error_function

            if self.windowing == False:
                mean_value_up_final = filtered_signal*error_function

        if self.calibration == False:
     
            if self.windowing == True:
                mean_value_up_final = filtered_signal*np.kaiser(self.samples_per_ramp, beta = 3.5)

            if self.windowing == False:
                mean_value_up_final = filtered_signal
    
        #Calculate the IF spectrum.
        distance_corrected = np.linspace(self.distance[0], self.distance[len(self.distance)-1], self.total) #Adjust distance vector to the zero-padding.
        
        frequency_corrected = np.linspace(self.IF[0], self.IF[len(self.IF)-1], self.total) #Adjust frequency vector to the zero-padding.
        
        compensation_term = 2*np.pi*self.f0*(2*distance_corrected)/self.speed

        spectrum_up = np.fft.fft(mean_value_up_final, norm = 'forward', n = self.total)
                
        spectrum_up_corr = spectrum_up*np.exp(-1j*compensation_term)    #Multiply the range FFT with the phase correction term.
        
        self.spectrum_raw = spectrum_up
        self.signal_up = mean_value_up_final
        self.spectrum_up = spectrum_up_corr
        self.distance_corrected = distance_corrected
        self.frequency_corrected = frequency_corrected
        
    def plot_results(self):

        current_dir = os.path.dirname(__file__)

        #Plot IF signal.
        filepath = r'{0}\Results\Plot_IF_Signal\{1}.pdf'.format(current_dir,self.name)
        
        if os.path.exists(filepath):
            os.remove(filepath)
        
        plt.style.use(r"{0}\Style_MM.mplstyle".format(current_dir))
        plt.plot(self.time*1e6, np.real(self.IFsignal)*1000, label = "IF-I")
        plt.plot(self.time*1e6, np.imag(self.IFsignal)*1000, label = "IF-Q")
        plt.legend(loc = 'best')
        plt.xlabel("Time (µs)")
        plt.ylabel("Amplitude (mV)")
        plt.savefig(filepath, format="pdf")
        plt.clf()
        plt.cla()

        #Plot IF-Spectrum.
        filepath = r'{0}\Results\Plot_IF_Spectrum\{1}.pdf'.format(current_dir,self.name)
        
        if os.path.exists(filepath):
            os.remove(filepath)
        
        plt.style.use(r"{0}\Style_MM.mplstyle".format(current_dir))
        
        fig, ax1 = plt.subplots()
        ax1.plot(self.distance_corrected[0:int(self.total/2)], 20*np.log10(np.abs(self.spectrum_raw[0:int(self.total/2)])))
        ax2 = ax1.twiny()
        ax2.plot(self.frequency_corrected[0:int(self.total/2)]/1e3, 20*np.log10(np.abs(self.spectrum_raw[0:int(self.total/2)])))
        ax1.set_xlabel("Distance (m)")
        ax2.set_xlabel("Frequency (kHz)")
        ax1.set_ylabel("Amplitude (dBV)")
        ax1.set_xticks([0,1,2,3,4,5,6,7,8,9])
        ax2.set_xticks([0,500,1000,1500,2000,2500])
        ax1.grid(True) 
        ax2.grid(False) 
        plt.savefig(filepath, format="pdf")
        plt.clf()
        plt.cla()

        plt.close('all')

    def run_radar_evaluation(self):
    
        self.getdata()
        self.find_starting_point()  
        self.collect_ramp_data()
        self.average_data_calculate_FTT()
        
        if self.plotting == True:
            self.plot_results()