# 🧠 Mind Control EEG

**Mind Control EEG** is a real-time, brain-computer interface that reads EEG signals via Arduino and processes them in Python to trigger customizable outputs — such as virtual movement in games. This toolkit is flexible and modular, allowing developers to map mental state changes (e.g. alpha/beta activity) to any action they define.

---

## 📌 Features

- 🧠 Real-time EEG signal acquisition (via Arduino)
- 📊 Live bandpower computation using Welch's method
- ⚡ Threshold-based trigger system
- 🎮 Simulated keyboard actions (e.g. pressing `space`) — easily replaceable with any custom output
- 📈 Real-time matplotlib visualizations
- 📁 EEG data logging to text file

# Requirements
- [BioAmp EXG Pill](https://www.crowdsupply.com/upside-down-labs/bioamp-exg-pill) 
- Libraries: Serial, threading, matplotlib, scipy, time

Credits: This project uses [EEGFilter](https://github.com/upsidedownlabs/BioAmp-EXG-Pill/blob/86bb1f45575054b4b9af78517c24ad682c3a65b6/software/EEGFilter/EEGFilter.ino) by Upside Down Labs
