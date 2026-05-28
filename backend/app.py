from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import datetime
import os

app = Flask(__name__, template_folder='.')

# --- CONFIGURACIÓN DE MONGODB (RED INTERNA DOCKER EN AWS) ---
# En AWS, se conecta al contenedor de MongoDB mediante su alias en la red de Docker.
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client.proyecto_so2
    logs_col = db.eventos
    print("🚀 [AWS CLOUD] Conexión interna a MongoDB exitosa.")
except Exception as e:
    print(f"❌ [AWS CLOUD] Error de conexión a la base de datos interna: {e}")
    logs_col = None

# --- CONFIGURACIÓN SERIAL INACTIVA EN AWS (BLINDADA) ---
# Al ser un servidor en la nube, anulamos el puerto físico para evitar excepciones por falta de hardware.
ser = None
print("[AWS CLOUD] Modo Servidor Web Activo: Puerto serial físico deshabilitado.")

# --- ENDPOINTS API ---

@app.route('/')
def index():
    # Cuando alguien entra a la IP de AWS, Flask renderiza el index.html moderno
    try:
        return render_template('index.html')
    except Exception as e:
        return jsonify({
            "status": "Backend API running - Carrito Explorador V2",
            "error": "index.html no encontrado en la raíz del servidor de AWS"
        }), 404

@app.route('/api/salud')
def api_salud():
    # OPCEÓN B: El frontend de AWS consume este endpoint cada 2 segundos.
    # Aquí buscamos el registro que la computadora local actualiza constantemente.
    if logs_col is not None:
        try:
            telemetria = logs_col.find_one({"tipo": "telemetria_tiempo_real"})
            
            if telemetria:
                return jsonify({
                    "bpm": telemetria.get("bpm", 0.0),
                    "promedio": telemetria.get("promedio", 0),
                    "estado": telemetria.get("estado", "Estación local sin telemetría activa")
                })
        except Exception as e:
            print(f"⚠️ [AWS] Error al consultar telemetría en tiempo real: {e}")
            
    return jsonify({"bpm": 0.0, "promedio": 0, "estado": "Sensor fuera de línea (Estación Local Apagada)"})

@app.route('/api/get_logs')
def get_logs():
    # Devuelve el Historial Clínico de los Pacientes registrados en la nube
    if logs_col is not None:
        try:
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
        except Exception as e:
            print(f"⚠️ [AWS] Error al traer el historial clínico: {e}")
    return jsonify([])

@app.route('/api/control')
def control():
    # Ruta pasiva en AWS. Mantiene la compatibilidad por si el diseño intenta mandar comandos de movimiento,
    # pero en la nube no ejecuta acciones de hardware.
    return "OK"

@app.route('/api/capturar_foto')
def capturar_foto():
    # Informativo para el frontend: Las capturas y procesamiento de imágenes
    # se ejecutan en local e impactan de manera directa en el MongoDB compartido.
    return jsonify({"mensaje": "La captura fotográfica se procesa e inserta directamente desde la estación local."})

if __name__ == '__main__':
    # Producción en AWS dentro de Docker
    app.run(host='0.0.0.0', port=5000, debug=False)
