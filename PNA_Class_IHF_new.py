############################## H E A D E R 

"""Class for the used PNA. New Functions can be added acording to the needs.

Version: 1.1
Date: 26.11.24
Author: Moritz Landwehr
"""

### Python Libaries
import numpy as np
import pyvisa
import time

############################## G L O B A L   V A R I A B L E S
t_timeout = 5000 # If a Tasks takes longer than timeout [s] some functions will exit

############################## F U N C T I O N S

############################## C L A S S E S
class E8361C:
    """PNA-Class for Agilent E8361C. Contains several functions for communication with the device."""

##########################################################

    def __init__(self, IPv4Address = None):
        """Initializes the instrument for a measurement."""
        self.instr = None
        self.connected = False
        self.resourceStr = 'TCPIP::' + str(IPv4Address)
        self.timeout= 15.0
        self.scpiTimeout = 15.0
        self.usbTimeout = 15.0
        self.socketTimeout = 1.0
        self.scpiWaitAfterRequest = 1

        rm = pyvisa.ResourceManager()

        if IPv4Address == None:
            self.resourceStr = 'USB0::0x0957::0x0118::US43140553::INSTR'   # PNA via USB
            print("- Connecting PNA over USB..")
        else:
            print("- Connecting PNA over LAN..")
        self.Connect()
        print("- PNA Connected.")

##########################################################

    def Cal_SourcePower(self):
        """Performs a Source Power Calibration with R2 as Receiver."""
    def Cal_ReceiverPower(self):
        """Performs a Receiver Power Calibration with on R2. First a Souecer power Calibration has to be done."""

    def Connect(self):
        ### Network analyzer 134.169.79.149 oder 192.168.42.2
        """Connects the object instance to the actual instrument on the specified port."""
        try:
            rm = pyvisa.ResourceManager()
            self.instr = rm.open_resource(self.resourceStr, timeout=5000)
        except:
            self.instr = None
            print('\033[1m' + '\033[91m' + "- Error: Can not establish connection with PNA. Programm will exit. @'Connect'\n" + '\033[0m' + '\x1B[0m')
            exit()

    def Channel_Delete(self,number):
        """Delete channel{number}"""
        self.instr.write(f"SYST:CHAN:DEL {number}")

##########################################################

    def DisplayUpdate(self):
        """Display Upgrade Options , Not working atm."""
        self.instr.write('DISP:UPD:IMM')  
        self.instr.write('DISP:ENAB ON')  
        self.instr.write('DISP:VIS ON')  

###########################################################

    def FOM_Set(self,channel,coupled,sweep,f_start,f_stop,f_multiplier):
        """
        Set specific parameters for FOM

        # 1 Primary 
        # 2 Source 
        # 3 Receiver
        
        # CW - Also specify CW frequency
        # LINear - Also specify frequency Start/Stop or Center/Span
        # LOG -  Also specify frequency Start/Stop or Center/Span
        # PHASe - See all Phase sweep settings
        # POWer -  Also specify power Start/Stop or Center/Span
        # SEGMent - Also specify segment sweep settings
        """
            
        # Mode - Coupled (1) and Un-coupled (0)
        self.instr.write(f'SENSe:FOM:RANGe{channel}:COUPled {coupled}')  	 

        # Settings
        if coupled == "0":       
            self.instr.write(f'SENSe:FOM:RANGe{channel}:FREQuency:STARt {f_start}')  
            self.instr.write(f'SENSe:FOM:RANGe{channel}:FREQuency:STOP {f_stop}')  
            self.instr.write(f'SENSe:FOM:RANGe{channel}:SWEep:TYPE {sweep}')
        else:
            self.instr.write(f'SENSe:FOM:RANGe{channel}:FREQ:MULT {f_multiplier}')   	
        print(f"- Applied FOM Settings to Channel {channel}: '{f_start}' - '{f_stop}' x {f_multiplier}.")
    def FOM_Setup(self, f_start, f_stop, status : int, annotation:str="Receivers"):
        """Set general Parameters for FOM."""
        # Primary Frequency
        self.instr.write(f'SENSe:FOM:RANGe1:FREQuency:STARt {f_start}')  
        self.instr.write(f'SENSe:FOM:RANGe1:FREQuency:STOP {f_stop}')  
        # Annotation - Primary, Source, and Receivers 
        self.instr.write(f'SENS:FOM:DISPlay:SELect "{annotation}"') 	           	
        # Frequency Offset... 	Frequency Offset (ON/OFF) (1/0)       
        self.instr.write(f'SENS:FOM {status}') 
        print(f"- FOM Status: '{status}'.")

###########################################################
    
    def Data_Trace(self,NumOfPoints, Trace1:str = 'A,1', Trace2:str = 'B,2'):
        self.instr.write("CALC4:PAR:SDEF 'Ch4Tr1', 'S11'") 
        print("Done.")
    def Data_FullSParameter(self,NumOfPoints):    
        """Captures all 2 Port S-Parameter."""
        if  self.instr.query('CALC:PAR:SEL?')[1:-2] != 'Test':
            self.instr.write('CALC:PAR:DEL Test')
            self.instr.write('CALC:PAR:DEF Test, S21')
            self.instr.write('CALC:PAR:SEL Test')
        
        # Switch PNA to single measurement
        self.Trigger_SetMode('SING')
        print("- Sweeping..")
        time.sleep(5)
        # Wait until Sweep/ Status is complete or Timeout
        start = time.time()
        end = time.time()
        while("+1" in self.instr.query('STAT:QUES:INT:MEAS1:COND?')) and (end-start) <= t_timeout:
        #while(not "+1" in self.instr.query("*OPC?")):
            #print("COND" + self.instr.query('STAT:QUES:INT:MEAS1:COND?'))
            #print("OCP2" + self.instr.query("*OPC?"))
            end = time.time()
            time.sleep(1)
            pass
            
            if (end-start) >= t_timeout:
                #print('\033[1m' + '\033[91m' + "- Error: Sweep Duration Overtime. Programm will exit. @'GetFullSParam'\n" + '\033[0m' + '\x1B[0m')
                #exit()
                print('\033[1m' + '\033[93m' + "- Warning: Sweep Duration Overtime. Maybe wrong S-Parameters have been captured!" + '\033[0m' + '\x1B[0m')
        # Get Data
        #Data = self.instr.query_binary_values('CALC:DATA:SNP:PORTs? "1,2"', datatype= u'd', is_big_endian=True, container=np.ndarray)
        data = self.instr.query_ascii_values('CALC:DATA:SNP:PORTs? "1,2"', container=np.ndarray)  
        data = np.reshape(data,(9,NumOfPoints)) # Data = [Freq Re(S11) Im(S11) Re(S12) Im(S12) ... Im(S22)]
        print("- Captured S-Parameter.")
        return data

############################################################

    def IFBW_Get(self):
        """Returns IF-Bandwidth."""
        return(float(self.instr.query('SENS:BAND?')))
    def IFBW_Set(self,Bandwidth):
        """Set IF-Bandwidth."""
        self.instr.write('SENS:BAND ' + str(Bandwidth))
        print(f"- IF-Bandwidth set to '{Bandwidth}'.")    
    
############################################################

############################################################

############################################################

    def Load_CalFile(self,file):
        """Load Cal-File."""
        try:
            self.instr.write(f'MMEM:LOAD:CORR "{file}"') 
            print("- Calibration File Loaded.")
        except FileNotFoundError:
            print(f"- Error: The file '{file}' does not exist.")
    def Load_ConfigFile(self,Path,Filename):
        """Load CSAR-File from desired path."""
        # the cofiguration file is a .csa file (see: https://rfmw.em.keysight.com/wireless/helpfiles/e5080a/index.htm#programming/gp-ib_command_finder/sense/sweep_scpi.htm#ssty)
        # a csa-file includes Instrument State Information, Cal Set Information and calibration data
        # the csa-file has to be loaded from the PNA's HDD (Path and Filename)
        self.instr.write('MMEM:LOAD:CSAR ' + '"' + Path + Filename + '"')
        self.instr.write('FORM REAL,64')
        self.instr.write('MMEM:STOR:TRAC:FORM:SNP RI')
        time.sleep(2) # wait to apply all configurations to the measurement
    def Load_Preset(self):
        """Load current preset. Default S11, Window1, Trace 1."""
        self.instr.write('SYST:PRES')

###########################################################
   
    def NOF_Set(self,number):
        """Set number of frequency points to desired value"""
        self.instr.write('SENS:SWE:POIN ' + str(number))
        print(f"- Number of Frequency Points set to '{number}'.")
    def NOF_Get(self):
        """Gives back the number of frequency points used"""
        return self.instr.query('SENS:SWE:POIN?')

############################################################

    def Power_GetPower(self):
        """Gives back the used power level."""
        power = self.instr.query('SOUR1:POWer?')
        return(float(power))
    def Power_SetPower(self,level):
        """Set the power level to desired value"""
        # Level in dBm
        if level > 20 or level < -50:
            print("- Powerlevel out of Specification (20-50 dBm).")
        else:
            self.instr.write('SOUR1:POW ' + str(level))
            print(f"- Powerlevel set to {level} dBm.")

############################################################

    def Query(self,Command):
        """Send msg to the instrument and returns its response."""
        return(self.instr.query(Command))

############################################################

    def Ref_SetLVLAuto(self):
        """Setting the Y-reference level automaticly."""
        self.instr.write('DISP:WIND:TRAC:Y:AUTO')
    def Ref_SetLVL(self,level):
        """Setting the Y-reference level to disired value"""
        self.instr.write(f'DISP:WIND:TRAC:Y:RLEV {level}')

############################################################

    def SetSourcePowerMode(self,Port,Mode):
        """Define the ports power."""
        # Mode:
        # 'ON' turn the source of the <Port> on 
        # 'AUTO' for measurements
        match Mode:
            case 'ON':
                match Port:
                    case 1:
                        self.instr.write('SOUR:POW2:MODE OFF')
                        self.instr.write('SOUR:POW1:MODE ON')
                        print("- Port 1 activated.")
                    case 2:
                        self.instr.write('SOUR:POW1:MODE OFF')
                        self.instr.write('SOUR:POW2:MODE ON')
                        print("- Port 2 activated.")
            case 'AUTO':
                        self.instr.write('SOUR:POW1:MODE AUTO')
                        self.instr.write('SOUR:POW2:MODE AUTO')
                        print("- Auto Mode activated.")

    def Sweep_Mode_CW(self,frequency):
        """Set Stimulus-Mode to CW."""
        self.instr.write('SENS:SWEEP:TYPE CW') 
        self.instr.write('SENS:FREQ:CW ' + str(frequency))
        print(f"- Activated CW-Mode @ {frequency} Hz.")
    def Sweep_Mode_Lin(self):
        """Set mode to linear sweep"""
        self.instr.write('SENS:SWEEP:TYPE LIN')
        print(f"- Activated Linear Sweep Mode.")
    def Sweep_GetTime(self):
        """Prints the time taken ofr a single sweep."""
        print(self.instr.query("SENS1:SWE:TIME?"))

############################################################

    def Trace_Delete(self,window:int, trace:int):
        """Deletes the trace."""
        self.instr.write(f"DISP:WIND{window}:TRAC{trace} off")
        print(f"Trace {trace} deleted.")     
    def Trace_Create(self, window:int, trace:int, name:str,port:str):
        """Create a new trace with a name and port."""
        self.instr.write(f"CALC:PAR:DEF '{name}', {port}") 
    def Trace_Display(self, window:int, trace:int, name:str):
        """Displays the trace in desireed window."""
        self.instr.write(f"DISP:WIND{window}:TRAC{trace}:FEED '{name}'")
    def Trace_Select(self, name:str):
        """Selects the named trace in the current channel"""
        self.instr.write(f'CALC:PAR:SEL "{name}"')
        print(f"- Trace '{name}' selected.")
    def Trace_GetRawData(self):
        """Querys the Raw-Data from the before selected channel."""
        #self.instr.write("FORM:DATA ASCII")
        self.instr.write("FORM:DATA ASCii,0")
        data = self.instr.query_ascii_values("CALC:DATA? SDATA",container=np.ndarray)
        print("- Data of selected Trace queried.")
        data = data.reshape((int(self.NOF_Get()), 2)) # N points with its real + imag part
        data_real, data_imag = data.reshape(-1, 2).T  # split for easier post processing
        return data_real,data_imag
    def Trace_List(self):
        """Lists all Traces in the current Channel."""
        print(self.instr.query('CALC:PAR:CAT?'))

    def Trigger_SetMode(self,mode):
        """Set Trigger Mode. (HOLD, CONT, GRO, SING)"""
        self.instr.write(f'SENS:SWE:MODE {mode}')
        print(f"- Trigger Mode set to '{mode}'.")

############################################################

############################################################

############################################################

    def Write(self,Command):
        """Sends msg to the instrument."""
        self.instr.write(Command)

    def Window_State(self, number:int = 1, state:int = 1):
        """Activate{state=1} or deactivates{state=0} window{number}."""
        self.instr.write(f"DISP:WIND{number}:STATE {state}")

############################################################

    def GetNumberOfFreqPoints(self):
        """Gives back the number of frequency points used"""
        return self.instr.query('SENS:SWE:POIN?')

    def getSParameterFull2Port(self,NumOfPoints):
        """Capture S-Parameter."""
        self.instr.write('FORM REAL,64')
        if  self.instr.query('CALC:PAR:SEL?')[1:-2] != 'Test':
            self.instr.write('CALC:PAR:DEL Test')
            self.instr.write('CALC:PAR:DEF Test, S21')
            self.instr.write('CALC:PAR:SEL Test')
        # switch PNA to single measurement
        self.instr.write('SENS:SWE:MODE SING')
        self.instr.write('*WAI')
        # Get Data
        Data = self.instr.query_binary_values('CALC:DATA:SNP:PORTs? "1,2"', datatype= u'd', is_big_endian=True, container=np.ndarray)
        #Data = self.instr.query_ascii_values('CALC:DATA:SNP:PORTs? "1,2"', container=np.ndarray)

        Data = np.reshape(Data,(9,NumOfPoints)) # Data = [Freq Re(S11) Im(S11) Re(S12) Im(S12) ... Im(S22)]

        # switch PNA back to continuous measurement
        # self.instr.write('SENS:SWE:MODE CONT')
        print("Captured S-Parameter.")
        return Data

"""if __name__ == '__main__':
    PNA = E8361C()
    PNA.connect()"""