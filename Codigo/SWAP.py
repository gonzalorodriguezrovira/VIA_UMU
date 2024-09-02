#https://github.com/gonzalorodriguezrovira/VIA_UMU

import cv2 as cv
from umucv.stream import autoStream
from collections import deque
import numpy as np
from umucv.util import putText


points2=deque(maxlen=8)#Lista donde almacenare los puntos que delimitan mis dos secciones a intercambiar
activado=False#Variable para controlar si quiere que se esten intercambiando mis dos secciones
TAMAÑO_SECCION=50#Constnte que determina el tamaño de las secciones a intercambiar

def fun(event, x, y, flags, param):#Funcion que al detetar el click añade puntos al rededor de donde se hizo el click para determinar la seccion a intercambiar
    
    if event == cv.EVENT_LBUTTONDOWN:
        
        points2.append((x-TAMAÑO_SECCION,y+TAMAÑO_SECCION))
        points2.append((x+TAMAÑO_SECCION,y+TAMAÑO_SECCION))
        points2.append((x+TAMAÑO_SECCION,y-TAMAÑO_SECCION))
        points2.append((x-TAMAÑO_SECCION,y-TAMAÑO_SECCION))
        
cv.namedWindow("webcam")
cv.setMouseCallback("webcam", fun)

for key, frame in autoStream():
         
    for p in points2:
        
        cv.circle(frame, p,3,(0,0,255),-1)
            
    if points2:#Cuando tengo puntos, es decir hice por lo menos un click se dibuja la seccion (puntos y lineas)
            
        cv.line(frame, points2[0],points2[1],(0,0,255))
        cv.line(frame, points2[1],points2[2],(0,0,255))
        cv.line(frame, points2[2],points2[3],(0,0,255))
        cv.line(frame, points2[3],points2[0],(0,0,255))
    
    if len(points2) == 8:#En el caso de qwue tenga 8 puntos quiere decir de que tengo mis dos secciones por lo que dibujo la segunda

        cv.line(frame, points2[4],points2[5],(0,0,255))
        cv.line(frame, points2[5],points2[6],(0,0,255))
        cv.line(frame, points2[6],points2[7],(0,0,255))
        cv.line(frame, points2[7],points2[4],(0,0,255))
        
    if key == ord('i'):#Si pulso la tecla i quiere decir que quiero intercambiar mis dos secciones, si vuelve a ser pulsada volvera a la imagen original
            
        activado= not activado
            
    if activado:#Si quiero intercambiar mis secciones
            
        #Guardo mis regiones para intercambiar y cloco el copy para crea copias independientes de las áreas del frame evitando que se sobrescriban accidentalmente
        part1 = frame[points2[2][1]:points2[0][1], points2[0][0]:points2[2][0]].copy()
        part2 = frame[points2[6][1]:points2[4][1], points2[4][0]:points2[6][0]].copy()
        #Realizo el intercambio de secciones con las variables donde tenia guardada la otra seccion
        frame[points2[6][1]:points2[4][1], points2[4][0]:points2[6][0]] = part1
        frame[points2[2][1]:points2[0][1], points2[0][0]:points2[2][0]] = part2
            
    cv.imshow('webcam',frame)
    
cv.destroyAllWindows()