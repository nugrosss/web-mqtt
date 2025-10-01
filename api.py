from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="192.168.0.106",     # atau IP VM kalau MySQL di VM
            user="firos",          # ganti user mysql
            password="1234",  # ganti password mysql
            database="sensor_db",
            port=3306
        )
        print("[DEBUG] ✅ Koneksi ke MySQL berhasil")
        return conn
    except mysql.connector.Error as err:
        print(f"[DEBUG] ❌ Gagal koneksi ke MySQL: {err}")
        return None

@app.route('/data')
def get_data():
    range_type = request.args.get("range", "hari")

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Tidak bisa koneksi ke database"}), 500

    cursor = conn.cursor(dictionary=True)

    if range_type == "menit":
        query = "SELECT timestamp, temperature, humidity FROM sensor_data WHERE timestamp >= NOW() - INTERVAL 1 HOUR"
    elif range_type == "jam":
        query = "SELECT timestamp, temperature, humidity FROM sensor_data WHERE timestamp >= NOW() - INTERVAL 1 DAY"
    else:  # default hari
        query = "SELECT timestamp, temperature, humidity FROM sensor_data WHERE timestamp >= NOW() - INTERVAL 30 DAY"

    cursor.execute(query)
    rows = cursor.fetchall()

    # Ambil 5 data terakhir
    cursor.execute("SELECT timestamp, temperature, humidity FROM sensor_data ORDER BY timestamp DESC LIMIT 5")
    last_five = cursor.fetchall()

    print("[DEBUG] 5 Data terakhir:")
    for row in last_five:
        print(row)

    cursor.close()
    conn.close()

    return jsonify(rows)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)