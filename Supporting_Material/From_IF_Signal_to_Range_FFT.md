Here, I want to explain how to obtain the range FFT based on the measured IF signal.

The mixer on the transceiver PCB is the HMC8191 by Analog Devices, which is an I/Q mixer. The in-phase (I) and quadrature (Q) components are sampled with an oscilloscope. The start frequency of the ramp is 6 GHz and the stop frequency is 14 GHz. The ramp duration is set to 200 µs. In the image below, an exemplary measured IF signal is shown. It is immediately apparent that the signal repeats every 400 µs. This is due to the configuration of the phase-locked loop (PLL). It generates a triangular signal. This means that up and down ramps are generated alternately.

![Time_Large](https://github.com/user-attachments/assets/bc124680-d291-40a3-bdf0-1889387b5a60)
