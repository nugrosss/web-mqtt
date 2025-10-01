import paho.mqtt.client as mqtt
import time
import random

# Konfigurasi broker (WebSocket)
BROKER = "192.168.225.215"   # IP Ubuntu server
PORT = 9001                  # Port WS (biasanya 9001 untuk Mosquitto WS)
TOPIC_TEMP = "sensor1/temp"
TOPIC_HUMID = "sensor1/humidity"
USERNAME = "firos"
PASSWORD = "1234"

# Buat client MQTT dengan transport websockets
client = mqtt.Client(transport="websockets")
client.username_pw_set(USERNAME, PASSWORD)

print("Connecting to MQTT broker via WebSocket...")
client.connect(BROKER, PORT, 60)

# Publish loop
try:
    while True:
        temp_value = random.randint(20, 40)     # contoh data suhu
        humid_value = random.randint(40, 90)    # contoh data kelembapan

        # Publish ke 2 topic berbeda
        client.publish(TOPIC_TEMP, temp_value)
        client.publish(TOPIC_HUMID, humid_value)

        print(f"Sent -> Temp: {temp_value}°C | Humidity: {humid_value}%")

        time.sleep(2)

except KeyboardInterrupt:
    print("Stopped by user")
    client.disconnect()
