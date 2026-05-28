from flask import Flask, request, jsonify
import serial
from pymongo import MongoClient
import datetime
import os
import requests  

app = Flask(__name__)

# --- CONFIGURACIÓN DE MONGODB (RED INTERNA DOCKER AWS) ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client.proyecto_so2
    logs_col = db.eventos
    print("Conexión a MongoDB AWS exitosa")
except Exception as e:
    print(f"Error de base de datos en AWS: {e}")
    logs_col = None

# --- CONFIGURACIÓN SERIAL EN AWS (Opcional/Passthrough) ---
SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
SERIAL_BAUD = int(os.getenv("SERIAL_BAUD", "9600"))

try:
    ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
    print(f"Bluetooth conectado en AWS {SERIAL_PORT}")
except Exception as e:
    ser = None
    print(f"Bluetooth no detectado en AWS (Normal si es solo servidor nube): {e}")

estado_actual = "X"

# --- ENDPOINTS API ---

@app.route('/')
def index():
    return jsonify({"status": "Backend API AWS running - Historial Clínico Activo"})

# 📥 --- NUEVO: ENDPOINT RECEPTOR DEL PUENTE DESDE EL LOCAL ---
@app.route('/api/guardar_registro_remoto', methods=['POST'])
def guardar_registro_remoto():
    if logs_col is None:
        return jsonify({"status": "error", "mensaje": "Base de datos AWS no disponible"}), 500
        
    datos_recibidos = request.get_json()
    if not datos_recibidos:
        return jsonify({"status": "error", "mensaje": "No se recibieron datos válidos"}), 400
        
    try:
        # Convertimos la fecha actual a formato datetime de Python para el guardado nativo
        datos_recibidos["fecha"] = datetime.datetime.now()
        logs_col.insert_one(datos_recibidos)
        return jsonify({"status": "ok", "mensaje": "Registro clínico replicado en AWS"}), 200
    except Exception as e:
        return jsonify({"status": "error", "mensaje": f"Error al insertar en AWS: {str(e)}"}), 500

# 📋 --- MODIFICADO: RUTA DE CONTROL DE LOGS PARA EL NUEVO FRONTEND ---
@app.route('/get_logs')
def get_logs():
    if logs_col is not None:
        # Recupera los 10 registros clínicos insertados por el puente
        eventos = logs_col.find().sort("fecha", -1).limit(10)
        lista_logs = []
        for e in eventos:
            lista_logs.append({
                "hora": e.get("hora", e.get("fecha", datetime.datetime.now()).strftime("%H:%M:%S")),
                "bpm_promedio": e.get("bpm_promedio", 0),
                "estado_clinico": e.get("estado_clinico", e.get("accion", "N/A")),
                "foto": e.get("foto", "sin_imagen.jpg")
            })
        return jsonify(lista_logs)
    return jsonify([])

@app.route('/control')
def control():
    global estado_actual
    cmd = request.args.get('cmd', '')
    
    if cmd != estado_actual:
        if ser and ser.is_open:
            ser.write(cmd.encode('utf-8'))
            print(f"[SERIAL DOCKER AWS] Comando '{cmd}' enviado.")
            
        if logs_col is not None:
            nombres = {'W':'Adelante', 'S':'Atrás', 'A':'Izquierda', 'D':'Derecha', 'X':'Parar'}
            log = {
                "fecha": datetime.datetime.now(),
                "accion": nombres.get(cmd, "Comando"),
                "origen": "Orchestrated AWS Dashboard",
                "hora": datetime.datetime.now().strftime("%H:%M:%S"),
                "bpm_promedio": "--",
                "estado_clinico": nombres.get(cmd, "Movimiento"),
                "foto": "control_remoto.jpg"
            }
            try:
                logs_col.insert_one(log)
            except Exception as e:
                print(f"Error guardando evento en AWS: {e}")
                
        estado_actual = cmd
        
    return "OK"

@app.route('/capturar_foto')
def capturar_foto():
    ip_camara = request.args.get('ip', '')
    if not ip_camara:
        return jsonify({"mensaje": "Error: No se especificó la IP."}), 400
    return jsonify({"mensaje": "Para capturas clínicas centralizadas, use el disparador local."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
