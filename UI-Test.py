import tkinter as tk
from tkinter import messagebox
import serial
import time
import subprocess
import os
from tkinter import scrolledtext
import sys
import re
from tkinter import filedialog
from tkinter import  StringVar
from tkinter import ttk
import serial.tools.list_ports
import subprocess
import time
import sys

from Automatisation_Modul import automatisation
from osc_test import single_measurement

sys.stdout.reconfigure(line_buffering=True)

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # Kein Fensterrahmen
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

class Redirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, message):
        self.widget.configure(state='normal')
        self.widget.insert(tk.END, message)
        self.widget.see(tk.END)
        self.widget.configure(state='disabled')

    def flush(self):
        pass

current_dir = os.path.dirname(__file__)

step_size = 1
start_x = 0
start_z = 0
end_x = 600
end_z = 0

steps_x = 0
steps_y = 0

# IP = '169.254.155.204'
IP = "169.254.25.75"
default_IP = "169.254.25.75"

MAX_PATH_LENGTH = 50

storage = current_dir

absolut = 0
feed_rate_x = 200
feed_rate_z = 175

methode_choice = "Einzelmessung"

path = current_dir

if os.path.exists(r'{0}\ui-settings.txt'.format(path)):
    with open(r'{0}\ui-settings.txt'.format(path), 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) >= 2:
                key = parts[0].strip()
                value = parts[1].strip()

                # Zuweisung basierend auf dem Namen
                if key == 'start_x':
                    start_x = int(value)
                elif key == 'end_x':
                    end_x = int(value)
                elif key == 'start_z':
                    start_z = int(value)
                elif key == 'end_z':
                    end_z = int(value)
                elif key == 'step_size':
                    step_size = int(value)
                elif key == 'feed_rate_x':
                    feed_rate_x = int(value)
                elif key == 'feed_rate_z':
                    feed_rate_z = int(value)
                elif key == 'IP':
                    IP = value
                elif key == 'Storage':
                    Storage = value
else:
    print("Datei nicht gefunden.")
    with open(r'{0}\ui-settings.txt'.format(path), 'w') as the_file:
        the_file.write('start_x, {0},\n'.format(start_x))
        the_file.write('end_x, {0},\n'.format(end_x))
        the_file.write('start_z, {0},\n'.format(start_z))
        the_file.write('end_z, {0},\n'.format(end_z))
        the_file.write('step_size, {0},\n'.format(step_size))
        the_file.write('feed_rate_x, {0},\n'.format(feed_rate_x))
        the_file.write('feed_rate_z, {0},\n'.format(feed_rate_z))
        the_file.write('IP, {0},\n'.format(default_IP))
        the_file.write('Storage, {0},\n'.format(storage))

ser = None

def get_com_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def update_com_ports():
    ports = get_com_ports()
    combobox['values'] = ports
    if ports:
        combobox.current(0)
    else:
        combobox.set('--')

def on_com_select(event):
    com_ports = get_com_ports()
    selected_port = combobox.get()
    print(f"Ausgewählter COM-Port: {selected_port}")

# COM-Ports abrufen
com_ports = get_com_ports()

# Send GRBL commands
def send_gcode(gcode):
    ser.write(gcode.encode() + b'\n')  # Send g-code command
    time.sleep(0.1)  # Wait for command to be processed
    response = ser.readline().strip().decode()
    print(f"\tGRBL Response: {response}")
    return response

# Unlock GRBL
def unlock_grbl():
    send_gcode("$X")  # Unlock GRBL

def hold_motion():
    send_gcode("!") #feed hold

# Wait for GRBL to become idle
def wait_until_idle():
    while True:
        ser.write(b'?')  # Send status query
        status = ser.readline().decode('utf-8').strip()
        if "Idle" in status:
            break
        time.sleep(0.5)

# === GRBL Verbindung ===
def connecting(port):
    global  ser
    if ser is None:
        # Verbinden
        try:
            print("Connecting...")
            ser = serial.Serial(port, 115200, timeout=1)
            time.sleep(2)
            ser.flushInput()
            btn_connecting.config(text="Trennen", bg="red")
            print("Connected!")
            unlock_grbl()
        except Exception as e:
            print(f"Fehler bei Verbindungsaufbau: {e}")
            ser = None
    else:
        # Trennen
        try:
            ser.close()
            print("Disconnected.")
        except Exception as e:
            print(f"Fehler beim Trennen: {e}")
        ser = None
        btn_connecting.config(text="Verbinden", bg="green")

# === G-Code senden ===
def move_to(absolut, feed_rate, x_pos, z_pos):
    global step_size
    try:
        step_size = int(entry_step_size.get())
    except ValueError:
        print("Not valid value!")
    # print(step_size)
    send_gcode("~")
    if x_pos == 1:
        try:
            feed_rate = int(entry_feedrate_x.get())
        except ValueError:
            print("Not valid value!")
            feed_rate = 0  # oder eine Fehlermeldung anzeigen
    else:
        try:
            feed_rate = int(entry_feedrate_z.get())
        except ValueError:
            print("Not valid value!")
            feed_rate = 0  # oder eine Fehlermeldung anzeigen

    try:
        if absolut == 1:
            set_ref = 90
        else:
            set_ref = 91
        x_pos = x_pos * step_size
        z_pos = z_pos * step_size
        send_gcode(f"G{set_ref} G1 X{x_pos} Y{z_pos} F{feed_rate}")
        # wait_until_idle()
    except Exception as e:
        if str(e) == "'NoneType' object has no attribute 'write'":
            print(f"Not connected.")
        else:
            print(f"{e}")

# === Externes Skript starten ===
def starte_script():
    global start_x, start_z, end_x, end_z
    # Messfenster bestimmen
    try:
        # if methode_choice == "Ebenenmessung":
        #     start_x = int(entry_start_x_plane.get())
        # if methode_choice == "3D-Messung":
        #     start_x = int(entry_start_x_3D.get())
        start_x = Var_start_x
    except ValueError:
        print("Not valid value!")
        start_x = 0  # oder eine Fehlermeldung anzeigen
    try:
        # if methode_choice == "Ebenenmessung":
        #     end_x = int(entry_end_x_plane.get())
        # if methode_choice == "3D-Messung":
        #     end_x = int(entry_end_x_3D.get())
        end_x =  Var_end_x
    except ValueError:
        print("Not valid value!")
        end_x = 0  # oder eine Fehlermeldung anzeigen
    try:
        # start_z = int(entry_start_z_3D.get())
        start_z = Var_start_z
    except ValueError:
        print("Not valid value!")
        start_z = 0  # oder eine Fehlermeldung anzeigen
    try:
        # end_z = int(entry_end_z_3D.get())
        end_z = Var_end_z
    except ValueError:
        print("Not valid value!")
        end_z = 0  # oder eine Fehlermeldung anzeigen

    print(storage)
    automate = automatisation(ser, start_x, end_x, start_z, end_z, storage, IP, feed_rate_x, feed_rate_z)
    print("Running test automatisation.")
    automate.run_automatisation()

def starte_pll():
    prozess = subprocess.Popen(
        ["python", "ControllPLL/PLLconfigurator_V1.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE,
        text=True
    )

    for line in prozess.stdout:
        print(">>", line.strip())
    #     read_done = False
    #     if "r -> read file. Else: -> quit program. Type in: " in line and read_done == False:
    #         print("-> Eingabe erkannt. Sende 'r'")
    #         prozess.stdin.write("r\n")
    #         prozess.stdin.flush()
    #
    #     # read_done = True
    #     # if "r -> read file. Else: -> quit program. Type in: " in line and read_done == True:
    #     #     print("-> Eingabe erkannt. Sende 'k'")
    #     #     prozess.stdin.write("k\n")
    #     #     prozess.stdin.flush()
    #
    print("PLL is starting")

def starte_psu():
    print("Powersupplies are starting.")

def starte_einzelmessung(ip_address):
    measurement_name = entry_measurement_name.get()
    calibration = True
    VNA = False
    measurement = single_measurement(ip_address, storage, measurement_name, calibration, VNA)
    measurement.running()

# === Nur Integer erlauben ===
def validate_int(text):
    return text == "" or text.isdigit()

# nur IP Addressen erlauben
def validate_ip(ip):
    # Leere Eingabe ist erlaubt, damit man Zeichen löschen kann
    if ip == "":
        return True

    pattern = r'^(\d{1,3}\.){0,3}\d{0,3}$'
    if not re.match(pattern, ip):
        return False

    parts = ip.split(".")
    for part in parts:
        if part == "":
            continue  # Ermöglicht Teilbearbeitung
        if not part.isdigit():
            return False
        if not 0 <= int(part) <= 255:
            return False
    return True

def on_entry_click(event):
    if entry_IP.get() == default_IP:
        entry_IP.delete(0, "end")  # Platzhalter löschen
        entry_IP.config(fg='black')

def on_focusout(event):
    if entry_IP.get() == "":
        entry_IP.insert(0, IP)
        entry_IP.config(fg='grey')

def ordner_waehlen():
    global storage
    ordner = filedialog.askdirectory(title="Speicherordner wählen")
    if ordner:
        storage = ordner
        gekuerzt = (ordner[:MAX_PATH_LENGTH] + '...') if len(ordner) > MAX_PATH_LENGTH else ordner
        label.config(text=f"Ausgewählt: {gekuerzt}")
        # Tooltip aktualisieren
        label.tooltip.text = ordner

def update_measurements(*args):
    try:
        x1 = float(Var_start_x.get())
        x2 = float(Var_end_x.get())
        z1 = float(Var_start_z.get())
        z2 = float(Var_end_z.get())

        mx = abs(int((x2 - x1) / 10)) + 1
        mz = abs(int((z2 - z1) / 10)) + 1

        label_x_var.set(f"Measurements in X: {mx}")
        label_z_var.set(f"Measurements in Z: {mz}")
    except ValueError:
        label_x_var.set("Measurements in X: Fehler")
        label_z_var.set("Measurements in Z: Fehler")

def on_close():
    print("Fenster wird geschlossen. Speichere Daten oder räume auf...")
    global start_x, end_x

    if methode_choice == "Ebenenmessung":
        start_x = int(entry_start_x_plane.get())
        end_x = int(entry_end_x_plane.get())
    if methode_choice == "3D-Messung":
        start_x = int(entry_start_x_3D.get())
        end_x = int(entry_end_x_3D.get())
    start_z = int(entry_start_z_3D.get())
    end_z = int(entry_end_z_3D.get())
    step_size = int(entry_step_size.get())
    feed_rate_x = int(entry_feedrate_x.get())
    feed_rate_z = int(entry_feedrate_z.get())
    IP = entry_IP.get()

    with open(r'{0}\ui-settings.txt'.format(path), 'w') as the_file:
        the_file.write('start_x, {0},\n'.format(start_x))
        the_file.write('end_x, {0},\n'.format(end_x))
        the_file.write('start_z, {0},\n'.format(start_z))
        the_file.write('end_z, {0},\n'.format(end_z))
        the_file.write('step_size, {0},\n'.format(step_size))
        the_file.write('feed_rate_x, {0},\n'.format(feed_rate_x))
        the_file.write('feed_rate_z, {0},\n'.format(feed_rate_z))
        the_file.write('IP, {0},\n'.format(IP))
        the_file.write('Storage, {0},\n'.format(storage))

    # Aufräumen
    if ser:
        ser.close()

    root.destroy()  # Fenster schließen

def show_layout(method_choice):
    # Alle Layout-Frames verstecken
    for frame in layouts.values():
        frame.grid_forget()

    # Passenden Frame anzeigen
    if method_choice in layouts:
        layouts[method_choice].grid(pady=10)

def on_dropdown_change(event):
    method_choice = Messungsmethoden_dropdown.get()
    show_layout(method_choice)

    # if methode_choice == "Ebenenmessung":
    #     entry_start_x_plane.insert(0, str(Var_start_x))
    #     entry_end_x_plane.insert(0, str(Var_end_x))
    # if methode_choice == "3D-Messung":
    #     entry_start_x_3D.insert(0, str(Var_start_x))
    #     entry_end_x_3D.insert(0, str(Var_end_x))
    # entry_start_z_3D.insert(0, str(start_z))
    # entry_end_z_3D.insert(0, str(end_z))

# === GUI ===
root = tk.Tk()
root.title("Mini G-Code Sender")
# root.geometry("650x650")  # Breiter wegen neuem Bereich

vcmd = (root.register(validate_int), '%P')  # Validator für Eingabefelder
vIP = (root.register(validate_ip), '%P')  # Validator für IP-Adressen)

# Hauptcontainer: 2 Spalten
main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10, fill="both", expand=True)

main_frame.grid_columnconfigure(0, weight=0)  # frame_left & Konsole
main_frame.grid_columnconfigure(1, weight=0)  # frame_right
main_frame.grid_rowconfigure(0, weight=0)     # Obere Zeile
main_frame.grid_rowconfigure(1, weight=1)     # Konsole soll mitwachsen

root.resizable(width=False, height=True)

# === Linke Seite ===
left_frame = tk.Frame(main_frame)
left_frame.grid(row=0, column=0, padx=(0, 20))

step = 1.0

# COM Port
combobox = ttk.Combobox(left_frame, values=com_ports, state="readonly", width=10, postcommand=update_com_ports)
combobox.grid(row=1, column=0, pady=(0, 0))
combobox.bind("<<ComboboxSelected>>", on_com_select)

# Optional: Standardauswahl
if com_ports:
    combobox.current(0)

# Verbindung starten/ stoppen
port = str(combobox.get())
# if port == '':
#     port = "COM3"
btn_connecting = tk.Button(left_frame, text="Verbinden", command=lambda: connecting(port), width=10, height=2)
btn_connecting.config(text="Verbinden", bg="green")
btn_connecting.grid(row=0, column=0)

# Stop Bewegung
btn_stop = tk.Button(left_frame, text="Stop", command=lambda: hold_motion(), width=10, height=2)
btn_stop.config(text="Stop")
btn_stop.grid(row=0, column=1)

# Unlock
btn_unlock = tk.Button(left_frame, text="Unlock", command=lambda: unlock_grbl(), width=10, height=2)
btn_unlock.config(text="Unlock")
btn_unlock.grid(row=0, column=2)

# Schrittgröße
tk.Label(left_frame, text="Step size:").grid(row=4, column=0, sticky="w", pady=(0, 0))
entry_step_size = tk.Entry(left_frame, validate="key", validatecommand=vcmd, justify="center")
entry_step_size.grid(row=4, column=1, pady=(0, 0))
entry_step_size.insert(0, str(step_size))

# Feedrate für X und Z Achse
tk.Label(left_frame, text="Feedrate X:").grid(row=5, column=0, sticky="w")
entry_feedrate_x = tk.Entry(left_frame, validate="key", validatecommand=vcmd, justify="center")
entry_feedrate_x.grid(row=5, column=1)

tk.Label(left_frame, text="Feedrate Z:").grid(row=6, column=0, sticky="w")
entry_feedrate_z = tk.Entry(left_frame, validate="key", validatecommand=vcmd, justify="center")
entry_feedrate_z.grid(row=6, column=1)

# Bewegungstasten
btn_z_plus = tk.Button(left_frame, text="Z+", command=lambda: move_to(0, feed_rate_z, 0, 1), width=10, height=2)
btn_z_plus.grid(row=1, column=1)

btn_x_minus = tk.Button(left_frame, text="X-", command=lambda: move_to(0, feed_rate_x, -1, 0), width=10, height=2)
btn_x_minus.grid(row=2, column=0)

btn_x_plus = tk.Button(left_frame, text="X+", command=lambda: move_to(0, feed_rate_x, 1, 0), width=10, height=2)
btn_x_plus.grid(row=2, column=2)

btn_z_minus = tk.Button(left_frame, text="Z-", command=lambda: move_to(0, feed_rate_z, 0, -1), width=10, height=2)
btn_z_minus.grid(row=3, column=1)

# === Vertikale Linie ===
line = tk.Frame(main_frame, width=2, bg="grey")
line.grid(row=0, column=1, sticky="ns", padx=10)

# === Rechte Seite: Textfelder ===
right_frame = tk.Frame(main_frame)
right_frame.grid(row=0, column=2, sticky="n")

top_right_frame = tk.Frame(right_frame)
top_right_frame.grid(row=0, sticky="n")

btn_PLL = tk.Button(top_right_frame, text="PLL starten", command=starte_pll, bg="green", fg="white", height=2)
btn_PLL.grid(row=3, column=0, columnspan=1, pady=(10, 10))

btn_power = tk.Button(top_right_frame, text="Netzteile starten", command=starte_psu, bg="green", fg="white", height=2)
btn_power.grid(row=3, column=1, columnspan=1, pady=(10, 10))

tk.Label(top_right_frame, text="IP-Address of Oszi:").grid(row=0, column=0, sticky="w")
entry_IP = tk.Entry(top_right_frame, fg='grey', validate="key", validatecommand=vIP, justify="right")
entry_IP.grid(row=0, column=1)
entry_IP.tooltip = ToolTip(entry_IP, f"Default IP: {default_IP}")

button_storage = tk.Button(top_right_frame, text="Speicherordner wählen", command=ordner_waehlen)
button_storage.grid(row=1, column=0, columnspan=2, pady=(10, 10))

label = tk.Label(top_right_frame, text=f"{storage} (default)", wraplength=250)
label.grid(row=2, column=0, columnspan=2)
# Tooltip initialisieren
label.tooltip = ToolTip(label, "Default folder")

Messungsmethoden = ["Einzelpunktmessung", "Ebenenmessung", "3D-Messung"]
Messungsmethoden_dropdown = ttk.Combobox(top_right_frame, values=Messungsmethoden, state="readonly", width=20)
Messungsmethoden_dropdown.grid(row=4, column=0, pady=(10, 10), columnspan=2)

# Optional: Standardauswahl setzen
Messungsmethoden_dropdown.current(0)

# Ereignis binden
Messungsmethoden_dropdown.bind("<<ComboboxSelected>>", on_dropdown_change)

# Layout Einzelpunktmessung
frame_single = tk.Frame(right_frame)
frame_single.grid(row=1, sticky="n")
label_measurement_name = tk.Label(frame_single, text="Messungsname: ").grid(row=0, column=0, sticky="w")
entry_measurement_name = tk.Entry(frame_single, validate="key", justify="right")
entry_measurement_name.grid(row=0, column=1)

btn_single_meas = tk.Button(frame_single, text="Messung durchführen", command=lambda: starte_einzelmessung(ip_address=IP), bg="green", fg="white", height=2)
btn_single_meas.grid(row=1, column=0, columnspan=2, pady=(10, 10))

# Layout Ebenenmessung
Var_start_x = StringVar()
Var_start_z = StringVar()
Var_end_x = StringVar()
Var_end_z = StringVar()
label_x_var = StringVar(value="Measurements in X: 0")
label_z_var = StringVar(value="Measurements in Z: 0")

# Trigger bei Änderung
for var in [Var_start_x, Var_start_z, Var_end_x, Var_end_z]:
    var.trace_add("write", update_measurements)

frame_plane = tk.Frame(right_frame)
frame_plane.grid(row=1, sticky="n")
# btn_script = tk.Button(frame_plane, text="Automatisierung starten", command=starte_script, bg="green", fg="white", height=2, wraplength=100)
# btn_script.grid(row=3, column=0, columnspan=2, pady=(10, 10))

# start_x / end_x
label_start_x_plane = tk.Label(frame_plane, text="Start X:").grid(row=0, column=0, sticky="w")
entry_start_x_plane = tk.Entry(frame_plane, validate="key", validatecommand=vcmd, justify="right", textvariable=Var_start_x)
entry_start_x_plane.grid(row=0, column=1)

label_end_x_plane = tk.Label(frame_plane, text="End X:").grid(row=1, column=0, sticky="w")
entry_end_x_plane = tk.Entry(frame_plane, validate="key", validatecommand=vcmd, justify="right", textvariable=Var_end_x)
entry_end_x_plane.grid(row=1, column=1)

label_steps_x_plane = tk.Label(frame_plane, text=f"Measurements in X: {steps_x}", fg="grey", textvariable=label_x_var)
label_steps_x_plane.grid(row=2, column=0)

# Layout 3D-Messung
frame_3D = tk.Frame(right_frame)
frame_3D.grid(row=1, sticky="n")
btn_meas_3D = tk.Button(frame_3D, text="Automatisierung starten", command=starte_script, bg="green", fg="white", height=2, wraplength=100)
btn_meas_3D.grid(row=6, column=0, columnspan=2, pady=(10, 10))

tk.Label(frame_3D, text="Start X:").grid(row=0, column=0, sticky="w")
entry_start_x_3D = tk.Entry(frame_3D, validate="key", validatecommand=vcmd, justify="right", textvariable=Var_start_x)
entry_start_x_3D.grid(row=0, column=1)

tk.Label(frame_3D, text="End X:").grid(row=1, column=0, sticky="w")
entry_end_x_3D = tk.Entry(frame_3D, validate="key", validatecommand=vcmd, justify="right", textvariable=Var_end_x)
entry_end_x_3D.grid(row=1, column=1)

label_steps_x_3D = tk.Label(frame_3D, text=f"Measurements in X: {steps_x}", fg="grey", textvariable=label_x_var)
label_steps_x_3D.grid(row=2, column=0)

# start_z / end_z
tk.Label(frame_3D, text="Start Z:").grid(row=3, column=0, sticky="w", pady=(20, 0))
entry_start_z_3D = tk.Entry(frame_3D, validate="key", validatecommand=vcmd, justify="right", textvariable=Var_start_z)
entry_start_z_3D.grid(row=3, column=1, pady=(20, 0))

tk.Label(frame_3D, text="End Z:").grid(row=4, column=0, sticky="w")
entry_end_z_3D = tk.Entry(frame_3D, validate="key", validatecommand=vcmd, justify="right", textvariable=Var_end_z)
entry_end_z_3D.grid(row=4, column=1)

label_steps_y_3D = tk.Label(frame_3D, text=f"Measurements in Z: {steps_y}", fg="grey", textvariable=label_z_var)
label_steps_y_3D.grid(row=5, column=0)

# Dictionary zur Zuordnung
layouts = {
    "Einzelpunktmessung": frame_single,
    "Ebenenmessung": frame_plane,
    "3D-Messung": frame_3D
}

# Start mit erstem Layout
show_layout("Einzelpunktmessung")

if methode_choice == "Ebenenmessung":
    entry_start_x_plane.insert(0, str(start_x))
    entry_end_x_plane.insert(0, str(end_x))
if methode_choice == "3D-Messung":
    entry_start_x_3D.insert(0, str(start_x))
    entry_end_x_3D.insert(0, str(end_x))
entry_start_z_3D.insert(0, str(start_z))
entry_end_z_3D.insert(0, str(end_z))

entry_feedrate_x.insert(0, str(feed_rate_x))
entry_feedrate_z.insert(0, str(feed_rate_z))
entry_IP.insert(0, IP)

entry_IP.bind('<FocusIn>', on_entry_click)
entry_IP.bind('<FocusOut>', on_focusout)

# Trennlinie horizontal
separator = tk.Frame(root, height=2, bg="grey")
separator.pack(fill="x", padx=10, pady=(5, 0))

# Konsole unten über die ganze Breite
console = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=8, state="disabled")
console.grid(row=1, column=0, columnspan=3, sticky="nsew")  # Dehnt sich horizontal
# console.pack(fill="both", expand=False, padx=10, pady=5)

# Umleitung aktivieren
sys.stdout = Redirector(console)
sys.stderr = Redirector(console)

# Event-Handler registrieren
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

# Aufräumen
if ser:
    ser.close()

