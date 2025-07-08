## Part 1: EEG Stuff
import serial
import time
import threading
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import welch
import keyboard

# === Config ===
arduino_port = "COM5"
baud = 9600
sampling_rate = 256  # Hz, matches Arduino
epoch_duration = 2   # seconds
epoch_length = sampling_rate * epoch_duration
max_plot_points = 100
file_name = "EEG_Log.txt"
threshold = None
pressing = False

# === Shared Data ===
signal = []
alpha_powers = []
beta_powers = []
lock = threading.Lock()

# === Frequency Bands ===
def bandpower(data, sf, band, window_sec=None):
    band = np.asarray(band)
    low, high = band

    if window_sec is not None:
        nperseg = int(window_sec * sf)
    else:
        nperseg = (2 ** 10)

    freqs, psd = welch(data, sf, nperseg=nperseg)
    idx_band = np.logical_and(freqs >= low, freqs <= high)
    return np.trapezoid(psd[idx_band], freqs[idx_band])

def generate_fake_eeg(duration=10, sampling_rate=256):
    t = np.arange(0, duration, 1/sampling_rate)

    # Simulate alpha (10 Hz) and beta (20 Hz) + noise
    alpha_wave = 50 * np.sin(2 * np.pi * 10 * t)
    beta_wave  = 30 * np.sin(2 * np.pi * 20 * t)
    noise = np.random.normal(0, 5, len(t))

    signal = alpha_wave + beta_wave + noise
    return signal

def walker():
    global pressing
    if not pressing:
        keyboard.press("w")
        pressing = True

def walker_stop():
    global pressing
    if pressing:
        keyboard.release("w")
        pressing = False

# === Serial Reading Thread ===
# def read_serial():
#     with open(file_name, "a") as file:
#         while True:
#             try:
#                 line = ser.readline().decode('ascii').strip()
#                 value = float(line)
#
#                 with lock:
#                     raw_data.append(value)
#                     if len(raw_data) > epoch_length * 10:  # keep ~10 epochs max
#                         del raw_data[:-(epoch_length * 10)]
#
#                 file.write(f"{value}\n")
#             except:
#                 continue
# === Plotting ===
fig, (ax1, ax2) = plt.subplots(2, 1)

def animate(i):
    with lock:
        generate_fake_eeg()
        if len(signal) >= epoch_length:
            epoch = signal[-epoch_length:]
            alpha = bandpower(epoch, sampling_rate, [8, 12])
            beta = bandpower(epoch, sampling_rate, [13, 30])

            alpha_powers.append(alpha)
            beta_powers.append(beta)

            if (alpha_powers and alpha_powers[-1] > threshold) or (beta_powers and beta_powers[-1] > threshold):
                walker()
            else:
                walker_stop()

            if len(alpha_powers) > max_plot_points: # review lists
                del alpha_powers[:-max_plot_points]
                del beta_powers[:-max_plot_points]

        # === Plot raw EEG ===
        ax1.clear()
        ax1.plot(signal[-epoch_length:])
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
# ser = serial.Serial(arduino_port, baud)
time.sleep(2)

# t = threading.Thread(target=read_serial, daemon=True)
# t.start()

ani = animation.FuncAnimation(fig, animate, interval=500)
plt.tight_layout()
plt.show()

ser.close()