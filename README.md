# Radar_Signal_Processing

In this repository you can find python scripts for microwave imaging using a vector network analyzer (VNA) and a frequency modulated continuous wave (FMCW) radar system.

For the imaging with the vector network analyzer the delay-and-sum (DAS) beamforming algorithm is implemented. For the FMCW radar system the standard synthetic aperture radar (SAR) approach is used. However, both algorithms are ultimatively just the application of a matched filter.

## Imaging with VNA

To compute an image based on a set of s-parameter measurements it is necessary that you have a folder with the corresponding `.s2p` touchstone files.

## Imaging with FMCW Radar

The example shows the fitting of 3-port s-parameters of an RF inductor with center tap. The s-parameters are imported directly from the `s3p` touchstone file.
