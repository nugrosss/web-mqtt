from flask import Flask, jsonify, request
from flask_cors import CORS  # Install: pip install flask-cors
import mysql.connector
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS untuk akses dari browser

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="192.168.225.215",
            user="firos",
            password="1234",
            database="sensor_db",
            port=3306
        )
        print("[DEBUG] ✅ Koneksi ke MySQL berhasil")
        return conn
    except mysql.connector.Error as err:
        print(f"[DEBUG] ❌ Gagal koneksi ke MySQL: {err}")
        return None

def get_where_clause(range_type):
    """Menentukan WHERE clause berdasarkan range waktu"""
    clauses = {
        "5min": "WHERE timestamp >= NOW() - INTERVAL 5 MINUTE",
        "hour": "WHERE timestamp >= NOW() - INTERVAL 1 HOUR",
        "day": "WHERE DATE(timestamp) = CURDATE()",
        "week": "WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 1 WEEK)",
        "month": "WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 1 MONTH)"
    }
    return clauses.get(range_type, clauses["day"])

@app.route('/data')
def get_data():
    range_type = request.args.get("range", "day")
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Tidak bisa koneksi ke database"}), 500

    cursor = conn.cursor(dictionary=True)
    
    try:
        # Query untuk data chart dan tabel
        where_clause = get_where_clause(range_type)
        query = f"""
            SELECT id, temperature, humidity, timestamp
            FROM sensor_data
            {where_clause}
            ORDER BY timestamp DESC
            LIMIT 1000
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Query untuk statistik
        stats_query = f"""
            SELECT 
                AVG(temperature) as temp_avg,
                MIN(temperature) as temp_min,
                MAX(temperature) as temp_max,
                AVG(humidity) as hum_avg,
                MIN(humidity) as hum_min,
                MAX(humidity) as hum_max,
                COUNT(*) as total
            FROM sensor_data
            {where_clause}
        """
        
        cursor.execute(stats_query)
        stats_row = cursor.fetchone()
        
        # Format data untuk chart (urutan chronological)
        chart_data = {
            'labels': [],
            'temperature': [],
            'humidity': []
        }
        
        # Format data untuk tabel
        table_data = []
        
        # Reverse untuk urutan chronological di chart
        reversed_rows = list(reversed(rows))
        for row in reversed_rows:
            # Handle timestamp - bisa berupa datetime object atau string
            if isinstance(row['timestamp'], datetime):
                ts = row['timestamp']
            else:
                # Jika string, parse dengan format Python yang benar
                ts = datetime.strptime(str(row['timestamp']), '%Y-%m-%d %H:%M:%S')
            
            chart_data['labels'].append(ts.strftime('%H:%M'))
            chart_data['temperature'].append(float(row['temperature']))
            chart_data['humidity'].append(float(row['humidity']))
        
        # Format data untuk tabel (tetap DESC order)
        for row in rows:
            if isinstance(row['timestamp'], datetime):
                timestamp_str = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            else:
                timestamp_str = str(row['timestamp'])
            
            table_data.append({
                'id': row['id'],
                'temperature': float(row['temperature']),
                'humidity': float(row['humidity']),
                'timestamp': timestamp_str
            })
        
        # Format response
        response_data = {
            'stats': {
                'temp': {
                    'avg': float(stats_row['temp_avg']) if stats_row['temp_avg'] else 0,
                    'min': float(stats_row['temp_min']) if stats_row['temp_min'] else 0,
                    'max': float(stats_row['temp_max']) if stats_row['temp_max'] else 0
                },
                'humidity': {
                    'avg': float(stats_row['hum_avg']) if stats_row['hum_avg'] else 0,
                    'min': float(stats_row['hum_min']) if stats_row['hum_min'] else 0,
                    'max': float(stats_row['hum_max']) if stats_row['hum_max'] else 0
                },
                'total': int(stats_row['total']) if stats_row['total'] else 0
            },
            'chartData': chart_data,
            'tableData': table_data
        }
        
        print(f"[DEBUG] ✅ Data berhasil diambil: {len(rows)} baris")
        print(f"[DEBUG] Range: {range_type}, Total: {stats_row['total']}")
        
        cursor.close()
        conn.close()
        
        return jsonify(response_data)
        
    except Exception as err:
        print(f"[DEBUG] ❌ Error: {err}")
        cursor.close()
        conn.close()
        return jsonify({"error": f"Error: {str(err)}"}), 500

@app.route('/last-five')
def get_last_five():
    """Endpoint tambahan untuk mendapatkan 5 data terakhir"""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Tidak bisa koneksi ke database"}), 500

    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT id, temperature, humidity, timestamp
            FROM sensor_data 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        last_five = cursor.fetchall()
        
        # Format timestamp
        formatted_data = []
        for row in last_five:
            if isinstance(row['timestamp'], datetime):
                timestamp_str = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            else:
                timestamp_str = str(row['timestamp'])
            
            formatted_data.append({
                'id': row['id'],
                'temperature': float(row['temperature']),
                'humidity': float(row['humidity']),
                'timestamp': timestamp_str
            })
        
        print("[DEBUG] 5 Data terakhir:")
        for row in formatted_data:
            print(row)
        
        cursor.close()
        conn.close()
        
        return jsonify(formatted_data)
        
    except Exception as err:
        print(f"[DEBUG] ❌ Error: {err}")
        cursor.close()
        conn.close()
        return jsonify({"error": str(err)}), 500

@app.route('/health')
def health_check():
    """Endpoint untuk mengecek status API"""
    conn = get_db_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Database connection failed"}), 500
    
    conn.close()
    return jsonify({"status": "ok", "message": "API dan database berjalan normal"})

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Flask API Server Starting...")
    print("=" * 50)
    print("📍 URL: http://localhost:5000")
    print("📊 Endpoints:")
    print("   - GET /data?range=[5min|hour|day|week|month]")
    print("   - GET /last-five")
    print("   - GET /health")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)