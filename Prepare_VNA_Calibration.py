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

def signal_processing_vna(frequency_raw, s21_dut, start_frequency, stop_frequency, nPad, c0):

    #Get the corresponding indices.
    index_0 = np.argmax(frequency_raw >= start_frequency)
    index_1 = np.argmax(frequency_raw >= stop_frequency)

    #Slice S-parameter.
    S = s21_dut[index_0:index_1+1]
    frequency_desired = frequency_raw[index_0:index_1+1]

    #Extract parameter from frequency vector.
    fBu = frequency_desired[0]     #f_0
    fBo = frequency_desired[len(frequency_desired)-1]    #f_1
    df = frequency_desired[1]-frequency_desired[0]  #Frequency step.
    N = len(frequency_desired)

    #Calculate maximum unambigious range and distance vector.
    Lmax = 0.5*c0/df
    lengthAxis = np.linspace(0, Lmax, nPad, endpoint=True)

    #Fill the spectrum with corresponding number of zeroes on the left side.
    Nu, dum = divmod(fBu, df)
    if dum > 0.01:
        print('Warning: f_0 divided by frequency step is not an integer value.')
    Nu = int(Nu)

    Spad = np.hstack((np.zeros(Nu), S))

    #Calculate the IFFT. Attention: It is important that the result of the IFFT is a complex signal. Otherwise the phase information will be lost.
    Stp = np.fft.ifft(Spad, n=nPad)

    #Use distance_VNA and signal_VNA to make the rest of the script comparable to the image generation with the FMCW radar system.
    distance_VNA = lengthAxis 
    signal_VNA = Stp 

    return [distance_VNA, signal_VNA, S]

def signal_processing_vna_cal(frequency_raw, s21_dut, error_function, start_frequency, stop_frequency, nPad, c0):

    #Get the corresponding indices.
    index_0 = np.argmax(frequency_raw >= start_frequency)
    index_1 = np.argmax(frequency_raw >= stop_frequency)

    #Slice S-parameter.
    S = s21_dut[index_0:index_1+1]
    frequency_desired = frequency_raw[index_0:index_1+1]

    #Extract parameter from frequency vector.
    fBu = frequency_desired[0]     #f_0
    fBo = frequency_desired[len(frequency_desired)-1]    #f_1
    df = frequency_desired[1]-frequency_desired[0]  #Frequency step.
    N = len(frequency_desired)

    Sf = S*error_function

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

    #Use distance_VNA and signal_VNA to make the rest of the script comparable to the image generation with the FMCW radar system.
    distance_VNA = lengthAxis 
    signal_VNA = Stp 

    return [distance_VNA, signal_VNA, Sf]

def signal_processing_ideal(frequency_raw, ideal_distance, start_frequency, stop_frequency, nPad, c0):

    #Get the corresponding indices.
    index_0 = np.argmax(frequency_raw >= start_frequency)
    index_1 = np.argmax(frequency_raw >= stop_frequency)

    #Slice S-parameter.
    S = s21_dut[index_0:index_1+1]
    frequency_desired = frequency_raw[index_0:index_1+1]
    
    #Extract parameter from frequency vector.
    fBu = frequency_desired[0]     #f_0
    fBo = frequency_desired[len(frequency_desired)-1]    #f_1
    df = frequency_desired[1]-frequency_desired[0]  #Frequency step.
    N = len(frequency_desired)

    ideal_spectrum = np.exp(-1j*4*np.pi*frequency_desired*ideal_distance/c0)

    #Calculate maximum unambigious range and distance vector.
    Lmax = 0.5*c0/df
    print('Lmax ',Lmax)
    lengthAxis = np.linspace(0, Lmax, nPad, endpoint=True)

    Nu, dum = divmod(fBu, df)
    if dum > 0.01:
        print('Warning: f_0 divided by frequency step is not an integer value.')
    Nu = int(Nu)

    padded_ideal_spectrum = np.hstack((np.zeros(Nu), ideal_spectrum))

    Spad = padded_ideal_spectrum

    #Calculate the IFFT. Attention: It is important that the result of the IFFT is a complex signal. Otherwise the phase information will be lost.
    Stp = np.fft.ifft(Spad, n=nPad)

    #Use distance_VNA and signal_VNA to make the rest of the script comparable to the image generation with the FMCW radar system.
    distance_VNA = lengthAxis #In cm. 
    signal_VNA = Stp 

    return [distance_VNA, signal_VNA, ideal_spectrum]

#Define general settings.
start_frequency = 6e9
stop_frequency = 14e9
nPad = 8192
c0 = speed_of_light

#Get current directory.
current_dir = os.path.dirname(__file__)

#Load style sheet.
plt.style.use(r"{0}\Style_MM.mplstyle".format(current_dir))

#Evaluate measurement of calibration object.

#Load s-parameter of measurement without target.
net = rf.Network(r"C:\Users\Martin\Desktop\Messungen 06-11-2024\Run 3\Leermessung Cal\8.s2p")
s21_absorber = net.s[:,1,0]
#Load s-parameter of metal plate.
net = rf.Network(r"C:\Users\Martin\Desktop\Messungen 06-11-2024\Run 3\Metallplatte_0\8.s2p")
s21_raw = net.s[:,1,0]
#Subtract s-parameter of absorber from metal plate measurement.
s21_dut = s21_raw-s21_absorber
frequency_raw = net.f

output = signal_processing_vna(frequency_raw,s21_dut,start_frequency, stop_frequency, nPad, c0)

distance_vector = output[0]
amplitude = output[1]
spectrum_plate_0 = output[2]

plt.plot(distance_vector, 20*np.log10(np.abs(amplitude)), label = "Uncalibrated Metal 1")
plt.xlabel("Distance (m)")
plt.ylabel("Amplitude (dBV)")
plt.show()


#Generate ideal signal.
ideal_distance = 2.0166 #Define ideal_distance according to the measurement of the metal plate.
output = signal_processing_ideal(frequency_raw,ideal_distance,start_frequency, stop_frequency, nPad, c0)

distance_vector = output[0]
amplitude_ideal = output[1]
spectrum_ideal = output[2]

plt.plot(distance_vector, 20*np.log10(np.abs(amplitude_ideal)), label = "Ideal Signal")
plt.xlabel("Distance (m)")
plt.ylabel("Amplitude (dBV)")
plt.legend(loc = 'best')
plt.show()

#Obtain error_function by dividing the ideal S21 by the measured 21.
error_function = spectrum_ideal/spectrum_plate_0

#Write the error-function into .pickle file.
with open(r"{0}\Pickle Files\error_function_VNA.pkl".format(current_dir), 'wb') as file: 
          
        # A new file will be created 
        pickle.dump(error_function, file) 

#Calibrate an exemplary measurement.

#Load s-parameter of absorber.
net = rf.Network(r"C:\Users\Martin\Desktop\Messungen 06-11-2024\Run 3\Leermessung Cal\13.s2p")
s21_absorber = net.s[:,1,0]
#Load s-parameter of metal plate.
net = rf.Network(r"C:\Users\Martin\Desktop\Messungen 06-11-2024\Run 3\Dual_Target\13.s2p")
s21_raw = net.s[:,1,0]
#Subtract s-parameter of absorber from metal plate measurement.
s21_dut = s21_raw-s21_absorber
frequency_raw = net.f

output = signal_processing_vna_cal(frequency_raw, s21_dut, error_function,start_frequency, stop_frequency, nPad, c0)

distance_vector = output[0]
amplitude_cal = output[1]
spectrum_cal = output[2]

output = signal_processing_vna(frequency_raw, s21_dut,start_frequency, stop_frequency, nPad, c0)

distance_vector = output[0]
amplitude_uncal = output[1]
spectrum_uncal = output[2]

plt.plot(distance_vector, 20*np.log10(np.abs(amplitude_uncal)/np.max(np.abs(amplitude_uncal))), label = "Uncalibrated")
plt.plot(distance_vector, 20*np.log10(np.abs(amplitude_cal)/np.max(np.abs(amplitude_cal))), label = "Calibrated")
plt.xlabel("Distance (m)")
plt.ylabel("Normalized Amplitude (dB)")
plt.legend(loc = 'best')
plt.show()





