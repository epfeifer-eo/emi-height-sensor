# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 13:30:14 2025

@author: elija
"""
import os
import csv
import matplotlib.pyplot as plt
from tkinter import filedialog
import tkinter as tk

# Let user select a CSV file from the logs directory
def select_csv_file():
    root = tk.Tk()
    root.withdraw()
    root.update()  # Ensure dialog appears in Spyder
    file_path = filedialog.askopenfilename(
        initialdir="logs/",
        title="Select a CSV File",
        filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
    )
    root.destroy()
    return file_path

# Load data from the selected CSV and plot it
def load_and_plot_csv(file_path):
    timestamps = []
    lidar = []
    ultra1 = []
    ultra2 = []
    average = []
    tilt = []

    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            try:
                timestamps.append(row["Timestamp"])
                lidar.append(float(row["LIDAR"]))
                ultra1.append(float(row["Ultrasonic1"]))
                ultra2.append(float(row["Ultrasonic2"]))
                average.append(float(row["Average"]))
                tilt.append(float(row["Tilt"]))
            except Exception as e:
                print(f"Skipping row {i} due to error: {e}")

    x = list(range(len(lidar)))  # Use sample index as x-axis

    # Plot sensor heights
    plt.figure(figsize=(12, 6))
    plt.plot(x, lidar, label='LIDAR')
    plt.plot(x, ultra1, label='Ultrasonic 1')
    plt.plot(x, ultra2, label='Ultrasonic 2')
    plt.plot(x, average, label='Average', linestyle='--')

    plt.title("Sensor Heights Over Samples")
    plt.xlabel("Sample Number")
    plt.ylabel("Height (inches)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Plot tilt separately
    plt.figure(figsize=(12, 4))
    plt.plot(x, tilt, label='Tilt', color='orange')
    plt.title("Tilt Angle Over Samples")
    plt.xlabel("Sample Number")
    plt.ylabel("Tilt (°)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Run the script
if __name__ == "__main__":
    file_path = select_csv_file()
    if file_path:
        print(f"Plotting: {file_path}")
        load_and_plot_csv(file_path)
    else:
        print("No file selected.")
