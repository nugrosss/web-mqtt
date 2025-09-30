import paho.mqtt.client as mqtt
import time
import random

# Konfigurasi broker
BROKER = "192.168.131.114"   # Ganti dengan IP Ubuntu server
PORT = 9001
TOPIC = "sensor1/temp"
USERNAME = "firos"        # Sesuai dengan mosquitto_passwd
PASSWORD = "1234"    # Sesuai password

# Buat client MQTT
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)

print("Connecting to MQTT broker...")
client.connect(BROKER, PORT, 60)

# Publish loop
try:
    while True:
        value = random.randint(20, 40)  # contoh data sensor
        # message = f"Temperature: {value}°C"
        message = value
        client.publish(TOPIC, message)
        print(f"Sent: {message}")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Stopped by user")
    client.disconnect()