# 🤖 Rover Autonomo con Rilevamento ArUco e Incendio

Sistema robotico autonomo che combina visione artificiale (tracking marker ArUco e rilevamento incendi) con controllo di un rover via comunicazione seriale Arduino.

---

## 📁 Struttura del progetto

```
├── Rover.ino           # Firmware Arduino - controllo motori del rover
├── riceviDati.ino      # Firmware Arduino - bridge seriale (Serial → Serial1)
├── ArucoTracker.py     # Classe Python per il rilevamento marker ArUco
├── aruco.py            # Script principale: tracking ArUco + controllo rover
└── fuocoGpu.py         # Rilevamento incendio via HSV + YOLO (GPU)
```

---

## ⚙️ Componenti e funzionamento

### 🔧 `Rover.ino` — Controllo motori
Firmware Arduino che riceve comandi via seriale (9600 baud) e controlla 4 motori DC tramite pin digitali.

| Comando | Azione |
|---------|--------|
| `F` | Avanza |
| `B` | Arretra |
| `J` | Gira a destra |
| `I` | Gira a sinistra |
| `T` | Stop |

**Pin utilizzati:** 10, 11, 12, 13

---

### 🔌 `riceviDati.ino` — Bridge seriale
Sketch Arduino che legge caratteri da `Serial` (USB) e li ritrasmette su `Serial1` (UART hardware). Utile per inoltrare comandi da PC a un secondo dispositivo (es. modulo Bluetooth o secondo Arduino).

---

### 🎯 `ArucoTracker.py` — Classe tracker ArUco
Classe Python basata su **OpenCV** per il rilevamento di marker ArUco.

**Funzionalità:**
- Dizionario: `DICT_ARUCO_ORIGINAL`
- Calcola la posizione del marker normalizzata in `[-1, 1]` rispetto al centro del frame
- Calcola l'**angolo di orientamento** del marker in radianti
- Disegna bounding box, centro e freccia direzionale sul frame

**Metodo principale:**
```python
markerID, (cXnorm, cYnorm), angle, frame = tracker.find_markers(frame)
```

---

### 🧠 `aruco.py` — Script principale di controllo
Integra `ArucoTracker` con la comunicazione seriale verso Arduino per guidare il rover in base all'orientamento del marker rilevato.

**Logica di controllo basata sull'angolo del marker:**

| Angolo (gradi) | Comando inviato | Azione rover |
|----------------|-----------------|--------------|
| 80° – 100°     | `F`             | Avanza       |
| 100° – 150°    | `J`             | Gira a destra |
| 50° – 80°      | `I`             | Gira a sinistra |
| Marker assente | `T`             | Stop         |

**Marker ArUco riconosciuti:** ID `23`, ID `42`  
**Porta seriale:** `COM5` a 9600 baud  
**Camera:** indice `1`

---

### 🔥 `fuocoGpu.py` — Rilevamento incendio (HSV + YOLO)
Sistema ibrido a due stadi per il rilevamento di incendi in tempo reale con accelerazione GPU.

**Stadio 1 — Filtro HSV (trigger rapido):**
- Maschera su rosso/arancio: `H[0-22]`, `S[120-255]`, `V[100-255]`
- Maschera su giallo brillante: `H[23-45]`, `S[50-255]`, `V[200-255]`
- Pulizia morfologica con kernel 5×5
- YOLO viene attivato **solo se** i pixel rilevati superano la soglia di **300**

**Stadio 2 — Inferenza YOLO (GPU):**
- Modello custom caricato da file `.pt`
- Eseguito su `cuda` per massime prestazioni
- Soglia di confidenza: `0.5`
- Se YOLO conferma: overlay `"FUOCO RILEVATO"` sul frame

---

## 🛠️ Requisiti

### Python
```
opencv-python
numpy
pyserial
ultralytics
```

Installa con:
```bash
pip install opencv-python numpy pyserial ultralytics
```

### Hardware richiesto
- Arduino (con driver motori collegati) su `COM5`
- Webcam USB (indice `1`)
- GPU NVIDIA con CUDA (per `fuocoGpu.py`)
- Modello YOLO custom (`best.pt`) addestrato su fiamme

### Arduino
- Carica `Rover.ino` sull'Arduino che controlla i motori
- Carica `riceviDati.ino` su un eventuale Arduino bridge

---

## 🚀 Utilizzo

### Avviare il tracking ArUco + controllo rover
```bash
python aruco.py
```
- Premi `Q` per uscire

### Avviare il rilevamento incendio
```bash
python fuocoGpu.py
```
- Modifica il path del modello `.pt` in `fuocoGpu.py` prima di avviare
- Premi `Q` per uscire

---

## 📝 Note
- Verifica che la porta seriale (`COM5`) corrisponda al tuo sistema. Su Linux potrebbe essere `/dev/ttyUSB0` o simile.
- L'indice della camera (`0` o `1`) dipende dalle webcam disponibili sul sistema.
- Il modello YOLO (`best.pt`) non è incluso nel repository: deve essere addestrato o fornito separatamente.
