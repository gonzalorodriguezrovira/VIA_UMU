#!/usr/bin/env python
#https://github.com/gonzalorodriguezrovira/VIA_UMU

import cv2 as cv
import math
from umucv.stream import autoStream
from collections import deque
import numpy as np
from umucv.util import putText


points = deque(maxlen=2)#Declaro una lista de maximo dos elementos para poder guardas las cordenadas x y de mis dos puntos
f=613.81#Parametro f sacado de calibrate.py
w=605#Parametro ancho en pixeles de las fotos de mi camara
h=806#Parametro alto en pixeles de las fotos de mi camara

def fun(event, x, y, flags, param):#Defino una función para que en caso de dar un click en la pantalla me guarde las cordendas x,y del punto clikeado
    if event == cv.EVENT_LBUTTONDOWN:
        points.append((x,y))

cv.namedWindow("webcam")#Inicializo mi ventana donde monstrare el video
cv.setMouseCallback("webcam", fun)#Asigno a mi ventana  la funcion previamente declarada

for key, frame in autoStream():
    
    for p in points:#Para cada punto que forma mi lista de puntos les dibujo un circulo en sus cordenadas
        
        cv.circle(frame, p,3,(0,0,255),-1)
        
    if len(points) == 2:#Una vez que tengo dos puntos puedo empezar a calcular sobre estos los angulos que forman
        
        cv.line(frame, points[0],points[1],(0,0,255))#Dibujo una linea entre mis dos puntos
        c = np.mean(points, axis=0).astype(int)#Calculo el punto medio de mis dos puntos para poder colocar en su posición el valor del angulo que forman
        
        u=[(points[0])[0]-w/2,(points[0])[1]-h/2,f]#Calculo mi matriz K completa
        v=[(points[1])[0]-w/2,(points[1])[1]-h/2,f]
        
        
        a=(np.dot(u,v))/(np.linalg.norm(u)*np.linalg.norm(v))#Despejo mi angulo al calcular el producto escalar de mis matrices y lo divido entre la multiplicacion de los modulos de mis vectores
        a= np.rad2deg((math.acos(a)))#Finalmente paso a grados mi valor
            
        putText(frame,f'{a}', c)#Coloco mi valor del angulo
        
    cv.imshow('webcam',frame)

cv.destroyAllWindows()