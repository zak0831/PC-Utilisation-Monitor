import tkinter as tk
from tkinter import ttk
import psutil

# ---------------- Settings ----------------
WINDOW_TITLE = "System Monitor"
WINDOW_WIDTH = 525
WINDOW_HEIGHT = 555

UPDATE_INTERVAL_MS = 1000   # refresh rate in milliseconds
DISK_PATH = "C:\\"

LOW_THRESHOLD = 50
HIGH_THRESHOLD = 80

COLOUR_LOW = "green"
COLOUR_MEDIUM = "orange"
COLOUR_HIGH = "red"

BAR_LENGTH = 300
CORE_BAR_LENGTH = 120


# Decide which colour a bar/label should show based on usage %
def get_colour_for_percentage(percentage):
    if percentage < LOW_THRESHOLD:
        return COLOUR_LOW
    elif percentage < HIGH_THRESHOLD:
        return COLOUR_MEDIUM
    else:
        return COLOUR_HIGH


# ---------------- Main window ----------------
window = tk.Tk()
window.title(WINDOW_TITLE)
window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
window.resizable(False, False)


# ---------------- Progress bar colour styles ----------------
# ttk.Progressbar can't be recoloured directly - you have to define
# named styles up front, then switch a bar's style to change colour.
style_manager = ttk.Style()
style_manager.theme_use("default")

style_manager.configure("green.Horizontal.TProgressbar", troughcolor="lightgrey", background=COLOUR_LOW)
style_manager.configure("orange.Horizontal.TProgressbar", troughcolor="lightgrey", background=COLOUR_MEDIUM)
style_manager.configure("red.Horizontal.TProgressbar", troughcolor="lightgrey", background=COLOUR_HIGH)


def apply_colour_to_bar(bar_widget, percentage):
    colour_name = get_colour_for_percentage(percentage)
    bar_widget.config(style=f"{colour_name}.Horizontal.TProgressbar")


# ---------------- Main title ----------------
tk.Label(window, text="System Monitor", font=("Arial", 16, "bold", "underline")).pack(pady=(15, 5))


# ---------------- CPU / RAM / Disk meters ----------------
def create_usage_meter(parent_widget, title_text):
    """Builds a title + progress bar + percentage label, returns the bar and label."""
    tk.Label(parent_widget, text=title_text, font=("Arial", 12, "bold")).pack(pady=(10, 0))

    progress_bar = ttk.Progressbar(parent_widget, length=BAR_LENGTH, maximum=100,
                                    style="green.Horizontal.TProgressbar")
    progress_bar.pack(pady=5)

    percentage_label = tk.Label(parent_widget, text="0%", font=("Arial", 10))
    percentage_label.pack()

    return progress_bar, percentage_label


cpu_bar, cpu_label = create_usage_meter(window, "CPU Usage")
ram_bar, ram_label = create_usage_meter(window, "RAM Usage")
disk_bar, disk_label = create_usage_meter(window, f"Disk Usage ({DISK_PATH})")


# ---------------- Per-core CPU section ----------------
tk.Label(window, text="Per-Core CPU Usage", font=("Arial", 12, "bold")).pack(pady=(15, 5))

core_section_frame = tk.Frame(window)
core_section_frame.pack()

number_of_cores = psutil.cpu_count()
core_bars = []
core_labels = []

for core_index in range(number_of_cores):
    # Arrange cores in a 2-column grid
    core_row = tk.Frame(core_section_frame)
    core_row.grid(row=core_index // 2, column=core_index % 2, padx=8, pady=4, sticky="w")

    tk.Label(core_row, text=f"Core {core_index}", font=("Arial", 9), width=8, anchor="w").pack(side="left")

    core_bar = ttk.Progressbar(core_row, length=CORE_BAR_LENGTH, maximum=100,
                                style="green.Horizontal.TProgressbar")
    core_bar.pack(side="left", padx=5)

    core_percentage_label = tk.Label(core_row, text="0%", font=("Arial", 9), width=4)
    core_percentage_label.pack(side="left")

    core_bars.append(core_bar)
    core_labels.append(core_percentage_label)


# ---------------- Update loop ----------------
def update_stats():
    cpu_percentage = psutil.cpu_percent()
    cpu_bar["value"] = cpu_percentage
    cpu_label.config(text=f"{cpu_percentage}%")
    apply_colour_to_bar(cpu_bar, cpu_percentage)

    ram_percentage = psutil.virtual_memory().percent
    ram_bar["value"] = ram_percentage
    ram_label.config(text=f"{ram_percentage}%")
    apply_colour_to_bar(ram_bar, ram_percentage)

    disk_percentage = psutil.disk_usage(DISK_PATH).percent
    disk_bar["value"] = disk_percentage
    disk_label.config(text=f"{disk_percentage}%")
    apply_colour_to_bar(disk_bar, disk_percentage)

    # percpu=True returns a list of per-core percentages
    per_core_percentages = psutil.cpu_percent(percpu=True)
    for core_index in range(number_of_cores):
        this_core_percentage = per_core_percentages[core_index]
        core_bars[core_index]["value"] = this_core_percentage
        core_labels[core_index].config(text=f"{this_core_percentage}%")
        apply_colour_to_bar(core_bars[core_index], this_core_percentage)

    # Reschedule itself instead of using a while-loop, so the window never freezes
    window.after(UPDATE_INTERVAL_MS, update_stats)


update_stats()
window.mainloop()