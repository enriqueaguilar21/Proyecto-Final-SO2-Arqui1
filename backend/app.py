from flask import Flask, request, jsonify
import serial
from pymongo import MongoClient
import datetime
import os
import requests  # Requerido para extraer la captura desde IP Webcam

app = Flask(__name__)

# --- CONFIGURACIÓN DE MONGODB (RED INTERNA DOCKER) ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client.proyecto_so2
    logs_col = db.eventos
    print("Conexión a MongoDB exitosa")
except Exception as e:
    print(f"Error de base de datos: {e}")
    logs_col = None

# --- CONFIGURACIÓN SERIAL (PASSTHROUGH EN DOCKER) ---
SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
SERIAL_BAUD = int(os.getenv("SERIAL_BAUD", "9600"))

try:
    ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
    print(f"Bluetooth conectado en {SERIAL_PORT}")
except Exception as e:
    ser = None
    print(f"Bluetooth no detectado: {e}")

# --- VARIABLE DE CONTROL DE ESTADO (ANTI-REBOTE) ---
estado_actual = "X"

# --- ENDPOINTS API ---

@app.route('/')
def index():
    return jsonify({"status": "Backend API running - Carrito Explorador V1"})

@app.route('/get_logs')
def get_logs():
    if logs_col is not None:
        # Recupera los 10 eventos más recientes en AWS, simplificados sin humedad
        eventos = logs_col.find().sort("fecha", -1).limit(10)
        lista_logs = []
        for e in eventos:
            lista_logs.append({
                "accion": e.get("accion", "N/A"),
                "hora": e.get("fecha").strftime("%H:%M:%S")
            })
        return jsonify(lista_logs)
    return jsonify([])

@app.route('/control')
def control():
    global estado_actual
    cmd = request.args.get('cmd', '')
    
    # Filtro de rebote: Solo procesa si la dirección cambió
    if cmd != estado_actual:
        # 1. Enviar byte directo por el puerto mapeado en Docker al coche
        if ser and ser.is_open:
            ser.write(cmd.encode('utf-8'))
            print(f"[SERIAL DOCKER] Comando '{cmd}' enviado con éxito.")
            
        # 2. Registrar la operación en el contenedor de MongoDB
        if logs_col is not None:
            nombres = {'W':'Adelante', 'S':'Atrás', 'A':'Izquierda', 'D':'Derecha', 'X':'Parar'}
            log = {
                "fecha": datetime.datetime.now(),
                "accion": nombres.get(cmd, "Comando"),
                "origen": "Orchestrated Pulsador Dashboard"
            }
            try:
                logs_col.insert_one(log)
            except Exception as e:
                print(f"Error guardando evento en MongoDB: {e}")
                
        estado_actual = cmd
        
    return "OK"

@app.route('/capturar_foto')
def capturar_foto():
    # Extraemos la IP que el usuario ingresó dinámicamente en el Dashboard
    ip_camara = request.args.get('ip', '')
    if not ip_camara:
        return jsonify({"mensaje": "Error: No se especificó la IP de la cámara."}), 400
        
    try:
        url_shot = f"http://{ip_camara}/shot.jpg"
        respuesta = requests.get(url_shot, timeout=4)
        
        if respuesta.status_code == 200:
            # Creamos una carpeta 'capturas' dentro del contenedor si no existe
            if not os.path.exists('capturas'):
                os.makedirs('capturas')
                
            nombre_foto = datetime.datetime.now().strftime("capturas/foto_%Y%m%d_%H%M%S.jpg")
            
            with open(nombre_foto, 'wb') as f:
                f.write(respuesta.content)
                
            print(f"[CÁMARA DOCKER] Foto capturada exitosamente: {nombre_foto}")
            return jsonify({"mensaje": f"¡Foto guardada en servidor AWS! Código de archivo: {nombre_foto}"})
        else:
            return jsonify({"mensaje": "La cámara no entregó el flujo de imagen."}), 500
            
    except Exception as e:
        print(f"Error de red con IP Webcam en Docker: {e}")
        return jsonify({"mensaje": f"No se pudo enlazar la cámara. Verifica que comparta red Wi-Fi: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
