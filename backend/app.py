from flask import Flask, request, jsonify
import serial
from pymongo import MongoClient
import datetime
import threading
import os

app = Flask(__name__)  # Sin template_folder

# --- VARIABLES GLOBALES ---
ultima_humedad = "---"

# --- CONFIGURACIÓN DE MONGODB ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")

try:
    print(f"[*] Intentando conectar a la base de datos en: {MONGO_URI}") # <-- CAMBIO: Log de intento
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client.proyecto_so2
    logs_col = db.eventos
    print("[+] Conexión a MongoDB exitosa y lista para registrar") # <-- CAMBIO: Mensaje ampliado
except Exception as e:
    print(f"[-] Error crítico de base de datos: {e}") # <-- CAMBIO: Mensaje de error modificado
    logs_col = None

# --- CONFIGURACIÓN SERIAL ---
SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
SERIAL_BAUD = int(os.getenv("SERIAL_BAUD", "9600"))

try:
    ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
    print(f"[+] Bluetooth del carrito conectado en {SERIAL_PORT}") # <-- CAMBIO: Contexto añadido
except Exception as e:
    ser = None
    print(f"[-] Bluetooth no detectado: {e}")

# --- HILO DE LECTURA DE ARDUINO ---
def escuchar_arduino():
    global ultima_humedad
    while ser and ser.is_open:
        try:
            linea = ser.readline().decode('utf-8').strip()
            if linea.startswith("H:"):
                ultima_humedad = linea.split(":")[1]
                # print(f"Humedad actualizada a: {ultima_humedad}") # <-- CAMBIO: Comentario de depuración
        except:
            pass

if ser:
    threading.Thread(target=escuchar_arduino, daemon=True).start()

# --- ENDPOINTS API (sin render_template) ---

@app.route('/')
def index():
    return jsonify({"status": "Backend API running", "version": "1.1-debug"}) # <-- CAMBIO: Versión añadida

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
    git add nombre_de_tu_archivo.py
git commit -m "Add verbose logging for MongoDB and Bluetooth connections"
