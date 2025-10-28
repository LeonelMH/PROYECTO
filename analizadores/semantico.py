import time
import pygame
import speech_recognition as sr
from threading import Thread
import spacy
from analizadores.facial_monitor import estado_facial, avg_ear
import os

# Inicializar spaCy
nlp = spacy.load("es_core_news_md")

# Variables globales
frases_detectadas = []
log_voz = []
analisis_semantico = []
contador_intenciones = {
    "fatiga_verbal": 0,
    "fatiga_ocular": 0,
    "positiva": 0,
    "contradiccion": 0,
    "solicitud": 0,
    "recuperacion": 0
}

# Control de captura
activo = False
hilo_activo = False

# Frases léxicas
frases_cansancio = [
    "estoy cansado", "necesito descansar", "no puedo más",
    "me siento fatigado", "estoy agotado", "me siento exhausto"
]
frases_recuperacion = [
    "ya estoy bien", "me siento mejor", "ya descansé", "estoy despierto"
]

def set_activo(valor):
    global activo
    activo = valor
    log_voz.append("🟢 Captura iniciada" if valor else "🟡 Captura detenida")
    analisis_semantico.append("🟢 Captura iniciada" if valor else "🟡 Captura detenida")

def analizar_semantica(texto):
    doc = nlp(texto)

    if "pero" in texto and ("bien" in texto or "mejor" in texto) and ("cansado" in texto or "agotado" in texto):
        contador_intenciones["contradiccion"] += 1
        return "⚠️ Contradicción detectada: bienestar vs fatiga"

    if any(token.lemma_ in ["ayudar", "necesitar"] for token in doc):
        contador_intenciones["solicitud"] += 1
        return "🟠 Intención de solicitud detectada"

    if any(token.lemma_ in ["agradecer", "gracias", "mejorar"] for token in doc):
        contador_intenciones["positiva"] += 1
        return "🟢 Intención positiva detectada"

    if doc.similarity(nlp("me siento agotado")) > 0.75:
        contador_intenciones["fatiga"] += 1
        return "🔴 Fatiga verbal detectada (por similitud)"

    if estado_facial == "fatiga":
        contador_intenciones["fatiga"] += 1
        return "🔴 Fatiga visual detectada (EAR={:.2f})".format(avg_ear)

    return "🔍 Sin intención semántica destacada"

def iniciar_semantico():
    global hilo_activo
    Thread(target=iniciar_semantico, daemon=True).start()
    try:
        pygame.mixer.init()
        ruta_audio = os.path.join(os.path.dirname(__file__), "..", "static", "Estoy cansado jefe.mp3")
        pygame.mixer.music.load(ruta_audio)
    except Exception as e:
        log_voz.append(f"⚠️ Error al cargar audio: {e}")
        analisis_semantico.append(f"⚠️ Error al cargar audio: {e}")
        return

    r = sr.Recognizer()
    with sr.Microphone(device_index=1) as source:
        while True:
            if not activo:
                time.sleep(1)
                continue

            log_voz.append("🎤 Escuchando...")
            try:
                r.adjust_for_ambient_noise(source, duration=1)
                audio = r.listen(source, timeout=10, phrase_time_limit=8)
                texto = r.recognize_google(audio, language="es-MX").lower()
                timestamp = time.strftime('%H:%M:%S')
                frases_detectadas.append(f"{timestamp} → {texto}")
                log_voz.append(f"🗣️ Frase reconocida: {texto}")

                # Análisis léxico
                if any(f in texto for f in frases_cansancio):
                    log_voz.append("🔴 Fatiga verbal detectada.")
                    contador_intenciones["fatiga"] += 1
                    pygame.mixer.music.play(-1)
                elif any(f in texto for f in frases_recuperacion):
                    log_voz.append("🟢 Recuperación verbal detectada.")
                    contador_intenciones["recuperacion"] += 1
                    pygame.mixer.music.stop()
                else:
                    log_voz.append("🔍 Sin coincidencia léxica destacada.")

                # Análisis semántico
                resultado_semantico = analizar_semantica(texto)
                analisis_semantico.append(resultado_semantico)

            except sr.WaitTimeoutError:
                log_voz.append("⏳ Tiempo de espera agotado.")
                analisis_semantico.append("⏳ Tiempo de espera agotado.")
            except sr.UnknownValueError:
                log_voz.append("🤷 No se entendió la frase.")
                analisis_semantico.append("🤷 No se entendió la frase.")
            except Exception as e:
                log_voz.append(f"⚠️ Error: {e}")
                analisis_semantico.append(f"⚠️ Error: {e}")

            time.sleep(1)