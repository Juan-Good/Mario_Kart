import cv2
import mediapipe as mp
import numpy as np
import time
from directkeys import A, D, Z, S,  left, right, X, Space, ReleaseKey, PressKey


#Se declaran los estilos con los que se dibujara la pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

#Se define una función que permite  calcular el angulo entre la linea formada por dos puntos y la horizontal

def calculate_angle(a,b):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = [a[0]+1, a[1]] 
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = (radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle 

#Se hace una declaración de los puntos con los que se va a trabajar 
mano_der = [1, 1]
mano_izq = [1.1, 2]
hombro_der = [1,1]
hombro_izq = [1,1]


# Se definen los umbrales, es decir las condiciones de activación para distintas acciones, 
# modificar estos valores cambiara la sensibilidad

# Define el angulo respecto a la liea formada por las muñecas, que activa la dirección derecha o izquierda
umbral_manejo=15
umbral_acelerar=20  
umbral_poder=-2

    
#configurar camaras 0 webcam, 1 externa
cap = cv2.VideoCapture(0)


with mp_pose.Pose(min_detection_confidence=0.5,
                  min_tracking_confidence=0.5) as pose:
    direc = "Recta"
    msg_a = "nada"
    msg_f = "nada"
 

    while cap.isOpened():
        go = False 
        success, image = cap.read()
        no_dir=True    
        results = pose.process(image)

        #Exraer landmaks
        try:
            landmarks = results.pose_landmarks.landmark

            mano_izq = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            mano_der = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
            hombro_izq = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            hombro_der = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            go = True  #Indica que si existe una pose
        except:
            pass

        # Dibuja la pose sobre la iamgen capturada
        mp_drawing.draw_landmarks(image,
                                  results.pose_landmarks,
                                  mp_pose.POSE_CONNECTIONS,
                                  landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        cv2.line(image, tuple(np.multiply(mano_izq, [640, 480]).astype(int)),
                 tuple(np.multiply(mano_der, [640, 480]).astype(int)), (255, 0, 0))

        #######
        image = cv2.flip(image, 1)

        #Interpretación de gestos

        ############################## Player 1    
        #Controles P1
        #Derecha D
        #Izquierda A
        #Acelerar X
        #Poder Z
        #Saltar S
        #Frenar c
        
        #Dirección
        angulo_manejo = calculate_angle(mano_izq, mano_der)    

        if angulo_manejo>umbral_manejo: # Si inclina las manos hacia la derecha
            ReleaseKey(A)  #Se liberan todas las teclas
            ReleaseKey(Z)
            ReleaseKey(S)       
            direc= "derecha"
            #Si existe una pose acelere y gire a la direcha
            if go:        
                PressKey(D)
                PressKey(X)
                no_dir = False

        if angulo_manejo<-umbral_manejo:
            ReleaseKey(D)
            ReleaseKey(Z)
            ReleaseKey(S)
            direc= "izquierda"
            #Si existe una pose acelere y gire a la izquierda
            if go: 
                PressKey(A)
                PressKey(X)   
                no_dir = False
        #Si no esta girando en ninguna dirección, suelte las teclas de dirección.
        if no_dir:   
            ReleaseKey(D)
            ReleaseKey(A)
 
        #Poder
        # Se activa subiendo la mano derecha
        angulo_poder=calculate_angle(hombro_izq, mano_der) 
 
        if angulo_poder<umbral_poder:
            ReleaseKey(A)
            ReleaseKey(Z)
            PressKey(Z)
            time.sleep(0.01)

         #SALTAR   
         # Se activa subiendo la mano izquerda
        angulo_salto=calculate_angle(mano_izq, hombro_der) 
        if angulo_salto>-5: 
            ReleaseKey(D)  
            ReleaseKey(S)
            PressKey(S)
            time.sleep(0.01)

        #Acelerar 
        # Si baja las manos
        if angulo_poder>umbral_acelerar and angulo_salto<-umbral_acelerar:
            msg_a= "acelera"
            PressKey(X)
        
        cv2.putText(image, direc, 
                               (70,50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (25, 0, 250), 2, cv2.LINE_AA
                                    )

        cv2.imshow('MediaPipe Pose', image)
        if cv2.waitKey(10) & 0xFF == ord('q'):
                break
cap.release()
cv2.destroyAllWindows()
