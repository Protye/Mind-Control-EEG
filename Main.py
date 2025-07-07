'''
Collect electrode readings by opening file and writing to it.
Compute Alpha/Beta Power bands...
Graphing...
When Alpha/Beta power bands exceed threshold, then activate walking().
'''


## Part 1: EEG Stuff
import serial
import time
import threading
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import welch

# === Config ===
arduino_port = "COM5"
baud = 9600
sampling_rate = 256  # Hz, matches Arduino
epoch_duration = 2   # seconds
epoch_length = sampling_rate * epoch_duration
max_plot_points = 100
file_name = "EEG_Log.txt"

# === Shared Data ===
raw_data = []
alpha_powers = []
beta_powers = []
lock = threading.Lock()

# === Frequency Bands ===
def bandpower(data, sf, band, window_sec=None):
    from scipy.signal import welch
    band = np.asarray(band)
    low, high = band

    if window_sec is not None:
        nperseg = int(window_sec * sf)
    else:
        nperseg = (2 ** 10)

    freqs, psd = welch(data, sf, nperseg=nperseg)
    idx_band = np.logical_and(freqs >= low, freqs <= high)
    return np.trapezoid(psd[idx_band], freqs[idx_band])

# === Serial Reading Thread ===
def read_serial():
    with open(file_name, "a") as file:
        while True:
            try:
                line = ser.readline().decode('ascii').strip()
                value = float(line)

                with lock:
                    raw_data.append(value)
                    if len(raw_data) > epoch_length * 10:  # keep ~10 epochs max
                        del raw_data[:-(epoch_length * 10)]

                file.write(f"{value}\n")
            except:
                continue

# === Plotting ===
fig, (ax1, ax2) = plt.subplots(2, 1)

def animate(i):
    with lock:
        if len(raw_data) >= epoch_length:
            epoch = raw_data[-epoch_length:]
            alpha = bandpower(epoch, sampling_rate, [8, 12])
            beta = bandpower(epoch, sampling_rate, [13, 30])

            alpha_powers.append(alpha)
            beta_powers.append(beta)

            if len(alpha_powers) > max_plot_points:
                del alpha_powers[:-max_plot_points]
                del beta_powers[:-max_plot_points]

        # === Plot raw EEG ===
        ax1.clear()
        ax1.plot(raw_data[-epoch_length:])
        ax1.set_title("Raw EEG")
        ax1.set_ylabel("Amplitude")
        ax1.set_ylim([-10,10])

        # === Plot bandpowers ===
        ax2.clear()
        ax2.plot(alpha_powers, label="Alpha (8-12Hz)")
        ax2.plot(beta_powers, label="Beta (13-30Hz)")
        ax2.set_title("Alpha and Beta Bandpower (Welch)")
        ax2.set_ylabel("Power")
        ax2.set_xlabel("Epoch")
        ax2.legend(loc='upper right')

# === Start Serial and Plot ===
ser = serial.Serial(arduino_port, baud)
time.sleep(2)

t = threading.Thread(target=read_serial, daemon=True)
t.start()

ani = animation.FuncAnimation(fig, animate, interval=500)
plt.tight_layout()
plt.show()

ser.close()


## Part 2: Wheelchair Walking in Roblox

import keyboard
import time
import threading
from pynput.keyboard import Listener, KeyCode


'''once pressed toggled button, continuous press down on the key 'w' until toggled off
'''

TOGGLE_KEY = KeyCode(char="t") #instead of a toggle wth a character, it would be with a threshhold of band power.

pressing = False

def toggle_event(key):
    if key == TOGGLE_KEY:
        global pressing #global to refer to the global instead of a one-time local
        pressing = not pressing


def walker():
    while True:
        if pressing: #why do I need this ifstatement? why not just the while?
            keyboard.press("w")
        else:
            keyboard.release("w")
        time.sleep(0.01)

click_thread = threading.Thread(target=walker) #main thread listening for toggle key, while other thread does clicking
click_thread.start()

with Listener(on_press=toggle_event) as listener:
    listener.join()

