import customtkinter as ctk
from tkintermapview import TkinterMapView
from tkinter import filedialog
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
        
        # Realtime & Simulation Section
        self.bottom_frame = ctk.CTkFrame(self, width=800)
        self.bottom_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=10)  # Place below the map
        
        self.realtime_label = ctk.CTkLabel(self.bottom_frame, text="Real-Time Audio", font=ctk.CTkFont(size=16, weight="bold"))
        self.realtime_label.grid(row=0, column=0, pady=5, padx=5, sticky="w")
        
        self.volume_label = ctk.CTkLabel(self.bottom_frame, text="Volume: - dB")
        self.volume_label.grid(row=1, column=0, pady=5, padx=5, sticky="w")
        
        self.prediction_label = ctk.CTkLabel(self.bottom_frame, text="Prediction: -")
        self.prediction_label.grid(row=2, column=0, pady=5, padx=5, sticky="w")
        
        self.confidence_label = ctk.CTkLabel(self.bottom_frame, text="Confidence: -%")
        self.confidence_label.grid(row=3, column=0, pady=5, padx=5, sticky="w")
        
        self.simulation_label = ctk.CTkLabel(self.bottom_frame, text="Simulate Audio", font=ctk.CTkFont(size=16, weight="bold"))
        self.simulation_label.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        
        self.upload_button = ctk.CTkButton(self.bottom_frame, text="Upload WAV", command=self.simulate_audio)
        self.upload_button.grid(row=1, column=1, pady=5, padx=5)
        
        self.simulation_result_label = ctk.CTkLabel(self.bottom_frame, text="Result: -")
        self.simulation_result_label.grid(row=2, column=1, pady=5, padx=5, sticky="w")
    
    def configure_grid(self):
        self.grid_rowconfigure(0, weight=1)  # Map section row
        self.grid_rowconfigure(1, weight=0)  # Realtime & simulation section row
        self.grid_columnconfigure(1, weight=1)  # Map and bottom section column
    
    def simulate_audio(self):
        # Simulate audio handling logic
        file_path = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav")])
        if file_path:
            self.simulation_result_label.configure(text=f"Simulating: {file_path.split('/')[-1]}")
            threading.Thread(target=self.run_simulation, args=(file_path,), daemon=True).start()
    
    def run_simulation(self, file_path):
        # Placeholder: Simulate processing the WAV file
        import time
        time.sleep(2)
        self.simulation_result_label.configure(text="Prediction: Gunshot, Confidence: 85%")


if __name__ == "__main__":
    app = SoundwatcherApp()
    app.mainloop()