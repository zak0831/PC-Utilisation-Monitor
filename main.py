import psutil

cpu = psutil.cpu_percent(interval=1)
ram = psutil.virtual_memory()
disk = psutil.disk_usage("C:\\")

print(f"CPU Usage: {cpu}%")
print(f"RAM Usage: {ram.percent}%")
print(f"Disk Usage: {disk.percent}%")
