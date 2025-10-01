import paho.mqtt.client as mqtt
import mysql.connector
import json

# Konfigurasi broker MQTT
BROKER = "192.168.0.106"
PORT = 9001
TOPIC_TEMP = "sensor1/temp"
TOPIC_HUMID = "sensor1/humidity"
USERNAME = "firos"
PASSWORD = "1234"

# Variabel global untuk simpan sementara
latest_temp = None
latest_humid = None

# Konfigurasi MySQL
db = mysql.connector.connect(
    host="192.168.0.106",     # atau IP VM kalau MySQL di VM
    user="firos",          # ganti user mysql
    password="1234",  # ganti password mysql
    database="sensor_db",
    port=3306
)
cursor = db.cursor()

# Callback saat pesan diterima
def on_message(client, userdata, msg):
    global latest_temp, latest_humid

    topic = msg.topic
    payload = msg.payload.decode()

    if topic == TOPIC_TEMP:
        latest_temp = int(payload)
    elif topic == TOPIC_HUMID:
        latest_humid = int(payload)

    # Kalau dua-duanya sudah ada, simpan ke DB
    if latest_temp is not None and latest_humid is not None:
        sql = "INSERT INTO sensor_data (temperature, humidity) VALUES (%s, %s)"
        val = (latest_temp, latest_humid)
        cursor.execute(sql, val)
        db.commit()
        print(f"Data saved -> Temp: {latest_temp}, Humidity: {latest_humid}")

        # Reset biar data baru bisa masuk lagi
        latest_temp = None
        latest_humid = None

# Setup MQTT client
client = mqtt.Client(transport="websockets")
client.username_pw_set(USERNAME, PASSWORD)
client.on_message = on_message

client.connect(BROKER, PORT, 60)

# Subscribe ke 2 topic
client.subscribe(TOPIC_TEMP)
client.subscribe(TOPIC_HUMID)

print("Listening MQTT and saving to MySQL...")
client.loop_forever()
