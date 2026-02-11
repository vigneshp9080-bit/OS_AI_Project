import psutil
import time
import csv
from datetime import datetime
import os

file_path = os.path.join(os.getcwd(), "system_data.csv")
print("Saving to:", file_path)

file_exists = os.path.isfile(file_path)

with open(file_path, "a", newline="") as file:
    writer = csv.writer(file)

    # Write header only first time
    if not file_exists:
        writer.writerow(["Time", "CPU", "RAM", "Disk"])
        file.flush()

    while True:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        writer.writerow([now, cpu, ram, disk])
        file.flush()   # Force save to disk

        print("Saved:", now, cpu, ram, disk)

        time.sleep(5)
