from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime
import os

app = Flask(__name__)

# --- CONFIGURACIÓN DE MONGODB ---
# En Docker, 'mongodb' es el nombre del servicio en docker-compose
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client.proyecto_so2
    logs_col = db.eventos
    estado_col = db.estado_actual # Colección para la humedad en tiempo real
    print("AWS: Conexión a MongoDB exitosa")
except Exception as e:
    print(f"AWS Error BD: {e}")
    logs_col = None

@app.route('/')
def index():
    return jsonify({"status": "AWS Cloud Backend Running"})

@app.route('/get_humedad')
def get_humedad():
    try:
        # AWS lee lo que la laptop subió a MongoDB
        estado = estado_col.find_one({"sensor": "humedad"})
        if estado:
            return str(estado['valor'])
    except:
        pass
    return "---"

@app.route('/get_logs')
def get_logs():
    if logs_col is not None:
        try:
            eventos = logs_col.find().sort("fecha", -1).limit(10)
            lista_logs = []
            for e in eventos:
                # Nos aseguramos de que la fecha sea un string antes de enviar
                fecha_obj = e.get("fecha")
                hora_str = fecha_obj.strftime("%H:%M:%S") if isinstance(fecha_obj, datetime.datetime) else "N/A"
                
                lista_logs.append({
                    "accion": e.get("accion", "N/A"),
                    "humedad": e.get("humedad", "0"),
                    "hora": hora_str
                })
            return jsonify(lista_logs)
        except Exception as e:
            print(f"Error logs: {e}")
    return jsonify([])

@app.route('/control')
def control():
    cmd = request.args.get('cmd')
    # En AWS, el control solo guarda la intención en la BD
    # La laptop verá este registro y moverá el carrito
    if logs_col is not None:
        nombres = {'W':'Adelante','S':'Atrás','A':'Izquierda','D':'Derecha','X':'Parar','P':'Sembrar','R':'Regar'}
        log = {
            "fecha": datetime.datetime.now(),
            "accion": nombres.get(cmd, cmd),
            "humedad": "---", # Se actualizará cuando la laptop lo procese
            "origen": "Cloud Dashboard"
        }
        logs_col.insert_one(log)
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
