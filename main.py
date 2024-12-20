import customtkinter as ctk

app = ctk.CTk()
app.geometry("600x400")
app.title("SoundWatcher PoC")

# Sidebar (Logs)
logs_label = ctk.CTkLabel(app, text="Logs")
logs_label.grid(row=0, column=0, sticky="nsew")

# Map Area
map_label = ctk.CTkLabel(app, text="Map")
map_label.grid(row=0, column=1, sticky="nsew")

# Bottom Section
real_time_button = ctk.CTkButton(app, text="Real-Time Audio")
real_time_button.grid(row=1, column=0, sticky="ew")

simulate_button = ctk.CTkButton(app, text="Simulate")
simulate_button.grid(row=1, column=1, sticky="ew")

app.mainloop()