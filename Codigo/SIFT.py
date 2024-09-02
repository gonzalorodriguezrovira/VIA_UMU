#!/usr/bin/env python
#https://github.com/gonzalorodriguezrovira/VIA_UMU

import cv2 as cv
import time
import os

from umucv.stream import autoStream
from umucv.util import putText

KEYPOINTS=100#Cantidad de caracteristicas a observar de la imagen

sift = cv.SIFT_create(nfeatures=KEYPOINTS)#Creo la deteccion de caracteristicas

matcher = cv.BFMatcher()#Creo un objeto de coincidencia de características
imagenesAux = os.listdir('imagenes')#Obtengo las imagenes de mi carpeta de imagenes
imagenes=[]#Creo una lista de mis imagenes a buscar


for imagen in imagenesAux:#Me aseguro de coger solo imagenes de mi carpeta con formato .png o .jpg
    
    if '.jpg' in imagen or '.png' in imagen:
        imagenes.append(imagen)

for key, frame in autoStream():
  
    t0 = time.time()
    keypoints , descriptors = sift.detectAndCompute(frame, mask=None)#LLamo al detector para mi imagen de captura
    t1 = time.time()
    putText(frame, f'{len(keypoints)} pts  {1000*(t1-t0):.0f} ms')#Imprimo el retraso al llamar al detector
    
    for imagen in imagenes:#Recorro mis imagenes buscando cual de todas es la que corresponde con la imagen capturada
        
            frame2=cv.imread('imagenes/'+imagen)#Obtengo un frame de cada imagen a buscar
            keypoints2 , descriptors2 = sift.detectAndCompute(frame2, mask=None)#LLamo al detector para cada una de mis imagenes a buscar
            k0, d0, x0 = keypoints2, descriptors2, frame2
            t2 = time.time()
            matches = matcher.knnMatch(descriptors, d0, k=2)#Solicito las dos mejores coincidencias de cada punto, no solo la mejor
            t3 = time.time()
            good = []#Creo una lista de mis coincidencias correctas
            
            for m in matches:#Recorro mis coincidencias y las validas las añado a mi lista de correctas
                
                if len(m) >= 2:
                    best,second = m
                    if best.distance < 0.75*second.distance:
                        good.append(best)
                        
            if (len(good)>KEYPOINTS*0.2):#En caso de tener una coincidencia mayor al 20% se tomara como si se ha encontrado el objeto
                
                frame[40:140,0:100]=cv.resize(frame2,(100,100))#Coloco la imagen con la que tiene coincidencia mi frame capturado
                putText(frame ,f'{len(good)} matches  {1000*(t3-t2):.0f} ms {len(good)}%', #Imprimo informacion
                          orig=(5,36), color=(200,255,200))
                cv.imshow("SIFT",frame)
                break #Una vez encontrado el objeto ya no es necesario seguir comprobando el conjunto
                
            else:
                
                cv.imshow('SIFT', frame)
        
  
        
  

