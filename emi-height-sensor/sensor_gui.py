# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 11:23:06 2025

@author: elija
"""
import sys
import os
import csv
import datetime
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QGroupBox, QLineEdit
)
from PyQt5.QtCore import QTimer

class SensorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sensor Dashboard")
        self.resize(400, 350)

        # Serial setup
        self.serial_port = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial)

        # Logging
        self.recording = False
        self.csv_file = None
        self.csv_writer = None
        
        # Timer
        self.start_time = None
        self.elapsed_timer = QTimer()
        self.elapsed_timer.timeout.connect(self.update_elapsed_label)
        
        # Simple Moving Average (SMA)
        self.buffer_size = 5  
        self.buffers = {
            "lidar": [],
            "ultra1": [],
            "ultra2": [],
            "average": [],
            "tilt": []
        }

        self.init_ui()
        
    def smooth(self, key, new_value):
        buffer = self.buffers[key]
        buffer.append(float(new_value))
        if len(buffer) > self.buffer_size:
            buffer.pop(0)
        return sum(buffer) / len(buffer)

    def init_ui(self):
        layout = QVBoxLayout()

        # COM Port selection
        com_layout = QHBoxLayout()
        self.com_dropdown = QComboBox()
        self.refresh_com_ports()
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_serial)
        com_layout.addWidget(QLabel("Select COM Port:"))
        com_layout.addWidget(self.com_dropdown)
        com_layout.addWidget(self.connect_button)

        self.status_label = QLabel("Not connected")
        self.status_label.setStyleSheet("color: red")

        # Filename input
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("Enter file name (optional)")

        # Sensor labels
        self.lidar_label = QLabel("LIDAR: ---")
        self.ultra1_label = QLabel("Ultrasonic 1: ---")
        self.ultra2_label = QLabel("Ultrasonic 2: ---")
        self.avg_label = QLabel("Average: ---")
        self.tilt_label = QLabel("Tilt: ---")

        sensor_group = QGroupBox("Sensor Readings")
        sensor_layout = QVBoxLayout()
        sensor_layout.addWidget(self.lidar_label)
        sensor_layout.addWidget(self.ultra1_label)
        sensor_layout.addWidget(self.ultra2_label)
        sensor_layout.addWidget(self.avg_label)
        sensor_layout.addWidget(self.tilt_label)
        sensor_group.setLayout(sensor_layout)

        # Start/Stop recording
        self.record_button = QPushButton("Start Recording")
        self.record_button.clicked.connect(self.toggle_recording)
        self.elapsed_label = QLabel("Recording Time: 00:00:00")
        layout.addWidget(self.elapsed_label)
        self.elapsed_label.hide()  # Hide by default until recording starts

        # Assemble layout
        layout.addLayout(com_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(self.filename_input)
        layout.addWidget(sensor_group)
        layout.addWidget(self.record_button)

        self.setLayout(layout)

    def update_elapsed_label(self):
        if self.start_time:
            elapsed = datetime.datetime.now() - self.start_time
            hours, remainder = divmod(elapsed.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.elapsed_label.setText(f"Recording Time: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")

    def refresh_com_ports(self):
        self.com_dropdown.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.com_dropdown.addItem(port.device)

    def connect_serial(self):
        port_name = self.com_dropdown.currentText()
        try:
            self.serial_port = serial.Serial(port_name, 115200, timeout=1)
            self.status_label.setText(f"Connected to {port_name}")
            self.status_label.setStyleSheet("color: green")
            self.timer.start(100)  # Poll every 100ms
        except Exception as e:
            self.status_label.setText(f"Connection failed: {e}")
            self.status_label.setStyleSheet("color: red")

    def toggle_recording(self):
        if not self.recording:
            if not os.path.exists("logs"):
                os.makedirs("logs")

            base_name = self.filename_input.text().strip()
            if base_name == "":
                base_name = datetime.datetime.now().strftime("sensor_log_%Y-%m-%d_%H-%M-%S")
            filename = os.path.join("logs", base_name + ".csv")

            try:
                self.csv_file = open(filename, mode='w', newline='')
                self.csv_writer = csv.writer(self.csv_file)
                self.csv_writer.writerow(["Timestamp", "LIDAR", "Ultrasonic1", "Ultrasonic2", "Average", "Tilt"])
                self.start_time = datetime.datetime.now()
                self.recording = True
                self.record_button.setText("Stop Recording")
                print(f"Recording started: {filename}")
                self.elapsed_label.show()
                self.update_elapsed_label()
                self.elapsed_timer.start(1000)
            except Exception as e:
                print(f"Failed to open file: {e}")
        else:
            if self.csv_file:
                self.csv_file.close()
                self.csv_file = None
            self.recording = False
            self.record_button.setText("Start Recording")
            print("Recording stopped.")
            self.elapsed_timer.stop()
            self.elapsed_label.hide()
            self.elapsed_label.setText("Recording Time: 00:00:00")

    def read_serial(self):
        if self.serial_port and self.serial_port.in_waiting:
            try:
                line = self.serial_port.readline().decode().strip()
                parts = line.split(",")

                if len(parts) == 5:
                    # Apply smoothing
                    smoothed = {
                        "lidar": self.smooth("lidar", parts[0]),
                        "ultra1": self.smooth("ultra1", parts[1]),
                        "ultra2": self.smooth("ultra2", parts[2]),
                        "average": self.smooth("average", parts[3]),
                        "tilt": self.smooth("tilt", parts[4])
                    }
                
                    # Update GUI
                    self.lidar_label.setText(f"LIDAR: {smoothed['lidar']:.2f}")
                    self.ultra1_label.setText(f"Ultrasonic 1: {smoothed['ultra1']:.2f}")
                    self.ultra2_label.setText(f"Ultrasonic 2: {smoothed['ultra2']:.2f}")
                    self.avg_label.setText(f"Average: {smoothed['average']:.2f}")
                    self.tilt_label.setText(f"Tilt: {smoothed['tilt']:.2f}")
                
                    # Write to CSV (if recording)
                    if self.recording and self.csv_writer:
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                        
                        row = [
                            timestamp,
                            f"{smoothed['lidar']:.2f}",
                            f"{smoothed['ultra1']:.2f}",
                            f"{smoothed['ultra2']:.2f}",
                            f"{smoothed['average']:.2f}",
                            f"{smoothed['tilt']:.2f}"
                        ]
                        self.csv_writer.writerow(row)


            except Exception as e:
                print(f"Error reading serial: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SensorApp()
    window.show()
    sys.exit(app.exec_())
