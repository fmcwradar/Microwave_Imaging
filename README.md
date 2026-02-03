# Microwave_Imaging

![Animated_Measurement](https://github.com/user-attachments/assets/8cbfbf93-13f0-43df-b8c3-7f84ccdb4dc9)

In this repository, you can find python scripts for microwave imaging using a vector network analyzer (VNA) and a frequency-modulated continuous wave (FMCW) radar system operating in the frequency range from 6 - 14 GHz.

The FMCW radar system is realized with off-the-shelf components. More details can be found in my publications (https://ieeexplore.ieee.org/document/10305102) and (https://ieeexplore.ieee.org/document/10590586).

As a VNA I used the E8361C from Keysight.

For both the FMCW radar and the VNA, delay-and-sum (DAS) beamforming is implemented which correponds to the application of a matched filter. Much more details are presented in my journal paper, which is available as open access on IEEE Xplore (https://ieeexplore.ieee.org/document/10931040).

## General Information

Right now, there are two different version: V01 and V02. The version V01 was used for the comparison of imaging with a VNA and the FMCW radar system. For this purpose, I have developed the two classes "radar_measurement_evaluation" and "radar_imaging". The user has to define the settings in the script `Calculate_Radar_Image.py` and `Calculate_VNA_Image.py` by hand.

In the version V02, I expanded the FMCW part of V01 into a Python package called "RSP_Toolbox_MM". It contains the classes "prepare_radar_measurement" and "DAS_imaging". The settings are defined by a file containing the configurations called `Radar_Config.txt`. 

# V02

For the image generation with the FMCW radar system, you have to run the file `Calculate_Radar_Image.py`. The input data for `Calculate_Radar_Image.py` are `.csv` files that contain the output data of the radar system that was recorded using an oscilloscope. This includes the time values, the I-part of the IF signal and the Q-part of the IF signal. In the variable 'path' you just have to specfiy the folder with your `.csv` files. The name of the file indicates the measurement position in mm, e.g. `0.0_0.0.csv`, `0.0_10.0.csv`, `0.0_20.0.csv` and so on.

After the calculation of the image is completed, a subfolder is created in the "Pickle_Files" directory. The name of the subfolder is the date and time when the image was completed. This folder contains the final images a pickle files. Additionally, there is a logfile in which all the used settings are stored. The images is also saved as .png. The path of the image is specified in `Calculate_Radar_Image.py`. 

The script `Calculate_Radar_Image.py` supports multiprocessing. 

# V01

## Imaging with VNA

To compute an image based on a set of s-parameter measurements, it is necessary that you have a folder with the corresponding `.s2p` touchstone files. A separate touchstone file is required for every antenna position. The name of the file indicates the measurement position in mm, e.g. `0.0_0.0.s2p`, `0.0_10.0.s2p`, `0.0_20.0.s2p` and so on. To generate the image, it is necessary to run the script `Calculate_VNA_Image.py`. In the variable 'path' you just have to specfiy the folder with your touchstone files. After the calculation of the image is completed, a subfolder is created in the "Pickle_Files" directory. The name of the subfolder is the date and time when the image was completed. The final image is saved in this folder as a pickle file. Additionally, there is a logfile in which all the used settings are stored.

## Imaging with FMCW Radar

For the image generation with the FMCW radar system you have to run the file `Calculate_Radar_Image.py`. The input data for `Calculate_Radar_Image.py` are `.csv` files that contain the output data of the radar system that was recorded using an oscilloscope. This includes the time values, the I-part of the IF signal and the Q-part of the IF signal. In the variable 'path' you just have to specfiy the folder with your `.csv` files. The name of the file indicates the measurement position in mm, e.g. `0.0_0.0.csv`, `0.0_10.0.csv`, `0.0_20.0.csv` and so on.

After the calculation of the image is completed, a subfolder is created in the "Pickle_Files" directory. The name of the subfolder is the date and time when the image was completed. The final image is saved in this folder as a pickle file. Additionally, there is a logfile in which all the used settings are stored.

## Animation of FMCW Radar Imaging

There is also the possibility to generate fancy animations of the radar image like the one above. To do this, you must first execute `Calculate_Radar_Image_Animated.py` and then `Generate_GIF_File.py`.

## Calibration

The script `Calculate_Error_Function_Radar.py` is used to calculate the error-function for the FMCW radar system. For ideal data the calibration is useless, since there are no errors that need to be corrected.

# Getting started
VO1 contains two scripts (`Ideal_VNA_Data_Generator.py` and `Ideal_Radar_Data_Generator.py`) for the generation of ideal VNA and radar data. The ideal data is saved in the folders 'Ideal_Data_VNA' and 'Ideal_Data_Radar'. If these folders do not already exist they will be created automatically. The default settings are chosen so that you simply have to download the entire repository. Then you have to execute `Ideal_VNA_Data_Generator.py` and `Imaging_VNA.py` to get a VNA image. To generate a radar image, the correct order is `Ideal_Radar_Data_Generator.py` and  `Calculate_Radar_Image.py`.

For the generation of the ideal data, the user has to specify an array of (x,y)-coordinates. To compute the ideal FMCW radar signals, the corresponding IF frequency and phase shift based on the ideal signal model is calculated. For the ideal VNA data, a set of microstrip lines with the corresponding lengths is simulated using the `scikit-rf` package.

V02 also contains `Ideal_Radar_Data_Generator.py` that is controlled by the configuration file.

# What else?
In the folder `Supporting_Material` you can find some more information about the details of the signal processing.

If you have any comments feel free to write me an e-mail to m.maier@tu-braunschweig.de.

Exemplary measurement data is unfortunately too large for GitHub. If you are interested you can contact me and I will provide a Google Drive link where you can find measurement data.

I hope you find my scripts helpful!

