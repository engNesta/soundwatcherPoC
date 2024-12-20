import customtkinter as ctk
from tkintermapview import TkinterMapView
from tkinter import filedialog, messagebox
import threading

# Main application class
class SoundwatcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Soundwatcher PoC")
        self.geometry("1280x720")
        self.configure_grid()
        
        # Sidebar (Logs Section)
        self.sidebar = ctk.CTkScrollableFrame(self, width=300)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="ns", padx=10, pady=10)  # Span two rows
        self.sidebar_label = ctk.CTkLabel(self.sidebar, text="Logs", font=ctk.CTkFont(size=16, weight="bold"))
        self.sidebar_label.pack(pady=5)
        
        # Map Section
        self.map_view = TkinterMapView(self, width=800, height=400, corner_radius=10)
        self.map_view.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)  # Map at the top-right
        self.map_view.set_position(56.0, 14.0)  # Example location
        self.map_view.set_zoom(10)
        self.add_microphone_buttons()
        
        # Realtime, Simulation, and Prediction Section
        self.bottom_frame = ctk.CTkFrame(self, width=800)
        self.bottom_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=10)  # Place below the map
        
        # Configure bottom frame into three sections
        self.bottom_frame.grid_columnconfigure((0, 1, 2), weight=1)  # Three equal sections
        
        # 1. Realtime Audio Section
        self.realtime_frame = ctk.CTkFrame(self.bottom_frame, corner_radius=10)
        self.realtime_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(self.realtime_frame, text="Microphone ID# Realtime Volume", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.realtime_volume_label = ctk.CTkLabel(self.realtime_frame, text="- dB", font=ctk.CTkFont(size=36, weight="bold"))
        self.realtime_volume_label.pack(pady=20)
        
        # 2. Simulation Section
        self.simulation_frame = ctk.CTkFrame(self.bottom_frame, corner_radius=10)
        self.simulation_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(self.simulation_frame, text="Event Simulation", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.upload_button = ctk.CTkButton(self.simulation_frame, text="Upload WAV audio", command=self.simulate_audio)
        self.upload_button.pack(pady=10)
        self.simulate_event_button = ctk.CTkButton(self.simulation_frame, text="Simulate Event", command=self.simulate_event, fg_color="#FF4500")  # Cherry red
        self.simulate_event_button.pack(pady=10)
        
        
        # 3. Prediction Section
        self.prediction_frame = ctk.CTkFrame(self.bottom_frame, corner_radius=10)
        self.prediction_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(self.prediction_frame, text="Prediction", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.prediction_label = ctk.CTkLabel(self.prediction_frame, text="Prediction: -", font=ctk.CTkFont(size=14))
        self.prediction_label.pack(pady=5)
        self.confidence_label = ctk.CTkLabel(self.prediction_frame, text="Confidence: -%", font=ctk.CTkFont(size=14))
        self.confidence_label.pack(pady=5)
    
    def configure_grid(self):
        self.grid_rowconfigure(0, weight=1)  # Map section row
        self.grid_rowconfigure(1, weight=0)  # Realtime, Simulation, and Prediction section row
        self.grid_columnconfigure(1, weight=1)  # Map and bottom section column
    
    def add_microphone_buttons(self):
        # Define fake microphone positions
        microphones = [
            {"id": "Mic001", "lat": 56.0, "lon": 14.2, "ip": "192.168.1.101"},
            {"id": "Mic002", "lat": 56.05, "lon": 14.05, "ip": "192.168.1.102"},
            {"id": "Mic003", "lat": 55.75, "lon": 13.35, "ip": "192.168.1.103"}
        ]
    
        # Add buttons for each microphone
        for mic in microphones:
            x, y = self.convert_coordinates_to_pixels(mic["lat"], mic["lon"])
            print(f"Placing button for {mic['id']} at: ({x}, {y})")  # Debugging coordinates
            button = ctk.CTkButton(self.map_view.canvas,
                                   text=mic["id"],
                                   fg_color="red",
                                   width=30, height=20,
                                   command=lambda m=mic: self.show_microphone_popup(m))
            button.place(x=x, y=y)


    def convert_coordinates_to_pixels(self, lat, lon):
        # Custom conversion logic based on map position and zoom
        center_lat, center_lon = self.map_view.get_position()
        delta_lat = (lat - center_lat) * 500  # Adjust multiplier as needed
        delta_lon = (lon - center_lon) * 500  # Adjust multiplier as needed
        return 400 + delta_lon, 200 - delta_lat  # Offset for the map's position

    def show_microphone_popup(self, mic):
        # Show microphone details in a popup
        details = f"ID: {mic['id']}\nLocation: ({mic['lat']}, {mic['lon']})\nIP Address: {mic['ip']}"
        print(f"Popup triggered for: {details}")  # Debugging
        messagebox.showinfo("Microphone Details", details)

    def simulate_audio(self):
        # Simulate audio handling logic
        file_path = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav")])
        if file_path:
            self.simulation_result_label.configure(text=f"Simulating: {file_path.split('/')[-1]}")
            threading.Thread(target=self.run_simulation, args=(file_path,), daemon=True).start()
    
    def simulate_event(self):
        # Simulate event logic without a file
        self.simulation_result_label.configure(text="Simulating Event...")
        threading.Thread(target=self.run_simulation_event, daemon=True).start()
    
    def run_simulation(self, file_path):
        # Placeholder: Simulate processing the WAV file
        import time
        time.sleep(2)
        self.simulation_result_label.configure(text="Prediction: Gunshot, Confidence: 85%")

    def run_simulation_event(self):
        # Placeholder: Simulate an event directly
        import time
        time.sleep(2)
        self.simulation_result_label.configure(text="Prediction: Firework, Confidence: 90%")


if __name__ == "__main__":
    app = SoundwatcherApp()
    app.mainloop()

