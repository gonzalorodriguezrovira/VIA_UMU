#!/usr/bin/env python

# ejemplo de selección de ROI
#https://github.com/gonzalorodriguezrovira/VIA_UMU


import numpy as np
import cv2 as cv

from umucv.util import ROI, putText
from umucv.stream import autoStream
from umucv.util import Video

from collections import deque


cv.namedWindow("input")
cv.moveWindow('input', 0, 0)

region = ROI("input")

seleccionado=False#Variable que usare para saber en que parteb del programa estoy ya sea seleccion o observacion

video = Video(fps=15, codec="MJPG",ext="avi")#Inicializacion del video a grabar al detectar movimiento
kernel = np.ones((3,3),np.uint8)#Variable usada para conseguir el objeto que produzca movimiento sustrayendolo del fondo

d = deque(maxlen=20)#Creo una lista de fotogramas del video para comparar el mas reciente con el menos para poder detectar movimiento en el video

for key, frame in autoStream():
    video.write(frame)#Indico el frame que va a grabar mi video
    
    if region.roi:
        
        if seleccionado==False:#Fase de seleccionado de zona a observar
            
            [x1,y1,x2,y2] = region.roi 
            
        if key == ord('c'): #Empiezo a capturar movimiento en la region
            
            seleccionado=True
            trozo1 = frame[y1:y2+1, x1:x2+1]#Obtengo la imagen inicial la cual comparare a la hora de buscar movimiento, al usar
                                            #bgsub sirve con comparar una imagen negra con la fmask que se generara al detectar movimiento ya que no sera negra
            height, width, channels = trozo1.shape
            minimoMovimiento=height*width*0.3#Constantes usadas para delimitar los rangos en los ue grabar
        if key == ord('x'): #Dejo de capturar movimiento en la region 
            
            region.roi = []#Vacio las cordenadas de mi rectangulo
            if seleccionado==True:#En el caso de que tenga algo seleccionado y lo tenga en observacion al pusar x se destruira la ventana que detecta cambios
                
                seleccionado=False #Indico que debo volver a la fase de seleccionado   
                video.ON=False#Al eliminar la region observada se para el video si estaba siendo capturado
                video = Video(fps=15, codec="MJPG",ext="avi")#Cada vez que selecciono una nueva zona debo crear nuevas secuencias de videos, no todo en el mismo archivo
                
        if seleccionado==True:#Fase de observacion
            
            trozo = frame[y1:y2+1, x1:x2+1]#Recorto del frame la zona a observar y la guardo en otro frame
            d.appendleft(trozo)#Añado constantemente los trozos observados a la lista
            fgmask2 = cv.erode(trozo,kernel,iterations = 1)#Realizo la sustraccion de fondo que monstrara recortada solo al zona del movimiento
            fgmask2 = cv.medianBlur(fgmask2,3)
            masked = trozo.copy()
            masked[fgmask2==0] = 0
            cv.imshow('object', masked)
            
            if (cv.absdiff(d[0],d[-1])).sum()>minimoMovimiento: #Al detectar movimiento comparando la imagen en negro(inicial) con la que se esta capturando
                                                       #al encontrar que son distintas empiezo a grabar en caso contrario detengo 
                video.ON=True#Al encontrar que son distintas empiezo a grabar en caso contrario detengo 
            else:
                video.ON=False
       
        cv.rectangle(frame, (x1,y1), (x2,y2), color=(0,255,0), thickness=2)#Dibujo el rectangulo de la zona seleccionada
        
    cv.imshow('input',frame)

cv.destroyAllWindows()
video.release()
