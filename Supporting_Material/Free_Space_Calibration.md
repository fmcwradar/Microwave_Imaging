# Free-Space Calibration

In the journal paper, the free-space calibration of the radar system and the VNA is explained. Here, I would like to show a few more examples that illustrate the effects of the free-space calibration, which were not included in the journal paper.

In the image below, the uncalibrated and calibrated range FFT of a metal plate at a distance of 65 cm is shown. It is evident that due to calibration, the main lobe beomes narrower and the spectral leakage is reduced. After calibration, the side-lobe level is approximately 13 dB, as one would expect for a rectangular window.

![Calibrated_Spectrum](https://github.com/user-attachments/assets/264aaa28-84dd-47af-98d1-50925bc728bb)

The mentioned effects can also be found in the computed images. The next image shows the comparison between an uncalibrated and a calibrated radar image of a metal plate with dimensions of 10 cm x 10 cm. 

![Metal_Plate](https://github.com/user-attachments/assets/510aa8a6-04f3-4fcf-a061-2883294d223d)

It can be seen that the actual radar echo of the metal plate is narrower in the calibrated image and the apparent echoes behind the plate - due to spectral leakage - have been significantly reduced.



