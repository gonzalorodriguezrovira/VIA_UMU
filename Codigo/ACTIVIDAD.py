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
bgsub = cv.createBackgroundSubtractorMOG2(500, 16, False)#Creo la sustraccion de fondo

seleccionado=False#Variable que usare para saber en que parteb del programa estoy ya sea seleccion o observacion

video = Video(fps=15, codec="MJPG",ext="avi")#Inicializo el video que quiero grabar al detectar movimiento
kernel = np.ones((3,3),np.uint8)#Variable usada para conseguir el objeto que produzca movimiento sustrayendolo del fondo

for key, frame in autoStream():
    
    video.write(frame)#Indico el frame que va a grabar mi video
    
    if region.roi:#Si tengo ya una zona marcadaSS
        
        if seleccionado==False:#Fase de seleccionado de zona a observar
            
            [x1,y1,x2,y2] = region.roi 
            
        if key == ord('c'): #Empiezo a capturar movimiento en la region
            
            seleccionado=True#Indico que ya he seleccionado un parte a observar y puede pasar a la fase de observacion
            trozo1 = frame[y1:y2+1, x1:x2+1]#Obtengo la imagen inicial la cual comparare a la hora de buscar movimiento, al usar
                                            #bgsub sirve con comparar una imagen negra con la fmask que se generara al detectar movimiento ya que no sera negra
            height, width, channels = trozo1.shape
            minimoMovimiento=height*width*0.3 #Constantes usadas para delimitar los rangos en los ue grabar
            maximoMovimiento=height*width
            
        if key == ord('x'): #Dejo de capturar movimiento en la region 
            
            region.roi = []#Vacio las cordenadas de mi rectangulo
            
            if seleccionado==True:#En el caso de que tenga algo seleccionado y lo tenga en observacion al pusar x se destruira la ventana que detecta cambios
                
                cv.destroyWindow('mask')#En caso de que quiera dejar de observar una zona debo elimnar las ventamas que me transmitian la informacion de esa zona
                cv.destroyWindow('object')
                seleccionado=False#Indico que debo volver a la fase de seleccionado  
                video.ON=False#Al eliminar la region observada se para el video si estaba siendo capturado
                video = Video(fps=15, codec="MJPG",ext="avi")#Cada vez que selecciono una nueva zona debo crear nuevas secuencias de videos, no todo en el mismo archivo
                
        if seleccionado==True:#Fase de observacion
            
            trozo = frame[y1:y2+1, x1:x2+1]#Recorto del frame la zona a observar y la guardo en otro frame
            fgmask = bgsub.apply(trozo)#Le aplico la deteccion de movimiento a esa zona 
            cv.imshow('mask', fgmask)           
            fgmask2 = bgsub.apply(trozo, learningRate = -1 if seleccionado else 0)#Realizo la sustraccion de fondo que monstrara recortada solo al zona del movimiento
            fgmask2 = cv.erode(fgmask2,kernel,iterations = 1)
            fgmask2 = cv.medianBlur(fgmask2,3)
            masked = trozo.copy()
            masked[fgmask2==0] = 0
            cv.imshow('object', masked)
        
            
            if fgmask.sum()>minimoMovimiento and fgmask.sum()<maximoMovimiento: #Al detectar movimiento comparando la imagen en negro(inicial) con la que se esta capturando                                          
                video.ON=True#Al encontrar que son distintas empiezo a grabar en caso contrario detengo 
     
            else:
                video.ON=False
       
        cv.rectangle(frame, (x1,y1), (x2,y2), color=(0,255,0), thickness=2)#Dibujo el rectangulo de la zona seleccionada
        
    cv.imshow('input',frame)

cv.destroyAllWindows()
video.release()
