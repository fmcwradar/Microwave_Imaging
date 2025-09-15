#This script is used to calculate the error-function that is necessary to compute calibrated images. This script can only be executed with real measurement data.
#Import of necessary Python libraries.
import scipy.constants as sc
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import pickle
import os
import pathlib
#Import of the Radar Measurement Evaluation Modul.
from Radar_Evaluation_Modul import radar_measurement_evaluation
#Get current directory.
current_dir = os.path.dirname(__file__)
#Check if all necessary folders exist and if not create them.
path = pathlib.Path(r'{0}\Pickle_Files'.format(current_dir))
path.mkdir(parents=True, exist_ok=True)
#Path in which the .csv-files are located.
path_csv = r"E:\Messungen_07-03-25"

file_names = ["Oszi_Kalibrierung_60cm_13dB-07-03-25","Oszi_Kalibrierung_64cm_13dB-07-03-25"]      #The first measurement has to be the calibration object (metal plate). The second measurement can be anything.

#Define settings for Radar_Evaluation_Modul.
f0 = 6e9
f1 = 14e9
B = (f1-f0)
T_c = 200*1e-6
c0 = sc.speed_of_light
number_of_ramps = 100
total = 8192
windowing = False   #Has to be "False" for generating the error-function.
ideal = False
swap_IQ = True
calibration = False #Has to be "False" for generating the error-function.
plotting = False
filtering = False    #Has to be "True" for generating the error-function.
fc_low = 350e3
fc_high = 500e3
filterorder = 10
single_measurement = False
distance_offset = 0.935
save_last_measurement = False
background_subtraction = False
hilbert = False
#End of define settings.
new_calibration = True  #Set to "True" if you want to generate a new error-function.
#Load style sheet.
plt.style.use(r"{0}\Style_MM.mplstyle".format(current_dir))
#Write the filter settings into .txt file. This is done to be able to later verify whether the same filter settings are used for the execution of 'Calculate_Radar_Image.py'.
open("{0}\Calibration_Settings.txt".format(current_dir), "a")
f = open("{0}\Calibration_Settings.txt".format(current_dir), "r+")
f.write("1st line: filterorder, 2nd line: fc_low, 3rd line: fc_high")
f.write("\n{0}".format(filterorder))
f.write("\n{0} Hz".format(fc_low))
f.write("\n{0} Hz".format(fc_high))
f.close()

#Iterate over the measurements.
for count, name in enumerate(file_names):
    print(count)
    single_measurement = radar_measurement_evaluation(path_csv,name,B,T_c,c0,number_of_ramps,total,f0,f1,windowing,ideal,swap_IQ,calibration,filtering,fc_low,fc_high,filterorder,distance_offset,save_last_measurement,background_subtraction,hilbert)
    single_measurement.run_radar_evaluation()
    
    if count == 0:
        spectrum_matrix = np.zeros((len(file_names),total), dtype = complex)
        time_domain_matrix = np.zeros((len(file_names),single_measurement.samples_per_ramp), dtype = complex)
    
    time_domain_matrix[count,:] = single_measurement.signal_up
    spectrum_matrix[count,:] = single_measurement.spectrum_raw

distance_corrected = single_measurement.distance_corrected   
frequency_corrected = single_measurement.frequency_corrected      
      
#Plot the IF spectrum of the calibration object.
fig, ax1 = plt.subplots()
ax1.plot(distance_corrected[0:int(total/2)], 20*np.log10(np.abs(spectrum_matrix[0,0:int(total/2)])))
ax2 = ax1.twiny()
ax2.plot(frequency_corrected[0:int(total/2)]/1e3, 20*np.log10(np.abs(spectrum_matrix[0,0:int(total/2)])))
ax1.tick_params(axis='both', which='major')
ax2.tick_params(axis='both', which='major')
ax1.set_xlabel("Distance (m)")
ax2.set_xlabel("Frequency (kHz)")
ax1.set_ylabel("Amplitude (dBV)")
ax1.set_xticks([0,1,2,3,4,5,6,7,8,9])
ax2.set_xticks([0,250,500,750,1000,1250,1500,1750,2000,2250,2500])
plt.show()

#Plot the IF signal of the calibration object.
fig, ax1 = plt.subplots()
ax1.plot(single_measurement.time*1e6, np.real(time_domain_matrix[0,:])*1e3, label = "IF-I")
ax1.plot(single_measurement.time*1e6, np.imag(time_domain_matrix[0,:])*1e3, label = "IF-Q")

ax1.tick_params(axis='both', which='major')
ax1.set_xlabel("Time (µs)")
ax1.set_ylabel("Amplitude (mV)")
ax1.legend(loc = 'best')
plt.show()


#Generate the same filter that was used in the Radar_Evaluation_Modul.
sos = signal.butter(filterorder, [fc_low,fc_high], 'bp', fs=1/single_measurement.timestep, output='sos')

if new_calibration == True:

    #Set ideal IF frequency according to the received signal.
    ideal_IF_frequency = 412e3

    time = np.linspace(0, T_c, single_measurement.samples_per_ramp)

    tau = ideal_IF_frequency*T_c/B

    ideal_signal = signal.sosfiltfilt(sos, np.exp(1j*(2*np.pi*ideal_IF_frequency*time+2*np.pi*f0*tau)))

    #Calibration Metal Plate 1
    error_function = ideal_signal/time_domain_matrix[0,:]

    current_dir = os.path.dirname(__file__)

    filepath = r"{0}\Pickle_Files\error_function_radar.pkl".format(current_dir)
            
    if os.path.exists(filepath):
        os.remove(filepath)

    with open(filepath, 'wb') as file: 
        pickle.dump(error_function, file) 

if new_calibration == False:

    with open(filepath, 'rb') as file: 
                
                # Call load method to deserialze. 
                error_function = pickle.load(file) 

#Calibrate the other measurements and plot the results.
for index in range(1,len(file_names)):

    calibrated_signal = (time_domain_matrix[index,:])*error_function
    
    calibrated_spectrum = np.fft.fft(calibrated_signal, norm = 'forward', n = total)
    calibrated_spectrum_norm = np.abs(calibrated_spectrum)/np.max(np.abs(calibrated_spectrum))
    uncalibrated_spectrum_norm = np.abs(spectrum_matrix[index,:])/np.max(np.abs(spectrum_matrix[index,:]))

    index_maximum = np.argmax(np.abs(uncalibrated_spectrum_norm[0:int(total/2)]))
    
    fig, ax1 = plt.subplots()
    plt.plot(distance_corrected[0:int(total/2)], 20*np.log10(np.abs(uncalibrated_spectrum_norm[0:int(total/2)])), label = "Uncalibrated")
    plt.plot(distance_corrected[0:int(total/2)], 20*np.log10(np.abs(calibrated_spectrum_norm[0:int(total/2)])), label = "Calibrated")
    plt.xlabel("Distance (m)")
    plt.ylabel("Normalized Amplitude (dB)") 
    plt.legend(loc = 'best')
    plt.show()
