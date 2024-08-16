# Microwave_Imaging

In this repository you can find python scripts for microwave imaging using a vector network analyzer (VNA) and a frequency modulated continuous wave (FMCW) radar system.

The FMCW radar system is realized with commercially available components. More details can be found in my publications (https://ieeexplore.ieee.org/document/10305102) and (https://ieeexplore.ieee.org/document/10590586).

As a VNA I used the E8361C from Keysight.

For the imaging with the vector network analyzer the delay-and-sum (DAS) beamforming algorithm is implemented. For the FMCW radar system the standard synthetic aperture radar (SAR) approach is used. However, both algorithms are ultimatively just the application of a matched filter.

## Imaging with VNA

To compute an image based on a set of s-parameter measurements it is necessary that you have a folder with the corresponding `.s2p` touchstone files. A separate touchstone file is required for every antenna position. The name of the file indicates the measurement number, e.g. `0.s2p`, `1.s2p`, `2.s2p` and so on. To generate the image, it is necessary to run the script `Imaging_VNA.py`. In the variable 'path' you just have to specfiy the folder with your touchstone files.

## Imaging with FMCW Radar

For the image generation with the FMCW radar system you have to run two files. First, the file `Prepare_Radar_Data.py` and then the file `Imaging_FMCW_Radar.py`.

`Prepare_Radar_Data.py` computes the range FFT of every measurement and combines them in a matrix. This matrix and the corresponding distance vector is saved in two pickle files `spectrum.pkl` and `distance_corrected.pkl`. For this, it is necessary that there is a folder named 'Pickle Files' in the directory. `Imaging_FMCW_Radar.py` then calculates the image based on `spectrum.pkl` and `distance_corrected.pkl`. The input data for `Prepare_Radar_Data.py` are `.csv` files that contain the output data of the radar system that was recorded using an oscilloscope. This includes the time values, the I-part of the IF signal and the Q-part of the IF signal. In the variable 'path' you just have to specfiy the folder with your `.csv` files. The name of the file indicates the measurement number, e.g. `0.csv`, `1.csv`, `2.csv` and so on.

The actual preparation of the radar data is done in `Radar_Evaluation_Modul.py`. This file contains the class 'radar_measurement_evaluation'.

## Documentation
All the signal processing steps that are implemented can be found in the `.pdf` file 'Flow_Chart_Comparison'.

## What else?
If you have any comments feel free to write me an e-mail to m.maier@tu-braunschweig.de.

Exemplary measurement data is unfortunately too large for GitHub. If you are interested you can write me an e-mail and I will provide a Google Drive link where you can find measurement data.

I hope you find my scripts helpful!

