import psutil
import requests
import time
import socket

SERVER_URL = "http://127.0.0.1:5000/data"

SYSTEM_NAME = socket.gethostname()

while True:
    data = {
        "system": SYSTEM_NAME,
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }

    try:
        response = requests.post(SERVER_URL, json=data)
        print("✅ Data Sent:", data)
    except:
        print("❌ Server Not Reachable")

    time.sleep(5)
