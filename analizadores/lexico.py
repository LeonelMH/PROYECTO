import time, pygame, speech_recognition as sr
import os

frases_detectadas = []
log_voz = []
activo = False
hilo_activo = False

frases_cansancio = [
    "estoy cansado",
    "necesito descansar",
    "no puedo más",
    "no puedo mas",
    "me siento fatigado",
    "estoy agotado",
    "me siento exhausto",
    "ya no rindo",
    "me cuesta concentrarme",
    "tengo sueño",
    "me siento débil",
    "me siento debil",
    "estoy adormilado",
    "no tengo energía",
    "no tengo energia",
    "me siento lento",
    "estoy abrumado",
    "me siento saturado",
    "necesito una pausa",
    "estoy quemado",
    "me siento sin fuerzas",
    "no estoy al cien",
    "no estoy al 100",
    "me siento distraído"
]

frases_recuperacion = [
    "ya estoy bien",
    "me siento mejor",
    "ya descansé",
    "ya descanse",
    "estoy despierto",
    "me siento renovado",
    "estoy listo",
    "me siento con energía",
    "ya me recuperé",
    "ya me recupere",
    "me siento enfocado",
    "estoy al cien",
    "ya estoy al 100",
    "ya estoy activo",
    "me siento despejado",
    "estoy alerta",
    "ya estoy concentrado",
    "me siento motivado",
    "ya estoy de vuelta",
    "me siento presente",
    "estoy en forma",
    "ya pasó el cansancio",
    "me siento estable"
]






def set_activo(valor):
    global activo
    activo = valor
    log_voz.append("🟢 Captura iniciada" if valor else "🟡 Captura detenida")

    if not valor:
        try:
            import pygame
            pygame.mixer.music.stop()
            log_voz.append("🔇 Alarma detenida")
        except Exception as e:
            log_voz.append(f"⚠️ Error al detener alarma: {str(e)}")


def iniciar_lexico():
    pygame.mixer.init()
    ruta_audio = os.path.join(os.path.dirname(__file__), "..", "static", "Estoy cansado jefe.mp3")
    pygame.mixer.music.load(ruta_audio)


    r = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            if not activo:
                pygame.mixer.music.stop()  # 🔇 Detener alarma si está sonando
                time.sleep(1)
                continue

            log_voz.append(" Escuchando...")
            try:
                audio = r.listen(source, timeout=10)

                if not activo:
                    continue  # Evita procesar si se desactivó justo después de escuchar

                texto = r.recognize_google(audio, language="es-MX").lower()
                log_voz.append(f" Frase reconocida: {texto}")
                frases_detectadas.append(f"{time.strftime('%H:%M:%S')} → {texto}")

                if any(f in texto for f in frases_cansancio):
                    log_voz.append("🔴 Fatiga verbal detectada.")
                    pygame.mixer.music.play(-1)
                elif any(f in texto for f in frases_recuperacion):
                    log_voz.append("🟢 Recuperación verbal detectada.")
                    pygame.mixer.music.stop()
            except Exception as e:
                if activo:  # Solo mostrar error si la captura está activa
                    log_voz.append(f" Error al reconocer voz: {str(e)}")
            time.sleep(1)