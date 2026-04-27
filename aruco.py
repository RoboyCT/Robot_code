import cv2
import serial
import time
from ArucoTracker import ArucoTracker

try:
    arduino = serial.Serial('COM5', 9600)
    time.sleep(2)
    print("Connessione seriale con Arduino stabilita.")
except:
    arduino = None
    print("Errore: impossibile connettersi all'Arduino su COM5.")

# Funzione per inviare una lettera via seriale
def invia_lettera(lettera):
    if arduino:
        arduino.write(lettera.encode())
        print(f"Lettera inviata: {lettera}")

def main():
    # Initialize USB camera
    cap = cv2.VideoCapture(0)
    
    # Initialize ArucoTracker object
    aruco_tracker = ArucoTracker([23, 42])

    try:
        while True:
            # Read frame from camera
            _, frame = cap.read()

            # Find aruco markers in the frame
            markerID, errors, angle, frame_aruco = aruco_tracker.find_markers(frame)
            if markerID is not None:
                frame = frame_aruco
                print(f'Found aruco {markerID}')            
                print(f'Errors: {errors}')
                angolo=(angle * 180 / 3.1415)
                print(f'Angolo: {angolo}')
                if angolo > 80 and angolo < 100:
                    invia_lettera('F')
                if angolo > 100 and angolo < 150:
                    invia_lettera('J')
                if angolo < 80 and angolo > 50:
                    invia_lettera('I')
                if angolo < -80 and angolo <-100:
                    invia_lettera('B')
            else:
                invia_lettera('T')
            # Show frame
            cv2.imshow('Aruco Marker Detection', frame)
            
            # Exit on 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        print('\nCtrl+C pressed')

    finally:
        # Release camera and close windows
        print('Closing...')
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
