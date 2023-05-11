import cv2
import mediapipe as mp
import numpy as np

import time
from directkeys import A, D, Z, S,  X, R,T, Y,F ,H,  ReleaseKey, PressKey


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

def calculate_angle(a,b):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = [a[0]+1, a[1]] 
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = (radians*180.0/np.pi)
    
    if angle >180.0:
        angle = 360-angle
        
    return angle 


mano_der = [1, 1]
mano_izq = [1.1, 2]
hombro_der = [1,1]
hombro_izq=[1,1]

mano_der_2 = [1, 1]
mano_izq_2 = [1.1, 2]
hombro_der_2 = [1,1]
hombro_izq_2=[1,1]


umbral_manejo=15

umbral_acelerar=20  


    
#configurar camaras 0 webcam, 1 externa

cap = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)



if not cap.isOpened() or not cap2.isOpened():
    print("No se pudieron abrir las cámaras")
    exit()

with mp_pose.Pose(min_detection_confidence=0.5,
                  min_tracking_confidence=0.5) as pose:
    direc = "Recta"
    msg_a = "nada"
    msg_f = "nada"
 

    while cap.isOpened():
        go = False 
        go_2 = False
        success, image = cap.read()
        ret2, image_2 = cap2.read()

        no_dir=True    
        no_dir_2=True
        results = pose.process(image)
        results_2 = pose.process(image_2)

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
            go = True
        except:
            pass
        #Segundo Jugador
        try:
            landmarks_2 = results_2.pose_landmarks.landmark

            mano_izq_2 = [landmarks_2[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                        landmarks_2[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            mano_der_2 = [landmarks_2[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                        landmarks_2[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
            hombro_izq_2 = [landmarks_2[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                          landmarks_2[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            hombro_der_2 = [landmarks_2[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks_2[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            go_2 = True
        except:
            pass


        # Draw the pose annotation on the image.
        mp_drawing.draw_landmarks(image,
                                  results.pose_landmarks,
                                  mp_pose.POSE_CONNECTIONS,
                                  landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        cv2.line(image, tuple(np.multiply(mano_izq, [640, 480]).astype(int)),
                 tuple(np.multiply(mano_der, [640, 480]).astype(int)), (255, 0, 0),2)
        
        mp_drawing.draw_landmarks(image_2,
                                  results_2.pose_landmarks,
                                  mp_pose.POSE_CONNECTIONS,
                                  landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        cv2.line(image_2, tuple(np.multiply(mano_izq_2, [640, 480]).astype(int)),
                 tuple(np.multiply(mano_der_2, [640, 480]).astype(int)), (255, 0, 0),2)

        #######
        image = cv2.flip(image, 1)
        image_2 = cv2.flip(image_2, 1)

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

        if angulo_manejo > umbral_manejo: 
            ReleaseKey(A)
            ReleaseKey(Z)
            ReleaseKey(S)       

            direc= "derecha"
            if go: 
                ReleaseKey(D)
                PressKey(D)
                PressKey(X)
                time.sleep(0.01)
                no_dir = False

        if angulo_manejo<-umbral_manejo:
            ReleaseKey(D)
            ReleaseKey(Z)
            ReleaseKey(S)
            direc= "izquierda"
            if go: 

                ReleaseKey(A)
                PressKey(A)
                PressKey(X) 
                time.sleep(0.01)
                  
                no_dir = False

        if no_dir:
            ReleaseKey(D)
            ReleaseKey(A)
 
        #Poder
        angulo_poder=calculate_angle(hombro_izq, mano_der) 

        #Frenado
        distancia_manos=mano_izq[0]- mano_der[0]
        umbral_frenar=0.65
        if distancia_manos>umbral_frenar:
            msg_f= "frenar"
            
        #Poder     
        if angulo_poder<-2:
            ReleaseKey(A) 
            ReleaseKey(Z) 
            PressKey(Z)
            time.sleep(0.01)
            

         #SALTAR   
        angulo_salto=calculate_angle(mano_izq, hombro_der) 
        if angulo_salto>-5: 
            ReleaseKey(D) 
            ReleaseKey(S) 
            PressKey(S)
            time.sleep(0.01)

        #Acelerar 
        if angulo_poder>umbral_acelerar and angulo_salto<-umbral_acelerar:
            msg_a= "acelera"
            PressKey(X)

        ############################## Player 2    
        #Controles P2 
        #Derecha H
        #Izquierda F
        #Acelerar T
        #Poder R
        #Saltar Y
        #Frenar H

        #Dirección

        angulo_manejo_2 = calculate_angle(mano_izq_2, mano_der_2)    

        if angulo_manejo_2>umbral_manejo: #Derecha
            ReleaseKey(F)
            ReleaseKey(Y)
            ReleaseKey(R)       

            if go_2: 
                ReleaseKey(H)
                PressKey(H)
                PressKey(T)   
                time.sleep(0.01)
                no_dir_2 = False

        if angulo_manejo_2<-umbral_manejo: # Izquierda
            ReleaseKey(H)
            ReleaseKey(Y)
            ReleaseKey(R)       
            if go_2: 
                ReleaseKey(F)
                PressKey(F)
                PressKey(T)  
                time.sleep(0.01) 
                no_dir_2 = False

        if no_dir_2:
            ReleaseKey(F)
            ReleaseKey(H)
 
        #Poder
        angulo_poder_2=calculate_angle(hombro_izq_2, mano_der_2) 


        #Poder     
        if angulo_poder_2<-2:
            ReleaseKey(F) 
            ReleaseKey(R) 
            PressKey(R)
            time.sleep(0.01)

         #SALTAR   
        angulo_salto_2=calculate_angle(mano_izq_2, hombro_der_2) 

        if angulo_salto_2>-5: 
            ReleaseKey(H) 
            ReleaseKey(Y) 
            PressKey(Y)
            time.sleep(0.01)
           

        #Acelerar 
        if angulo_poder_2>umbral_acelerar and angulo_salto_2<-umbral_acelerar:
            msg_a= "acelera"
            PressKey(T)


        cv2.imshow('MediaPipe Pose', image)

        cv2.imshow('Camera 2', image_2)
        if cv2.waitKey(10) & 0xFF == ord('q'):
                break
cap.release()
cv2.destroyAllWindows()
