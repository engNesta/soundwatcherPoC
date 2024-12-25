import customtkinter as ctk
from tkintermapview import TkinterMapView
from tkinter import messagebox, filedialog
import threading
import time
import json
import os
from audio_capture import AudioCapture
from model_inference import run_inference
import librosa
import numpy as np


class SoundwatcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Soundwatcher PoC - Full Layout with Info Buttons")
        self.geometry("1280x720")
        self.running = True
        self.loaded_log_ids = set()
        self.threshold_value = 90
        self.audio_file_path = None
        self.log_file_path = "logs.json"

        # Initialize AudioCapture
        self.audio_capture = AudioCapture()

        # Configure grid layout
        self.configure_grid()

        # Sidebar (Logs Section)
        self.sidebar = ctk.CTkScrollableFrame(self, width=300)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="ns", padx=10, pady=10)
        self.sidebar_label = ctk.CTkLabel(self.sidebar, text="Logs", font=ctk.CTkFont(size=16, weight="bold"))
        self.sidebar_label.pack(pady=5)

        self.logs_container = ctk.CTkFrame(self.sidebar)
        self.logs_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Add info button for Logs section
        
        info_logs_button = ctk.CTkButton(self.logs_container, text="?", width=25, height=25, command=self.show_logs_info)
        info_logs_button.pack(side="bottom", anchor="se", pady=5, padx=5)  # Align bottom-right


        # Map Section
        self.map_view = TkinterMapView(self, width=800, height=400, corner_radius=0)
        self.map_view.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.map_view.set_position(56.0, 14.0)
        self.map_view.set_zoom(10)
        self.add_microphone_markers()

        # Add info button for Map section
        info_map_button = ctk.CTkButton(self.map_view, text="?", width=25, height=25, command=self.show_map_info)
        info_map_button.place(relx=1.0, rely=1.0, anchor="se")  # Position at bottom-right


        

        # Bottom Frame
        self.bottom_frame = ctk.CTkFrame(self, width=800)
        self.bottom_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=10)
        self.bottom_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Realtime Audio Section
        self.realtime_frame = ctk.CTkFrame(self.bottom_frame, corner_radius=10)
        self.realtime_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(self.realtime_frame, text="Microphone ID# Realtime Volume", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.realtime_volume_label = ctk.CTkLabel(self.realtime_frame, text="- dB", font=ctk.CTkFont(size=36, weight="bold"))
        self.realtime_volume_label.pack(pady=10)

        self.threshold_slider = ctk.CTkSlider(self.realtime_frame, from_=70, to=130, number_of_steps=50, command=self.update_threshold_label)
        self.threshold_slider.set(self.threshold_value)
        self.threshold_slider.pack(pady=5)

        self.threshold_label = ctk.CTkLabel(self.realtime_frame, text=f"Threshold: {self.threshold_value:.2f} dB")
        self.threshold_label.pack(pady=2)

        self.set_threshold_button = ctk.CTkButton(self.realtime_frame, text="Set", command=self.set_threshold)
        self.set_threshold_button.pack(pady=5)

        # Add info button for Realtime section
        info_realtime_button = ctk.CTkButton(self.realtime_frame, text="?", width=25, height=25, command=self.show_realtime_info)
        info_realtime_button.pack(side="bottom", anchor="se", pady=5, padx=5)  # Align bottom-right


        # Simulation Section
        self.simulation_frame = ctk.CTkFrame(self.bottom_frame, corner_radius=10)
        self.simulation_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(self.simulation_frame, text="Event Simulation", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        self.upload_button = ctk.CTkButton(self.simulation_frame, text="Upload WAV audio", command=self.simulate_audio)
        self.upload_button.pack(pady=10)

        self.simulate_event_button = ctk.CTkButton(self.simulation_frame, text="Simulate Event", state="disabled", command=self.simulate_event)
        self.simulate_event_button.pack(pady=10)

        self.audio_file_label = ctk.CTkLabel(self.simulation_frame, text="No audio loaded", font=ctk.CTkFont(size=12))
        self.audio_file_label.pack(pady=5)

        # Add info button for Simulation section
        info_simulation_button = ctk.CTkButton(self.simulation_frame, text="?", width=25, height=25, command=self.show_simulation_info)
        info_simulation_button.pack(side="bottom", anchor="se", pady=5, padx=5)  # Align bottom-right


        # Prediction Section
        self.prediction_frame = ctk.CTkFrame(self.bottom_frame, corner_radius=10)
        self.prediction_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(self.prediction_frame, text="Prediction", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.prediction_label = ctk.CTkLabel(self.prediction_frame, text="Prediction: -", font=ctk.CTkFont(size=14))
        self.prediction_label.pack(pady=5)
        self.confidence_label = ctk.CTkLabel(self.prediction_frame, text="Confidence: -%", font=ctk.CTkFont(size=14))
        self.confidence_label.pack(pady=5)

        # Add info button for Prediction section
        info_prediction_button = ctk.CTkButton(self.prediction_frame, text="?", width=25, height=25, command=self.show_prediction_info)
        info_prediction_button.pack(side="bottom", anchor="se", pady=5, padx=5)  # Align bottom-right


        # Start Threads
        self.audio_thread = threading.Thread(target=self.start_realtime_audio, daemon=True)
        self.audio_thread.start()

        self.logs_thread = threading.Thread(target=self.fetch_logs, daemon=True)
        self.logs_thread.start()

        # Closing Event
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def configure_grid(self):
        self.grid_rowconfigure(0, weight=5)
        self.grid_rowconfigure(1, weight=3)
        self.grid_columnconfigure(1, weight=1)

    def update_threshold_label(self, value):
        self.threshold_label.configure(text=f"Threshold: {float(value):.2f} dB")

    def set_threshold(self):
        self.threshold_value = self.threshold_slider.get()

    def add_microphone_markers(self):
        microphones = [
            {"id": "Mic001", "lat": 55.93, "lon": 13.54},
            {"id": "Mic002", "lat": 56.04, "lon": 14.46},
            {"id": "Mic003", "lat": 55.97, "lon": 14.17}
        ]
        for mic in microphones:
            marker = self.map_view.set_marker(mic["lat"], mic["lon"], text=mic["id"])
            marker.data = mic  # Store microphone data in the marker object

    def start_realtime_audio(self):
        try:
            while self.running:
                audio_data, volume_db = self.audio_capture.get_audio_data()
                self.realtime_volume_label.configure(text=f"{volume_db:.2f} dB")

                # Check if the volume exceeds the threshold
                if volume_db > self.threshold_value:
                    label, confidence = run_inference(audio_data)
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    event_id = f"RT-{len(self.loaded_log_ids) + 1}"
                    self.register_log(event_id, timestamp, f"{volume_db:.2f}", label)
        except Exception as e:
            print(f"Error in real-time audio: {e}")

    def simulate_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav")])
        if file_path:
            self.audio_file_path = file_path
            self.audio_file_label.configure(text=f"Loaded: {os.path.basename(file_path)}")
            self.simulate_event_button.configure(state="normal")

    def simulate_event(self):
        if not self.audio_file_path:
            self.prediction_label.configure(text="Prediction: Error")
            self.confidence_label.configure(text="Confidence: Error")
            return

        try:
            audio_data, sr = librosa.load(self.audio_file_path, sr=16000)
            audio_data = (audio_data * 32768).astype(np.int16)

            label, confidence = run_inference(audio_data)
            self.prediction_label.configure(text=f"Prediction: {label}")
            self.confidence_label.configure(text=f"Confidence: {confidence:.2f}%")

            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            event_id = f"Sim-{len(self.loaded_log_ids) + 1}"
            self.register_log(event_id, timestamp, "-", label)
        except Exception as e:
            print(f"Error during simulation: {e}")
            self.prediction_label.configure(text="Prediction: Error")
            self.confidence_label.configure(text="Confidence: Error")

    def fetch_logs(self):
        try:
            if not os.path.exists(self.log_file_path):
                with open(self.log_file_path, "w") as f:
                    json.dump([], f)

            with open(self.log_file_path, "r") as f:
                logs = json.load(f)
                for log in logs:
                    if log["id"] not in self.loaded_log_ids:
                        self.register_log(log["id"], log["time"], log["volume"], log["prediction"])
        except Exception as e:
            print(f"Error fetching logs: {e}")

    def register_log(self, event_id, timestamp, volume, prediction):
        if event_id not in self.loaded_log_ids:
            self.loaded_log_ids.add(event_id)

            # Add the log to the UI
            log_button = ctk.CTkButton(
                self.logs_container,
                text=f"Log {event_id}",
                command=lambda: self.show_log_popup({"id": event_id, "time": timestamp, "volume": volume, "prediction": prediction})
            )
            log_button.pack(pady=2)

            # Save the log to logs.json
            self.save_log_to_file(event_id, timestamp, volume, prediction)

    def save_log_to_file(self, event_id, timestamp, volume, prediction):
        try:
            with open(self.log_file_path, "r") as f:
                logs = json.load(f)

            logs.append({"id": event_id, "time": timestamp, "volume": volume, "prediction": prediction})

            with open(self.log_file_path, "w") as f:
                json.dump(logs, f, indent=4)
        except Exception as e:
            print(f"Error saving log: {e}")

    def show_log_popup(self, log):
        details = f"Time: {log['time']}\nVolume: {log['volume']}\nPrediction: {log['prediction']}"
        messagebox.showinfo("Log Details", details)

    def show_logs_info(self):
        messagebox.showinfo(
            "Logs Info",
            "This section displays all registered events, both simulated and real-time. "
            "Click on a log button to view detailed information about an event."
        )

    def show_map_info(self):
        messagebox.showinfo(
            "Map Info",
            "The map displays the geographical locations of the microphones. "
            "Markers represent the physical position of sensors."
        )

    def show_realtime_info(self):
        messagebox.showinfo(
            "Realtime Audio Info",
            "This section monitors the real-time audio captured from the microphone. "
            "It displays the current volume and allows you to set a detection threshold."
        )

    def show_simulation_info(self):
        messagebox.showinfo(
            "Simulation Info",
            "This section allows you to simulate events by uploading audio files. "
            "Click 'Simulate Event' after uploading to test the system."
        )

    def show_prediction_info(self):
        messagebox.showinfo(
            "Prediction Info",
            "This section shows the result of the system's analysis. "
            "It displays the predicted event type and confidence level."
        )

    def on_close(self):
        self.running = False
        self.destroy()


if __name__ == "__main__":
    app = SoundwatcherApp()
    app.mainloop()
