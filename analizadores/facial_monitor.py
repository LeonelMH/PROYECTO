import time, cv2, mediapipe as mp, numpy as np
import threading

# Variables exportadas
estado_facial = "normal"
avg_ear = 0.30

# Parámetros de fatiga visual
EAR_THRESHOLD = 0.30
WINDOW_DURATION = 3
FATIGUE_PERCENTAGE_THRESHOLD = 0.85
RECOVERY_THRESHOLD = 0.51

# Inicialización de MediaPipe
mp_dibujo = mp.solutions.drawing_utils
mp_malla_cara = mp.solutions.face_mesh

def compute_EAR(eye_pts):
    p1, p2, p3, p4, p5, p6 = [np.array(pt) for pt in eye_pts]
    vertical = np.linalg.norm(p2 - p6) + np.linalg.norm(p3 - p5)
    horizontal = np.linalg.norm(p1 - p4)
    return vertical / horizontal

def monitorear_facial():
    global estado_facial, avg_ear
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("No se pudo acceder a la cámara.")
        return

    records = []

    with mp_malla_cara.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as malla_cara:
        while True:
            ok, frame = cap.read()
            if not ok:
                continue

            frame_rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
            results = malla_cara.process(frame_rgb)

            if results.multi_face_landmarks:
                cara = results.multi_face_landmarks[0]

                # Ojo derecho
                eye_idxs = [33, 160, 158, 133, 153, 144]
                eye_pts = [(cara.landmark[i].x * frame.shape[1], cara.landmark[i].y * frame.shape[0]) for i in eye_idxs]
                ear = compute_EAR(eye_pts)

                # Ojo izquierdo
                left_eye_idxs = [263, 387, 385, 362, 380, 373]
                left_eye_pts = [(cara.landmark[i].x * frame.shape[1], cara.landmark[i].y * frame.shape[0]) for i in left_eye_idxs]
                left_ear = compute_EAR(left_eye_pts)

                avg_ear = (ear + left_ear) / 2
                timestamp = time.time()
                records.append((timestamp, avg_ear))
                records = [(t, e) for (t, e) in records if timestamp - t <= WINDOW_DURATION]

                ears = [e for (_, e) in records]
                low_count = sum(e < EAR_THRESHOLD for e in ears)
                fatigue_rate = low_count / len(ears) if ears else 0

                estado_facial = "fatiga" if fatigue_rate > FATIGUE_PERCENTAGE_THRESHOLD else "normal"

            time.sleep(0.5)

# Iniciar hilo automáticamente
#hilo = threading.Thread(target=monitorear_facial, daemon=True)
#hilo.start()