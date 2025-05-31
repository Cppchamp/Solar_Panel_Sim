import threading
import tkinter as tk
from tkinter import ttk

import simulation

# -------------------------
# Main Window Setup
# -------------------------
root = tk.Tk()
main_canvas = tk.Canvas(root, bg="#fff4e6", highlightthickness=0)
main_canvas.pack(side="left", fill="both", expand=True)

# --- Add scrollbar ---
scrollbar = ttk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
scrollbar.pack(side="right", fill="y")

# --- Configure canvas scrolling ---
main_canvas.configure(yscrollcommand=scrollbar.set)

# --- Create an interior frame for content ---
scrollable_frame = ttk.Frame(main_canvas)
scrollable_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))

# --- Add the frame to the canvas ---
window_id = main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")


def _on_mousewheel(event):
    main_canvas.yview_scroll(-int(event.delta / 120), "units")


main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

root.title("🌞 Solar Panel Control Panel")
root.geometry("600x750")
root.configure(bg="#fff4e6")  # Soft off-white with warm undertone


def on_canvas_configure(event):
    # Set the scrollable_frame width to match canvas width
    canvas_width = event.width
    main_canvas.itemconfig(window_id, width=canvas_width)


main_canvas.bind("<Configure>", on_canvas_configure)

# -------------------------
# Styles
# -------------------------
style = ttk.Style()
style.theme_use("clam")

deep_orange = "#d35400"  # Deep orange base
dark_deep_orange = "#a84300"  # Darker shade for pressed
hover_orange = "#e67e22"  # Hover bright orange
text_dark = "#4e2a00"  # Dark brown text for contrast
frame_bg = "#ffe6cc"  # Light orange-beige for frames

style.configure("TLabel",
                background="#fff4e6",
                font=("Segoe UI", 12),
                foreground=text_dark)

style.configure("TButton",
                font=("Segoe UI", 11, "bold"),
                padding=8,
                foreground="#fff4e6",  # Light text on buttons
                background=deep_orange)

style.map("TButton",
          background=[("active", hover_orange), ("pressed", dark_deep_orange)])

style.configure("TFrame", background="#fff4e6")

style.configure("TLabelframe",
                background=frame_bg,
                font=("Segoe UI", 12, "bold"),
                foreground=deep_orange)

style.configure("TLabelframe.Label",
                background=frame_bg,
                font=("Segoe UI", 12, "bold"),
                foreground=deep_orange)

# -------------------------
# Title
# -------------------------
title_label = ttk.Label(scrollable_frame, text="☀️ Solar Panel Controller", font=("Segoe UI", 20, "bold"),
                        anchor="center")
title_label.pack(pady=20)

# -------------------------
# Control Frame
# -------------------------
control_frame = ttk.Frame(scrollable_frame)
control_frame.pack(pady=10)


# --- Start Button ---
def start_simulation_thread():
    sim_thread = threading.Thread(target=simulation.sim_start)
    sim_thread.daemon = True
    sim_thread.start()


start_button = ttk.Button(control_frame, text="▶️ Start Simulation", command=start_simulation_thread)
start_button.grid(row=0, column=0, columnspan=2, pady=10, padx=20)

# -------------------------
# Stats Frame (Initially Hidden)
# -------------------------
stats_frame = ttk.LabelFrame(scrollable_frame, text="📊 Power Output Stats", padding=10)
stats_labels = {}

stats_data = {
    "Current Tilt": f"{float(simulation.tilt_angle):.2f}°",
    "Sun Altitude": f"{float(simulation.sun_altitude):.2f}°",
    "Sun Azimuth": f"{float(simulation.sun_azimuth):.2f}°",
    "Efficiency": f"{float(simulation.efficiency * 100):.2f}%",
    "Power Output": f"{float(simulation.p_out):.2f} W",
    "Incident Output": f"{float(simulation.p_in):.2f} W",
    "Instant Power Output": f"{float(simulation.ipo):.2f}%"
}

for key, value in stats_data.items():
    row = ttk.Frame(stats_frame)
    row.pack(fill="x", pady=4)
    label = ttk.Label(row, text=f"{key}: ", width=22, anchor="w")
    label.pack(side="left")
    value_label = ttk.Label(row, text=value, width=15, anchor="w")
    value_label.pack(side="left")
    stats_labels[key] = value_label

stats_visible = False


# -------------------------
# Show Stats and Periodic Update
# -------------------------
def update_stats_periodically():
    global stats_visible
    if not stats_visible:
        stats_frame.pack(after=battery_frame, fill="x", padx=40)
        stats_visible = True

    updated_stats = {
        "Current Tilt": f"{float(simulation.tilt_angle):.2f}°",
        "Sun Altitude": f"{float(simulation.sun_altitude):.2f}°",
        "Sun Azimuth": f"{float(simulation.sun_azimuth):.2f}°",
        "Efficiency": f"{float(simulation.efficiency * 100):.2f}%",
        "Power Output": f"{float(simulation.p_out):.2f} W",
        "Incident Output": f"{float(simulation.p_in):.2f} W",
        "Instant Power Output": f"{float(simulation.ipo):.2f}%"
    }

    for key, value in updated_stats.items():
        stats_labels[key].config(text=value)

    root.after(1000, update_stats_periodically)


# --- Show Stats Button ---
stats_button = ttk.Button(scrollable_frame, text="📈 Show Power Output", command=update_stats_periodically)
stats_button.pack(pady=10)

# -------------------------
# Panel Orientation Frame
# -------------------------
orientation_frame = ttk.LabelFrame(scrollable_frame, text="📐 Panel Orientation", padding=10)
orientation_frame.pack(pady=10, fill="x", padx=40)


# --- Tilt Angle Slider ---
def on_tilt_change(val):
    simulation.tilt_angle = float(val)


tilt_slider = tk.Scale(orientation_frame, from_=-90, to=90, orient="horizontal",
                       label="Tilt Angle (°)", command=on_tilt_change, bg=frame_bg)
tilt_slider.set(simulation.tilt_angle)
tilt_slider.pack(fill="x", pady=5)


# --- Azimuth Angle Slider ---
def on_azimuth_change(val):
    simulation.azimuth_angle = float(val)


azimuth_slider = tk.Scale(orientation_frame, from_=-90, to=90, orient="horizontal",
                          label="Azimuth (°)", command=on_azimuth_change, bg=frame_bg)
azimuth_slider.set(simulation.azimuth_angle)
azimuth_slider.pack(fill="x", pady=5)

# -------------------------
# Battery Control Frame
# -------------------------
battery_frame = ttk.LabelFrame(scrollable_frame, text="🔋 Battery Options", padding=10)
battery_frame.pack(pady=10, fill="x", padx=40)

battery_charging = tk.BooleanVar(value=True)


def toggle_battery():
    simulation.battery_enabled = battery_charging.get()


battery_check = ttk.Checkbutton(battery_frame, text="Enable Battery Charging",
                                variable=battery_charging, command=toggle_battery)
battery_check.pack(anchor="w", pady=5)

# -------------------------
# Footer
# -------------------------
footer_frame = ttk.Frame(scrollable_frame)
footer_frame.pack(side="bottom", fill="x", pady=15)

footer_label = ttk.Label(footer_frame, text="• 2025", font=("Segoe UI", 9, "italic"), anchor="center")
footer_label.pack()

# -------------------------
# Run the GUI
# -------------------------
root.mainloop()
