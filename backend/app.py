from flask import Flask, request, jsonify
import serial
from pymongo import MongoClient
import datetime
import threading
import os

app = Flask(__name__)   # Inicialización principal Flask

# --- VARIABLES GLOBALES ---
ultima_humedad = "---"

# --- CONFIGURACIÓN DE MONGODB ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client.proyecto_so2
    logs_col = db.eventos
    print("Conexión a MongoDB exitosa")
except Exception as e:
    print(f"Error de base de datos: {e}")
    logs_col = None

# --- CONFIGURACIÓN SERIAL ---
SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
SERIAL_BAUD = int(os.getenv("SERIAL_BAUD", "9600"))

try:
    ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
    print(f"Bluetooth conectado en {SERIAL_PORT}")
except Exception as e:
    ser = None
    print(f"Bluetooth no detectado: {e}")

# --- HILO DE LECTURA DE ARDUINO ---
def escuchar_arduino():
    global ultima_humedad
    while ser and ser.is_open:
        try:
            linea = ser.readline().decode('utf-8').strip()
            if linea.startswith("H:"):
                ultima_humedad = linea.split(":")[1]
        except:
            pass

if ser:
    threading.Thread(target=escuchar_arduino, daemon=True).start()

# --- ENDPOINTS API (sin render_template) ---

@app.route('/')
def index():
    return jsonify({"status": "Backend API running"})

@app.route('/get_humedad')
def get_humedad():
    return str(ultima_humedad)

@app.route('/get_logs')
def get_logs():
    if logs_col is not None:
        eventos = logs_col.find().sort("fecha", -1).limit(10)
        lista_logs = []
        for e in eventos:
            lista_logs.append({
                "accion": e.get("accion", "N/A"),
                "humedad": e.get("humedad", "0"),
                "hora": e.get("fecha").strftime("%H:%M:%S")
            })
        return jsonify(lista_logs)
    return jsonify([])

@app.route('/control')
def control():
    cmd = request.args.get('cmd')
    if ser and ser.is_open:
        ser.write((cmd + '\n').encode())
    
    if logs_col is not None:
        nombres = {'W':'Adelante','S':'Atrás','A':'Izquierda','D':'Derecha','X':'Parar','P':'Sembrar','R':'Regar'}
        log = {
            "fecha": datetime.datetime.now(),
            "accion": nombres.get(cmd, "Comando"),
            "humedad": ultima_humedad,
            "origen": "Orchestrated Dashboard"
        }
        logs_col.insert_one(log)
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
