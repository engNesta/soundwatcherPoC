import customtkinter as ctk
from tkintermapview import TkinterMapView
from tkinter import messagebox, filedialog
import threading
import time
import json
from audio_capture import AudioCapture
from model_inference import run_inference


class SoundwatcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Soundwatcher PoC - Full Layout with CTk Buttons")
        self.geometry("1280x720")
        self.configure_grid()
        self.running = True  # To manage thread termination
        self.loaded_log_ids = set()  # Track already displayed log IDs
        self.threshold_value = 90  # Default detection threshold

        # Sidebar (Logs Section)
        self.sidebar = ctk.CTkScrollableFrame(self, width=300)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="ns", padx=10, pady=10)
        self.sidebar_label = ctk.CTkLabel(self.sidebar, text="Logs", font=ctk.CTkFont(size=16, weight="bold"))
        self.sidebar_label.pack(pady=5)

        self.logs_container = ctk.CTkFrame(self.sidebar)
        self.logs_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Map Section
        self.map_view = TkinterMapView(self, width=800, height=400, corner_radius=0)
        self.map_view.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.after(100, lambda: self.map_view.set_position(56.0, 14.0))
        self.after(100, lambda: self.map_view.set_zoom(10))

        # Add real CTk buttons for microphones
        self.after(200, self.add_microphone_buttons)

        # Realtime, Simulation, and Prediction Section
        self.bottom_frame = ctk.CTkFrame(self, width=800)
        self.bottom_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=10)
        self.bottom_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # 1. Realtime Audio Section
        self.realtime_frame = ctk.CTkFrame(self.bottom_frame, corner_radius=10)
        self.realtime_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(self.realtime_frame, text="Microphone ID# Realtime Volume", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.realtime_volume_label = ctk.CTkLabel(self.realtime_frame, text="- dB", font=ctk.CTkFont(size=36, weight="bold"))
        self.realtime_volume_label.pack(pady=10)

        # Threshold slider and set button
        self.threshold_slider = ctk.CTkSlider(self.realtime_frame, from_=70, to=130, number_of_steps=50, command=self.update_threshold_label)
        self.threshold_slider.set(self.threshold_value)  # Set default value
        self.threshold_slider.pack(pady=5)

        self.threshold_label = ctk.CTkLabel(self.realtime_frame, text=f"Threshold: {self.threshold_value:.2f} dB")
        self.threshold_label.pack(pady=2)

        self.set_threshold_button = ctk.CTkButton(self.realtime_frame, text="Set", command=self.set_threshold)
        self.set_threshold_button.pack(pady=5)

        # 2. Simulation Section
        self.simulation_frame = ctk.CTkFrame(self.bottom_frame, corner_radius=10)
        self.simulation_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(self.simulation_frame, text="Event Simulation", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.upload_button = ctk.CTkButton(self.simulation_frame, text="Upload WAV audio", command=self.simulate_audio)
        self.upload_button.pack(pady=10)
        self.simulate_event_button = ctk.CTkButton(self.simulation_frame, text="Simulate Event", fg_color="#FF4500", command=self.simulate_event)
        self.simulate_event_button.pack(pady=10)

        # 3. Prediction Section
        self.prediction_frame = ctk.CTkFrame(self.bottom_frame, corner_radius=10)
        self.prediction_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(self.prediction_frame, text="Prediction", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.prediction_label = ctk.CTkLabel(self.prediction_frame, text="Prediction: -", font=ctk.CTkFont(size=14))
        self.prediction_label.pack(pady=5)
        self.confidence_label = ctk.CTkLabel(self.prediction_frame, text="Confidence: -%", font=ctk.CTkFont(size=14))
        self.confidence_label.pack(pady=5)

        # Initialize Audio Capture and Logs Thread
        self.audio_capture = AudioCapture()
        self.audio_thread = threading.Thread(target=self.start_realtime_audio, daemon=True)
        self.audio_thread.start()

        self.logs_thread = threading.Thread(target=self.fetch_logs, daemon=True)
        self.logs_thread.start()

        # Bind closing event
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def configure_grid(self):
        self.grid_rowconfigure(0, weight=5)  # Map section
        self.grid_rowconfigure(1, weight=3)  # Bottom section
        self.grid_columnconfigure(1, weight=1)

    def update_threshold_label(self, value):
        """
        Update the threshold label as the slider moves.
        """
        self.threshold_label.configure(text=f"Threshold: {float(value):.2f} dB")

    def set_threshold(self):
        """
        Set the current threshold value from the slider.
        """
        self.threshold_value = self.threshold_slider.get()
        print(f"Threshold set to: {self.threshold_value:.2f} dB")

    def add_microphone_buttons(self):
        microphones = [
            {"id": "Mic001", "lat": 56.2, "lon": 14.2, "ip": "192.168.1.101"},
            {"id": "Mic002", "lat": 56.88, "lon": 14.05, "ip": "192.168.1.102"},
            {"id": "Mic003", "lat": 55.35, "lon": 13.35, "ip": "192.168.1.103"}
        ]
        for mic in microphones:
            x, y = self.convert_coordinates_to_pixels(mic["lat"], mic["lon"])
            button = ctk.CTkButton(self.map_view, text=mic["id"], fg_color="red", text_color="white", width=40, height=20,
                                   command=lambda m=mic: self.show_microphone_popup(m))
            button.place(x=x, y=y)

    def convert_coordinates_to_pixels(self, lat, lon):
        center_lat, center_lon = self.map_view.get_position()
        zoom = 10
        scale_factor = 500 * (1.0 / zoom)  # Adjust scale factor for zoom
        delta_lat = (lat - center_lat) * scale_factor
        delta_lon = (lon - center_lon) * scale_factor
        return 400 + delta_lon, 200 - delta_lat

    def show_microphone_popup(self, mic):
        details = f"ID: {mic['id']}\nLocation: ({mic['lat']}, {mic['lon']})\nIP Address: {mic['ip']}"
        messagebox.showinfo("Microphone Details", details)

    def start_realtime_audio(self):
        try:
            while self.running:
                audio_data, volume_db = self.audio_capture.get_audio_data()
                if not self.running:  # Avoid UI updates after shutdown
                    break
                self.realtime_volume_label.configure(text=f"{volume_db:.2f} dB")

                # Check if the detected volume exceeds the dynamic threshold
                if volume_db > self.threshold_value and audio_data is not None:
                    label, confidence = run_inference(audio_data)
                    self.prediction_label.configure(text=f"Prediction: {label}")
                    self.confidence_label.configure(text=f"Confidence: {confidence:.2f}%")
        except Exception as e:
            print(f"Error in real-time audio: {e}")

    def fetch_logs(self):
        try:
            while self.running:
                with open("logs.json", "r") as log_file:
                    logs = json.load(log_file)
                    for log in logs:
                        log_id = log.get("id")
                        if log_id not in self.loaded_log_ids:
                            self.add_log_to_sidebar(log)
                            self.loaded_log_ids.add(log_id)
                time.sleep(2)
        except Exception as e:
            print(f"Error fetching logs: {e}")

    def add_log_to_sidebar(self, log):
        log_id = log.get("id", "Unknown")
        button_text = f"Log {log_id}"
        ctk.CTkButton(
            self.logs_container,
            text=button_text,
            command=lambda l=log: self.show_log_popup(l)
        ).pack(pady=2, padx=2, anchor="w")

    def show_log_popup(self, log):
        details = f"Time: {log['time']}\nVolume: {log['volume']}\nPrediction: {log['prediction']}"
        messagebox.showinfo("Log Details", details)

    def simulate_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav")])
        if file_path:
            threading.Thread(target=self.run_simulation, args=(file_path,), daemon=True).start()

    def simulate_event(self):
        threading.Thread(target=self.run_simulation_event, daemon=True).start()

    def run_simulation(self, file_path):
        try:
            with open(file_path, "rb") as f:
                audio_data = f.read()
            label, confidence = run_inference(audio_data)
            self.prediction_label.configure(text=f"Prediction: {label}")
            self.confidence_label.configure(text=f"Confidence: {confidence:.2f}%")
        except Exception as e:
            print(f"Error in simulation: {e}")

    def run_simulation_event(self):
        try:
            audio_data = [0] * 16000
            label, confidence = run_inference(audio_data)
            self.prediction_label.configure(text=f"Prediction: {label}")
            self.confidence_label.configure(text=f"Confidence: {confidence:.2f}%")
        except Exception as e:
            print(f"Error in simulation event: {e}")

    def on_close(self):
        self.running = False
        self.destroy()


if __name__ == "__main__":
    app = SoundwatcherApp()
    app.mainloop()
