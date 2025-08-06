import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import time
import os

# Imports for VNA
import skrf
from PNA_Class_IHF_new import E8361C

def S2NW(S_Param,FreqPoints):
    """Converts [9,FreqPoints] S-Parameter Array to NW-File from 'skrf' and returns it."""
    print("Converting S-Parameter to NW-File.")
    # stack matrices along 3rd axis to create (2x2xN) array
    S_Param_2x2 = np.array(([S_Param[1,0] + 1j * S_Param[2,0], S_Param[3,0] + 1j * S_Param[4,0]],
                            [S_Param[5,0] + 1j * S_Param[6,0], S_Param[7,0] + 1j * S_Param[8,0]]), dtype='complex')
    for i in range(1, FreqPoints):
        stack = np.array(([S_Param[1,i] + 1j * S_Param[2,i], S_Param[3,i] + 1j * S_Param[4,i]],
                          [S_Param[5,i] + 1j * S_Param[6,i], S_Param[7,i] + 1j * S_Param[8,i]]), dtype='complex')
        S_Param_2x2 = np.dstack((S_Param_2x2, stack))
    # re-shape into (Nx2x2)
    s = np.swapaxes(S_Param_2x2,0,2)
    # create network object with frequency converted to GHz units
    nw = skrf.Network(name='nw_from_numpy',s=s , frequency=S_Param[0], z0=50)
    return(nw)

def Save_Touchstone(self,Filename):
    """Saves Data as S2P-File."""
    self.write_touchstone(Filename, form='dB')
    print(f"File saved as '{Filename}'.")

def save_data_MM(Filename):

    #Save first VNA measurement
    # Cal_File = "MoritzMartinMittwoch.cal"
    ## Define & Connect PNA
    PNA = E8361C()
    # PNA.LoadCalFile(Cal_File)
    FreqPoints = int(PNA.GetNumberOfFreqPoints())
    S_Param = PNA.getSParameterFull2Port(int(FreqPoints)) # Freq Re(S11) Im(S11) Re(S21) Im(S21) ... Im(S22)
    ## Convert S-Parameter into NW-File
    NW = S2NW(S_Param, FreqPoints)
    ## Safe File as .S2P
    Save_Touchstone(NW, Filename)

# ip_address = '169.254.25.75'
# ip_address = '192.168.1.100'
# calitration = True
# VNA = False

# measurement_name = ""

class RTE1054():
    def __init__(self, ipV4) -> None:
        self.instr = None
        self.connected = None
        self.resourceStr = 'TCPIP::' + ipV4
        self.connect()

    def connect(self):
        try:
            rm = visa.ResourceManager()
            self.instr = rm.open_resource(self.resourceStr, timeout=5000)
        except:
            self.instr = None
            print('Error no connection to RTE')

    def query(self, command):
        return (self.instr.query(command))

    def write(self, command):
        self.instr.write(command)

    def start_osci(self, channel):
        self.instr.write('RUN')

    def stop_osci(self, channel):
        self.instr.write('STOP')

    def getWaveform(self, channel):
        # see RTO_UserManual_en p. 426f. (PDF page 442f)
        self.instr.write('FORM:DATA REAL, 32')
        self.instr.write('FORM:BPAT BIN')
        # see RTO_UserManual_en p. 440f. (PDF page 456f)
        return (self.instr.query_binary_values('CHAN' + str(channel) + ':WAV1:DATA?', datatype='f', container=np.array))

    def getChannelHeader(self, channel):
        # see RTO_UserManual_en p. 440f. (PDF page 456f)
        return (self.instr.query('CHAN' + str(channel) + ':DATA:HEAD?'))

    def martin(self, channel):
        # see RTO_UserManual_en p. 440f. (PDF page 456f)
        self.instr.write('FORM:DATA REAL, 32')

class single_measurement():
    def __init__(self, ip_address, storage, measurement_name, calibration, VNA):
        self.ip = ip_address
        self.storage = storage
        self.name = measurement_name
        self.calibration = calibration
        self.VNA = VNA

    def running(self):
        if self.VNA == False:
            print(self.ip)
            osc = RTE1054(self.ip)

            time.sleep(1)

            osc.stop_osci(1)
            Data_1 = osc.getWaveform(1)
            osc.getChannelHeader(1)

            Data_2 = osc.getWaveform(2)

            # Recover Time
            header = osc.getChannelHeader(1)
            start_time = float(header.split(',')[0])
            stop_time = float(header.split(',')[1])
            number_of_points = float(header.split(',')[2])
            time_vector = np.linspace(start_time, stop_time, int(number_of_points))

            osc.stop_osci(1)

            dataset = np.vstack((time_vector, Data_1, Data_2)).T
            print(np.shape(dataset))

            osc.start_osci(1)

            if self.calibration == True:
                # Write Data to .csv File

                filepath = f"{self.storage}\Oszi_{self.name}.csv"
                # filepath = f"C:\\Users\mjsch\Desktop\Measurement Data Cache\\Oszi_{measurement_name}.csv"
                if os.path.exists(filepath):
                    os.remove(filepath)
                    np.savetxt(filepath, dataset, delimiter=",")

                else:
                    np.savetxt(filepath, dataset, delimiter=",")
        else:
            Filename = f"C:\\Users\mjsch\Desktop\Measurement Data Cache\\VNA_{self.name}.s2p"

            if os.path.exists(Filename):
                os.remove(Filename)

            save_data_MM(Filename)

        print(f"{self.name} saved.")