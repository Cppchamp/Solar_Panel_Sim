import tkinter as tk
from tkinter import ttk
import simulation  # Import your simulation module

# Create the main control panel window
root = tk.Tk()
root.title("Solar Panel Control Panel")
root.geometry("600x400")

# Title label
title_label = ttk.Label(root, text="Solar Panel Controller", font=("Helvetica", 16))
title_label.pack(pady=10)

def start_simulation():
    simulation.sim_start()  # Start the simulation (OpenGL rendering)

def show_stats():
    print("Displaying power output stats...")

# Add a slider for adjusting the panel angle

# Buttons
start_button = ttk.Button(root, text="Start Simulation", command=start_simulation)
start_button.pack(pady=5)

stats_button = ttk.Button(root, text="Show Power Output", command=show_stats)
stats_button.pack(pady=5)

# Run the Tkinter window
root.mainloop()
