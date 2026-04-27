import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO('C:\\Users\\vacca\\Desktop\\best.pt')
model.to('cuda')

# --- CONFIGURAZIONE RANGE ---
# Range 1: Rosso e Arancio (Colori ricchi)
lower_red_orange = np.array([0, 120, 100])
upper_red_orange = np.array([22, 255, 255])

# Range 2: Giallo Brillante (Nucleo della fiamma, es. accendino)
lower_yellow = np.array([23, 50, 200]) # S più bassa per il giallo/bianco, V molto alta
upper_yellow = np.array([45, 255, 255])

cap = cv2.VideoCapture(1)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Creazione delle due maschere
    mask_red = cv2.inRange(hsv, lower_red_orange, upper_red_orange)
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # Unione delle maschere: prende Rosso OR Arancio OR Giallo
    combined_mask = cv2.bitwise_or(mask_red, mask_yellow)

    # Pulizia morfologica (rimuove i pixel isolati)
    kernel = np.ones((5, 5), np.uint8)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)

    # Trigger per YOLO
    fire_pixels = cv2.countNonZero(combined_mask)
    trigger_active = fire_pixels > 400 

    display_frame = frame.copy()

    if trigger_active:
        # Esegui YOLO solo se il trigger HSV è attivo
        results = model(frame, conf=0.5, verbose=False, device='cuda')
        
        if len(results[0].boxes) > 0:
            display_frame = results[0].plot()
            cv2.putText(display_frame, "FUOCO RILEVATO", (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        else:
            cv2.putText(display_frame, "SOSPETTO (Analisi YOLO...)", (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # DEBUG VISIVO
    cv2.putText(display_frame, f"Pixel: {fire_pixels}", (20, frame.shape[0]-20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    cv2.imshow('Rilevamento Incendio', display_frame)
    cv2.imshow('Maschera Combinata (Debug)', combined_mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
