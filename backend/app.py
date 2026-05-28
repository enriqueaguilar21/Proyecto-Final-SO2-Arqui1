from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import datetime
import os
import requests  # Requerido para extraer la captura desde IP Webcam

app = Flask(__name__, template_folder='.') # Permite servir el index.html en la misma raíz si es necesario

# --- CONFIGURACIÓN DE MONGODB (RED INTERNA DOCKER EN AWS) ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client.proyecto_so2
    logs_col = db.eventos
    print("Conexión a MongoDB en AWS exitosa")
except Exception as e:
    print(f"Error de base de datos en AWS: {e}")
    logs_col = None

# --- CONFIGURACIÓN SERIAL INACTIVA EN AWS (BLINDADA) ---
# En la nube no hay conexión física Bluetooth, por lo que se anula limpiamente para evitar errores.
ser = None
print("[AWS CLOUD] Puerto Serial deshabilitado localmente (Modo Servidor Web Activo)")

# --- VARIABLE DE CONTROL DE ESTADO ---
estado_actual = "X"

# --- ENDPOINTS API ---

@app.route('/')
def index():
    # En lugar de solo responder un JSON, en AWS servimos tu frontend index.html moderno
    try:
        return render_template('index.html')
    except Exception:
        return jsonify({"status": "Backend API running - Carrito Explorador V2", "nota": "Sube el index.html al servidor"})

@app.route('/get_logs')
def get_logs():
    if logs_col is not None:
        try:
            # ✨ ACTUALIZADO: Busca los registros médicos que tu PC local subió a AWS
            eventos = logs_col.find({"biomedicos": {"$exists": True}}).sort("fecha", -1).limit(10)
            lista_logs = []
            
            for e in eventos:
                biomedicos = e.get("biomedicos", {})
                lista_logs.append({
                    "hora": e.get("fecha").strftime("%H:%M:%S") if e.get("fecha") else "N/A",
                    "bpm_promedio": biomedicos.get("bpm_promedio", 0),
                    "estado_clinico": biomedicos.get("estado_clinico", "N/A"),
                    "foto": e.get("archivo_foto", "N/A")
                })
            return jsonify(lista_logs)
        except Exception as err:
            print(f"⚠️ Error al consultar MongoDB en AWS: {err}")
    return jsonify([])

@app.route('/control')
def control():
    # Mantenemos la ruta viva por si el frontend hace peticiones de movimiento,
    # pero en AWS no realiza ninguna acción serial para evitar excepciones.
    return "OK"

@app.route('/capturar_foto')
def capturar_foto():
    # Este endpoint en AWS puede quedar pasivo, ya que tu PC local se encarga de tomar
    # la captura y subir el objeto estructurado a MongoDB.
    return jsonify({"mensaje": "La captura se procesa desde la estación local."})

# Endpoint simulado por si el HTML de AWS intenta consultar estados locales
@app.route('/api/salud')
def api_salud():
    return jsonify({"bpm": 0.0, "promedio": 0, "estado": "Monitoreo disponible en estación local"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
