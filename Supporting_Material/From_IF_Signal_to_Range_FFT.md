# From the IF Signal to the Range FFT

Here, I want to explain how to obtain the range FFT based on the measured IF signal.

The mixer on the transceiver PCB is the HMC8191 by Analog Devices, which is an I/Q mixer. The in-phase (I) and quadrature (Q) components are sampled with an oscilloscope. The start frequency of the ramp is 6 GHz and the stop frequency is 14 GHz. The ramp duration is set to 200 µs. In the image below, an exemplary measured IF signal is shown. It is immediately apparent that the signal repeats every 400 µs. This is due to the configuration of the phase-locked loop (PLL). It generates a triangular signal. This means that up and down ramps are generated alternately.

![Time_Large](https://github.com/user-attachments/assets/bc124680-d291-40a3-bdf0-1889387b5a60)

For signal processing, either the up or down ramp must be used. Additionally, it is possible to average the measurements of multiple ramps to reduce noise. The next image shows the IF signal of an up ramp. It can be seen that the amplitude at the beginning of the ramp is significantly higher than at the end. This is related to the hardware, which is described in detail in the related papers.

![Time_Small](https://github.com/user-attachments/assets/f8210b89-09b1-473a-af36-e99e1d003d18)

Once the IF signal is available in this form, calculating the fast-Fourier transform (FFT) yields the range FFT. Normally, it is interesting to look at the amplitude vs. frequency plot of the FFT, which is shown in the next image.

![Spectrum_IF](https://github.com/user-attachments/assets/64b7fbfe-ad3a-401d-ab40-3e90069d70e2)

For an FMCW radar system, this can be modified into the amplitude vs. distance plot.

![Spectrum_Distance](https://github.com/user-attachments/assets/9cbb493d-d625-4737-9e74-fe2639990f3c)

The images show two measurements: one without a target, where the antennas are placed in front of an absorbing wall, and one with a large metal plate at a distance of approximately 60 cm in front of the antennas. It can be seen that both measurements result in a peak at 0 Hz or 0 m and at approximately 250 kHz or 95 cm. The peak at 0 Hz is caused by the DC offset, and the peak at 250 kHz is due to coupling between the transmitting and receiving antenna. This raises the question of why the coupling between antennas appears as an echo at 95 cm. This is because the cables connecting the transceiver with the antennas also contribute to the effectively measured distance. When calculating the offset distance, the permittivity of the cable must also be considered. In my measurements, I usually place a metal plate at a certain distance in front of the antennas. Then I measure the distance with a laser and adjust the offset distance so that the distance measured by the radar system corresponds to the laser measurement.
