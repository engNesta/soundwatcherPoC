import customtkinter as ctk
from tkintermapview import TkinterMapView
from tkinter import messagebox


class SoundwatcherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Soundwatcher PoC - Full Layout with CTk Buttons")
        self.geometry("1280x720")
        self.configure_grid()
        
        # Sidebar (Logs Section)
        self.sidebar = ctk.CTkScrollableFrame(self, width=300)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="ns", padx=10, pady=10)
        self.sidebar_label = ctk.CTkLabel(self.sidebar, text="Logs", font=ctk.CTkFont(size=16, weight="bold"))
        self.sidebar_label.pack(pady=5)
        
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
        self.realtime_volume_label.pack(pady=20)
        
        # 2. Simulation Section
        self.simulation_frame = ctk.CTkFrame(self.bottom_frame, corner_radius=10)
        self.simulation_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        ctk.CTkLabel(self.simulation_frame, text="Event Simulation", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.upload_button = ctk.CTkButton(self.simulation_frame, text="Upload WAV audio")
        self.upload_button.pack(pady=10)
        self.simulate_event_button = ctk.CTkButton(self.simulation_frame, text="Simulate Event", fg_color="#FF4500")
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
        self.grid_rowconfigure(0, weight=5)  # Map section
        self.grid_rowconfigure(1, weight=3)  # Bottom section
        self.grid_columnconfigure(1, weight=1)

    def add_microphone_buttons(self):
        """
        Add CTk buttons with "MicID" as the text on the buttons.
        """
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
        """
        Convert lat/lon to approximate x, y coordinates for map.
        """
        center_lat, center_lon = self.map_view.get_position()
        zoom = 10
        scale_factor = 500 * (1.0 / zoom)  # Adjust scale factor for zoom
        delta_lat = (lat - center_lat) * scale_factor
        delta_lon = (lon - center_lon) * scale_factor
        return 400 + delta_lon, 200 - delta_lat

    def show_microphone_popup(self, mic):
        """
        Show a popup with microphone details.
        """
        details = f"ID: {mic['id']}\nLocation: ({mic['lat']}, {mic['lon']})\nIP Address: {mic['ip']}"
        messagebox.showinfo("Microphone Details", details)


if __name__ == "__main__":
    app = SoundwatcherApp()
    app.mainloop()
