from flask import Flask, render_template, request, jsonify
import serial
from pymongo import MongoClient
import datetime
import threading
import os

app = Flask(__name__, template_folder='../frontend')

# --- VARIABLES GLOBALES ---
ultima_humedad = "---"

# --- CONFIGURACIÓN DE MONGODB (AWS) ---
# Se intenta leer la URI de una variable de entorno para facilitar la orquestación
MONGO_URI = os.getenv("MONGO_URI", "mongodb://34.227.72.135:27017/")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    db = client.proyecto_so2
    logs_col = db.eventos
    print("Conexión a MongoDB exitosa")
except Exception as e:
    print(f"Error de base de datos: {e}")
    logs_col = None

# --- CONFIGURACIÓN SERIAL ---
try:
    ser = serial.Serial('COM5', 9600, timeout=1)
    print("Bluetooth conectado")
except:
    ser = None
    print("Error: Bluetooth no detectado.")

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

threading.Thread(target=escuchar_arduino, daemon=True).start()

@app.route('/')
def index():
    # Renderiza el archivo index.html que estará en la carpeta frontend
    return render_template('index.html')

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
