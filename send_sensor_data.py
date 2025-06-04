# send_sensor_data.py

import requests
import datetime
import time

# Replace with the actual URL of your FastAPI backend
FASTAPI_BACKEND_URL = "http://localhost:8000"

def send_data(temperature, humidity, sensor_id=None):
    """Sends sensor data to the FastAPI backend via HTTP POST."""
    timestamp = datetime.datetime.now().isoformat()

    payload = {
        "timestamp": timestamp,
        "temperature": temperature,
        "humidity": humidity,
        "sensor_id": sensor_id
    }

    try:
        response = requests.post(f"{FASTAPI_BACKEND_URL}/sensor_data/", json=payload)
        response.raise_for_status() # Raise an exception for bad status codes
        print(f"Successfully sent data: {payload}")
        print(f"Backend response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data: {e}")

# --- Example Usage ---
# Simulate sending data every 10 seconds
if __name__ == "__main__":
    print(f"Sending simulated sensor data to {FASTAPI_BACKEND_URL}...")
    
    # Example with sensor ID
    send_data(28, 75, "sensor_001")

    # Example without sensor ID
    # send_data(25, 60)

    # To send data periodically:
    # while True:
    #     # In a real scenario, read actual sensor values here
    #     temp = 20 + (time.time() % 10) # Simulate temperature changing
    #     hum = 50 + (time.time() % 20)  # Simulate humidity changing
    #     send_data(int(temp), int(hum), "simulated_sensor")
    #     time.sleep(10) # Send every 10 seconds 