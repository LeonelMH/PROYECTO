from flask import Flask, render_template, request, jsonify
from threading import Thread
from analizadores import lexico
import speech_recognition as sr
print(sr.Microphone.list_microphone_names())

for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"{i}: {name}")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('semantico.html')

@app.route('/lexico')
def lexico_page():
    return render_template('lexico.html')  # No inicia el hilo aún

@app.route('/toggle', methods=['POST'])
def toggle():
    activo = request.json.get('activo')
    lexico.set_activo(activo)

    if activo and not lexico.hilo_activo:
        lexico.hilo_activo = True
        Thread(target=lexico.iniciar_lexico, daemon=True).start()

    return jsonify({'estado': 'actualizado'})

@app.route('/limpiar', methods=['POST'])
def limpiar():
    lexico.frases_detectadas.clear()
    lexico.log_voz.clear()
    return jsonify({'estado': 'limpio'})

@app.route('/frases')
def frases():
    return jsonify({
        'frases': lexico.frases_detectadas[-50:],
        'deteccion': lexico.log_voz[-50:],
        'frases_fatiga': lexico.frases_cansancio,
        'frases_recuperacion': lexico.frases_recuperacion
    })

from analizadores import semantico

@app.route('/semantico')
def semantico_page():
    return render_template('semantico.html')

@app.route('/toggle_semantico', methods=['POST'])
def toggle_semantico():
    activo = request.json.get('activo')
    semantico.set_activo(activo)
    if activo and not semantico.hilo_activo:
        semantico.hilo_activo = True
        Thread(target=semantico.iniciar_semantico, daemon=True).start()
    return jsonify({'estado': 'actualizado'})

@app.route('/limpiar_semantico', methods=['POST'])
def limpiar_semantico():
    semantico.frases_detectadas.clear()
    semantico.log_voz.clear()
    semantico.analisis_semantico.clear()
    semantico.contador_intenciones = {k: 0 for k in semantico.contador_intenciones}
    return jsonify({'estado': 'limpio'})

@app.route('/frases_semantico')
def frases_semantico():
    return jsonify({
        'frases': semantico.frases_detectadas[-50:],
        'lexico': semantico.log_voz[-50:],
        'semantico': semantico.analisis_semantico[-50:],
        'contador': semantico.contador_intenciones
    })

@app.route('/estado_facial')
def estado_facial_web():
    from analizadores import facial_monitor
    return jsonify({'estado': facial_monitor.estado_facial, 'ear': round(facial_monitor.avg_ear, 2)})

from datetime import datetime

@app.route('/registrar_fatiga', methods=['POST'])
def registrar_fatiga():
    data = request.get_json()
    ear = data.get('ear')
    estado = data.get('estado')
    tipo = data.get('tipo', 'ocular')
    hora = data.get('hora', datetime.now().strftime('%H:%M:%S'))

    if tipo == "ocular":
        mensaje = f"{hora} → 🔴 Fatiga ocular detectada (EAR={ear:.3f})"
        semantico.analisis_semantico.append(mensaje)
        semantico.contador_intenciones["fatiga_ocular"] += 1
    else:
        mensaje = f"{hora} → 🔴 Fatiga verbal detectada"
        semantico.analisis_semantico.append(mensaje)
        semantico.contador_intenciones["fatiga_verbal"] += 1

    print(mensaje)
    return jsonify({"status": "ok"})

import subprocess

@app.route('/iniciar_lexico', methods=['POST'])
def iniciar_lexico():
    try:
        subprocess.Popen(["python", "camarafrontalLexico.py"])
        return jsonify({"estado": "iniciado"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)