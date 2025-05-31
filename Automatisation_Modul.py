import serial
import time
import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os
import pathlib
from datetime import datetime
import sys

ser = None

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

class automatisation:
    def __init__(self, ser, start_x, end_x, start_y, end_y, storage, IP, feed_rate_x, feed_rate_z):
        self.ser = ser
        self.start_x = start_x
        self.end_x = end_x
        self.start_y = start_y
        self.end_y = end_y
        self.storage = storage
        self.IP = IP
        self.feed_rate_x = feed_rate_x
        self.feed_rate_z = feed_rate_z

    # Send GRBL commands
    def send_gcode(self, gcode):
        self.ser.write(gcode.encode() + b'\n')  # Send g-code command
        time.sleep(0.1)  # Wait for command to be processed
        response = self.ser.readline().strip().decode()
        print(f"\tGRBL Response: {response}")
        return response

    # Example: Unlock the GRBL and home the machine
    def unlock_grbl(self):
        self.send_gcode("$X")  # Unlock GRBL

    def home_table(self):
        self.send_gcode("$H")  # Home the machine

    # Function to wait for GRBL to become idle
    def wait_until_idle(self):
        while True:
            self.ser.write(b'?')  # Send status query
            status = self.ser.readline().decode('utf-8').strip()
            if "Idle" in status:
                break
            time.sleep(0.5)

    def move_to_quick(self, x_pos, y_pos):
        self.send_gcode(f"G0 X{x_pos} Y{y_pos}")

    def move_to(self, absolut, feed_rate, x_pos, y_pos):
        if absolut == 1:
            set_ref = 90
        else:
            set_ref = 91
        self.send_gcode(f"G{set_ref} G1 X{x_pos} Y{y_pos} F{feed_rate}")

        # Update the plot with the new data point
        # update_plot(current_x_pos, current_y_pos)

        self.wait_until_idle()

    def setup(self, absolut):
        if absolut == 1:
            set_ref = 90
        else:
            set_ref = 91
        self.send_gcode(f"G21 G{set_ref}")

    def motor_test(self):
        self.send_gcode(f"G91  G1 X1 Y0 F100")
        print("First move.")
        time.sleep(1)
        self.send_gcode(f"G91  G1 X0 Y1 F100")
        print("Second move.")
        time.sleep(1)
        self.send_gcode(f"G91  G1 X1 Y0 F100")
        print("Third move.")
        time.sleep(1)
        self.send_gcode(f"G91  G1 X0 Y1 F100")
        print("Forth move.")
        time.sleep(1)

    # Real-time plot update function
    def update_plot(self, new_x, new_y):
        # Append new data point to data lists
        self.x_data.append(new_x)
        self.y_data.append(new_y)

        # Update the line data
        self.line.set_data(self.x_data, self.y_data)

        # Update start and end points
        if self.x_data and self.y_data:
            self.start_point.set_data(self.x_data[0], self.y_data[0])  # First point in green
            self.end_point.set_data(self.x_data[-1], self.y_data[-1])  # Last point in red

        # Redraw the plot
        plt.pause(0.05)  # Pause briefly to update the plot

    def run_automatisation(self):
        if self.ser is None:
            # Verbinden
            try:
                print("Connecting...")
                self.ser = serial.Serial('COM3', 115200, timeout=1)
                # Wake up the GRBL
                self.ser.write(b"\r\n\r\n")
                time.sleep(2)
                self.ser.flushInput()
                print("Connected!")
            except Exception as e:
                print(f"Fehler bei Verbindungsaufbau: {e}")
                self.ser = None

        test_run = False
        move_test = False

        # Get the current date and time
        now = datetime.now()

        # Format the date and time
        timestamp = now.strftime("%d-%m-%Y_%H-%M-%S")

        # self.feed_rate_x = 200
        # self.feed_rate_y = 175

        steps_x = int(((self.end_x - self.start_x) / 10) + 1)
        steps_y = int(((self.end_y - self.start_y) / 10) + 1)

        x_axis = np.linspace(self.start_x, self.end_x, steps_x)
        y_axis = np.linspace(self.start_y, self.end_y, steps_y)

        self.step_size_x = x_axis[1] - x_axis[0]
        if self.start_y == self.end_y:
            self.step_size_y = len(y_axis)
        else:
            self.step_size_y = y_axis[1] - y_axis[0]

        print(f"x_axis: {x_axis}, step_size_x: {self.step_size_x}")
        print(f"y_axis: {y_axis}, step_size_y: {self.step_size_y}")

        # Define the figure and axis
        fig, ax = plt.subplots()
        line, = ax.plot([], [], '-b')  # 'b-' for blue line
        start_point, = ax.plot([], [], 'go')  # 'go' for green start point
        end_point, = ax.plot([], [], 'ro')    # 'ro' for red end point

        # Set the axis limits
        ax.set_xlim(self.start_x - 1, self.end_x + 1)
        ax.set_ylim(self.start_y - 1, self.end_y + 1)

        # Initialize data lists
        x_data, y_data = [], []

        self.setup(absolut=0)
        self.unlock_grbl()

        if move_test == True:
            self.motor_test()
        else:
            # home_table()
            current_x_pos = self.start_x
            current_y_pos = self.start_y

            # print("Moving to start position.")
            # move_to(0, feed_rate_y, current_x_pos, current_y_pos)
            # update_plot(current_x_pos, current_y_pos)
            # print("first done.")
            time.sleep(2)

            #send_gcode("$")


            #initialize oscilloscope class
            if test_run == False:
                osc = RTE1054(self.IP)
                pathlib.Path(f"{self.storage}\Measurement Data Cache\\{timestamp}").mkdir(parents=True, exist_ok=True)
            for i in range(len(y_axis)):
                for j in range(len(x_axis)):
                    # print(f"i: {i}, j: {j}")
                    j += 1
                    if test_run == False:
                        # Save first data set
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

                        # Plot Data
                        plt.plot(time_vector * 1e3, Data_1)
                        plt.plot(time_vector * 1e3, Data_2)
                        # plt.show()

                        osc.start_osci(1)

                        dataset = np.vstack((time_vector, Data_1, Data_2)).T

                        # Write Data to .csv File

                        filepath = f"{self.storage}\Measurement Data Cache\\{timestamp}\\{current_y_pos}_{current_x_pos}.csv"

                        if os.path.exists(filepath):
                            os.remove(filepath)
                            np.savetxt(filepath, dataset, delimiter=",")

                        else:
                            np.savetxt(filepath, dataset, delimiter=",")

                        print(f"{current_y_pos}_{current_x_pos} Dataset Saved")

                        print("Start Moving the Antennas")
                    if i % 2 == 0:
                        if current_x_pos != self.end_x:
                            current_x_pos += self.step_size_x
                            # j += 1
                            # current_x_pos = x_axis[j]
                            print("\tRotating +x ...")
                            # move_to(1, feed_rate_x, current_x_pos, current_y_pos)
                            self.move_to(0, self.feed_rate_x, self.step_size_x, 0)
                            print("\t(current_y_pos, current_x_pos): ", (current_y_pos, current_x_pos))
                            time.sleep(0.5)

                            # Update the plot with the new data point
                            # update_plot(current_x_pos, current_y_pos)

                        else:
                            print("End reached...")
                            if current_y_pos != self.end_y:
                                # current_x_pos = current_x_pos
                                print(f"\033[31mLast Position Reached in row {i}.\033[0m")

                                current_y_pos += self.step_size_y
                                i += 1
                                # current_y_pos = y_axis[i]
                                print("\tRotating +y...")
                                # move_to(1, feed_rate_y, current_x_pos, current_y_pos)
                                self.move_to(0, self.feed_rate_z, 0, self.step_size_y)
                                print("(current_y_pos, current_x_pos): ", (current_y_pos, current_x_pos))
                                time.sleep(0.5)

                                # Update the plot with the new data point
                                # update_plot(current_x_pos, current_y_pos)
                            else:
                                print("\033[32mMeasurements done!\033[0m")

                    else:
                        if int(current_x_pos) != self.start_x:
                            # current_x_pos -= step_size_x
                            current_x_pos = x_axis[len(x_axis) - j - 1]
                            print("\tRotating -x...")
                            # move_to(1, feed_rate_x, current_x_pos, current_y_pos)
                            self.move_to(0, self.feed_rate_x, -self.step_size_x, 0)
                            print("\t(current_y_pos, current_x_pos): ", (current_y_pos, current_x_pos))
                            time.sleep(0.5)

                            # Update the plot with the new data point
                            # update_plot(current_x_pos, current_y_pos)

                        elif int(current_x_pos) == self.start_x:
                            if current_y_pos != self.end_y:
                                print(f"\033[31mLast Position Reached in row {i}.\033[0m")
                                # current_y_pos += step_size_y
                                i += 1
                                current_y_pos = y_axis[i]
                                print("\tRotating +y...")
                                # move_to(0, feed_rate_y, current_x_pos, current_y_pos)
                                self.move_to(0, self.feed_rate_z, 0, self.step_size_y)
                                print("(current_y_pos, current_x_pos): ", (current_y_pos, current_x_pos))
                                time.sleep(0.5)

                                # Update the plot with the new data point
                                # update_plot(current_x_pos, current_y_pos)
                            else:
                                print("\033[32mMeasurements done!\033[0m")

            # Close the serial connection
            self.ser.close()