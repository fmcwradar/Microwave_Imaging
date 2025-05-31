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

from Automatisation_Modul import automatisation

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
end_x = 0
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

ser = None

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

# Wait for GRBL to become idle
def wait_until_idle():
    while True:
        ser.write(b'?')  # Send status query
        status = ser.readline().decode('utf-8').strip()
        if "Idle" in status:
            break
        time.sleep(0.5)

# === GRBL Verbindung ===
def connecting():
    global  ser
    if ser is None:
        # Verbinden
        try:
            print("Connecting...")
            ser = serial.Serial('COM3', 115200, timeout=1)
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
        wait_until_idle()
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
        start_x = int(entry_start_x.get())
    except ValueError:
        print("Not valid value!")
        start_x = 0  # oder eine Fehlermeldung anzeigen
    try:
        end_x = int(entry_end_x.get())
    except ValueError:
        print("Not valid value!")
        end_x = 0  # oder eine Fehlermeldung anzeigen
    try:
        start_z = int(entry_start_z.get())
    except ValueError:
        print("Not valid value!")
        start_z = 0  # oder eine Fehlermeldung anzeigen
    try:
        end_z = int(entry_end_z.get())
    except ValueError:
        print("Not valid value!")
        end_z = 0  # oder eine Fehlermeldung anzeigen

    print(storage)
    # automate = automatisation(ser, start_x, end_x, start_z, end_z, storage, IP, feed_rate_x, feed_rate_z)
    print("Running test automatisation.")
    # automate.run_automatisation()

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
        entry_IP.insert(0, default_IP)
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

# === GUI ===
root = tk.Tk()
root.title("Mini G-Code Sender")
root.geometry("600x400")  # Breiter wegen neuem Bereich

vcmd = (root.register(validate_int), '%P')  # Validator für Eingabefelder
vIP = (root.register(validate_ip), '%P')  # Validator für IP-Adressen)

# Hauptcontainer: 2 Spalten
main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10, fill="both", expand=True)

# === Linke Seite ===
left_frame = tk.Frame(main_frame)
left_frame.grid(row=0, column=0, padx=(0, 20))

step = 1.0

# Verbindung starten/ stoppen
btn_connecting = tk.Button(left_frame, text="Verbinden", command=lambda: connecting(), width=10, height=2)
btn_connecting.config(text="Verbinden", bg="green")
btn_connecting.grid(row=0, column=0)

# Schrittgröße
tk.Label(left_frame, text="Step size:").grid(row=4, column=0, sticky="w", pady=(0, 0))
entry_step_size = tk.Entry(left_frame, validate="key", validatecommand=vcmd, justify="center")
entry_step_size.grid(row=4, column=1, pady=(0, 0))
entry_step_size.insert(0, "1")

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

Var_start_x = StringVar()
Var_start_z = StringVar()
Var_end_x = StringVar()
Var_end_z = StringVar()
label_x_var = StringVar(value="Measurements in X: 0")
label_z_var = StringVar(value="Measurements in Z: 0")

# Trigger bei Änderung
for var in [Var_start_x, Var_start_z, Var_end_x, Var_end_z]:
    var.trace_add("write", update_measurements)

# start_x / end_x
tk.Label(right_frame, text="Start X:").grid(row=4, column=0, sticky="w")
entry_start_x = tk.Entry(right_frame, validate="key", validatecommand=vcmd, justify="right", textvariable=Var_start_x)
entry_start_x.grid(row=4, column=1)

tk.Label(right_frame, text="End X:").grid(row=5, column=0, sticky="w")
entry_end_x = tk.Entry(right_frame, validate="key", validatecommand=vcmd, justify="right", textvariable=Var_end_x)
entry_end_x.grid(row=5, column=1)

# start_z / end_z
tk.Label(right_frame, text="Start Z:").grid(row=7, column=0, sticky="w", pady=(20, 0))
entry_start_z = tk.Entry(right_frame, validate="key", validatecommand=vcmd, justify="right", textvariable=Var_start_z)
entry_start_z.grid(row=7, column=1, pady=(20, 0))

tk.Label(right_frame, text="End Z:").grid(row=8, column=0, sticky="w")
entry_end_z = tk.Entry(right_frame, validate="key", validatecommand=vcmd, justify="right", textvariable=Var_end_z)
entry_end_z.grid(row=8, column=1)

btn_script = tk.Button(right_frame, text="Automatisierung starten", command=starte_script, bg="green", fg="white", height=2)
btn_script.grid(row=3, column=0, columnspan=2, pady=(10, 10))

tk.Label(right_frame, text="IP-Address of Oszi:").grid(row=0, column=0, sticky="w")
entry_IP = tk.Entry(right_frame, fg='grey', validate="key", validatecommand=vIP, justify="right")
entry_IP.grid(row=0, column=1)

button_storage = tk.Button(right_frame, text="Speicherordner wählen", command=ordner_waehlen)
button_storage.grid(row=1, column=0, columnspan=2, pady=(10, 10))

label = tk.Label(right_frame, text=f"{storage} (default)", wraplength=250)
label.grid(row=2, column=0, columnspan=2)
# Tooltip initialisieren
label.tooltip = ToolTip(label, "Default folder")

entry_start_x.insert(0, "0")
entry_end_x.insert(0, "100")
entry_start_z.insert(0, "0")
entry_end_z.insert(0, "50")

label_steps_x = tk.Label(right_frame, text=f"Measurements in X: {steps_x}", fg="grey", textvariable=label_x_var)
label_steps_x.grid(row=6, column=0)
label_steps_y = tk.Label(right_frame, text=f"Measurements in Z: {steps_y}", fg="grey", textvariable=label_z_var)
label_steps_y.grid(row=9, column=0)

entry_feedrate_x.insert(0, "200")
entry_feedrate_z.insert(0, "175")
entry_IP.insert(0, default_IP)

entry_IP.bind('<FocusIn>', on_entry_click)
entry_IP.bind('<FocusOut>', on_focusout)

# Trennlinie horizontal
separator = tk.Frame(root, height=2, bg="grey")
separator.pack(fill="x", padx=10, pady=(5, 0))

# Konsole unten über die ganze Breite
console = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=8, state="disabled")
console.pack(fill="both", expand=False, padx=10, pady=5)

# Umleitung aktivieren
sys.stdout = Redirector(console)
sys.stderr = Redirector(console)

root.mainloop()

# Aufräumen
if ser:
    ser.close()
